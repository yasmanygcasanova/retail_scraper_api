""" Department """
import asyncio
import json

from loguru import logger as log
from user_agent import generate_user_agent

from core.util.strings import clean_html
from models.ifood.department import DepartmentHeader, DepartmentModel


class Department:
    """ Class Department """
    host = 'marketplace.ifood.com.br'
    base_url = 'https://www.ifood.com.br'

    @classmethod
    async def request(
        cls,
        client: object,
        store_id: str,
        request_waiting: int
    ) -> dict:
        """
        Function Request
        :param client:
        :param store_id:
        :param request_waiting:
        :return: dict
        """
        url = f"https://{cls.host}/v1/merchants/{store_id}/taxonomies"
        log.info(f"{url}: scraping data")

        headers = {
            'User-Agent': generate_user_agent(),
            'Accept': "application/json, text/plain, */*",
            'Accept-Language': "pt-BR,pt;q=1",
            'Accept-Encoding': "gzip, deflate, br",
            'Referer': cls.base_url,
            'Cache-Control': "no-cache, no-store",
            'access_key': "69f181d5-0046-4221-b7b2-deef62bd60d5",
            'secret_key': "9ef4fb4f-7a1d-4e0d-a9b1-9b82873297d8",
            'platform': "Desktop",
            'app_version': "9.94.6",
            'Origin': cls.base_url,
            'Sec-Fetch-Dest': "empty",
            'Sec-Fetch-Mode': "cors",
            'Sec-Fetch-Site': "same-site",
            'Connection': "keep-alive",
            'Pragma': "no-cache",
            'TE': "trailers",
            'cache-control': "no-cache"
        }
        await asyncio.sleep(request_waiting)
        response = await client.get(
            url,
            headers=headers
        )
        data = json.loads(response.text)
        return {} if not data else data

    @staticmethod
    async def get_category(categories: list) -> list:
        """
        Function Get Category
        :param categories:
        :return: list
        """
        category_list = []
        for row in categories:
            name = 'NA' if not row.get('name') \
                else row.get('name')

            data = {
                'name': name
            }
            category_list.append(data)
        return category_list

    @classmethod
    async def get_data(cls, **kwargs):
        """
        Function Get Data
        :param kwargs:
        :return:
        """
        try:
            department_list = []
            category_list = []
            for row in kwargs['data']:
                department_id = 'NA' if not row.get('id') \
                    else row.get('id')
                name = 'NA' if not row.get('name') \
                    else clean_html(row.get('name'))

                categories = [] if not row.get("parentTaxonomies") \
                    else row.get("parentTaxonomies")
                if categories:
                    category_list = await cls.get_category(row.get("parentTaxonomies"))

                fields = {
                    'name': name,
                    'department_id': department_id,
                    'categories': category_list,
                    'segment_type': kwargs['segment_type'],
                    'store_id': kwargs['store_id'],
                    'latitude': kwargs['latitude'],
                    'longitude': kwargs['longitude']
                }
                data = DepartmentModel(**fields)
                department_list.append(data)

            result = DepartmentHeader(
                data=department_list
            )
            return result
        except Exception as e:
            log.info(e.args)
