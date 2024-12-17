from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from datetime import datetime, timedelta

from .models import SearchQueryCreate, SearchQueryResponse, AdvertCountResponse, TopAdvertisementResponse
from .crud import DatabaseManager
from .parser import AvitoParser
from .config import settings

app = FastAPI(
    title='Avito Parser',
    description='Сервис мониторинга объявлений в авито',
    version='1.0.0'
)

parser = AvitoParser()

@app.post('/add', response_model=SearchQueryResponse)
async def add_search_query(
    query: SearchQueryCreate,
    db: AsyncSession=Depends(DatabaseManager.get_db)
):
    '''Регистрация нового поискового запроса'''
    try:
        created_query = await DatabaseManager.create_search_query(db, query)

        total_ads = await parser.get_total_ads_count(query.search_phrase, query.region)
        await DatabaseManager.save_advert_count(db, created_query.id, total_ads)

        top_ads = await parser.get_top_advertisements(query.search_phrase, query.region)
        await DatabaseManager.save_top_advertisements(db, created_query.id, top_ads)

        return created_query
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@app.get('/stat/{query_id}', response_model=List[AdvertCountResponse])
async def get_query_statistics(
    query_id: int,
    days: int=30,
    db: AsyncSession=Depends(DatabaseManager.get_db)
):
    '''Получение статистики объявлений для конкретного запроса'''

    try:
        query = await DatabaseManager.get_search_query_bu_id(db, query_id)
        if not query:
            raise HTTPException(status_code=404, detail='Запрос не найден')
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)

        stats = await DatabaseManager.get_advert_counts(
            db, query_id, start_date, end_date
        )
        return stats
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@app.get('/top/{query_id}', response_model=List[TopAdvertisementResponse])
async def get_top_advertisements(
    query_id: int,
    limit: int=5,
    db: AsyncSession=Depends(DatabaseManager.get_db)
):
    '''Получение топ объявлений для конкретного запроса'''

    try:
        query = await DatabaseManager.get_search_query_by_id(db, query_id)
        if not query:
            raise HTTPException(status_code=404, detail='Запрос не найден')
        
        top_ads = await DatabaseManager.get_top_advertisements(db, query_id, limit)

        return top_ads
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@app.on_event('startup')
async def startup():
    '''Обработчик запуска приложения'''
    pass

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(
        'main:app',
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=True
    )