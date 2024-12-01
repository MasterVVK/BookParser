from fastapi import FastAPI, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from pydantic import BaseModel
from contextlib import asynccontextmanager
from database.models import Book  # Импорт модели Book из существующего проекта

# Конфигурация базы данных
DATABASE_URL = "sqlite+aiosqlite:///./books.db"
engine = create_async_engine(DATABASE_URL, echo=True)

# Настройка асинхронной сессии
async_session_maker = sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
)

# Pydantic схема для сериализации данных книги (без excluded_texts)
class BookSchema(BaseModel):
    id: int
    title: str
    start_url: str
    total_chapters: int

    class Config:
        from_attributes = True  # Новый параметр вместо orm_mode

# Lifespan для создания таблиц при старте сервиса
@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Book.metadata.create_all)
    yield

# Инициализация FastAPI приложения
app = FastAPI(title="Book Parser API Service", version="1.0.0", lifespan=lifespan)

# Эндпоинт для получения списка книг
@app.get("/books", response_model=list[BookSchema])
async def get_books():
    async with async_session_maker() as session:
        result = await session.execute(select(Book))
        books = result.scalars().all()
        if not books:
            raise HTTPException(status_code=404, detail="No books found")
        return books
