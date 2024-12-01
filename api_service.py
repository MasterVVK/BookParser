from fastapi import FastAPI, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from pydantic import BaseModel
from contextlib import asynccontextmanager
import requests
from database.models import Book, Chapter

# Конфигурация базы данных
DATABASE_URL = "sqlite+aiosqlite:///./books.db"
engine = create_async_engine(DATABASE_URL, echo=True)

async_session_maker = sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
)

# Lifespan для создания таблиц
@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Book.metadata.create_all)
        await conn.run_sync(Chapter.metadata.create_all)
    yield

app = FastAPI(title="Book Parser API Service", lifespan=lifespan)

# Pydantic схемы
class BookSchema(BaseModel):
    id: int
    title: str
    start_url: str
    total_chapters: int

    class Config:
        from_attributes = True

class ChapterSchema(BaseModel):
    id: int
    chapter_number: int
    title: str
    content: str

    class Config:
        from_attributes = True

class ChapterProcessRequest(BaseModel):
    processed_content: str

class ChapterProcessResponse(BaseModel):
    message: str

# Эндпоинт: Получение списка книг
@app.get("/books", response_model=list[BookSchema])
async def get_books():
    """
    Возвращает список всех доступных книг.
    """
    async with async_session_maker() as session:
        result = await session.execute(select(Book))
        books = result.scalars().all()
        if not books:
            raise HTTPException(status_code=404, detail="No books found")
        return books

# Эндпоинт: Получение одной необработанной главы книги
@app.get("/books/{book_id}/unprocessed-chapter", response_model=ChapterSchema)
async def get_unprocessed_chapter(book_id: int, page: int = Query(1, ge=1)):
    """
    Возвращает одну необработанную главу для указанной книги.
    Параметр page определяет номер главы для выборки.
    """
    async with async_session_maker() as session:
        result = await session.execute(
            select(Chapter)
            .where(Chapter.book_id == book_id, Chapter.processed == False)
            .order_by(Chapter.chapter_number)
        )
        chapters = result.scalars().all()

        if page > len(chapters) or len(chapters) == 0:
            raise HTTPException(status_code=404, detail="Chapter not found")

        chapter = chapters[page - 1]
        return chapter

# Эндпоинт: Обработка одной главы книги
@app.post("/chapters/{chapter_id}/process", response_model=ChapterProcessResponse)
async def process_chapter(chapter_id: int, body: ChapterProcessRequest):
    """
    Обрабатывает одну главу и сохраняет обработанный контент.
    """
    async with async_session_maker() as session:
        chapter = await session.get(Chapter, chapter_id)
        if not chapter:
            raise HTTPException(status_code=404, detail="Chapter not found")

        if chapter.processed:
            return {"message": "Chapter is already processed"}

        chapter.processed_content = body.processed_content
        chapter.processed = True
        session.add(chapter)
        await session.commit()

        return {"message": "Chapter processed successfully"}
