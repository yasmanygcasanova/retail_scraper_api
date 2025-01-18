"""Account"""
import asyncio
import re
from typing import Optional

from fastapi import status
from loguru import logger
from user_agent import generate_user_agent
from httpx import AsyncClient, TimeoutException


class Account:
    """Class Account"""

    @staticmethod
    async def get_id(
        client: AsyncClient,
        domain: str,
        request_waiting: int
    ) -> Optional[int]:
        """
        Retrieve the account ID from a given domain.

        Args:
            client (AsyncClient): The HTTP client to use for requests.
            domain (str): The domain to fetch the account ID from.
            request_waiting (int): The time to wait between requests.

        Returns:
            Optional[int]: The account ID if found, None otherwise.

        Raises:
            TimeoutException: If the request times out.
        """
        url = f"https://{domain}"
        headers = {
            'Host': domain,
            'User-Agent': generate_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'cross-site',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache'
        }

        try:
            await asyncio.sleep(request_waiting)
            response = await client.get(url, headers=headers)

            if response.status_code == status.HTTP_200_OK:
                match = re.search(
                    r'accountId":(\d+),"checkoutDomain',
                    response.text,
                    re.IGNORECASE
                )
                return int(match.group(1)) if match else None

            return None

        except TimeoutException as e:
            logger.error(f"Request timed out: {e}")
            return None
        except Exception as e:
            logger.exception(f"An error occurred while fetching account ID: {e}")
            return None
