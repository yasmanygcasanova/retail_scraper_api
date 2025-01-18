""" Department """
import asyncio
from typing import Any, Dict, List

from httpx import AsyncClient, HTTPStatusError, RequestError
from loguru import logger
from user_agent import generate_user_agent

from core.util.strings import clean_html
from models.tendaatacado.department import DepartmentHeader, DepartmentModel


class Department:
    """ Class Department """
    domain = 'api.tendaatacado.com.br'
    base_url = f'https://{domain}'

    @classmethod
    async def request(
        cls,
        client: AsyncClient,
        request_waiting: int
    ) -> List[Dict[str, Any]]:
        """
        Fetch department data from the API.
        :param client: HTTP client
        :param request_waiting: Delay before the request
        :return: List of department data
        """
        url = f"{cls.base_url}/api/public/store/departments"
        headers = {
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
        try:
            logger.info(f"Requesting data from {url}")
            await asyncio.sleep(request_waiting)
            response = await client.get(
                url,
                headers=headers,
                timeout=None
            )
            # Levanta HTTPStatusError se o status for 4xx/5xx
            response.raise_for_status()
            data = response.json()
            return data if data else []
        except RequestError as e:
            logger.error(f"Request error: {e}")
        except HTTPStatusError as e:
            logger.error(f"HTTP error {e.response.status_code}: {e.response.text}")
        except ValueError as e:  # JSON parsing
            logger.error(f"Error decoding JSON response: {e}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")

        return []

    @staticmethod
    async def get_data(data: List[Dict[str, Any]]) -> List[DepartmentModel]:
        """
        Process raw department data into structured objects.
        :param data: Raw department data
        :return: List of DepartmentModel instances
        """
        department_list = []

        try:
            for row in data:
                fields = {
                    'name': clean_html(row.get('name', 'NA')),
                    'department_id': int(row.get('id', 0)),
                    'search_term': row.get('link', 'NA'),
                }

                department_model = DepartmentModel(**fields)
                department_list.append(department_model)

            return DepartmentHeader(data=department_list)

        except KeyError as e:
            logger.error(f"Missing key in department data: {e}")
        except ValueError as e:
            logger.error(f"Error processing department data: {e}")
        except Exception as e:
            logger.error(f"Unexpected error in get_data: {e}")

        return department_list
