"""Department"""
import asyncio
import json
import os

from httpx import AsyncClient, HTTPStatusError, Timeout
from loguru import logger as log
from tenacity import retry, stop_after_attempt, wait_exponential
from user_agent import generate_user_agent

from core.util.strings import clean_html
from models.vipcommerce.department import DepartmentHeader, DepartmentModel


class Department:
    """Class Department"""

    @staticmethod
    def _build_headers() -> dict:
        """Build headers for the HTTP request."""
        auth_token = os.getenv('AUTH_TOKEN_VIPCOMMERCE')
        if not auth_token:
            log.error("Token de autenticação não encontrado. Verifique as variáveis de ambiente.")
            raise ValueError("Token de autenticação ausente")

        return {
            'User-Agent': generate_user_agent(),
            'Accept': 'application/json',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Content-Type': 'application/json',
            'DNT': '1',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'Authorization': f"Bearer {auth_token}",
            'Connection': 'keep-alive'
        }

    @staticmethod
    @retry(wait=wait_exponential(min=1, max=10), stop=stop_after_attempt(3))
    async def request(
        client: AsyncClient,
        domain: str,
        branch_id: int,
        distribution_center_id: int,
        request_waiting: int
    ) -> list[dict]:
        """
        Perform an HTTP request to fetch department data.
        :param client: HTTP client
        :param domain: API domain
        :param branch_id: Branch ID
        :param distribution_center_id: Distribution center ID
        :param request_waiting: Time to wait before request
        :return: List of department data
        """
        if branch_id <= 0 or distribution_center_id <= 0:
            log.error("branch_id e distribution_center_id devem ser maiores que 0.")
            return []

        url = (f"https://api.{domain}/v1/loja/classificacoes_mercadologicas/"
               f"departamentos/arvore/filial/{branch_id}/"
               f"centro_distribuicao/{distribution_center_id}")
        log.info(f"{url}: scraping data")

        headers = Department._build_headers()
        await asyncio.sleep(request_waiting)

        try:
            timeout = Timeout(30)
            response = await client.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()  # Raise exception for HTTP errors

            try:
                response_data = response.json()
                return response_data.get('data', [])
            except json.JSONDecodeError as e:
                log.error(f"Erro ao decodificar JSON: {e}")
                return []

        except HTTPStatusError as e:
            log.error(f"Erro HTTP ({e.response.status_code}): {e.response.text}")
            return []
        except Exception as e:
            log.error(f"Erro inesperado durante a requisição: {e}", exc_info=True)
            return []

    @staticmethod
    async def get_data(
        branch_id: int,
        distribution_center_id: int,
        data: list[dict]
    ) -> list[DepartmentModel]:
        """
        Process department data into DepartmentModel objects.
        :param branch_id: Branch ID
        :param distribution_center_id: Distribution center ID
        :param data: Raw department data
        :return: List of DepartmentModel instances
        """
        try:
            department_list = [
                DepartmentModel(
                    name='NA' if not row.get('descricao') else clean_html(row['descricao']),
                    department_id=int(row.get('classificacao_mercadologica_id', 0)),
                    slug=row.get('link', 'NA'),
                    branch_id=branch_id,
                    distribution_center_id=distribution_center_id
                )
                for row in data
            ]

            return DepartmentHeader(data=department_list)
        except Exception as e:
            log.error(f"Erro ao processar os dados: {e}", exc_info=True)
            return []