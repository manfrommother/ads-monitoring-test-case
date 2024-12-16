from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


Base = declarative_base()

class SearchQuery(Base):
    '''Модель для хранения поисковых запросов'''
    __tablename__ = 'search_queries'

    id = Column(Integer, primary_key=True, index=True)
    search_phrase = Column(String, index=True, nullable=False)
    region = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    #связь с историей подсчета объявлений
    counts = relationship('AdvertCount', back_populates='query')
    #Связь с топом объявлений
    top_ads = relationship('TopAdvertisement', back_populates='query')

class AdvertCount(Base):
    '''Модель для хранения истории подсчета'''
    __tablename__ = 'advert_counts'

    id = Column(Integer, primary_key=True, index=True)
    query_id = Column(Integer, ForeignKey('searh_queries.id'), nullable=False)
    count = Column(DateTime, default=datetime.utcnow)

    query = relationship('SearchQuery', back_populates='counts')

class TopAdvertisement(Base):
    ''' Модель для хранения топ 5 объявлений'''
    __tablename__ = 'top_advertisements'

    id = Column(Integer, primary_key=True, index=True)
    query_id = Column(Integer, ForeignKey('searcg_queries.id'), nullable=False)
    title = Column(String, nullable=False)
    price = Column(String)
    url = Column(String, nullable=False)
    additional_info = Column(JSON)
    timestamp = Column(DateTime, default=datetime.utcnow)

    query = relationship('SearchQuery', back_populates='top_ads')

#Pydantic модели для валидации входящих\исходящих данных
class SearchQueryCreate(BaseModel):
    '''Схема для создания нового поиска'''
    search_phrase: str = Field(..., min_length=1, max_length=255)
    region: str = Field(..., min_length=1, max_length=100)

class SearchQueryResponse(SearchQueryCreate):
    '''Схема ответа после создания поиска'''

    id: int
    created_at: datetime

    class Config:
        orm_mode = True

class AdvertCountResponse(BaseModel):
    '''схема для возврата топ объявлений'''
    title: str
    price: Optional[str]
    url: str
    additional_info: Optional[dict]
    timestamp: datetime

    class Config:
        orm_mode = True