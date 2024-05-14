def get_why_journal_text():
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


def get_why_journal_button():
    return "🤔 Why Journal?"


def get_why_journal_callback():
    return "why_journal"

def get_entry_saved_text():
    return """Your thoughts have been saved! 🌟

Ready to revisit some memories? Just tap the buttons below to explore your previous entries. Enjoy the journey back! ✨"""


def get_remind_journal_text():
    return """"Hello! 🌟 It's been a couple of days since your last journal entry 📖✍️ \nWhy not take a moment now to share your thoughts or a special moment from your day?"""


def get_confirm_voice_save_text():
    return " \nWould you like to save this voice message as a journal entry? \n \nFeel free to re-record if you’d like to adjust anything."


def get_confirm_save_button():
    return "Yes, save it 📖"


def get_cancel_voice_save_button():
    return "No, record again 🔄"


def get_confirm_voice_save_callback():
    return "confirm_voice"


def get_cancel_callback():
    return "cancel"


def get_cancel_text():
    return "No worries, your entry has not been saved. \nWhenever you're ready, feel free to share your thoughts again. 😊"


def get_confirm_text_save_text():
    return "Would you like to add this text as a journal entry? \n \nFeel free to rewrite if you’d like to adjust your thoughts."


def get_cancel_text_save_button():
    return "No, write again 🔄"


def get_confirm_text_save_callback():
    return "confirm_text"


def get_select_time_frame_text():
    return "Choose a timeline to revisit your entries."


def get_last_week_button():
    return "🗓️ Last week"


def get_last_month_button():
    return "🗓️ Last month"


def get_last_week_callback():
    return "show_journal_1"


def get_last_month_callback():
    return "show_journal_4"


def get_no_entry_text():
    return "No entries found for this time frame. Why not add one now? 📖✨"


def get_main_menu_text():
    description = (
        "📘 <b>Welcome to Your Digital Journaling Assistant!</b> 📘\n\n"
        "<i>Start journaling anytime by sending a text or voice message. Here to help you capture your thoughts seamlessly!</i> 🖋️🎙️\n\n"
        "📝 <b>It helps you with:</b>\n"
        "- <b>Word Cloud:</b> See a visual of your most used words.\n"
        "- <b>View Your Journals:</b> Review entries or generate a word cloud.\n"
        "- <b>Discover Similar Entries:</b> Identify insights into recurring thoughts.\n\n"
        "Tap an option below or just send a message to begin journaling! 📝"
    )
    return description


def get_main_menu_button():
    return "🏠 Main Menu"


def get_main_menu_callback():
    return "main_menu"


def get_show_journal_button():
    return "🗂️ View Journals"


def get_show_journal_callback():
    return "journals_markup"


def get_wordcloud_callback():
    return "generate_wordcloud"


def get_wordcloud_button():
    return "☁️ Generate Word Cloud"


def get_wordcloud_description():
    return "Here's your word cloud, visualizing the themes and words you've expressed the most in your journal!"


def get_not_enough_entries_text():
    return "It seems you have less than 10 journal posts. A word cloud is more meaningful with more content.\nWhy not add some more thoughts? Every little bit adds up! 😊"


def get_similar_thoughts_text():
    return "🌟 While looking through your journal, I've discovered that you had similar Thoughts in the past. \nHere's a reflection of your thoughts over time:\n\n"
