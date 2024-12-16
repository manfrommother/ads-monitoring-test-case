from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from .models import SearchQueryCreate, SearchQueryResponse, AdvertCountResponse, TopAdvertisement
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
    pass