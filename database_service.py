from sqlalchemy.orm import sessionmaker, scoped_session

from models import *

engine = get_engine()
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)


def save_file_id(message_id, file_id):
    with Session() as session:
        new_file_id = FileId(message_id=message_id, file_id=file_id)
        session.add(new_file_id)
        session.commit()


def save_journal_entry(chat_id, text):
    with Session() as session:
        new_entry = JournalEntry(chat_id=chat_id, text=text)
        session.add(new_entry)
        session.commit()


def fetch_journal_entries(chat_id):
    with Session() as session:
        return session.query(JournalEntry.text).filter_by(chat_id=chat_id).all()


def is_journal_entry_more_than_10(chat_id):
    with Session() as session:
        return len(session.query(JournalEntry.text).filter_by(chat_id=chat_id).all()) > 10


def get_file_id(message_id):
    # get file_id with this message_id
    with Session() as session:
        file_association = session.query(FileId).filter_by(message_id=message_id).first()
        return file_association.file_id if file_association else None


def save_text_id(message_id, text):
    with Session() as session:
        new_text_id = TextId(message_id=message_id, text=text)
        session.add(new_text_id)
        session.commit()


def get_text_id(message_id):
    # get text with this message_id
    with Session() as session:
        found_text = session.query(TextId).filter_by(message_id=message_id).first()
        return found_text.text if found_text else None


def get_all_chatids():
    with Session() as session:
        return session.query(JournalEntry.chat_id).distinct().all()


def get_last_entry(chat_id):
    with Session() as session:
        return session.query(JournalEntry).filter_by(chat_id=chat_id).order_by(
            JournalEntry.timestamp.desc()).first()
def init_db():
    init_models()