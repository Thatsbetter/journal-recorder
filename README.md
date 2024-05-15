# Telegram Journal Bot

## Description

The Telegram Journal Bot allows users to maintain a journal using either text or voice messages. The bot offers features
such as automatic transcription of voice messages, weekly reminders, word cloud generation, and detection of similar
journal entries using advanced machine learning techniques.<br>

Inspiration: The need for a digital journal bot that leverages natural language processing (NLP).

Link to the Bot: https://t.me/JournalCompanionBot

## Features

- Voice Message Transcription: Convert voice messages to text using the OpenAI Whisper model.
- Automated Reminders: Sends periodic reminders to users if they haven't journaled for a while.
- Word Cloud Generation: Generate a word cloud from the most frequently occurring words in the user's journal entries.
- Similar Entries Detection: Find and display journal entries that have similar content based on TF-IDF vectorization
  and cosine similarity.
- Historical Journal Display: Users can view their journal entries by week or month.

## Installation

1. Clone the repository:

```sh
git clone https://github.com/Thatsbetter/journal-recorder
cd journal-recorder
``` 

2. Install required packages:

sh
pip install -r requirements.txt

3. Setup Database:
    - Ensure you have a PostgreSQL database or any other supported database.
    - Update the database configuration in `credential.py`.

4. Obtain Telegram Bot Token:
    - Get your bot token from https://core.telegram.org/bots#3-how-do-i-create-a-bot">BotFather.
    - Store the token in `credential.json` file.

5. Download NLTK Data:

sh
python -m nltk.downloader stopwords punkt

## Usage

1. Run the bot:

sh
python main.py

2. Interact with the bot using Telegram:
    - `/start`: Start the bot and display the main menu.
    - Text messages are automatically processed and stored after confirmation.
    - Voice messages are transcribed and stored after confirmation.

## Machine Learning Components

Voice Message Transcription

- Model: OpenAI Whisper Model
- Functionality: Converts voice messages into text. When a user sends a voice message, the bot transcribes the audio and
  saves it as a journal entry.

Word Cloud Generation

- Techniques: Natural Language Processing (NLP), Frequency Analysis
- Functionality: Analyzes journal entries to generate word frequencies, removes common stopwords, and creates a word
  cloud to visualize the most frequent words.

Similar Journal Entries Detection

- Techniques: TF-IDF Vectorization, Cosine Similarity
- Functionality: Detects similar journal entries by converting texts into numerical vectors using TF-IDF and calculating
  cosine similarity. Entries with a high similarity score are highlighted to the user to identify recurring themes or
  emotions.

How It Works

1. Transcription Process:
    - User sends a voice message.
    - The bot transcribes the audio using the Whisper model and saves it as a journal entry.

2. Word Cloud Process:
    - User requests a word cloud.
    - The bot processes journal entries, generates word frequencies, and creates a word cloud image.

3. Similar Entries Detection:
    - The bot compares new journal entries with past entries using TF-IDF and cosine similarity.
    - Similar entries are identified and summarized for the user, highlighting recurring themes or concerns.

## License

This project is licensed under the MIT License - see the LICENSE.md file for details.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## Acknowledgements

- OpenAI: For the Whisper model used for transcription of voice messages to text.
- Hugging Face: For providing the transformer models and pipeline.
- NLTK: For providing natural language processing tools used in text analysis.
- Matplotlib: For generating word cloud images.
- FFmpeg: For audio conversion functionality.
- Scikit-learn: For offering TF-IDF vectorization and cosine similarity tools.
- PyTelegramBotAPI: For providing the Python wrapper for the Telegram Bot API.
- APScheduler: For the scheduling functionality used for reminder messages.

---

Feel free to reach out for contributions, bug reports, or feature requests!
