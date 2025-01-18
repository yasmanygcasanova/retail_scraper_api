""" Distribution Center """
import asyncio
import os
from typing import Any, Dict, List

from fastapi import status
from loguru import logger as log
from user_agent import generate_user_agent

from core.util.strings import clean_html
from models.vipcommerce.distribution_center import (
    DistributionCenterHeader,
    DistributionCenterModel
)


class DistributionCenter:
    """ Class Distribution Center """

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
    async def request(
        client: object,
        domain: str,
        branch_id: int,
        zip_code: str,
        request_waiting: int
    ) -> List[Dict[str, Any]]:
        """
        Fetch distribution center data from the API.

        :param client: HTTP client for requests
        :param domain: API domain
        :param branch_id: Branch ID
        :param zip_code: ZIP code for the query
        :param request_waiting: Delay before request
        :return: List of data
        """
        url = (f"https://api.{domain}/v1/loja/centros_distribuicoes/"
               f"filial/{branch_id}/retiradas?cep={zip_code}")
        log.info(f"{url}: scraping data")

        headers = DistributionCenter._build_headers()
        await asyncio.sleep(request_waiting)

        try:
            response = await client.get(url, headers=headers, timeout=None)
            if response.status_code == status.HTTP_200_OK:
                data = response.json().get('data', [])
                return data
            log.warning(f"Failed request: {response.status_code} - {response.text}")
        except Exception as e:
            log.error(f"Error fetching data: {e}")
        return []

    @staticmethod
    async def parse_data(
        row: Dict[str, Any],
        branch_id: int,
        search_term: str
    ) -> DistributionCenterModel:
        """
        Parse a single distribution center record into a model.

        :param row: Raw data row
        :param branch_id: Branch ID
        :param search_term: Search term
        :return: Parsed DistributionCenterModel instance
        """
        location = row.get('endereco', {})
        client = row.get('relacionamento_cliente', {})

        fields = {
            'name': clean_html(row.get('nome', 'NA')),
            'site_url': row.get('nome_site', ''),
            'cnpj': row.get('cnpj', ''),
            'distribution_center_id': int(row.get('id', 0)),
            'zip_code': location.get('cep', ''),
            'address': clean_html(location.get('logradouro', '')),
            'number': location.get('numero', ''),
            'complement': clean_html(location.get('complemento', '')),
            'neighborhood': clean_html(location.get('bairro', '')),
            'city': clean_html(location.get('cidade', '')),
            'state': clean_html(location.get('estado', '')),
            'email': client.get('email', ''),
            'phone': client.get('telefone', ''),
            'whatsapp': client.get('whatsapp', ''),
            'branch_id': branch_id,
            'search_term': search_term
        }
        return DistributionCenterModel(**fields)

    @staticmethod
    async def get_data(
        branch_id: int,
        search_term: str,
        data: List[Dict[str, Any]]
    ) -> DistributionCenterHeader:
        """
        Process and return distribution center data.

        :param branch_id: Branch ID
        :param search_term: Search term
        :param data: Raw data from the API
        :return: DistributionCenterHeader containing parsed data
        """
        try:
            distribution_centers = [
                await DistributionCenter.parse_data(row, branch_id, search_term)
                for row in data
            ]
            return DistributionCenterHeader(data=distribution_centers)
        except Exception as e:
            log.error(f"Error parsing data: {e}")
            return DistributionCenterHeader(data=[])
