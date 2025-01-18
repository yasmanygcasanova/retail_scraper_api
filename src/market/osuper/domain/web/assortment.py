""" Assortment """
import asyncio
import json
from datetime import datetime

from fastapi import HTTPException, status
from loguru import logger as log
from user_agent import generate_user_agent

from core.util.model_validator import validate_and_parse_model
from core.util.strings import check_subdomain, clean_html
from models.osuper.assortment import AssortmentHeader, AssortmentModel
from src.market.osuper.models.web.product import ProductModel

RECORDS_PER_PAGE = 12


class Assortment:
    """ Class Assortment """

    @classmethod
    async def request(
        cls,
        **kwargs
    ) -> list:
        """
        Function Request
        :param kwargs:
        :return: list
        """
        try:
            url = "https://search.osuper.com.br/ecommerce_products_production/_search"
            log.info(f"{url}: scraping data")

            origin = check_subdomain(kwargs["domain"])

            headers = {
                'User-Agent': generate_user_agent(),
                'Accept': 'application/json, text/plain, */*',
                'Accept-Language': 'pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3',
                'Accept-Encoding': 'gzip, deflate, br',
                'Content-Type': 'application/json',
                'Origin': origin,
                'Connection': 'keep-alive',
                'Sec-Fetch-Dest': 'empty',
                'Sec-Fetch-Mode': 'cors',
                'Sec-Fetch-Site': 'cross-site',
                'Pragma': 'no-cache',
                'Cache-Control': 'no-cache',
                'TE': 'trailers'
            }
            payload = json.dumps({
                "accountId": kwargs['account_id'],
                "storeId": kwargs['store_id'],
                "categoryName": kwargs['search_term'],
                "first": RECORDS_PER_PAGE,
                "promotion": None,
                "after": kwargs['page'],
                "search": "",
                "brands": [],
                "categories": [],
                "tags": [],
                "personas": [],
                "sort": {
                    "field": "_score",
                    "order": "desc"
                },
                "pricingRange": {},
                "highlightEnabled": False
            })

            await asyncio.sleep(kwargs['request_waiting'])
            response = await kwargs['client'].post(
                url,
                headers=headers,
                data=payload
            )

            if response and response.status_code == status.HTTP_200_OK:
                data = json.loads(response.text)
                current_products = [] if not data.get('edges') else data.get('edges')
                kwargs['products'].append(current_products)

                page_info = {} if not data.get('pageInfo') else data.get('pageInfo')
                end_cursor = "" if not page_info else page_info.get('endCursor')

                if page_info.get('hasNextPage') is True:
                    await cls.request(
                        client=kwargs['client'],
                        domain=kwargs['domain'],
                        page=end_cursor,
                        account_id=kwargs['account_id'],
                        store_id=kwargs['store_id'],
                        search_term=kwargs['search_term'],
                        products=kwargs['products'],
                        request_waiting=kwargs['request_waiting']
                    )
            return kwargs['products']
        except Exception as e:
            log.info(e.args)

    @staticmethod
    async def get_data(**kwargs):
        """
        Function Get Data
        :param kwargs:
        :return:
        """
        try:
            now = datetime.now()
            assortment_list = []
            if len(kwargs['data']) > 0:
                for products in kwargs['data']:
                    for row in products:
                        node = {} if not row.get('node') else row.get('node')
                        name = 'NA' if not node else clean_html(node.get('name'))
                        ean = 0 if not node or not node.get('gtin') \
                            else int(node.get('gtin'))
                        sku = 'NA' if not node or not node.get('objectID') \
                            else node.get('objectID')
                        brand = 'NA' if not node or not node.get('brandName') \
                            else clean_html(node.get('brandName'))
                        available = 'S'
                        sale_unit = '' if not node or not node.get('saleUnit') \
                            else node.get('saleUnit')
                        slug = '' if not node.get('slug') or not node.get('slug') \
                            else node.get('slug')
                        image = '' if not node.get('image') or not node.get('image') \
                            else node.get('image')
                        # Price Info
                        price_from = price_to = discount = 0
                        pricing = [] if not node else node.get('pricing')
                        if len(pricing) > 0:
                            for price in pricing:
                                if price.get('store') == kwargs['store_id']:
                                    price_from = 0 if not price or not price.get('price') \
                                        else float(price.get('price'))
                                    price_to = 0 if not price or not price.get('promotionalPrice') \
                                        else float(price.get('promotionalPrice'))
                                    discount = 0 if not price or not price.get('discount') \
                                        else float(price.get('discount'))
                                    break

                        if price_from > 0 and price_to == 0:
                            price_to = price_from
                            price_from = 0

                        if (price_from > 0 and price_to > 0) and (price_from == price_to):
                            price_from = 0

                        # Stock info
                        quantity = [] if not node else node.get('quantity')
                        in_stock = 0
                        if len(quantity) > 0:
                            for qty in quantity:
                                if qty.get('store') == kwargs['store_id']:
                                    in_stock = 0 if not qty or not qty.get('inStock') \
                                        else int(qty.get('inStock'))
                                    break

                        sales_per_store = [] if not node.get('sales_per_store') \
                            else node.get('sales_per_store')
                        qty_sale = 0
                        if len(sales_per_store) > 0:
                            for sales in sales_per_store:
                                if sales.get('store') == kwargs['store_id']:
                                    qty_sale = 0 if not sales.get('count') \
                                        else int(sales.get('count'))
                                    break

                        fields = {
                            'name': name,
                            'ean': ean,
                            'sku': sku,
                            'store_id': kwargs['store_id'],
                            'category_id': kwargs['category_id'],
                            'search_term': kwargs['search_term'],
                            'brand': brand,
                            'available': available,
                            'sale_unit': sale_unit,
                            'qty_sale': qty_sale,
                            'price_from': price_from,
                            'price_to': price_to,
                            'discount': discount,
                            'in_stock': in_stock,
                            'slug': slug,
                            'image': image,
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
                                assortment_model = AssortmentModel(**fields)
                                assortment_list.append(assortment_model)
                            else:
                                log.info(product_model)
                        except ValueError as e:
                            log.info(e.args)
                            return HTTPException(
                                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                detail=str(e.args)
                            )
            result = AssortmentHeader(
                data=assortment_list
            )
            return result
        except Exception as e:
            log.info(e.args)
