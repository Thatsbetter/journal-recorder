import random

class WhyJournal:

    @staticmethod
    def description():
        return """
<b>Why Journal?</b>
Journaling is a powerful tool for self-reflection and stress relief. 
It helps you organize your thoughts, monitor your personal growth, and gain insight into your emotional well-being. 
For instance, according to a study published in the Journal of Psychiatric and Mental Health Nursing, participants who engaged in expressive writing reported a 28% reduction in stress levels.
By regularly recording your experiences and feelings, you can uncover patterns in your thoughts and behaviors, leading to better mental clarity and problem-solving skills.

<b>Getting started is easy:</b>

1. <b>Choose Your Moments </b>: 
Anytime you have a thought, a memory, or a detail from your day you wish to preserve, just send a text or a voice message to this bot.
2. <b>Write Regularly </b> : 
Make it a habit—try to journal daily. Even a few lines each day are enough to start reaping the benefits. Consistency is key!
3. <b>Express Freely </b>: 
There’s no judgment here. This bot is your private space to express yourself openly and honestly. The more truthful you are with your entries, the more meaningful your journaling experience will be.
4. <b>Reflect on Your Journey </b>: 
Use the bot's features to review past entries, see word clouds highlighting your common themes, or find similar past thoughts. This can be incredibly rewarding and insightful.

Don’t worry about structure or rules. Your journal is uniquely yours, and this bot is here to accommodate all forms of entries—whether you prefer to type them out or say them aloud.

Start journaling today! Tap a button to continue or simply send a message or voice note to add your first journal entry. 📘 🎙️
"""

    @staticmethod
    def button():
        return "🤔 Why Journal?"

    @staticmethod
    def callback():
        return "why_journal"


class WordCloud:
    @staticmethod
    def description():
        return "Here's your word cloud, visualizing the themes and words you've expressed the most in your journal!"

    @staticmethod
    def button():
        return "☁️ Generate Word Cloud"

    @staticmethod
    def callback():
        return "generate_wordcloud"

    @staticmethod
    def not_enough_entries():
        return "It seems you have less than 10 journal posts. A word cloud is more meaningful with more content.\nWhy not add some more thoughts? Every little bit adds up! 😊"


class TextJournal:
    @staticmethod
    def confirm_description():
        return " \nWould you like to save this voice message as a journal entry? \n \nFeel free to re-record if you’d like to adjust anything."

    @staticmethod
    def confirm_button():
        return "Yes, save it 📖"

    @staticmethod
    def confirm_callback():
        return "confirm_text"

    @staticmethod
    def cancel_description():
        return "No worries, your entry has not been saved. \nWhenever you're ready, feel free to share your thoughts again. 😊"

    @staticmethod
    def cancel_button():
        return "No, write again 🔄"

    @staticmethod
    def cancel_callback():
        return "cancel"

    @staticmethod
    def save_description():
        return "Your thoughts have been saved! 🌟\n\nReady to revisit some memories? Just tap the buttons below to explore your previous entries. Enjoy the journey back! ✨"


class VoiceJournal:
    @staticmethod
    def confirm_description():
        return " \nWould you like to save this voice message as a journal entry? \n \nFeel free to re-record if you’d like to adjust anything."

    @staticmethod
    def confirm_button():
        return "Yes, save it 📖"

    @staticmethod
    def confirm_callback():
        return "confirm_voice"

    @staticmethod
    def cancel_description():
        return "No worries, your entry has not been saved. \nWhenever you're ready, feel free to share your thoughts again. 😊"

    @staticmethod
    def cancel_button():
        return "No, record again 🔄"

    @staticmethod
    def cancel_callback():
        return "cancel"

    @staticmethod
    def save_description():
        return "Your thoughts have been saved! 🌟\n\nReady to revisit some memories? Just tap the buttons below to explore your previous entries. Enjoy the journey back! ✨"


class MainMenu:
    @staticmethod
    def description():
        description = (
            "📘 <b>Welcome to Your Digital Journaling Assistant!</b> 📘\n\n"
            "<i>Start journaling anytime by sending a text or voice message. Here to help you capture your thoughts seamlessly!</i> 🖋️🎙️\n\n"
            "📝 <b>It helps you with:</b>\n"
            "- <b>Word Cloud:</b> See a visual of your most used words.\n"
            "- <b>View Your Journals:</b> Review entries or generate a word cloud.\n"
            "- <b>Discover Similar Entries:</b> Identify insights into recurring thoughts.\n\n"
            "just send a text or voice message to begin journaling! 📝"
        )
        return description

    @staticmethod
    def button():
        return "🏠 Main Menu"

    @staticmethod
    def callback():
        return "main_menu"


class ShowJournal:
    @staticmethod
    def description():
        return "Choose a timeline to revisit your posts."

    @staticmethod
    def button():
        return "🗂️ View Journals"

    @staticmethod
    def callback():
        return "journals_markup"

    @staticmethod
    def last_week_button():
        return "🗓️ Last week"

    @staticmethod
    def last_month_button():
        return "🗓️ Last month"

    @staticmethod
    def last_week_callback():
        return "show_journal_1"

    @staticmethod
    def last_month_callback():
        return "show_journal_4"

    @staticmethod
    def no_entry_text():
        return "No entries found for this time frame. Why not add one now? 📖✨"


def get_remind_journal_text():
    messages = [
        "Hello! 🌟 It's been a couple of days since your last journal note 📖✍️ \nWhy not take a moment now to share your thoughts or a special moment from your day?",
        "🌞 Hello there! It's been a few days since your last journal note 📔✨. How about capturing a thought or memory from today? 🌸",
        "👋 Hi! We've missed your journaling vibes. It's been a little while since your last note 📒. Ready to unload your mind and jot down anything on your mind? 💭",
        "🌟 Hey! We noticed it's been a while since you last checked in 📓. How about taking a brief moment to write down things that stood out for you today? 🌻",
        "🌈 Hi there! Your journal is waiting to hear from you 📘. It's been some time since your last note - why not take a moment to reflect and jot something down? 🌿",
        "💫 Hey! It's been a few days since you last visited your journal 📙. Why not take a minute to jot down how you’re feeling or a memorable moment? 💖",
        "🧡 Hello! It’s been a little while since your last journal post 📖. How about reflecting on your day and sharing your thoughts? ✨"
    ]
    return random.choice(messages)


def get_similar_thoughts_text():
    return "🌟 While looking through your journal, I've discovered that you had similar Thoughts in the past. \n\nHere's a reflection of your thoughts over time:\n\n"
