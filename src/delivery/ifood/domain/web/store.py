""" Store """
import asyncio
import json
import re
from typing import Dict, List, Optional, Any

from fastapi import HTTPException, status
from loguru import logger as log
from user_agent import generate_user_agent

from core.util.model_validator import validate_and_parse_model
from core.util.strings import clean_html
from models.ifood.store import MarketHeader, MarketModel
from src.delivery.ifood.models.web.store import StoreModel


class Store:
    """ Class Store """
    host = 'marketplace.ifood.com.br'
    base_url = 'https://www.ifood.com.br'
    
    @classmethod
    def _get_default_headers(cls) -> Dict[str, str]:
        """Headers padrão para requisições"""
        return {
            'Accept': "application/json, text/plain, */*",
            'Accept-Encoding': "gzip, deflate, br",
            'Accept-Language': "pt-BR,pt;q=1",
            'app_version': "9.45.1",
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

    @classmethod
    def _get_default_payload(cls) -> Dict[str, Any]:
        """Payload padrão para requisições"""
        return {
            "supported-headers": ["OPERATION_HEADER"],
            "supported-cards": [
                "MERCHANT_LIST", "CATALOG_ITEM_LIST",
                "CATALOG_ITEM_LIST_V2", "FEATURED_MERCHANT_LIST",
                "CATALOG_ITEM_CAROUSEL", "BIG_BANNER_CAROUSEL",
                "IMAGE_BANNER", "MERCHANT_LIST_WITH_ITEMS_CAROUSEL",
                "SMALL_BANNER_CAROUSEL", "NEXT_CONTENT",
                "MERCHANT_CAROUSEL", "MERCHANT_TILE_CAROUSEL",
                "SIMPLE_MERCHANT_CAROUSEL", "INFO_CARD",
                "MERCHANT_LIST_V2", "ROUND_IMAGE_CAROUSEL", 
                "BANNER_GRID"
            ],
            "supported-actions": ["merchant", "page", "reorder"],
            "feed-feature-name": "",
            "faster-overrides": ""
        }

    @classmethod
    async def request(
        cls,
        client: object,
        alias: str,
        latitude: str,
        longitude: str,
        request_waiting: int
    ) -> Dict[str, Any]:
        """
        Function Request
        :param client: Cliente HTTP
        :param alias: Alias da loja
        :param latitude: Latitude
        :param longitude: Longitude
        :param request_waiting: Tempo de espera
        :return: Dados da requisição
        """
        url = f"https://{cls.host}/v2/home"
        log.info(f"{url}: scraping data for alias {alias}")

        try:
            params = {
                "alias": alias,
                "latitude": latitude,
                "longitude": longitude,
                "channel": "IFOOD"
            }

            await asyncio.sleep(request_waiting)
            response = await client.post(
                url,
                headers=cls._get_default_headers(),
                params=params,
                data=json.dumps(cls._get_default_payload())
            )
            response.raise_for_status()
            data = json.loads(response.text)
            return {} if not data else data
            
        except Exception as e:
            log.error(f"Erro ao buscar dados da loja {alias}: {str(e)}")
            return {}

    @staticmethod
    def _extract_store_info(url: str) -> tuple[str, str]:
        """Extrai informações da loja da URL"""
        store_info = re.search(r'slug=(.*?)%2F(.*?)$', url, re.IGNORECASE)
        region = store_info.group(1) if store_info and store_info.group(1) else ''
        store_slug = store_info.group(2) if store_info and store_info.group(2) else ''
        return region, store_slug

    @staticmethod
    def _extract_delivery_info(content: Dict[str, Any]) -> tuple[float, int, int, str]:
        """Extrai informações de entrega"""
        delivery_info = content.get('deliveryInfo', {})
        return (
            delivery_info.get('fee', 0),
            delivery_info.get('timeMaxMinutes') or 0,
            delivery_info.get('timeMinMinutes') or 0,
            delivery_info.get('type', 'NA')
        )

    @classmethod
    async def get_data(
        cls,
        latitude: str,
        longitude: str,
        zip_code: str,
        alias: str,
        data: List[Dict[str, Any]]
    ) -> Optional[MarketHeader]:
        """
        Function Get Data
        :param latitude: Latitude
        :param longitude: Longitude
        :param zip_code: CEP
        :param alias: Alias da loja
        :param data: Dados brutos
        :return: Dados processados
        """
        try:
            store_list = []
            
            for row in data:
                if not re.search(r'MERCHANT_LIST', row.get('cardType', ''), re.IGNORECASE):
                    continue

                contents = row.get('data', {}).get('contents', [])
                for content in contents:
                    # Extrai informações básicas
                    region, store_slug = cls._extract_store_info(content.get('action', ''))
                    fee, time_max, time_min, store_type = cls._extract_delivery_info(content)

                    fields = {
                        'name': clean_html(content.get('name', 'NA')),
                        'segment': clean_html(content.get('mainCategory', 'NA')),
                        'store_type': store_type,
                        'store_id': content.get('id', 'NA'),
                        'store_slug': store_slug,
                        'url': content.get('action', 'NA'),
                        'available': 'S' if content.get('available') else 'N',
                        'distance': content.get('distance', 0),
                        'user_rating': content.get('userRating', 0),
                        'fee': fee,
                        'time_min_minutes': time_min,
                        'time_max_minutes': time_max,
                        'latitude': latitude,
                        'longitude': longitude,
                        'zip_code': zip_code,
                        'region': region,
                        'alias': alias
                    }

                    try:
                        if store_model := validate_and_parse_model(fields, StoreModel):
                            market_model = MarketModel(**fields)
                            store_list.append(market_model)
                        else:
                            log.warning(f"Falha na validação da loja: {fields.get('store_id')}")
                            
                    except ValueError as e:
                        log.error(f"Erro ao processar loja {fields.get('store_id')}: {str(e)}")
                        raise HTTPException(
                            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail=str(e.args)
                        )

            return MarketHeader(data=store_list)
            
        except Exception as e:
            log.error(f"Erro ao processar dados das lojas: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao processar dados das lojas"
            )
