from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

Base = declarative_base()

class Book(Base):
    __tablename__ = 'books'

    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    start_url = Column(String, nullable=False)
    total_chapters = Column(Integer, default=0)
    chapters = relationship("Chapter", back_populates="book")

class Chapter(Base):
    __tablename__ = 'chapters'

    id = Column(Integer, primary_key=True)
    book_id = Column(Integer, ForeignKey('books.id'), nullable=False)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    processed_content = Column(Text, nullable=True)
    status = Column(Boolean, default=False)
    processed = Column(Boolean, default=False)

    book = relationship("Book", back_populates="chapters")

# Создание подключения к базе данных
engine = create_engine("sqlite:///books.db", echo=True)

# Создание таблиц, если они ещё не существуют
Base.metadata.create_all(engine)

# Создание сессии для работы с базой данных
Session = sessionmaker(bind=engine)
session = Session()
