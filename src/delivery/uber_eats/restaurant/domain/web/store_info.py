""" StoreInfo """
import asyncio
from typing import Any, Dict, Optional

from fastapi import HTTPException, status
from httpx import AsyncClient, HTTPStatusError, RequestError
from loguru import logger as log
from user_agent import generate_user_agent

from core.util.strings import clean_html
from models.uber_eats.restaurant.store_info import StoreInfoHeader, StoreInfoModel


class StoreInfo:
    """ Class to handle store information retrieval from Uber Eats. """
    domain = 'ubereats.com'
    base_url = f'https://www.{domain}'

    @classmethod
    def _build_headers(cls) -> Dict[str, str]:
        """ Constructs the headers for the HTTP request. """
        return {
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

    @classmethod
    def _build_payload(cls, store_id: str) -> Dict[str, Any]:
        """ Constructs the payload for the HTTP request. """
        return {
            "storeUuid": store_id,
            "diningMode": "DELIVERY",
            "time": {"asap": True},
            "cbType": "EATER_ENDORSED"
        }

    @classmethod
    async def request(
        cls,
        client: AsyncClient,
        store_id: str,
        request_waiting: int
    ) -> Optional[Dict[str, Any]]:
        """ Makes a request to the server to obtain store information.

        :param client: The HTTP client to use for the request.
        :param store_id: The ID of the store to fetch information for.
        :param request_waiting: Time to wait before making the request.
        :return: The JSON response from the server or None on failure.
        """

        # Validate inputs
        if not isinstance(store_id, str) or not store_id.strip():
            log.error("Invalid store_id provided.")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid store ID.")

        if not isinstance(request_waiting, int) or request_waiting < 0:
            log.error("Invalid request_waiting time provided.")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid waiting time.")

        url = f"{cls.base_url}/_p/api/getStoreV1"
        log.info(f"Fetching data from: {url}")

        payload = cls._build_payload(store_id)
        headers = cls._build_headers()

        await asyncio.sleep(request_waiting)

        try:
            log.info(f"Requesting data for store_id={store_id} with payload={payload}")
            response = await client.post(url, headers=headers, json=payload)
            response.raise_for_status()  # Raises error for HTTP codes 4xx/5xx

            return response.json()

        except RequestError as e:
            log.error(f"Request error for store_id={store_id}: {e}")
            raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Service unavailable.")

        except HTTPStatusError as e:
            log.error(f"HTTP error {e.response.status_code} for store_id={store_id}: {e.response.text}")
            raise HTTPException(status_code=e.response.status_code, detail=e.response.text)

        except ValueError as e:  # JSON parsing error
            log.error(f"Error decoding JSON response for store_id={store_id}: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error processing response.")

    @classmethod
    async def get_data(
        cls,
        store_id: str,
        data: dict
    ) -> StoreInfoHeader:
        """ Process data to extract store information.

        :param store_id: Store identifier.
        :param data: JSON response from the API.
        :return: StoreInfoHeader containing parsed items.
        """

        try:
            # Validate that data contains necessary fields before processing
            if not isinstance(data, dict):
                log.error(f"Invalid data format received for store_id={store_id}: {data}")
                raise ValueError("Invalid data format.")

            store_data = StoreInfoModel(
                name=clean_html(data.get('title', '')),
                store_id=store_id,
                slug=data.get('slug', ''),
                rating=data.get('rating', {}),
                location=data.get('location', {}),
                hours=data.get('hours', []),
                phone=data.get('phoneNumber', '')
            )

            return StoreInfoHeader(data=store_data)

        except Exception as e:
            log.error(f"Error processing data for store_id={store_id}: {e}")
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e))
