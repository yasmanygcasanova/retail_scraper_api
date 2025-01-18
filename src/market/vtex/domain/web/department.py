""" Department """

import asyncio
import json
from typing import List, Optional

from fastapi import status
from loguru import logger

from core.util.strings import clean_html
from models.vtex.department import DepartmentHeader, DepartmentModel


class Department:
    """ Class Department """

    @staticmethod
    async def request(
        client: object,
        subdomain: str,
        request_waiting: int
    ) -> List[dict]:
        """
        Fetch department data from the VTEX API.

        Args:
            client: The HTTP client object.
            subdomain: The subdomain for the VTEX store.
            request_waiting: Time to wait before making the request.

        Returns:
            A list of department data dictionaries.
        """
        url = f"https://{subdomain}.vtexcommercestable.com.br/api/catalog_system/pub/category/tree/3"
        logger.info(f"Scraping data from: {url}")

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
    async def get_data(data: List[dict]) -> Optional[DepartmentHeader]:
        """
        Process raw department data into structured format.

        Args:
            data: A list of raw department data dictionaries.

        Returns:
            A DepartmentHeader object containing processed department data.
        """
        try:
            department_list = []
            for row in data:
                fields = {
                    'name': clean_html(row.get('name', '')),
                    'department_id': int(row.get('id', 0)),
                    'url': row.get('url', '')
                }
                logger.info(fields)
                department_model = DepartmentModel(**fields)
                department_list.append(department_model)

            return DepartmentHeader(data=department_list)

        except Exception as e:
            logger.exception(f"Error processing department data: {e}")
            return None
