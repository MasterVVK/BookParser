from fastapi import FastAPI, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from pydantic import BaseModel
from math import ceil
from contextlib import asynccontextmanager
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
class ChapterSchema(BaseModel):
    id: int
    chapter_number: int
    title: str
    content: str

    class Config:
        from_attributes = True

class PaginatedResponse(BaseModel):
    total_pages: int
    current_page: int
    total_items: int
    items: list[ChapterSchema]

# Эндпоинт: Получение необработанных глав книги с пагинацией
@app.get("/books/{book_id}/unprocessed-chapters", response_model=PaginatedResponse)
async def get_unprocessed_chapters(
    book_id: int,
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100)
):
    async with async_session_maker() as session:
        # Получить общее количество необработанных глав
        total_items_query = select(Chapter).where(Chapter.book_id == book_id, Chapter.processed == False)
        total_items = await session.execute(total_items_query)
        total_items_count = len(total_items.scalars().all())

        # Пагинация
        total_pages = ceil(total_items_count / page_size)
        if page > total_pages and total_pages > 0:
            raise HTTPException(status_code=404, detail="Page not found")

        # Получить главы для текущей страницы
        offset = (page - 1) * page_size
        chapters_query = (
            select(Chapter)
            .where(Chapter.book_id == book_id, Chapter.processed == False)
            .offset(offset)
            .limit(page_size)
        )
        result = await session.execute(chapters_query)
        chapters = result.scalars().all()

        return PaginatedResponse(
            total_pages=total_pages,
            current_page=page,
            total_items=total_items_count,
            items=chapters
        )
