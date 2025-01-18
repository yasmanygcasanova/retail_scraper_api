""" Store """
import asyncio
import json
import re

from fastapi import HTTPException, status
from loguru import logger as log
from user_agent import generate_user_agent

from core.util.model_validator import validate_and_parse_model
from core.util.strings import clean_html
from models.ifood.store import MarketHeader, MarketModel
# from src.delivery.ifood.config.user_agent import USER_AGENT
from src.delivery.ifood.models.web.store import StoreModel


class Store:
    """ Class Store """
    host = 'marketplace.ifood.com.br'
    base_url = 'https://www.ifood.com.br'

    @classmethod
    async def request(
        cls,
        client: object,
        alias: str,
        latitude: str,
        longitude: str,
        request_waiting: int
    ) -> dict:
        """
        Function Request
        :param client:
        :param alias:
        :param latitude:
        :param longitude:
        :param request_waiting:
        :return: dict
        """
        url = f"https://{cls.host}/v2/home"
        log.info(f"{url}: scraping data")

        params = {
            "alias": alias,
            "latitude": latitude,
            "longitude": longitude,
            "channel": "IFOOD"
        }

        payload = {
            "supported-headers": ["OPERATION_HEADER"],
            "supported-cards": [
                "MERCHANT_LIST",
                "CATALOG_ITEM_LIST",
                "CATALOG_ITEM_LIST_V2",
                "FEATURED_MERCHANT_LIST",
                "CATALOG_ITEM_CAROUSEL",
                "BIG_BANNER_CAROUSEL",
                "IMAGE_BANNER",
                "MERCHANT_LIST_WITH_ITEMS_CAROUSEL",
                "SMALL_BANNER_CAROUSEL",
                "NEXT_CONTENT",
                "MERCHANT_CAROUSEL",
                "MERCHANT_TILE_CAROUSEL",
                "SIMPLE_MERCHANT_CAROUSEL",
                "INFO_CARD",
                "MERCHANT_LIST_V2",
                "ROUND_IMAGE_CAROUSEL", "BANNER_GRID"
            ],
            "supported-actions": ["merchant", "page", "reorder"],
            "feed-feature-name": "",
            "faster-overrides": ""
        }

        headers = {
            'Accept': "application/json, text/plain, */*",
            'Accept-Encoding': "gzip, deflate, br",
            'Accept-Language': "pt-BR,pt;q=1",
            'app_version': "9.45.1",
            # 'browser': "Ubuntu",
            'Cache-Control': "no-cache, no-store",
            'Connection': "keep-alive",
            'Content-Type': "application/json;charset=utf-8",
            'Host': cls.host,
            'Origin': cls.base_url,
            'platform': "Desktop",
            'Pragma': "no-cache",
            'TE': "Trailers",
            'User-Agent': generate_user_agent(),
            'cache-control': "no-cache"
        }
        await asyncio.sleep(request_waiting)
        response = await client.post(
            url,
            headers=headers,
            params=params,
            data=json.dumps(payload)
        )
        data = json.loads(response.text)
        return {} if not data else data

    @staticmethod
    async def get_data(
        latitude: str,
        longitude: str,
        zip_code: str,
        alias: str,
        data: list
    ):
        """
        Function Get Data
        :param latitude:
        :param longitude:
        :param zip_code:
        :param alias:
        :param data:
        :return:
        """
        store_list = []
        for row in data:
            if re.search(r'MERCHANT_LIST', row.get('cardType'), re.IGNORECASE):
                contents = [] if not row.get('data').get('contents') \
                    else row.get('data').get('contents')
                if contents:
                    for content in contents:
                        name = 'NA' if not content.get('name') \
                            else clean_html(content.get('name'))
                        store_id = 'NA' if not content.get('id') \
                            else content.get('id')
                        segment = 'NA' if not content.get('mainCategory') \
                            else clean_html(content.get('mainCategory'))
                        url = 'NA' if not content.get('action') \
                            else content.get('action')
                        available = 'S' if content.get('available') is True else 'N'
                        distance = 0 if not content.get('distance') \
                            else content.get('distance')
                        user_rating = 0 if not content.get('userRating') \
                            else content.get('userRating')
                        # Delivery Info
                        delivery_info = {} if \
                            not content.get('deliveryInfo') \
                            else content.get('deliveryInfo')
                        fee = 0 if not delivery_info \
                            else delivery_info.get('fee')
                        time_max_minutes = 0 if not delivery_info \
                            or delivery_info.get('timeMaxMinutes') is None \
                            else delivery_info.get('timeMaxMinutes')
                        time_min_minutes = 0 if not delivery_info \
                            or delivery_info.get('timeMinMinutes') is None \
                            else delivery_info.get('timeMinMinutes')
                        store_type = 'NA' if not delivery_info \
                            else delivery_info.get('type')

                        store_info = re.search(
                            r'slug=(.*?)%2F(.*?)$',
                            url,
                            re.IGNORECASE
                        )
                        region = store_info.group(1) \
                            if store_info.group(1) else ''
                        store_slug = store_info.group(2) \
                            if store_info.group(2) else ''

                        fields = {
                            'name': name,
                            'segment': segment,
                            'store_type': store_type,
                            'store_id': store_id,
                            'store_slug': store_slug,
                            'url': url,
                            'available': available,
                            'distance': distance,
                            'user_rating': user_rating,
                            'fee': fee,
                            'time_min_minutes': time_min_minutes,
                            'time_max_minutes': time_max_minutes,
                            'latitude': latitude,
                            'longitude': longitude,
                            'zip_code': zip_code,
                            'region': region,
                            'alias': alias
                        }

                        try:
                            # Validate Store Model
                            if store_model := validate_and_parse_model(
                                fields,
                                StoreModel
                            ):
                                market_model = MarketModel(**fields)
                                store_list.append(market_model)
                            else:
                                log.info(store_model)
                        except ValueError as e:
                            log.info(e.args)
                            return HTTPException(
                                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                detail=str(e.args)
                            )
        result = MarketHeader(
            data=store_list
        )
        return result
