# Bot token from BotFather
from datetime import datetime
import os
import shutil
from tempfile import NamedTemporaryFile
import logging
import ffmpeg
import requests
from sqlalchemy import create_engine, Column, Integer, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from transformers import pipeline
from text_processing import generate_word_frequencies, create_word_cloud,find_similar_journal_entries
from datetime import datetime, timedelta
from credential import Credential
from apscheduler.schedulers.background import BackgroundScheduler

logging.basicConfig(filename='error.log', level=logging.ERROR,
                    format='%(asctime)s:%(levelname)s:%(message)s')
Base = declarative_base()
transcriber = pipeline(model="openai/whisper-small")
TOKEN = Credential().get_telegram_token()

bot = telebot.TeleBot(TOKEN)

engine = create_engine(Credential().get_conn_uri())
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)


class JournalEntry(Base):
    __tablename__ = 'journal_entries'
    id = Column(Integer, primary_key=True)
    chat_id = Column(Integer, nullable=False)
    text = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
class FileId(Base):
    __tablename__ = 'file_id'
    id = Column(Integer, primary_key=True)
    message_id = Column(Integer, nullable=False)
    file_id = Column(Text, nullable=False)

class TextId(Base):
    __tablename__ = 'text_id'
    id = Column(Integer, primary_key=True)
    message_id = Column(Integer, nullable=False)
    text = Column(Text, nullable=False)

Base.metadata.create_all(engine)


# Initialize the Whisper pipeline
def save_journal_entry(chat_id, text):
    with Session() as session:
        new_entry = JournalEntry(chat_id=chat_id, text=text)
        session.add(new_entry)
        session.commit()

def save_file_id(message_id,file_id):
    with Session() as session:
        new_file_id = FileId(message_id=message_id,file_id=file_id)
        session.add(new_file_id)
        session.commit()
def fetch_journal_entries(chat_id):
    with Session() as session:
        return session.query(JournalEntry.text).filter_by(chat_id=chat_id).all()

def get_file_id(message_id):
    # get file_id with this message_id
    with Session() as session:
        file_association = session.query(FileId).filter_by(message_id=message_id).first()
        return file_association.file_id if file_association else None

def save_text_id(message_id,text):
    with Session() as session:
        new_text_id = TextId(message_id=message_id,text=text)
        session.add(new_text_id)
        session.commit()

def get_text_id(message_id):
    # get text with this message_id
    with Session() as session:
        found_text = session.query(TextId).filter_by(message_id=message_id).first()
        return found_text.text if found_text else None


def remind_users_to_journal():
    try:
        with Session() as session:
            chat_ids = session.query(JournalEntry.chat_id).distinct().all()

            for chat_id, in chat_ids:
                last_entry = session.query(JournalEntry).filter_by(chat_id=chat_id).order_by(
                    JournalEntry.timestamp.desc()).first()
                if last_entry is None or (datetime.utcnow() - last_entry.timestamp) > timedelta(days=2):
                    bot.send_message(chat_id,
                                     "Hey! You haven't journaled in the last two days. Why not make a new entry today?")
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


def fetch_journal_entries_by_week(chat_id,weeks=1):
    one_week_ago = datetime.utcnow() - timedelta(weeks=weeks)
    with Session() as session:
        entries = session.query(JournalEntry).filter(
            JournalEntry.chat_id == chat_id,
            JournalEntry.timestamp >= one_week_ago
        ).all()
    return [(entry.text, entry.timestamp) for entry in entries]



@bot.message_handler(commands=['weekly_entries'])
def show_weekly_entries(message):
    chat_id = message.chat.id
    entries = fetch_journal_entries_by_week(chat_id)
    if entries:
        response = "\n\n".join([f"{entry[1].strftime('%Y-%m-%d %H:%M:%S')}: {entry[0]}" for entry in entries])
        send_chunked_message(chat_id, f"Here are your journal entries from the past week:\n{response}")
    else:
        bot.send_message(chat_id, "You have no journal entries from the past week.")


@bot.message_handler(commands=['monthly_entries'])
def show_monthly_entries(message):
    chat_id = message.chat.id
    entries = fetch_journal_entries_by_week(chat_id, weeks=4)
    if entries:
        response = "\n\n".join([f"{entry[1].strftime('%Y-%m-%d %H:%M:%S')}: {entry[0]}" for entry in entries])
        send_chunked_message(chat_id, f"Here are your journal entries from the past month:\n{response}")
    else:
        bot.send_message(chat_id, "You have no journal entries from the past month.")


