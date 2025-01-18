""" SubCategory """
import asyncio
import json
from typing import List

from fastapi import status
from loguru import logger as log

from core.util.strings import clean_html
from models.vtex.subcategory import SubCategoryHeader, SubCategoryModel


class SubCategory:
    """Class SubCategory"""

    @staticmethod
    async def request(
        client: object,
        subdomain: str,
        request_waiting: int
    ) -> List[dict]:
        """
        Request subcategory data from VTEX API.

        :param client: HTTP client object
        :param subdomain: VTEX subdomain
        :param request_waiting: Delay before request in seconds
        :return: List of subcategory data
        """
        url = f"https://{subdomain}.vtexcommercestable.com.br/api/catalog_system/pub/category/tree/3"
        log.info(f"{url}: scraping data")

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'cache-control': 'no-cache'
        }

        await asyncio.sleep(request_waiting)
        response = await client.get(url, headers=headers, timeout=None)

        if response.status_code == status.HTTP_200_OK:
            return json.loads(response.text) or []
        return []

    @staticmethod
    async def get_data(data: List[dict]) -> SubCategoryHeader:
        """
        Process and structure subcategory data.

        :param data: List of raw subcategory data
        :return: Structured subcategory data
        """
        try:
            subcategory_list = []

            for department in data:
                department_id = int(department.get('id', 0))
                if department.get('hasChildren', False):
                    for category in department.get('children', []):
                        category_id = category.get('id', '')
                        if category.get('hasChildren', False):
                            for subcategory in category.get('children', []):
                                subcategory_model = SubCategoryModel(
                                    name=clean_html(subcategory.get('name', '')),
                                    department_id=department_id,
                                    category_id=category_id,
                                    subcategory_id=subcategory.get('id', ''),
                                    url=subcategory.get('url', '')
                                )
                                log.info(subcategory_model.dict())
                                subcategory_list.append(subcategory_model)

            return SubCategoryHeader(data=subcategory_list)
        except Exception as e:
            log.exception(f"Error processing subcategory data: {e}")
