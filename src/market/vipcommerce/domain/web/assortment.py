"""Assortment"""
import asyncio
import os
from datetime import datetime
from typing import Any, Dict

from fastapi import status
from httpx import AsyncClient
from loguru import logger as log
from tenacity import retry, stop_after_attempt, wait_exponential
from user_agent import generate_user_agent

from core.util.strings import clean_html
from models.vipcommerce.assortment import AssortmentHeader, AssortmentModel


class Assortment:
    """Class Assortment"""

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
        category_id: int,
        page: str,
        request_waiting: int
    ) -> Dict[str, Any]:
        """
        Performs a request to the assortment API.

        Args:
            client: HTTP client instance.
            domain: Domain of the API.
            branch_id: ID of the branch.
            distribution_center_id: ID of the distribution center.
            category_id: ID of the category.
            page: Page number for pagination.
            request_waiting: Time to wait before making the request.

        Returns:
            Response data as a dictionary.
        """
        url = (f"https://api.{domain}/v1/loja/classificacoes_mercadologicas/secoes/"
               f"{category_id}/produtos/filial/{branch_id}"
               f"/centro_distribuicao/{distribution_center_id}/"
               f"ativos?orderby=produto.descricao&page={page}")
        log.info(f"Fetching data from URL: {url}")

        headers = Assortment._build_headers()
        await asyncio.sleep(request_waiting)
        try:
            await asyncio.sleep(request_waiting)
            response = await client.get(url, headers=headers, timeout=None)
            response.raise_for_status()
            return response.json() if response.status_code == status.HTTP_200_OK else {}
        except Exception as e:
            log.error(f"Error fetching data: {str(e)}")
            return {}

    @staticmethod
    async def get_data(
        domain: str,
        branch_id: int,
        distribution_center_id: int,
        category_id: int,
        data: Dict[str, Any]
    ) -> AssortmentHeader:
        """
        Parses API response data into an AssortmentHeader.

        Args:
            domain: API domain.
            branch_id: ID of the branch.
            distribution_center_id: ID of the distribution center.
            category_id: ID of the category.
            data: Raw API response data.

        Returns:
            AssortmentHeader containing parsed data.
        """
        try:
            now = datetime.now()
            assortment_list = []

            products = data.get("data", [])
            if len(products) > 0:
                for row in products:
                    name = 'NA' if not row.get('descricao') \
                        else clean_html(row.get('descricao'))
                    ean = 0 if not row.get('codigo_barras') \
                        else int(row.get('codigo_barras'))
                    sku = 'NA' if not row.get('sku') \
                        else row.get('sku')
                    product_id = 0 if not row.get('produto_id') \
                        else int(row.get('produto_id'))
                    brand = 'NA' if not row.get('marca') else row.get('marca')
                    price_from = 0 if not row.get('preco_original') \
                        else float(row.get('preco_original'))
                    price_to = 0 if not row.get('preco') \
                        else float(row.get('preco'))
                    sold_amount = 0 if not row.get('quantidade_vendida') \
                        else int(row.get('quantidade_vendida'))
                    available = 'S' if row.get('disponivel') is True else 'N'
                    unit_label = '' if not row.get('unidade_sigla') \
                        else row.get('unidade_sigla')
                    unit_fraction = 0 if not row.get('unidade_fracao') \
                        else int(row.get('unidade_fracao').get('fracao'))
                    qty_fraction = 0 if not row.get('unidade_fracao') \
                        else int(row.get('unidade_fracao').get('quantidade'))
                    price_fraction = 0 if not row.get('unidade_fracao') \
                        else float(row.get('unidade_fracao').get('preco'))

                    prioritized_product = 'S' if row.get('') is True else 'N'
                    offer = {} if not row.get('oferta') else row.get('oferta')

                    price_offer = 0 if not offer \
                        else float(offer.get('preco_oferta'))
                    qty_min = 0 if not offer \
                        else float(offer.get('quantidade_minima'))
                    qty_max = 0 if not offer \
                        else float(offer.get('quantidade_maxima'))
                    main_volume = '' \
                        if not row.get('volume_principal') or len(row.get('volume_principal')) > 0 \
                        else row.get('volume_principal')
                    image = '' if not row.get('imagem') \
                        else (f"https://s3.amazonaws.com/produtos.vipcommerce.com.br/"
                              f"250x250/{row.get('imagem')}")
                    url = '' if not row.get('link') \
                        else (f"https://www.{domain}/produtos/detalhe/"
                              f"{product_id}/{row.get('link')}")

                    fields = {
                        'name': name,
                        'ean': ean,
                        'sku': sku,
                        'product_id': product_id,
                        'brand': brand,
                        'category_id': category_id,
                        'branch_id': branch_id,
                        'distribution_center_id': distribution_center_id,
                        'price_from': price_from,
                        'price_to': price_to,
                        'price_offer': price_offer,
                        'qty_min': qty_min,
                        'qty_max': qty_max,
                        'sold_amount': sold_amount,
                        'available': available,
                        'unit_label': unit_label,
                        'unit_fraction': unit_fraction,
                        'qty_fraction': qty_fraction,
                        'price_fraction': price_fraction,
                        'prioritized_product': prioritized_product,
                        'main_volume': main_volume,
                        'url': url,
                        'image': image,
                        'created_at': now.strftime("%Y-%m-%d"),
                        'hour': now.strftime("%H:%M:%S")
                    }

                    log.info(fields)
                    assortment_model = AssortmentModel(**fields)
                    assortment_list.append(assortment_model)

            paginator = data.get("paginator", {})
            return AssortmentHeader(
                records_per_page=paginator.get("items_per_page", 0),
                items=paginator.get("total_items", 0),
                pages=paginator.get("total_pages", 0),
                data=assortment_list,
            )
        except Exception as e:
            log.info(e.args)

