# Bot token from BotFather
import ffmpeg
import requests
import telebot
from transformers import pipeline
from credential import Credential
import os

# Initialize the Whisper pipeline
transcriber = pipeline(model="openai/whisper-small")
TOKEN = Credential().get_telegram_token()

bot = telebot.TeleBot(TOKEN)

def save_and_convert_audio(file_id):
    # Fetch file using Telegram's API
    file_info = bot.get_file(file_id)
    file = requests.get('https://api.telegram.org/file/bot{0}/{1}'.format(TOKEN, file_info.file_path))

    # Save the OGG file temporarily
    with open('temp_voice.ogg', 'wb') as f:
        f.write(file.content)

    # Convert OGG to MP3 using ffmpeg (as a more compatible format for many systems)
    ffmpeg.input('temp_voice.ogg').output('temp_voice.mp3').run(overwrite_output=True)

    return 'temp_voice.mp3'


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

        # Send the transcription back to the user
        bot.reply_to(message, f"Transcribed text: {transcription}")

    except Exception as e:
        bot.reply_to(message, f"Oops, something went wrong: {e}")


bot.infinity_polling(interval=0)
