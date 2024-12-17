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
    
    @staticmethod
    async def get_search_query_by_id(
        session: AsyncSession,
        query_id: int
    ) -> Optional[SearchQuery]:
        '''Получение поискового запроса по ID'''
        result = await session.execute(
            select(SearchQuery).filter(SearchQuery.id == query_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def save_advert_count(
        session: AsyncSession,
        query_id: int,
        count: int
    ) -> AdvertCount:
        '''Сохранение количества объявлений'''
        advert_count = AdvertCount(
            query_id=query_id,
            count=count
        )
        session.add(advert_count)
        await session.commit()
        await session.refresh(advert_count)
        return advert_count
    
    @staticmethod
    async def get_advert_counts(
        session: AsyncSession,
        query_id: int,
        start_date: Optional[datetime]=None,
        end_date: Optional[datetime]=None
    ) -> List[AdvertCount]:
        '''Получение статистики объявлений за период'''
        query = select(AdvertCount).filter(AdvertCount.query_id == query_id)

        if start_date:
            query = query.filter(AdvertCount.timestamp >= start_date)

        if end_date:
            query = query.filter(AdvertCount.timestamp <= end_date)

        query = query.order_by(AdvertCount.timestamp)

        result = await session.execute(query)
        return result.scalar().all()
    
    @staticmethod
    async def save_top_advertisements(
        session: AsyncSession,
        query_id: int,
        top_ads: List[dict]
    ) -> List[TopAdvertisement]:
        '''Сохранение топ 5 объявлений'''
        db_top_ads = [
            TopAdvertisement(
                query_id=query_id,
                title=ad.get('title', ''),
                price=ad.get('price', ''),
                url=ad.get('url', ''),
                additional_info=ad.get('additional_info', {})
            ) for ad in top_ads
        ]

        session.add_all(db_top_ads)
        await session.commit()

        for ad in db_top_ads:
            await session.refresh(ad)

        return db_top_ads
    
    @staticmethod
    async def get_top_advertisements(
        session: AsyncSession,
        query_id: int,
        limit: int=5
    ) -> List[TopAdvertisement]:
        '''Получение топ объявлений'''
        query = (
            select(TopAdvertisement)
            .filter(TopAdvertisement.query_id == query_id)
            .order_by(TopAdvertisement.timestamp.desc())
            .limit(limit)
        )

        result = await session.execute(query)
        return result.scalars().all()