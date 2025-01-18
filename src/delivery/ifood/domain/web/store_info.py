""" Store Info """
import asyncio
import json

from fastapi import HTTPException, status
from loguru import logger as log
from user_agent import generate_user_agent

from core.util.model_validator import validate_and_parse_model
from core.util.strings import clean_html
from models.ifood.store_info import StoreInfoHeader
from models.ifood.store_info import StoreInfoModel as StoreModel
# from src.delivery.ifood.config.user_agent import USER_AGENT
from src.delivery.ifood.models.web.store_info import StoreInfoModel


class StoreInfo:
    """ Class Store Info """
    host = 'marketplace.ifood.com.br'
    base_url = 'https://www.ifood.com.br'

    @classmethod
    async def request(
        cls,
        client: object,
        store_id: str,
        latitude: str,
        longitude: str,
        request_waiting: int
    ) -> dict:
        """
        Function Request
        :param client:
        :param store_id:
        :param latitude:
        :param longitude:
        :param request_waiting:
        :return: dict
        """
        url = f"https://{cls.host}/v1/merchant-info/graphql"
        log.info(f"{url}: scraping data")

        params = {
            "latitude": latitude,
            "longitude": longitude,
            "channel": "IFOOD"
        }

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

        headers = {
            'User-Agent': generate_user_agent(),
            'Accept': "application/json, text/plain, */*",
            'Accept-Language': "pt-BR,pt;q=1",
            'Accept-Encoding': "gzip, deflate, br",
            'Content-Type': "application/json",
            'Referer': cls.base_url,
            'Cache-Control': "no-cache, no-store",
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
        response = await client.post(
            url,
            headers=headers,
            params=params,
            data=json.dumps(payload)
        )
        data = json.loads(response.text)
        return {} if not data else data

    @staticmethod
    async def get_merchant(data: dict) -> dict:
        """
        Function Get Merchant
        :param data:
        :return: dict
        """
        logo = ''
        available = name = price_range = 'NA'
        delivery_fee = type_delivery_fee = delivery_time = 0
        distance = user_rating = 0
        minimum_order_value = preparation_time = takeout_time = 0

        if data:
            available = 'N' if data.get("available") is False else 'S'
            delivery_fee = 0 if not data.get('deliveryFee') \
                or not data.get('deliveryFee').get('originalValue') \
                else float(data.get('deliveryFee').get('originalValue'))
            type_delivery_fee = 'NA' if not data.get('deliveryFee') \
                or not data.get('deliveryFee').get('type') \
                else data.get('deliveryFee').get('type')
            delivery_time = 0 if not data.get('deliveryTime') \
                else int(data.get('deliveryTime'))
            distance = 0 if not data.get('distance') \
                else float(data.get('distance'))
            minimum_order_value = 0 if not data.get('minimumOrderValue') \
                else int(data.get('minimumOrderValue'))
            name = 'NA' if not data.get('name') \
                else clean_html(data.get('name'))
            preparation_time = 0 if not data.get('preparationTime') \
                else data.get('preparationTime')
            price_range = 'NA' if not data.get('priceRange') \
                else data.get('priceRange')
            takeout_time = 0 if not data.get('takeoutTime') \
                else int(data.get('takeoutTime'))
            user_rating = 0 if not data.get('userRating') \
                else float(data.get('userRating'))
            for resources in data.get('resources'):
                if resources.get('type') == 'LOGO':
                    logo = f"https://static-images.ifood.com.br/image/" \
                           f"upload/t_thumbnail/logosgde/{resources.get('fileName')}"
                    break

        merchant = {
            'available': available,
            'delivery_fee': delivery_fee,
            'type_delivery_fee': type_delivery_fee,
            'delivery_time': delivery_time,
            'distance': distance,
            'minimum_order_value': minimum_order_value,
            'name': name,
            'preparation_time': preparation_time,
            'price_range': price_range,
            'takeout_time': takeout_time,
            'user_rating': user_rating,
            'logo': logo
        }
        return merchant

    @staticmethod
    async def get_merchant_extra(data: dict) -> dict:
        """
        Function Get Merchant Extra
        :param data:
        :return: dict
        """
        country = district = latitude = longitude = state = 'NA'
        street_name = street_number = zip_code = 'NA'
        company_code = store_type = cnpj = 'NA'
        main_category = phone = city = 'NA'
        user_rating_count = 0
        if data:
            country = 'NA' if not data.get('address') \
                else data.get('address').get('country')
            city = 'NA' if not data.get('address') \
                else clean_html(data.get('address').get('city'))
            district = 'NA' if not data.get('address') \
                else clean_html(data.get('address').get('district'))
            latitude = 'NA' if not data.get('address') \
                else str(data.get('address').get('latitude'))
            longitude = 'NA' if not data.get('address') \
                else str(data.get('address').get('longitude'))
            state = 'NA' if not data.get('address') \
                else data.get('address').get('state')
            street_name = 'NA' if not data.get('address') \
                else clean_html(data.get('address').get('streetName'))
            street_number = 'NA' if not data.get('address') \
                else data.get('address').get('streetNumber')
            zip_code = 'NA' if not data.get('address') \
                else data.get('address').get('zipCode')
            company_code = 'NA' if not data.get('companyCode') \
                else data.get('companyCode')
            user_rating_count = 0 if not data.get('userRatingCount') \
                else int(data.get('userRatingCount'))
            store_type = 'NA' if not data.get('type') \
                else data.get('type')
            documents = {} if not data.get('documents') \
                else data.get('documents')
            cnpj = 'NA' if not documents or not documents.get('CNPJ').get('value') \
                else documents.get('CNPJ').get('value')
            main_category = 'NA' if not data.get('mainCategory').get('friendlyName') \
                else clean_html(data.get('mainCategory').get('friendlyName'))
            phone = 'NA' if not data.get('phoneIf') \
                else data.get('phoneIf')

        merchant_extra = {
            'country': country,
            'city': city,
            'district': district,
            'latitude': latitude,
            'longitude': longitude,
            'state': state,
            'street_name': street_name,
            'street_number': street_number,
            'zip_code': zip_code,
            'company_code': company_code,
            'user_rating_count': user_rating_count,
            'store_type': store_type,
            'cnpj': cnpj,
            'main_category': main_category,
            'phone': phone
        }
        return merchant_extra

    @classmethod
    async def get_data(
        cls,
        store_id: str,
        data: dict
    ):
        """
        Function Get Data
        :param store_id:
        :param data:
        :return:
        """
        merchant = {} if not data.get("merchant") else data.get("merchant")
        merchant_extra = {} if not data.get("merchantExtra") else data.get("merchantExtra")
        merchant_info = await cls.get_merchant(merchant)
        merchant_extra = await cls.get_merchant_extra(merchant_extra)

        fields = {
            'name': merchant_info.get('name'),
            'company_code': merchant_extra.get('company_code'),
            'phone': merchant_extra.get('phone'),
            'main_category': merchant_extra.get('main_category'),
            'store_id': store_id,
            'store_type': merchant_extra.get('store_type'),
            'cnpj': merchant_extra.get('cnpj'),
            'logo': merchant_info.get('logo'),
            'country': merchant_extra.get('country'),
            'state': merchant_extra.get('state'),
            'city': merchant_extra.get('city'),
            'district': merchant_extra.get('district'),
            'zip_code': merchant_extra.get('zip_code'),
            'latitude': merchant_extra.get('latitude'),
            'longitude': merchant_extra.get('longitude'),
            'street_name': merchant_extra.get('street_name'),
            'street_number': merchant_extra.get('street_number'),
            'price_range': merchant_info.get('price_range'),
            'delivery_fee': merchant_info.get('delivery_fee'),
            'type_delivery_fee': merchant_info.get('type_delivery_fee'),
            'takeout_time': merchant_info.get('takeout_time'),
            'delivery_time': merchant_info.get('delivery_time'),
            'minimum_order_value': merchant_info.get('minimum_order_value'),
            'preparation_time': merchant_info.get('preparation_time'),
            'distance': merchant_info.get('distance'),
            'available': merchant_info.get('available'),
            'user_rating': merchant_info.get('user_rating'),
            'user_rating_count': merchant_extra.get('user_rating_count')
        }

        try:
            # Validate Store info Model
            if store_info_model := validate_and_parse_model(
                    fields,
                    StoreInfoModel
            ):
                StoreModel(**fields)
                store_header = StoreInfoHeader(
                    data=fields
                )
                return store_header
            else:
                log.info(store_info_model)
        except ValueError as e:
            log.info(e.args)
            return HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=str(e.args),
                headers=None
            )
