# Bot token from BotFather
from datetime import timedelta, datetime
import logging
import os
import shutil
from tempfile import NamedTemporaryFile

from apscheduler.schedulers.background import BackgroundScheduler
import ffmpeg
import requests
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from transformers import pipeline

from consts import *
from credential import Credential
from database_service import save_text_id, save_file_id, save_journal_entry, get_last_entry, get_text_id, get_file_id, \
    get_all_chatids, fetch_journal_entries, is_journal_entry_more_than_10, init_db, get_journals_by_week
from text_processing import generate_word_frequencies, create_word_cloud, find_similar_journal_entries

logging.basicConfig(filename='error.log', level=logging.ERROR,
                    format='%(asctime)s:%(levelname)s:%(message)s')
transcriber = pipeline(model="openai/whisper-small")
TOKEN = Credential().get_telegram_token()

bot = telebot.TeleBot(TOKEN)
init_db()


def remind_users_to_journal():
    try:
        chat_ids = get_all_chatids()
        for chat_id, in chat_ids:
            last_entry = get_last_entry(chat_id)
            if last_entry is None or (datetime.utcnow() - last_entry.timestamp) > timedelta(days=2):
                bot.send_message(chat_id,
                                 get_remind_journal_text())
    except Exception as e:
        logging.error(f"Failed to send reminder: {e}")


def send_chunked_message(chat_id, text, max_length=4096):
    """
    Send a message in chunks if it exceeds Telegram's maximum message length.
    Splits the message at line breaks when possible, within the maximum allowed length.

    Args:
        chat_id (int): Telegram chat ID to send the message to.
        text (str): Text to be sent.
        max_length (int): Maximum length of each message chunk. Defaults to 4096.
    """
    while len(text) > 0:
        # Check if the text is within the maximum length
        if len(text) <= max_length:
            bot.send_message(chat_id, text)
            break

        # Find the nearest line break within the maximum length
        chunk_limit = text.rfind('\n', 0, max_length)
        if chunk_limit == -1:
            # No line break found, forced to cut at max_length
            chunk_limit = max_length

        # Send the current chunk
        bot.send_message(chat_id, text[:chunk_limit])

        # Remove the sent part from the text
        text = text[chunk_limit:].lstrip()


def save_and_convert_audio(file_id):
    file_info = bot.get_file(file_id)
    file_response = requests.get('https://api.telegram.org/file/bot{0}/{1}'.format(TOKEN, file_info.file_path),
                                 stream=True)

    with NamedTemporaryFile(delete=False, suffix='.ogg') as temp_file:
        shutil.copyfileobj(file_response.raw, temp_file)

    path_to_ogg = temp_file.name
    path_to_mp3 = path_to_ogg.replace('.ogg', '.mp3')

    # Convert OGG to MP3 using ffmpeg
    ffmpeg.input(path_to_ogg).output(path_to_mp3).run(overwrite_output=True)

    # Clean up the original OGG file
    os.remove(path_to_ogg)

    return path_to_mp3


def transcribe_audio(path_to_audio):
    # Use Whisper to transcribe the audio
    transcription = transcriber(path_to_audio)
    return transcription['text']


def fetch_journal_entries_by_week(chat_id, weeks=1):
    weeks_ago = datetime.utcnow() - timedelta(weeks=weeks)
    entries = get_journals_by_week(chat_id, weeks_ago)
    return [(entry.text, entry.timestamp) for entry in entries]


def get_weekly_entries(chat_id, week=1):
    entries = fetch_journal_entries_by_week(chat_id)
    if entries:
        response = "\n\n".join([f"{entry[1].strftime('%Y-%m-%d %H:%M:%S')}: {entry[0]}" for entry in entries])
        return response
    else:
        return None


@bot.message_handler(content_types=['voice'])
def handle_voice(message):
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    confirm_save = f"{get_confirm_voice_save_callback()}:{message.message_id}"
    cancel_save = get_cancel_callback()
    save_file_id(message_id=message.message_id, file_id=message.voice.file_id)
    markup.add(InlineKeyboardButton(get_confirm_save_button(), callback_data=confirm_save),
               InlineKeyboardButton(get_cancel_voice_save_button(), callback_data=cancel_save))
    bot.send_message(
        chat_id=message.chat.id,
        text=get_confirm_voice_save_text(),
        reply_markup=markup,
        reply_to_message_id=message.message_id
    )


