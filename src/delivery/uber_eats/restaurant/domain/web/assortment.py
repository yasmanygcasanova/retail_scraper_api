""" Assortment """
import asyncio
import json
import re
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import status
from loguru import logger as log
from user_agent import generate_user_agent

from core.util.strings import clean_html
from models.uber_eats.restaurant.assortment import (AssortmentHeader,
                                                    AssortmentModel)


class Assortment:
    """ Class Assortment """
    domain = 'ubereats.com'
    base_url = f'https://www.{domain}'

    @classmethod
    async def request(
        cls,
        client: object,
        store_id: str,
        request_waiting: int
    ) -> Dict[str, Any]:
        """
        Fetch store data from Uber Eats API.
        :param client: HTTP client for making requests
        :param store_id: Unique identifier for the store
        :param request_waiting: Delay before making the request (in seconds)
        :return: Dictionary containing store data
        """
        url = f"{cls.base_url}/_p/api/getStoreV1"
        log.info(f"Fetching data from: {url}")

        payload = json.dumps({
            "storeUuid": store_id,
            "diningMode": "DELIVERY",
            "time": {
                "asap": True
            },
            "cbType": "EATER_ENDORSED"
        })

        headers = {
            'User-Agent': generate_user_agent(),
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Content-Type': 'application/json',
            'x-csrf-token': 'x',
            'Origin': cls.base_url,
            'Alt-Used': f'www.{cls.domain}',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Priority': 'u=0',
            'TE': 'trailers'
        }
        await asyncio.sleep(request_waiting)
        try:
            response = await client.post(
                url,
                headers=headers,
                data=payload
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            log.error(f"Error fetching data: {e}")
            return {}

    @staticmethod
    def parse_price(item: dict) -> float:
        """
        Parse and convert the price field to a valid float.
        :param item: JSON object containing the price field
        :return: Valid price in float format
        """
        try:
            price_raw = item.get('price', 0)
            if not isinstance(price_raw, (int, float)):
                log.warning(f"Unexpected price format: {price_raw}")
                return 0.0
            price = float(price_raw) / 100
            return round(price, 2)  # Retorna com duas casas decimais
        except Exception as e:
            log.error(f"Error parsing price: {e}")
            return 0.0

    @staticmethod
    def parse_discount(price_tagline: dict)  -> tuple:
        """
        Parse and calculate the discount percentage from priceTagline.
        :param price_tagline: JSON object containing priceTagline data
        :return: Discount percentage as a float, or 0.0 if no discount
        """
        try:
            # Acessa o texto da tag de acessibilidade
            accessibility_text = price_tagline.get('accessibilityText', '')

            # Regex para extrair os preços
            match = re.search(
                r"\$(\d+\.\d+), "
                r"discounted from \$(\d+\.\d+)",
                accessibility_text
            )
            if not match:
                return 0.0, 0.0  # Sem preços disponíveis

            current_price = float(match.group(1))  # Preço atual
            original_price = float(match.group(2))  # Preço original

            # Calcula o desconto
            discount = ((original_price - current_price) / original_price) * 100
            return original_price, round(discount, 2)
        except Exception as e:
            log.error(f"Error parsing discount: {e}")
            return 0.0, 0.0

    @staticmethod
    def parse_item(
        item: dict,
        category: str,
        store_id: str,
        now: datetime
    ) -> Optional[AssortmentModel]:
        """
        Parse individual item from the catalog.
        :param item: JSON data for the item
        :param category: Category of the item
        :param store_id: Store identifier
        :param now: Current datetime for timestamping
        :return: AssortmentModel or None if parsing fails
        """
        try:
            name = item.get('title', '')
            description = clean_html(item.get('itemDescription', ''))
            product_id = item.get('uuid', '')
            price = Assortment.parse_price(item)
            available = 'S' if item.get('isAvailable', False) else 'N'
            has_customizations = 'S' if item.get('hasCustomizations', False) else 'N'

            # Calcula o desconto
            price_tagline = item.get('priceTagline', {})
            price_from, discount = Assortment.parse_discount(price_tagline)

            endorsement_analytics_tag = item.get("endorsementAnalyticsTag", '')
            endorsement = 'S' if re.search(
        r'confidence_builders_popular',
                endorsement_analytics_tag,
                re.IGNORECASE
            ) else 'N'

            image = item.get('imageUrl', '')
            rating = item.get(
                'catalogItemAnalyticsData', {}
            ).get(
                'endorsementMetadata', {}
            ).get('rating', '0%').strip('%')
            num_ratings = item.get(
                'catalogItemAnalyticsData', {}
            ).get(
                'endorsementMetadata', {}
            ).get('numRatings', 0)

            return AssortmentModel(
                name=name,
                description=description,
                product_id=product_id,
                category=category,
                store_id=store_id,
                available=available,
                has_customizations=has_customizations,
                price_to=price,
                price_from=price_from,  # Preço original
                discount=discount,  # Desconto calculado
                rating=int(rating),
                num_ratings=num_ratings,
                endorsement=endorsement,
                image=image,
                created_at=now.strftime("%Y-%m-%d"),
                hour=now.strftime("%H:%M:%S")
            )
        except Exception as e:
            log.error(f"Error parsing item: {e} | Item: {item}")
            return None

    @classmethod
    async def get_data(
        cls,
        store_id: str,
        data: dict
    ) -> AssortmentHeader:
        """
        Process store data to extract assortment information.
        :param store_id: Store identifier
        :param data: JSON response from the API
        :return: AssortmentHeader containing parsed items
        """
        try:
            now = datetime.now()
            assortment_list = []

            sections = data.get('sections', [{}])[0].get('uuid', '')
            if not sections:
                return AssortmentHeader(data=[])

            catalog = data.get('catalogSectionsMap', {}).get(sections, [])
            for item_data in catalog:
                payload = item_data.get('payload', {}).get('standardItemsPayload', {})
                category = clean_html(payload.get('title', {}).get('text', ''))
                if re.search(r'Save on Select Items', category, re.IGNORECASE):
                    continue

                for item in payload.get('catalogItems', []):
                    parsed_item = cls.parse_item(item, category, store_id, now)
                    if parsed_item:
                        assortment_list.append(parsed_item)

            return AssortmentHeader(data=assortment_list)
        except Exception as e:
            log.error(f"Error processing data: {e}")
            return AssortmentHeader(data=[])
