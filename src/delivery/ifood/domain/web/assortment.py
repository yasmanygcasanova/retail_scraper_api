""" Assortment """
import asyncio
import json
import re
import urllib.parse
from datetime import datetime
from math import ceil

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

    headers = {
        'User-Agent': generate_user_agent(),
        'Accept': "application/json, text/plain, */*",
        'Accept-Language': "pt-BR,pt;q=1",
        'Accept-Encoding': "gzip, deflate, br",
        'Cache-Control': "no-cache, no-store",
        # 'access_key': "69f181d5-0046-4221-b7b2-deef62bd60d5",
        # 'secret_key': "9ef4fb4f-7a1d-4e0d-a9b1-9b82873297d8",
        # 'platform': "Desktop",
        # 'app_version': "9.94.6",
        # 'browser': "Ubuntu",
        'Origin': base_url,
        'Connection': "keep-alive",
        'Referer': base_url,
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
    ) -> dict:
        """
        Function Request
        :param client:
        :param store_id:
        :param department_id:
        :param search_term:
        :param page:
        :param request_waiting:
        :return: dict
        """
        url = f"https://{cls.host}/v1/" \
              f"merchants/{store_id}/catalog-category/{department_id}"
        log.info(f"{url}: scraping data")

        params = {
            "items_page": page,
            "items_size": "50",
            # "parent_taxonomy_name": urllib.parse.quote(search_term)
        }

        await asyncio.sleep(request_waiting)
        response = await client.get(
            url,
            headers=cls.headers,
            params=params
        )
        data = json.loads(response.text)
        log.info(data)
        return {} if not data else data

    @classmethod
    async def get_product(cls, **kwargs):
        """
        Function Get Product
        :param kwargs:
        :return:
        """
        url = f"https://{cls.host}/ifood-ws-v3/" \
              f"restaurant/{kwargs['store_id']}/menuitem/{kwargs['category_id']}"
        log.info(f"{url}: scraping data")
        await asyncio.sleep(2)
        response = await kwargs['client'].get(
            url,
            headers=cls.headers
        )
        data = json.loads(response.text)
        items = {} if not data.get('data') or data.get('code') == '102' \
            else data.get('data').get('menu')[0].get('itens')
        availability = taxonomy_name = taxonomy_type = category = sku = ''

        if items:
            for row in items:
                sku = 'NA' if not row.get('posCode') \
                    else row.get('posCode')
                availability = 'S' if re.search(
                    r'AVAILABLE',
                    row.get('availability'),
                    re.IGNORECASE
                ) else 'N'
                taxonomy_name = 'NA' if not row.get('taxonomyName') \
                    else clean_html(row.get('taxonomyName'))
                taxonomy_type = 'NA' if not row.get('taxonomyType') \
                    else row.get('taxonomyType')
                category = 'NA' if not row.get('parentTaxonomyName') \
                    else clean_html(row.get('parentTaxonomyName'))

        prod = {
            'sku': sku,
            'availability': availability,
            'taxonomy_name': taxonomy_name,
            'taxonomy_type': taxonomy_type,
            'category': category
        }
        return prod

    @classmethod
    async def get_data(cls, **kwargs):
        """
        Function Get Data
        :param kwargs:
        :return:
        """
        now = datetime.now()
        assortment_list = []
        # Assortment Info
        category_menu = {} if not kwargs['data'].get('categoryMenu') \
            else kwargs['data'].get('categoryMenu')

        department = 'NA' if not category_menu.get('name') \
            else clean_html(category_menu.get('name'))

        items = [] if not category_menu.get('itens') \
            else category_menu.get('itens')
        if items:
            for product in items:
                name = 'NA' if not product.get('description') \
                    else clean_html(product.get('description'))
                ean = 0 if not product.get('ean') \
                    else clean_ean(product.get('ean'))
                category_id = 'NA' if not product.get('id') \
                    else product.get('id')
                details = 'NA' if not product.get('details') \
                    else clean_html(product.get('details'))

                slug = '' if not product.get('logoUrl') \
                    else product.get('logoUrl')
                base_url_image = 'https://static-images.ifood.com.br'
                slug_image = f'image/upload/t_high/pratos/{slug}'
                image = f'{base_url_image}/{slug_image}'

                url = f"{cls.base_url}/delivery/" \
                      f"{kwargs['region']}/{kwargs['store_slug']}" \
                      f"/{kwargs['store_id']}?" \
                      f"corredor={kwargs['department_id']}" \
                      f"&item={category_id}"

                price_from = 0 if not product.get('unitPrice') \
                    else float(product.get('unitPrice'))
                price_to = 0 if not product.get('unitMinPrice') \
                    else float(product.get('unitMinPrice'))

                if (price_from == price_to) and (price_from > 0 and price_to > 0):
                    price_from = 0

                unit_original_price = 0 if not product.get('unitOriginalPrice') \
                    else float(product.get('unitOriginalPrice'))

                discount = 0
                if unit_original_price > 0:
                    price_from = unit_original_price
                    discount = ceil(abs(((price_to / unit_original_price) * 100) - 100))

                # Product Info
                product_info = await cls.get_product(
                    store_id=kwargs['store_id'],
                    client=kwargs['client'],
                    category_id=category_id
                )
                fields = {
                    'name': name,
                    'ean': ean,
                    'sku': product_info.get('sku'),
                    'department': department,
                    'category': product_info.get('category'),
                    'sub_category': product_info.get('taxonomy_name'),
                    'department_id': kwargs['department_id'],
                    'category_id': category_id,
                    'search_term': kwargs['search_term'],
                    'details': details,
                    'availability': product_info.get('availability'),
                    'price_from': price_from,
                    'price_to': price_to,
                    'discount': discount,
                    'segment_type': kwargs['segment_type'],
                    'store_id': kwargs['store_id'],
                    'latitude': kwargs['latitude'],
                    'longitude': kwargs['longitude'],
                    # 'taxonomy_type': product_info.get('taxonomy_type'),
                    'image': image,
                    'url': url,
                    'created_at': now.strftime("%Y-%m-%d"),
                    'hour': now.strftime("%H:%M:%S")
                }
                log.info(fields)
                try:
                    # Validate Product Model
                    if product_model := validate_and_parse_model(
                        fields,
                        ProductModel
                    ):
                        # Save data in the Assortment Model
                        assortment = AssortmentModel(**fields)
                        assortment_list.append(assortment)
                    else:
                        log.info(product_model)
                except ValueError as e:
                    log.info(e.args)
                    return HTTPException(
                        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                        detail=str(e.args)
                    )
        # Pagination Info
        metadata = {} if not kwargs['data'].get('metadata') \
            else kwargs['data'].get('metadata')
        items = 0 if not metadata.get('pagination') \
            else metadata.get('pagination').get('items')
        pages = 0 if not metadata.get('pagination') \
            else metadata.get('pagination').get('pages')

        # Save data in the Assortment Header
        result = AssortmentHeader(
            records_per_page=50,
            items=items,
            pages=pages,
            data=assortment_list
        )
        return result
