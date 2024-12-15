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
        '''Получение общего количества объявлений'''
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

            

