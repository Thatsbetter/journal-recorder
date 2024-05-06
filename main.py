import requests
import soundfile as sf
import telebot
from transformers import WhisperProcessor, WhisperForConditionalGeneration
import librosa
from credential import Credential

# Instantiate the bot using your token
TOKEN = Credential().get_telegram_token()
bot = telebot.TeleBot(TOKEN)

# Load Whisper models
processor = WhisperProcessor.from_pretrained("openai/whisper-small")
model = WhisperForConditionalGeneration.from_pretrained("openai/whisper-small")


def save_and_convert_audio(file_id):
    # Fetch and save the file from Telegram
    file_info = bot.get_file(file_id)
    file = requests.get(f'https://api.telegram.org/file/bot{TOKEN}/{file_info.file_path}')
    file_path = 'temp_voice.ogg'
    with open(file_path, 'wb') as f:
        f.write(file.content)

    # Assuming a direct use of .ogg might be problematic, a conversion might be necessary in practice
    return file_path


def transcribe_audio(path_to_audio):
    # Load audio file
    data, samplerate = librosa.load(path_to_audio, sr=None)  # Load audio as is

    # Check samplerate and resample if necessary
    if samplerate != 16000:
        data = librosa.resample(data, orig_sr=samplerate, target_sr=16000)
        samplerate = 16000  # Update samplerate to new value

    # Process and transcribe the audio
    input_features = processor(data, sampling_rate=samplerate, return_tensors="pt").input_features
    predicted_ids = model.generate(input_features)
    transcription = processor.batch_decode(predicted_ids, skip_special_tokens=True)

    return transcription[0]

@bot.message_handler(content_types=['voice'])
def handle_voice(message):
    try:
        # Save and reload the voice message
        path_to_ogg = save_and_convert_audio(message.voice.file_id)

        # Transcribe the audio
        transcription = transcribe_audio(path_to_ogg)

        # Send the transcription back to the user
        bot.reply_to(message, f"Transcribed text: {transcription}")
    except Exception as e:
        bot.reply_to(message, f"Oops, something went wrong: {e}")


# Start bot polling
bot.polling()
