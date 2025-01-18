""" Intelligence Search """
import asyncio
import json

from fastapi import status
from loguru import logger as log

from core.util.strings import clean_html
from models.vtex.intelligent_search import (IntelligentSearchHeader,
                                            IntelligentSearchModel)


class IntelligentSearch:
    """ Class Intelligence Search """
    @staticmethod
    async def request(
        client: object,
        subdomain: str,
        request_waiting: int
    ) -> list:
        """
        Function Request
        :param client:
        :param subdomain:
        :param request_waiting:
        :return: list
        """
        data = []
        url = (f"https://{subdomain}.vtexcommercestable.com.br/api/"
               f"io/_v/api/intelligent-search/top_searches")
        log.info(f"{url}: scraping data")

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'cache-control': 'no-cache'
        }
        await asyncio.sleep(request_waiting)
        response = await client.get(
            url,
            headers=headers,
            timeout=None
        )
        if response.status_code == status.HTTP_200_OK:
            data = json.loads(response.text)
            return [] if not data.get('searches') \
                else data.get('searches')
        return data

    @staticmethod
    async def get_data(
        data: list
    ) -> list:
        """
        Function Get Data
        :param data:
        :return: list
        """
        try:
            intelligent_search_list = []
            for row in data:
                term = '' if not row.get('term') \
                    else clean_html(row.get('term'))
                count = 0 if not row.get('count') \
                    else int(row.get('count'))

                fields = {
                    'term': term,
                    'count': count

                }
                log.info(fields)
                intelligent_search_model = IntelligentSearchModel(**fields)
                intelligent_search_list.append(intelligent_search_model)

            result = IntelligentSearchHeader(
                data=intelligent_search_list
            )
            return result
        except Exception as e:
            log.info(e.args)
