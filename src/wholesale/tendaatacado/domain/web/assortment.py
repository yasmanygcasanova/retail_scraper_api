""" Assortment """
import asyncio
import re
from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import HTTPException, status
from loguru import logger
from user_agent import generate_user_agent

from core.util.strings import clean_html
from models.tendaatacado.assortment import AssortmentHeader, AssortmentModel


class Assortment:
    """Class Assortment: Handles product assortment requests and data processing"""
    domain = 'api.tendaatacado.com.br'
    base_url = f'https://{domain}'
    records_per_page = 20

    @classmethod
    async def request(
        cls,
        client: Any,
        category_id: int,
        search_term: str,
        page: str,
        request_waiting: int
    ) -> Dict[str, Any]:
        """
        Fetches product data from the API.

        Args:
            client: HTTP client for making requests
            category_id: Category ID for the products
            search_term: Search term for filtering products
            page: Page number for pagination
            request_waiting: Time to wait before making the request

        Returns:
            JSON response as a dictionary
        """
        url = f"{cls.base_url}/api/public/store/category/{category_id}/products"

        headers = cls._prepare_request_headers()
        params = cls._prepare_request_params(search_term, page)

        logger.info(f"Requesting data from {url}")
        await asyncio.sleep(request_waiting)

        try:
            response = await client.get(
                url,
                headers=headers,
                params=params,
                timeout=15
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.error(f"Error during API request: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to fetch assortment data."
            )

    @staticmethod
    def _prepare_request_headers() -> Dict[str, str]:
        """Prepare headers for the API request."""
        return {
            'User-Agent': generate_user_agent(),
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.5',
            'Origin': 'https://www.tendaatacado.com.br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'TE': 'trailers'
        }

    @staticmethod
    def _prepare_request_params(search_term: str, page: str) -> Dict[str, Any]:
        """Prepare parameters for the API request."""
        return {
            "query": {"link": search_term},
            "page": page,
            "order": "relevance",
            "save": "true",
            "cartId": "7383256"
        }

    @classmethod
    async def process_data(
        cls,
        category_id: int,
        search_term: str,
        data: Dict[str, Any]
    ) -> AssortmentHeader:
        """
        Processes the API response into structured models.
        :param category_id: Category ID
        :param search_term: Search term
        :param data: Raw API response data
        :return: AssortmentHeader object with processed data
        """
        now = datetime.now()
        products = data.get("products", [])
        assortment_list = []

        for product in products:
            assortment = cls._parse_product(product, category_id, search_term, now)
            if assortment:
                assortment_list.append(assortment)

        total_items = data.get("total_products", 0)
        total_pages = data.get("total_pages", 0)

        return AssortmentHeader(
            records_per_page=cls.records_per_page,
            items=total_items,
            pages=total_pages,
            data=assortment_list
        )

    @staticmethod
    def _parse_product(
        product: Dict[str, Any],
        category_id: int,
        search_term: str,
        now: datetime
    ) -> Optional[AssortmentModel]:
        """
        Parses a single product's data.
        :param product: Product data dictionary
        :param category_id: Category ID
        :param search_term: Search term
        :param now: Current timestamp
        :return: AssortmentModel or None if parsing fails
        """
        try:
            fields = {
                'name': clean_html(product.get('name', 'NA')),
                'title': clean_html(product.get('metaTitle', 'NA')),
                'ean': int(product.get('barcode', 0)),
                'sku': product.get('sku', 'NA'),
                'product_id': int(product.get('id', 0)),
                'brand': clean_html(product.get('brand', 'NA')).strip(),
                'category_id': category_id,
                'search_term': search_term,
                'available': 'S' if re.search(
                    r'in_stock',
                    product.get('availability', ''),
                    re.IGNORECASE
                ) else 'N',
                'delivery_available': 'S' if product.get('deliveryAvailable') else 'N',
                'stock_qty': int(product.get('totalStock', 0)),
                'rating': float(product.get('rating', 0)),
                'price_from': 0,
                'price_to': float(product.get('price', 0)),
                'price_wholesale': product.get(
                    'wholesalePrices', [{}]
                )[0].get('price', 0),
                'min_qty_wholesale': product.get(
                    'wholesalePrices', [{}]
                )[0].get('minQuantity', 0),
                'image': product.get('thumbnail', 'NA'),
                'url': product.get('url', 'NA'),
                'created_at': now.strftime("%Y-%m-%d"),
                'hour': now.strftime("%H:%M:%S")
            }
            return AssortmentModel(**fields)
        except Exception as e:
            logger.error(f"Error parsing product: {e}")
            return None
