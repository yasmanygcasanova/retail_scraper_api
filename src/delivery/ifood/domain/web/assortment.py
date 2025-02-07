""" Assortment """
import asyncio
import json
import re
from datetime import datetime
from math import ceil
from typing import Dict, List, Optional, Any
import random

from fastapi import HTTPException, status
from loguru import logger as log
from user_agent import generate_user_agent

from core.util.model_validator import validate_and_parse_model
from core.util.strings import clean_ean, clean_html
from models.ifood.assortment import AssortmentHeader, AssortmentModel
from src.delivery.ifood.models.web.product import ProductModel


class Assortment:
    """ Class Assortment """
    host = 'marketplace.ifood.com.br'
    base_url = 'https://www.ifood.com.br'
    base_image_url = 'https://static-images.ifood.com.br'

    @classmethod
    def _get_default_headers(cls) -> Dict[str, str]:
        """Headers padrão para requisições"""
        return {
            'User-Agent': generate_user_agent(),
            'Accept': "application/json, text/plain, */*",
            'Accept-Language': "pt-BR,pt;q=1",
            'Accept-Encoding': "gzip, deflate, br",
            'Cache-Control': "no-cache, no-store",
            'Origin': cls.base_url,
            'Connection': "keep-alive",
            'Referer': cls.base_url,
            'Sec-Fetch-Dest': "empty",
            'Sec-Fetch-Mode': "cors",
            'Sec-Fetch-Site': "same-site",
            'Pragma': "no-cache",
            'TE': "trailers",
            'cache-control': "no-cache"
        }

    @classmethod
    async def request(
        cls,
        client: object,
        store_id: str,
        department_id: str,
        page: str,
        request_waiting: int
    ) -> Dict[str, Any]:
        """
        Realiza requisição para obter dados do cardápio
        :param client: Cliente HTTP
        :param store_id: ID da loja
        :param department_id: ID do departamento
        :param page: Número da página
        :param request_waiting: Tempo de espera
        :return: Dados do cardápio
        """
        url = f"https://{cls.host}/v1/merchants/{store_id}/catalog-category/{department_id}"
        log.info(f"{url}: scraping data for store {store_id}")

        try:
            params = {
                "items_page": page,
                "items_size": "50"
            }

            await asyncio.sleep(request_waiting)
            response = await client.get(
                url,
                headers=cls._get_default_headers(),
                params=params
            )
            response.raise_for_status()
            data = json.loads(response.text)
            log.info(data)
            return {} if not data else data
            
        except Exception as e:
            log.error(f"Erro ao buscar cardápio da loja {store_id}: {str(e)}")
            return {}

    @classmethod
    async def get_product(cls, **kwargs) -> Dict[str, str]:
        """
        Obtém detalhes do produto
        :param kwargs: Parâmetros da requisição
        :return: Detalhes do produto
        """
        url = f"https://{cls.host}/ifood-ws-v3/restaurant/{kwargs['store_id']}/menuitem/{kwargs['category_id']}"
        log.info(f"{url}: scraping data")

        try:
            # Reduz o tempo de espera entre requisições e adiciona jitter aleatório
            await asyncio.sleep(random.uniform(0.5, 1.5))
            
            # Adiciona timeout e retry na requisição
            for attempt in range(3):
                try:
                    response = await kwargs['client'].get(
                        url,
                        headers=cls._get_default_headers(),
                        timeout=5.0
                    )
                    break
                except Exception as e:
                    if attempt == 2:  # última tentativa
                        raise
                    await asyncio.sleep(1 * (attempt + 1))
                    continue
            
            try:
                data = json.loads(response.text)
            except json.JSONDecodeError:
                log.warning(f"Resposta inválida para produto {kwargs['category_id']}")
                return cls._get_empty_product()

            # Verifica se tem dados válidos
            if not data or data.get('code') == '102':
                return cls._get_empty_product()

            menu = data.get('data', {}).get('menu', [])
            if not menu:
                return cls._get_empty_product()

            items = menu[0].get('itens', {})
            if not items:
                return cls._get_empty_product()

            # Processa apenas o primeiro item
            row = items[0] if items else {}
            if not row:
                return cls._get_empty_product()

            return {
                'sku': row.get('posCode', 'NA'),
                'availability': 'S' if re.search(
                    r'AVAILABLE',
                    row.get('availability', ''),
                    re.IGNORECASE
                ) else 'N',
                'taxonomy_name': clean_html(row.get('taxonomyName', 'NA')),
                'taxonomy_type': row.get('taxonomyType', 'NA'),
                'category': clean_html(row.get('parentTaxonomyName', 'NA'))
            }

        except Exception as e:
            log.error(f"Erro ao buscar produto {kwargs.get('category_id')}: {str(e)}")
            return cls._get_empty_product()

    @staticmethod
    def _get_empty_product() -> Dict[str, str]:
        """Retorna produto vazio com valores padrão"""
        return {
            'sku': 'NA',
            'availability': 'N',
            'taxonomy_name': 'NA',
            'taxonomy_type': 'NA',
            'category': 'NA'
        }

    @staticmethod
    def _calculate_discount(price_to: float, unit_original_price: float) -> tuple[float, int]:
        """Calcula desconto e preço original"""
        if unit_original_price > 0:
            discount = ceil(abs(((price_to / unit_original_price) * 100) - 100))
            return unit_original_price, discount
        return 0, 0

    @classmethod
    def _build_product_url(cls, **kwargs) -> str:
        """Constrói URL do produto"""
        return (f"{cls.base_url}/delivery/{kwargs['region']}/{kwargs['store_slug']}"
                f"/{kwargs['store_id']}?corredor={kwargs['department_id']}"
                f"&item={kwargs['category_id']}")

    @classmethod
    def _build_image_url(cls, slug: str) -> str:
        """Constrói URL da imagem"""
        if not slug:
            return ''
        return f"{cls.base_image_url}/image/upload/t_high/pratos/{slug}"

    @classmethod
    async def get_data(cls, **kwargs) -> Optional[AssortmentHeader]:
        """
        Processa dados do cardápio
        :param kwargs: Parâmetros de processamento
        :return: Dados processados do cardápio
        """
        try:
            now = datetime.now()
            assortment_list = []
            
            category_menu = kwargs['data'].get('categoryMenu', {})
            if not category_menu:
                log.warning("Menu de categorias vazio")
                return AssortmentHeader(records_per_page=50, items=0, pages=0, data=[])

            department = clean_html(category_menu.get('name', 'NA'))
            items = category_menu.get('itens', [])

            # Processa produtos em paralelo
            tasks = []
            for product in items:
                category_id = product.get('id', 'NA')
                if category_id == 'NA':
                    continue

                task = asyncio.create_task(cls.get_product(
                    store_id=kwargs['store_id'],
                    client=kwargs['client'],
                    category_id=category_id
                ))
                tasks.append((product, task))

            # Aguarda todos os produtos serem processados
            for product, task in tasks:
                try:
                    product_info = await task
                    
                    # Processa preços e desconto
                    price_to = float(product.get('unitMinPrice', 0) or 0)
                    price_from = float(product.get('unitPrice', 0) or 0)
                    unit_original_price = float(product.get('unitOriginalPrice', 0) or 0)

                    if price_from == price_to and price_from > 0:
                        price_from = 0

                    price_from, discount = cls._calculate_discount(price_to, unit_original_price)

                    fields = {
                        'name': clean_html(product.get('description', 'NA')),
                        'ean': clean_ean(product.get('ean', 0)),
                        'sku': product_info.get('sku'),
                        'department': department,
                        'category': product_info.get('category'),
                        'sub_category': product_info.get('taxonomy_name'),
                        'department_id': kwargs['department_id'],
                        'category_id': product.get('id', 'NA'),
                        'search_term': kwargs['search_term'],
                        'details': clean_html(product.get('details', 'NA')),
                        'availability': product_info.get('availability'),
                        'price_from': price_from,
                        'price_to': price_to,
                        'discount': discount,
                        'segment_type': kwargs['segment_type'],
                        'store_id': kwargs['store_id'],
                        'latitude': kwargs['latitude'],
                        'longitude': kwargs['longitude'],
                        'image': cls._build_image_url(product.get('logoUrl')),
                        'url': cls._build_product_url(**kwargs, category_id=product.get('id')),
                        'created_at': now.strftime("%Y-%m-%d"),
                        'hour': now.strftime("%H:%M:%S")
                    }

                    if product_model := validate_and_parse_model(fields, ProductModel):
                        assortment = AssortmentModel(**fields)
                        assortment_list.append(assortment)
                    else:
                        log.warning(f"Falha na validação do produto: {fields.get('sku')}")

                except Exception as e:
                    log.error(f"Erro ao processar produto: {str(e)}")
                    continue

            # Processa informações de paginação
            metadata = kwargs['data'].get('metadata', {})
            pagination = metadata.get('pagination', {})
            
            return AssortmentHeader(
                records_per_page=50,
                items=pagination.get('items', 0),
                pages=pagination.get('pages', 0),
                data=assortment_list
            )
            
        except Exception as e:
            log.error(f"Erro ao processar cardápio: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Erro ao processar dados do cardápio"
            )