@bot.message_handler(commands=['two_month_entries'])
def show_two_month_entries(message):
    chat_id = message.chat.id
    entries = fetch_journal_entries_by_month(chat_id, weeks=8)
    if entries:
        response = "\n\n".join([f"{entry[1].strftime('%Y-%m-%d %H:%M:%S')}: {entry[0]}" for entry in entries])
        send_chunked_message(chat_id, f"Here are your journal entries from the past two months:\n{response}")
    else:
        bot.send_message(chat_id, "You have no journal entries from the past two months.")

@bot.message_handler(content_types=['voice'])
def handle_voice(message):
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    confirm_save = f"confirm_voice:{message.message_id}"
    cancel_save = "cancel: "
    save_file_id(message_id=message.message_id, file_id=message.voice.file_id)
    markup.add(InlineKeyboardButton("Yes", callback_data=confirm_save),
               InlineKeyboardButton("No, I wanna try again", callback_data=cancel_save))
    bot.send_message(
        chat_id=message.chat.id,
        text="Do you want to add this voice message to your journal?",
        reply_markup=markup,
        reply_to_message_id=message.message_id
    )
@bot.message_handler(commands=['show_wordcloud'])
def send_word_cloud(message):
    entries = fetch_journal_entries(message.chat.id)
    complete_text = " ".join([entry.text for entry in entries])
    word_counts = generate_word_frequencies(complete_text)
    img = create_word_cloud(word_counts)
    bot.send_photo(chat_id=message.chat.id, photo=img, caption="Here's your word cloud!")
    img.close()  # Close the BytesIO object after sending to free memory
@bot.message_handler(content_types=['text'])
def handle_text(message):
    markup = InlineKeyboardMarkup()
    markup.row_width = 2
    confirm_save = f"confirm_text:{message.message_id}"
    cancel_save = "cancel: "
    save_text_id(message_id=message.message_id, text=message.text)
    markup.add(InlineKeyboardButton("Yes", callback_data=confirm_save),
               InlineKeyboardButton("No, I wanna try again", callback_data=cancel_save))
    bot.send_message(
        chat_id=message.chat.id,
        text="Do you want to add this text to your journal?",
        reply_markup=markup,
        reply_to_message_id=message.message_id
    )


@bot.callback_query_handler(func=lambda call:True)
def handle_query(call):
    split = call.data.split(":")
    chat_id = call.message.chat.id
    if split[0] == "cancel":
        # Notify user of cancellation
        bot.send_message(chat_id=chat_id,
                         text="Got it! It won´t be saved. \n You can try again.")
    elif split[0] == "confirm_voice":
        try:
            file_id = get_file_id(message_id=split[1])
            # Process the audio after confirmation
            path_to_mp3 = save_and_convert_audio(file_id=file_id)

            # Transcribe the audio
            transcription = transcribe_audio(path_to_mp3)

            # Save the journal entry
            save_journal_entry(chat_id, transcription)

            # Respond to the user
            bot.send_message(chat_id=chat_id,
                             text="Thank you for sharing your thoughts! It has been saved.")

            similar_entries = find_similar_journal_entries(fetch_journal_entries_by_week(chat_id,16))
            if similar_entries:
                response = "Just so you know, you had similar Thoughts in past 4 Months :\n"
                for entry, timestamp, score in similar_entries:
                    date = timestamp.strftime('%Y-%m-%d %H:%M')
                    response += f"- {date}: {entry} (Score: {score:.2f})\n"
                send_chunked_message(chat_id, response)
        except Exception as e:
            logging.error(f"Error handling query: {str(e)}")
            bot.answer_callback_query(call.id, "Failed to save you journal.")
    elif split[0] == "confirm_text":
        try:
            text = get_text_id(message_id=split[1])

            # Save the journal entry
            save_journal_entry(chat_id, text)

            # Respond to the user
            bot.send_message(chat_id=chat_id,
                             text="Thank you for sharing your thoughts! It has been saved.")
            similar_entries = find_similar_journal_entries(fetch_journal_entries_by_week(chat_id, 16))
            if similar_entries:
                response = "Just so you know, you had similar Thoughts in past 4 Months :\n \n"
                for entry, timestamp in similar_entries:
                    date = timestamp.strftime('%Y-%m-%d %H:%M')
                    response += f"- {date}: {entry}\n"
                send_chunked_message(chat_id, response)
        except Exception as e:
            logging.error(f"Error handling query: {str(e)}")
            bot.answer_callback_query(call.id, "Failed to save you journal.")


# Initialize scheduler
scheduler = BackgroundScheduler()
scheduler.add_job(remind_users_to_journal, 'cron', day_of_week='*', hour=19, minute=0)  # Run daily at 9:00 AM
scheduler.start()

# Setup polling
try:
    bot.polling(none_stop=True, interval=0, timeout=20)
except Exception as e:
    logging.error(f"Bot polling failed: {e}")
finally:
    # This ensures that the scheduler is properly shut down when the polling loop is stopped
    scheduler.shutdown()