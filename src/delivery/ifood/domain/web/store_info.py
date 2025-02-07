""" Store Info """
import asyncio
import json
from typing import Optional, Dict, Any

from fastapi import HTTPException, status
from loguru import logger as log
from user_agent import generate_user_agent

from core.util.model_validator import validate_and_parse_model
from core.util.strings import clean_html
from models.ifood.store_info import StoreInfoHeader, StoreInfoModel as StoreModel
from src.delivery.ifood.models.web.store_info import StoreInfoModel


class StoreInfo:
    """ Classe para gerenciar informações de lojas do iFood """
    
    # Constantes da classe
    HOST = 'marketplace.ifood.com.br'
    BASE_URL = 'https://www.ifood.com.br'
    GRAPHQL_URL = f"https://{HOST}/v1/merchant-info/graphql"
    LOGO_BASE_URL = "https://static-images.ifood.com.br/image/upload/t_thumbnail/logosgde/"
    
    @staticmethod
    def _get_default_headers() -> Dict[str, str]:
        """Retorna os headers padrão para as requisições"""
        return {
            'User-Agent': generate_user_agent(),
            'Accept': "application/json, text/plain, */*",
            'Accept-Language': "pt-BR,pt;q=1",
            'Accept-Encoding': "gzip, deflate, br",
            'Content-Type': "application/json",
            'Referer': StoreInfo.BASE_URL,
            'Cache-Control': "no-cache, no-store",
            'platform': "Desktop",
            'app_version': "9.94.6",
            'Origin': StoreInfo.BASE_URL,
            'Sec-Fetch-Dest': "empty",
            'Sec-Fetch-Mode': "cors",
            'Sec-Fetch-Site': "same-site",
            'Connection': "keep-alive",
            'Pragma': "no-cache",
            'TE': "trailers",
            'cache-control': "no-cache"
        }

    @staticmethod
    def _get_graphql_query() -> str:
        """Retorna a query GraphQL para busca de informações do merchant"""
        return """
            query ($merchantId: String!) {
                merchant(merchantId: $merchantId, required: true) {
                    available availableForScheduling contextSetup
                    { catalogGroup context regionGroup }
                    currency deliveryFee { originalValue type value }
                    deliveryMethods { catalogGroup deliveredBy id maxTime minTime mode originalValue priority schedule { now shifts { dayOfWeek endTime interval startTime } timeSlots { availableLoad date endDateTime endTime id isAvailable originalPrice price startDateTime startTime } } } subtitle title type value } deliveryTime distance features id mainCategory { code name } minimumOrderValue name paymentCodes preparationTime priceRange resources { fileName type } slug tags takeoutTime userRating } merchantExtra (merchantId: $merchantId, required: false) { address { city country district latitude longitude state streetName streetNumber timezone zipCode } categories { code description friendlyName } companyCode configs { bagItemNoteLength chargeDifferentToppingsMode nationalIdentificationNumberRequired orderNoteLength } deliveryTime description documents { CNPJ { type value } MCC { type value } } enabled features groups { externalId id name type } id locale mainCategory { code description friendlyName } merchantChain { externalId id name } metadata { ifoodClub { banner { action image priority title } } } } minimumOrderValue name phoneIf priceRange resources { fileName type } shifts { dayOfWeek duration start } shortId tags takeoutTime test type userRatingCount } }
        """

    @staticmethod
    def _safe_get(data: dict, *keys, default: Any = 'NA') -> Any:
        """
        Recupera valor do dicionário de forma segura
        :param data: Dicionário de dados
        :param keys: Chaves para acessar o valor
        :param default: Valor padrão caso não encontre
        :return: Valor encontrado ou default
        """
        try:
            result = data
            for key in keys:
                result = result[key]
            return result if result is not None else default
        except (KeyError, TypeError, AttributeError):
            return default

    @classmethod
    async def request(
        cls,
        client: object,
        store_id: str,
        latitude: str,
        longitude: str,
        request_waiting: int,
        max_retries: int = 3,
        retry_delay: int = 2
    ) -> Dict[str, Any]:
        """
        Realiza requisição para obter dados da loja
        :param client: Cliente HTTP
        :param store_id: ID da loja
        :param latitude: Latitude
        :param longitude: Longitude
        :param request_waiting: Tempo de espera entre requisições
        :param max_retries: Número máximo de tentativas
        :param retry_delay: Tempo de espera entre tentativas
        :return: Dados da loja
        """
        log.info(f"{cls.GRAPHQL_URL}: scraping data for store {store_id}")

        # Mantém a query original
        payload = {
            "query": "query ($merchantId: String!) { merchant "
                     "(merchantId: $merchantId, required: true) "
                     "{ available availableForScheduling contextSetup"
                     " { catalogGroup context regionGroup }"
                     " currency deliveryFee { originalValue type value }"
                     " deliveryMethods { catalogGroup "
                     "deliveredBy id maxTime minTime mode originalValue"
                     " priority schedule { now shifts { "
                     "dayOfWeek endTime interval startTime } timeSlots"
                     " { availableLoad date endDateTime"
                     " endTime id isAvailable originalPrice price"
                     " startDateTime startTime } }"
                     " subtitle title type value } deliveryTime "
                     "distance features id mainCategory"
                     " { code name } minimumOrderValue name paymentCodes"
                     " preparationTime priceRange"
                     " resources { fileName type } slug tags takeoutTime"
                     " userRating } merchantExtra"
                     " (merchantId: $merchantId, required: false) "
                     "{ address { city country district"
                     " latitude longitude state streetName streetNumber"
                     " timezone zipCode }"
                     " categories { code description friendlyName } "
                     "companyCode configs "
                     "{ bagItemNoteLength chargeDifferentToppingsMode "
                     "nationalIdentificationNumberRequired orderNoteLength } "
                     "deliveryTime description documents { CNPJ { type value } "
                     "MCC { type value } } enabled features groups "
                     "{ externalId id name type } id locale mainCategory { "
                     "code description friendlyName } merchantChain { externalId id name } "
                     "metadata { ifoodClub { banner { action image priority title } } } "
                     "minimumOrderValue name phoneIf priceRange resources { fileName type }"
                     " shifts { dayOfWeek duration start } shortId tags "
                     "takeoutTime test type userRatingCount } }",
            "variables": {
                "merchantId": store_id
            }
        }

        params = {
            "latitude": latitude,
            "longitude": longitude,
            "channel": "IFOOD"
        }

        await asyncio.sleep(request_waiting)
        
        for attempt in range(max_retries):
            try:
                response = await client.post(
                    cls.GRAPHQL_URL,
                    headers=cls._get_default_headers(),
                    params=params,
                    data=json.dumps(payload)
                )
                
                if response.status_code == 500:
                    log.warning(f"Tentativa {attempt + 1}/{max_retries}: Erro 500 do servidor iFood")
                    if attempt < max_retries - 1:
                        await asyncio.sleep(retry_delay * (attempt + 1))
                        continue
                
                response.raise_for_status()
                data = response.json()
                return {} if not data else data
                
            except Exception as e:
                error_msg = str(e)
                log.error(
                    f"Tentativa {attempt + 1}/{max_retries}: "
                    f"Erro ao buscar dados da loja {store_id}: {error_msg}"
                )
                
                if attempt < max_retries - 1:
                    await asyncio.sleep(retry_delay * (attempt + 1))
                    continue
                
                return {}

    @classmethod
    async def get_merchant(cls, data: dict) -> dict:
        """
        Processa dados do merchant
        :param data: Dados brutos do merchant
        :return: Dados processados
        """
        if not data:
            return cls._get_empty_merchant()

        logo = ''
        for resource in data.get('resources', []):
            if resource.get('type') == 'LOGO':
                logo = f"{cls.LOGO_BASE_URL}{resource.get('fileName')}"
                break

        return {
            'available': 'N' if data.get('available') is False else 'S',
            'delivery_fee': float(cls._safe_get(data, 'deliveryFee', 'originalValue', default=0)),
            'type_delivery_fee': cls._safe_get(data, 'deliveryFee', 'type'),
            'delivery_time': int(cls._safe_get(data, 'deliveryTime', default=0)),
            'distance': float(cls._safe_get(data, 'distance', default=0)),
            'minimum_order_value': int(cls._safe_get(data, 'minimumOrderValue', default=0)),
            'name': clean_html(cls._safe_get(data, 'name')),
            'preparation_time': cls._safe_get(data, 'preparationTime', default=0),
            'price_range': cls._safe_get(data, 'priceRange'),
            'takeout_time': int(cls._safe_get(data, 'takeoutTime', default=0)),
            'user_rating': float(cls._safe_get(data, 'userRating', default=0)),
            'logo': logo
        }

    @classmethod
    async def get_merchant_extra(cls, data: dict) -> dict:
        """
        Processa dados extras do merchant
        :param data: Dados brutos extras
        :return: Dados extras processados
        """
        if not data:
            return cls._get_empty_merchant_extra()

        return {
            'country': cls._safe_get(data, 'address', 'country'),
            'city': clean_html(cls._safe_get(data, 'address', 'city')),
            'district': clean_html(cls._safe_get(data, 'address', 'district')),
            'latitude': str(cls._safe_get(data, 'address', 'latitude')),
            'longitude': str(cls._safe_get(data, 'address', 'longitude')),
            'state': cls._safe_get(data, 'address', 'state'),
            'street_name': clean_html(cls._safe_get(data, 'address', 'streetName')),
            'street_number': cls._safe_get(data, 'address', 'streetNumber'),
            'zip_code': cls._safe_get(data, 'address', 'zipCode'),
            'company_code': cls._safe_get(data, 'companyCode'),
            'user_rating_count': int(cls._safe_get(data, 'userRatingCount', default=0)),
            'store_type': cls._safe_get(data, 'type'),
            'cnpj': cls._safe_get(data, 'documents', 'CNPJ', 'value'),
            'main_category': clean_html(cls._safe_get(data, 'mainCategory', 'friendlyName')),
            'phone': cls._safe_get(data, 'phoneIf')
        }

    @classmethod
    async def get_data(cls, store_id: str, data: dict) -> Optional[StoreInfoHeader]:
        """
        Processa e valida todos os dados da loja
        :param store_id: ID da loja
        :param data: Dados brutos
        :return: Dados processados e validados
        """
        # Verifica se houve erro na requisição
        if data.get("error"):
            log.error(f"Erro na requisição: {data.get('message')} - {data.get('details')}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Serviço do iFood temporariamente indisponível"
            )

        merchant_data = data.get("merchant", {})
        merchant_extra_data = data.get("merchantExtra", {})

        merchant_info = await cls.get_merchant(merchant_data)
        merchant_extra = await cls.get_merchant_extra(merchant_extra_data)

        fields = {
            'store_id': store_id,
            **merchant_info,
            **merchant_extra
        }

        try:
            if store_info_model := validate_and_parse_model(fields, StoreInfoModel):
                StoreModel(**fields)
                return StoreInfoHeader(data=fields)
            
            log.info(store_info_model)
            return None
            
        except ValueError as e:
            log.info(e.args)
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=str(e.args)
            )
