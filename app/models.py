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