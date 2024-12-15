from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import select
from typing import List, Optional
from datetime import datetime, timedelta
from config import settings

from .models import (
    SearchQuery,
    AdvertCount,
    TopAdvertisement,
    SearchQuertCreate,
    SearchQueryResponse
)

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True,
    future=True
)

AsyncSessionLocal = sessionmaker(
    engine,
    expire_on_commit=False,
    class_=AsyncSession
)

class DatabaseManager:
    '''Класс для управления операциями с БД'''
    @staticmethod
    async def get_db() -> AsyncSession:
        async with AsyncSessionLocal() as session:
            try:
                yield session
            finally:
                await session.close()
    
    @staticmethod
    async def create_search_query(
        session: AsyncSession,
        query: SearchQuertCreate
    ) -> SearchQueryResponse:
        '''Создание нового поискового запроса'''
        db_query = SearchQuery(
            search_phrase = query.search_phrase,
            region = query.region
        )
        session.add(db_query)
        await session.commit()
        await session.refresh(db_query)
        return SearchQueryResponse.model_validate(db_query)
    