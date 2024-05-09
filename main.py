# Bot token from BotFather
from datetime import datetime
import os

import ffmpeg
import requests
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
import telebot
from transformers import pipeline
from tempfile import NamedTemporaryFile
import shutil


from credential import Credential

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


Base.metadata.create_all(engine)


# Initialize the Whisper pipeline
def save_journal_entry(chat_id, text):
    with Session() as session:
        new_entry = JournalEntry(chat_id=chat_id, text=text)
        session.add(new_entry)
        session.commit()


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
    try:
        # Save and convert the received voice message
        path_to_mp3 = save_and_convert_audio(message.voice.file_id)

        # Transcribe the audio
        transcription = transcribe_audio(path_to_mp3)
        save_journal_entry(message.chat.id, transcription)

        # Send the transcription back to the user
        bot.reply_to(message, f"Thank you for sharing your thoughts! \n It has been saved.")

    except Exception as e:
        bot.reply_to(message, f"Oops, something went wrong: {e}")


bot.infinity_polling(interval=0)
