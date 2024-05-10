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
from text_processing import generate_word_frequencies, create_word_cloud
from datetime import datetime, timedelta
from credential import Credential
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
    if split[0] == "cancel":
        # Notify user of cancellation
        bot.send_message(chat_id=call.message.chat.id,
                         text="Got it! It won´t be saved. \n You can try again.")
    elif split[0] == "confirm_voice":
        try:
            file_id = get_file_id(message_id=split[1])
            # Process the audio after confirmation
            path_to_mp3 = save_and_convert_audio(file_id=file_id)

            # Transcribe the audio
            transcription = transcribe_audio(path_to_mp3)

            # Save the journal entry
            save_journal_entry(call.message.chat.id, transcription)

            # Respond to the user
            bot.send_message(chat_id=call.message.chat.id,
                             text="Thank you for sharing your thoughts! It has been saved.")
        except Exception as e:
            logging.error(f"Error handling query: {str(e)}")
            bot.answer_callback_query(call.id, "Failed to save you journal.")
    elif split[0] == "confirm_text":
        try:
            text = get_text_id(message_id=split[1])

            # Save the journal entry
            save_journal_entry(call.message.chat.id, text)

            # Respond to the user
            bot.send_message(chat_id=call.message.chat.id,
                             text="Thank you for sharing your thoughts! It has been saved.")
        except Exception as e:
            logging.error(f"Error handling query: {str(e)}")
            bot.answer_callback_query(call.id, "Failed to save you journal.")


bot.infinity_polling(interval=0)
