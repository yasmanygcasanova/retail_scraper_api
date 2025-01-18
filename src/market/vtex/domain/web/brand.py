import asyncio
import json
from typing import List, Optional

from fastapi import status
from loguru import logger as log

from core.util.strings import clean_html
from models.vtex.brand import BrandHeader, BrandModel


class Brand:
    """Class Brand"""

    @staticmethod
    async def request(
        client: object,
        subdomain: str,
        request_waiting: int
    ) -> List[dict]:
        """
        Fetch brand data from the VTEX API.

        Args:
            client: The HTTP client object.
            subdomain: The subdomain for the VTEX store.
            request_waiting: The waiting time between requests.

        Returns:
            A list of brand data dictionaries.
        """
        url = f"https://{subdomain}.vtexcommercestable.com.br/api/catalog_system/pub/brand/list"
        log.info(f"Scraping data from: {url}")

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
    async def get_data(data: List[dict]) -> Optional[BrandHeader]:
        """
        Process and structure the brand data.

        Args:
            data: A list of brand data dictionaries.

        Returns:
            A BrandHeader object containing processed brand data.
        """
        try:
            brand_list = []
            for row in data:
                if row.get('isActive', False):
                    brand_model = BrandModel(
                        name=clean_html(row.get('name', '')),
                        title=clean_html(row.get('title', '')),
                        brand_id=int(row.get('id', 0))
                    )
                    log.info(brand_model.dict())
                    brand_list.append(brand_model)

            return BrandHeader(data=brand_list)
        except Exception as e:
            log.error(f"Error processing brand data: {e}")
            return None
