from collections import Counter
from io import BytesIO

from langdetect import detect, DetectorFactory, lang_detect_exception
import matplotlib.pyplot as plt
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from wordcloud import WordCloud

# Ensure consistent language detection results
DetectorFactory.seed = 0

# Download stopwords for various languages
nltk.download('stopwords')
nltk.download('punkt')


def get_language(text):
    try:
        return detect(text)
    except lang_detect_exception.LangDetectException:
        # Default to English if language detection fails
        return 'en'


def generate_word_frequencies(complete_text):
    lang = get_language(complete_text)
    # Select stopwords based on detected language, default to English if not available
    stop_words = set(stopwords.words('english' if lang not in stopwords.fileids() else lang))

    words = word_tokenize(complete_text)
    filtered_words = [word.lower() for word in words if word.isalpha() and word.lower() not in stop_words]
    word_counts = Counter(filtered_words)
    return word_counts


def create_word_cloud(word_counts):
    wordcloud = WordCloud(width=800, height=400,background_color="white").generate_from_frequencies(word_counts)

    # Create a bytes buffer for the image to save
    img = BytesIO()

    # Create the plot
    plt.figure(figsize=(10, 5))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.tight_layout(pad=0)

    # Save the plot to the bytes buffer
    plt.savefig(img, format='png')
    plt.close()  # Make sure to close the plt to prevent memory issues
    img.seek(0)  # Important: move to the start of the BytesIO object!

    return img