@bot.message_handler(content_types=['text'])
def handle_text(message):
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    confirm_save = f"{get_confirm_text_save_callback()}:{message.message_id}"
    cancel_save = "cancel: "
    save_text_id(message_id=message.message_id, text=message.text)
    markup.add(InlineKeyboardButton(get_confirm_save_button(), callback_data=confirm_save),
               InlineKeyboardButton(get_cancel_text_save_button(), callback_data=cancel_save))
    bot.send_message(
        chat_id=message.chat.id,
        text=get_confirm_text_save_text(),
        reply_markup=markup,
        reply_to_message_id=message.message_id
    )


@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    split = call.data.split(":")
    chat_id = call.message.chat.id
    if split[0] == get_cancel_callback():
        markup = InlineKeyboardMarkup()
        markup.row_width = 2
        markup.add(InlineKeyboardButton(get_show_journal_button(), callback_data=get_show_journal_callback()),
                   InlineKeyboardButton(get_main_menu_button(), callback_data=get_main_menu_callback()))
        # Notify user of cancellation
        bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id,
                              text=get_cancel_text(), reply_markup=markup)
    elif split[0] == get_show_journal_callback():
        markup = InlineKeyboardMarkup()
        markup.row_width = 2
        markup.add(InlineKeyboardButton(get_last_week_button(), callback_data=get_last_week_callback()),
                   InlineKeyboardButton(get_last_month_button(), callback_data=get_last_month_callback()),
                   InlineKeyboardButton(get_main_menu_button(), callback_data=get_main_menu_callback()))
        # Respond to the user
        bot.send_message(chat_id=chat_id,
                         text=get_select_time_frame_text(),
                         reply_markup=markup)

    elif split[0] == get_last_week_callback():
        response = get_weekly_entries(chat_id)
        if response is not None:
            markup = InlineKeyboardMarkup()
            markup.row_width = 2
            markup.add(InlineKeyboardButton(get_last_month_button(), callback_data=get_last_month_callback()),
                       InlineKeyboardButton(get_main_menu_button(), callback_data=get_main_menu_callback()))
            bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id,
                                  text=response,
                                  reply_markup=markup)
        else:
            markup = InlineKeyboardMarkup()
            markup.row_width = 1
            markup.add(InlineKeyboardButton(get_main_menu_button(), callback_data=get_main_menu_callback()))
            bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id,
                                  text=get_no_entry_text(),
                                  reply_markup=markup)
    elif split[0] == get_last_month_callback():
        response = get_weekly_entries(chat_id, 4)
        if response:
            markup = InlineKeyboardMarkup()
            markup.row_width = 2
            markup.add(InlineKeyboardButton(get_last_week_button(), callback_data=get_last_week_callback()),
                       InlineKeyboardButton(get_main_menu_button(), callback_data=get_main_menu_callback()))
            bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id,
                                  text=response,
                                  reply_markup=markup)
        else:
            markup = InlineKeyboardMarkup()
            markup.row_width = 1
            markup.add(InlineKeyboardButton(get_main_menu_button(), callback_data=get_main_menu_callback()))
            bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id,
                                  text=get_no_entry_text(),
                                  reply_markup=markup)

    elif split[0] == get_main_menu_callback():
        markup = InlineKeyboardMarkup()
        markup.row_width = 2
        why_journal = "why_journal"
        markup.add(InlineKeyboardButton(get_show_journal_button(), callback_data=get_show_journal_callback()),
                   InlineKeyboardButton(get_wordcloud_button(), callback_data=get_wordcloud_callback()),
                   InlineKeyboardButton("🤔 Why Journal?", callback_data=why_journal))
        bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id,
                              text=description, reply_markup=markup, parse_mode='HTML')

    elif split[0] == get_wordcloud_callback():
        if is_journal_entry_more_than_10(chat_id):
            entries = fetch_journal_entries(chat_id)
            complete_text = " ".join([entry.text for entry in entries])
            word_counts = generate_word_frequencies(complete_text)
            img = create_word_cloud(word_counts)
            bot.send_photo(chat_id=chat_id, photo=img, caption=get_wordcloud_description())
            img.close()
        else:
            markup = InlineKeyboardMarkup()
            markup.row_width = 1
            markup.add(InlineKeyboardButton(get_main_menu_button(), callback_data=get_main_menu_callback()))
            bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id,
                                  text=response,
                                  reply_markup=markup)
    elif split[0] == "why_journal":
        markup = InlineKeyboardMarkup()
        markup.row_width = 1
        response = get_why_journal_text()
        markup.add(InlineKeyboardButton(get_main_menu_button(), callback_data=get_main_menu_callback()))
        bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id,
                              text=response, parse_mode='HTML',
                              reply_markup=markup)
    elif split[0] == get_confirm_voice_save_callback():
        try:
            file_id = get_file_id(message_id=split[1])
            # Process the audio after confirmation
            path_to_mp3 = save_and_convert_audio(file_id=file_id)

            # Transcribe the audio
            transcription = transcribe_audio(path_to_mp3)

            # Save the journal entry
            save_journal_entry(chat_id, transcription)

            markup = InlineKeyboardMarkup()
            markup.row_width = 2
            markup.add(InlineKeyboardButton(get_show_journal_button(), callback_data=get_show_journal_callback()),
                       InlineKeyboardButton(get_main_menu_button(), callback_data=get_main_menu_callback()))
            # Respond to the user
            bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id,
                             text=get_entry_saved_text(),
                             reply_markup=markup)
            bot.set_message_reaction(chat_id=chat_id, message_id=split[1],
                                     reaction=[telebot.types.ReactionTypeEmoji("👍")])
            fetched_entries = fetch_journal_entries_by_week(chat_id, 16)
            if fetched_entries:
                similar_entries = find_similar_journal_entries(fetched_entries)
                if similar_entries:
                    response = "Just so you know, you had similar Thoughts in past Months :\n"
                    for entry, timestamp in similar_entries:
                        date = timestamp.strftime('%Y-%m-%d %H:%M')
                        response += f"- {date}: {entry} (Score: {score:.2f})\n"
                    send_chunked_message(chat_id, response)
        except Exception as e:
            logging.error(f"Error handling query: {str(e)}")
            bot.answer_callback_query(call.id, "Failed to save you journal.")
    elif split[0] == get_confirm_text_save_callback():
        try:
            text = get_text_id(message_id=split[1])

            # Save the journal entry
            save_journal_entry(chat_id, text)

            markup = InlineKeyboardMarkup()
            markup.row_width = 2
            markup.add(InlineKeyboardButton(get_show_journal_button(), callback_data=get_show_journal_callback()),
                       InlineKeyboardButton(get_main_menu_button(), callback_data=get_main_menu_callback()))
            # Respond to the user
            bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id,
                             text=get_entry_saved_text(),
                             reply_markup=markup)
            bot.set_message_reaction(chat_id=chat_id, message_id=split[1],
                                     reaction=[telebot.types.ReactionTypeEmoji("👍")])

            fetched_entries = fetch_journal_entries_by_week(chat_id, 16)
            if fetched_entries:
                similar_entries = find_similar_journal_entries(fetched_entries)
                if similar_entries:
                    response = "Just so you know, you had similar Thoughts in past Months :\n \n"
                    for entry, timestamp in similar_entries:
                        date = timestamp.strftime('%Y-%m-%d %H:%M')
                        response += f"- {date}: {entry}\n"
                    send_chunked_message(chat_id, response)
        except Exception as e:
            logging.error(f"Error handling query: {str(e)}")
            bot.answer_callback_query(call.id, "Failed to save you journal.")


# Initialize scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(remind_users_to_journal, 'cron', day_of_week='*', hour=19, minute=0)  # Run daily at 7:00 PM
scheduler.start()

# Setup polling
try:
    bot.infinity_polling(interval=0)
except Exception as e:
    logging.error(f"Bot polling failed: {e}")
finally:
    # This ensures that the scheduler is properly shut down when the polling loop is stopped
    scheduler.shutdown()
