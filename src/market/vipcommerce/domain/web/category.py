""" Category Module """
import asyncio
import json
import os

from httpx import AsyncClient, HTTPStatusError, Timeout
from loguru import logger as log
from tenacity import retry, stop_after_attempt, wait_exponential
from user_agent import generate_user_agent

from core.util.strings import clean_html
from models.vipcommerce.category import CategoryHeader, CategoryModel


class Category:
    """ Class Category """

    @staticmethod
    def _build_headers() -> dict:
        """Build HTTP headers for the request."""
        auth_token = os.getenv('AUTH_TOKEN_VIPCOMMERCE')
        if not auth_token:
            log.error("Token de autenticação não encontrado. Verifique as variáveis de ambiente.")
            raise ValueError("Token de autenticação ausente.")

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
            'Connection': 'keep-alive',
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
        Fetch category data from the API.

        :param client: Async HTTP client
        :param domain: API domain
        :param branch_id: Branch ID
        :param distribution_center_id: Distribution Center ID
        :param request_waiting: Delay before making the request
        :return: List of raw category data
        """
        if branch_id <= 0 or distribution_center_id <= 0:
            log.error("Os IDs de branch e centro de distribuição devem ser positivos.")
            return []

        url = (
            f"https://api.{domain}/v1/loja/classificacoes_mercadologicas/"
            f"departamentos/arvore/filial/{branch_id}/"
            f"centro_distribuicao/{distribution_center_id}"
        )
        log.info(f"Solicitando dados de categorias em: {url}")

        headers = Category._build_headers()
        await asyncio.sleep(request_waiting)

        try:
            timeout = Timeout(30)
            response = await client.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()
            return response.json().get('data', [])

        except HTTPStatusError as e:
            log.error(f"Erro HTTP ({e.response.status_code}): {e.response.text}")
            return []
        except json.JSONDecodeError as e:
            log.error(f"Erro ao decodificar JSON: {e}")
            return []
        except Exception as e:
            log.error(f"Erro inesperado: {e}", exc_info=True)
            return []

    @staticmethod
    async def get_data(
        branch_id: int,
        distribution_center_id: int,
        data: list[dict]
    ) -> CategoryHeader:
        """
        Process raw category data into structured CategoryModel instances.

        :param branch_id: Branch ID
        :param distribution_center_id: Distribution Center ID
        :param data: Raw category data
        :return: CategoryHeader containing processed data
        """
        try:
            categories = [
                CategoryModel(
                    name='NA' if not value.get('descricao') else clean_html(value['descricao']),
                    category_id=int(value.get('classificacao_mercadologica_id', 0)),
                    department_id=int(row.get('classificacao_mercadologica_id', 0)),
                    slug=value.get('link', 'NA'),
                    branch_id=branch_id,
                    distribution_center_id=distribution_center_id,
                )
                for row in data
                for value in row.get('children', [])
            ]

            return CategoryHeader(data=categories)

        except Exception as e:
            log.error(f"Erro ao processar os dados de categorias: {e}", exc_info=True)
            return CategoryHeader(data=[])