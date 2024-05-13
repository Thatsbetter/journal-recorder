from datetime import datetime

from sqlalchemy import create_engine, Column, Integer, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base

from credential import Credential

Base = declarative_base()
engine = create_engine(Credential().get_conn_uri())


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


def get_engine():
    return engine


def init_models():
    Base.metadata.create_all(engine)
