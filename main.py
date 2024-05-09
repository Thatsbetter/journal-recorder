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

def get_file_id(message_id):
    # get file_id with this message_id
    with Session() as session:
        file_association = session.query(FileId).filter_by(message_id=message_id).first()
        return file_association.file_id if file_association else None


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
    confirm_save = message.message_id
    cancel_save = "cancel"
    save_file_id(message_id=message.message_id, file_id=message.voice.file_id)
    markup.add(InlineKeyboardButton("Okay. Continue", callback_data=confirm_save),
               InlineKeyboardButton("I wanna try again", callback_data=cancel_save))
    bot.send_message(
        chat_id=message.chat.id,
        text="This Audio will be transcribed and saved to you journal",
        reply_markup=markup,
        reply_to_message_id=message.message_id
    )


@bot.callback_query_handler(func=lambda call:True)
def handle_query(call):
    if call.data == "cancel":
        # Notify user of cancellation
        bot.send_message(chat_id=call.message.chat.id,
                         text="Got it! It won´t be saved. \n You can try again.")
    else:
        try:
            file_id = get_file_id(message_id=call.data)
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


bot.infinity_polling(interval=0)
