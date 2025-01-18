"""Category"""

import asyncio
import json
from typing import List, Union

from fastapi import status
from loguru import logger as log

from core.util.strings import clean_html
from models.vtex.category import CategoryHeader, CategoryModel


class Category:
    """Class Category"""

    @staticmethod
    async def request(
        client: object,
        subdomain: str,
        request_waiting: int
    ) -> List[dict]:
        """
        Fetch category data from VTEX API.

        Args:
            client: HTTP client object
            subdomain: Subdomain for VTEX commerce
            request_waiting: Time to wait before request

        Returns:
            List of category dictionaries
        """
        data: List[dict] = []
        url = (f"https://{subdomain}.vtexcommercestable.com.br/api/"
               f"catalog_system/pub/category/tree/3")

        log.info(f"{url}: scraping data")

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'cache-control': 'no-cache'
        }

        await asyncio.sleep(request_waiting)

        try:
            response = await client.get(
                url,
                headers=headers,
                timeout=None
            )

            if response.status_code == status.HTTP_200_OK:
                data = json.loads(response.text)
                return data if data else []
        except Exception as e:
            log.error(f"Error in request: {e}")

        return data

    @staticmethod
    async def get_data(
        data: List[dict]
    ) -> Union[CategoryHeader, None]:
        """
        Process and transform category data.

        Args:
            data: List of category dictionaries

        Returns:
            CategoryHeader with processed categories
        """
        try:
            category_list = []
            for row in data:
                department_id = int(row.get('id', 0)) if row.get('id') else 0
                has_children = row.get('hasChildren') is True

                # Categories List
                if has_children:
                    categories = row.get('children', [])
                    if categories:
                        for category in categories:
                            name = clean_html(category.get('name', '')) if category.get('name') else ''
                            url = category.get('url', '')
                            category_id = category.get('id', '')

                            fields = {
                                'name': name,
                                'department_id': department_id,
                                'category_id': category_id,
                                'url': url
                            }
                            log.info(fields)
                            category_model = CategoryModel(**fields)
                            category_list.append(category_model)

            result = CategoryHeader(data=category_list)
            return result

        except Exception as e:
            log.error(f"Error processing category data: {e}")
            return None
