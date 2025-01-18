""" Segment """
import asyncio
import json

from fastapi import HTTPException, status
from loguru import logger as log
from user_agent import generate_user_agent

from core.util.model_validator import validate_and_parse_model
from core.util.strings import clean_html
from models.ifood.segment import SegmentHeader
from models.ifood.segment import SegmentModel as SegmentListModel
# from src.delivery.ifood.config.user_agent import USER_AGENT
from src.delivery.ifood.models.web.segment import SegmentModel


class Segment:
    """ Class Segment """
    host = 'marketplace.ifood.com.br'
    base_url = 'https://www.ifood.com.br'

    @classmethod
    async def request(
        cls,
        client: object,
        latitude: str,
        longitude: str,
        request_waiting: int
    ) -> dict:
        """
        Function Request
        :param client:
        :param latitude:
        :param longitude:
        :param request_waiting:
        :return:
        """
        url = f"https://{cls.host}/v2/categories"
        log.info(f"{url}: scraping data")

        params = {
            "latitude": latitude,
            "longitude": longitude,
            "channel": "IFOOD"
        }
        headers = {
            'User-Agent': generate_user_agent(),
            'Accept': "application/json, text/plain, */*",
            'Accept-Language': "pt-BR,pt;q=1",
            'Accept-Encoding': "gzip, deflate, br",
            'Referer': cls.base_url,
            'Cache-Control': "no-cache, no-store",
            'platform': "Desktop",
            'X-Ifood-Session-Id': "9e348c9d-9815-4140-8ef7-fac180b3a5d5",
            'X-Ifood-Device-Id': "cdfcbb46-9bf9-4da9-af89-d6854c09eaa5",
            'x-device-model': "Ubuntu Firefox",
            'x-client-application-key': "41a266ee-51b7-4c37-9e9d-5cd331f280d5",
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
        response = await client.get(
            url,
            headers=headers,
            params=params
        )
        data = json.loads(response.text)
        return {} if not data else data

    @staticmethod
    async def get_data(**kwargs):
        """
        Function Get Data
        :param kwargs:
        :return:
        """
        segment_list = []
        for row in kwargs['data']:
            name = 'NA' if not row.get('title') \
                else clean_html(row.get('title'))
            segment_type = 'NA' if not row.get('type') \
                else clean_html(row.get('type'))
            alias = 'NA' if not row.get('alias') \
                else clean_html(row.get('alias'))

            fields = {
                'name': name,
                'segment_type': segment_type,
                'alias': alias,
                'latitude': kwargs['latitude'],
                'longitude': kwargs['longitude']
            }
            try:
                # Validate Segment Model
                if segment_model := validate_and_parse_model(
                    fields,
                    SegmentModel
                ):
                    data = SegmentListModel(**fields)
                    segment_list.append(data)
                else:
                    log.info(segment_model)
            except ValueError as e:
                log.info(e.args)
                return HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=str(e.args),
                    headers=None
                )
        result = SegmentHeader(
            data=segment_list
        )
        return result
