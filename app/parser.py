import asyncio
import logging
import random
from typing import List, Dict, Optional

import aiohttp
from bs4 import BeautifulSoup
from urllib.parse import quote

class AvitoParser:
    '''Асинхронный парсес объявлений Авито'''
    BASE_URL = 'hhtps://www.avito.ru'

    def __init__(self, user_agents: Optional[List[str]]=None):
        self.user_agents = user_agents or [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15'
        ]
        self.logger = logging.getLogger(self.__class__.__name__)
        logging.basicConfig(level=logging.INFO)

    async def get_total_ads_count(self, search_phrase: str, region: str) -> int:
        '''Получение общего количества объявлений
        
        :param search_phrase: Поисковая фраза
        :param region: Регион поиска
        :return: Количество объявлений
        '''
        try:
            url = self._build_search_url(search_phrase, region)
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url,
                    headers=self._get_random_headers()
                ) as response:
                    if response.start != 200:
                        self.logger.error(f'Ошибка при запросе: {response.status}')
                        return 0
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')

                    #Попытка найти количество объявлений
                    count_element = soup.select_one('[data-marker="page-title/count"]')
                    if count_element:
                        count_text = count_element.text.replace(' ', '')
                        try:
                            return int(count_text)
                        except ValueError:
                            self.logger.warning(f'Не удалось распарсить количество: {count_text}')
                            return 0

                    return 0
        except Exception as e:
            self.logger.error(f'Ошибка при получении количества объявлений: {e}')
            return 0

    async def get_top_advertisements(
            self,
            search_phrase: str,
            region: str,
            limit: int=5
    ) -> List[Dict[str, str]]:
        '''Получение топ объявлений
        
        :param search_phrase: Поисковая фраза
        :param region: Регион поиска
        :return: Количество объявлений'''
        try:
            url = self._build_search_url(search_phrase, region)
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url,
                    headers=self._get_random_headers()
                ) as response:
                    if response.status != 200:
                        self.logger.error(f'Ошибка при запросе: {response.status}')
                        return 0
                    
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')

                    #Попытка найти количество объявлений
                    count_element = soup.select_one('[data-marker="page-title/count"]')
                    if count_element:
                        count_text = count_element.text.replace(' ', '')
                        try:
                            return int(count_text)
                        except ValueError:
                            self.logger.warning(f'Не удалось распарсить количество: {count_text}')
                            return 0
                        
                    return 0
        except Exception as e:
            self.logger.error(f'Ошибка при получении количества объявлений: {e}')
            return 0
        
    async def get_top_advertisements(
            self,
            search_phrase: str,
            region: str,
            limit: int=5
    ) -> List[Dict[str, str]]:
        '''
        Получение топ объявлений

        :param search_phrase: Поисковая фраза
        :param region: Регион поиска
        :param limit: Количество объявлений
        :return: Список объявлений
        '''
        try:
            url = self._build_search_url(search_phrase, region)
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url,
                    headers=self._get_random_headers()
                ) as response:
                    if response.status != 200:
                        self.logger.error(f'Ошибка при запросе: {response.status}')
                        return []
                    
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')

                    #Поиск блоков объявлений
                    ad_blocks = soup.select('[data-marker="item"]')

                    top_ads = []
                    for ad in ad_blocks[:limit]:
                        title_elem = ad.select_one('[itemprop="name"]')
                        price_elem = ad.select_one('[itemprop="price"]')
                        url_elem = ad.select_one('a[itemprop="url"]')

                        top_ads.append({
                            'title': title_elem.text.strip() if title_elem else 'Без названия',
                            'price': price_elem.text.strip() if price_elem else 'Цена не указана',
                            'url': self.BASE_URL + url_elem['href'] if url_elem else '',
                            'additional_info': {}  # Место для расширения
                        })

                    return top_ads
        except Exception as e:
            self.logger.error(f'Ошибка при получении топ объявлений: {e}')
            return []
        
    def _build_search_url(self, search_phrase: str, region: str) -> str:
        '''
        Построение URL для поиска

        :param search_phrase: Поисковая фраза
        :param region: Регион поиска
        :return: Сформированный URL
        '''
        encoded_phrase = quote(search_phrase)
        encoded_region = quote(region)
        return f'{self.BASE_URL}/{encoded_region}?q={encoded_phrase}'
    
    def _get_random_headers(self) -> Dict[str, str]:
        '''
        Генерация случайных заголовков для маскировки

        :return: Словарь заголовков
        '''
        return{
            'User-Agent': random.choice(self.user_agents),
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8'
        }



