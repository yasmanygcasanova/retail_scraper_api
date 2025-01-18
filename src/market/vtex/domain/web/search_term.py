""" Search Term """
import asyncio
import json
import re
from datetime import datetime

from fastapi import HTTPException, status
from loguru import logger as log
from pydantic import ValidationError

from core.util.strings import clean_ean, clean_html
from models.vtex.search_term import SearchTermHeader, SearchTermModel


class SearchTerm:
    """ Class Search Term """
    @classmethod
    async def request(
        cls,
        client: object,
        alias: str,
        search_name: str,
        _from: int,
        _to: int,
        request_waiting: int
    ) -> list:
        """
        Function Request
        :param client:
        :param alias:
        :param search_name:
        :param _from:
        :param _to:
        :param request_waiting:
        :return: list
        """
        data = []

        url = f"https://{alias}.vtexcommercestable.com.br/api/catalog_system/pub/products/search/" \
              f"?ft={search_name}&_from={_from}&_to={_to}"
        log.info(f"{url}: scraping data")

        headers = {
            'Content-Type': "application/json",
            'Accept': "application/json",
            'cache-control': "no-cache"
        }

        await asyncio.sleep(request_waiting)
        response = await client.get(
            url,
            headers=headers,
            timeout=None
        )
        status_code_list = [
            status.HTTP_206_PARTIAL_CONTENT,
            status.HTTP_200_OK
        ]
        if response.status_code in status_code_list:
            data = json.loads(response.text)
            return [] if not data else data
        if response.status_code == status.HTTP_429_TOO_MANY_REQUESTS:
            data = [{'status_code': status.HTTP_429_TOO_MANY_REQUESTS}]
        return data

    @staticmethod
    def product_detail(store_url: str, product: dict) -> dict:
        """
        Function Product Detail
        :param store_url:
        :param product:
        :return: dict
        """
        product_name = 'NA' if not product.get('productName') \
            else clean_html(product.get('productName'))
        product_title = 'NA' if not product.get('productTitle') \
            else clean_html(product.get('productTitle'))
        sku = '' if not product.get('productId') \
            else product.get('productId')
        product_ref = '' if not product.get('productReference') \
            else product.get('productReference')
        product_slug = '' if not product.get('linkText') \
            else f"{store_url}{product.get('linkText')}/p"
        brand_id = '' if not product.get('brandId') \
            else int(product.get('brandId'))

        cluster = product.get('clusterHighlights')
        cluster_highlights = '' if not cluster and not cluster.get('2349') else cluster.get('2349')
        discount = 0
        if cluster_highlights:
            if regex_discount := re.search(
                    r'PIX\s*(\d+)%',
                    cluster_highlights,
                    re.IGNORECASE
            ):
                discount = 0 if not regex_discount else int(regex_discount.group(1))

        return {
            'product_name': product_name,
            'sku': sku,
            'product_ref': product_ref,
            'product_title': product_title,
            'product_slug': product_slug,
            'brand_id': brand_id,
            'discount': discount
        }

    @staticmethod
    def get_image(
        product: dict
    ) -> dict:
        """
        Get Image
        :param product:
        :return: dict
        """
        image = ''
        # Image Info
        images_info = {} if not product.get('images') \
            else product.get('images')
        if not images_info:
            image = ''
        else:
            for img in images_info:
                if not img.get('imageLabel'):
                    image = img.get('imageUrl')
                    break
                if re.search('front view', img.get('imageLabel'), re.IGNORECASE):
                    image = img.get('imageUrl')
                    break
                if re.search('principal', img.get('imageLabel'), re.IGNORECASE):
                    image = img.get('imageUrl')
                    break
        return {
            'image': image
        }

    @classmethod
    def get_seller(
        cls,
        products: dict
    ) -> list:
        """
        Get Seller
        :param products:
        :return: list
        """
        seller_info = []
        installments_amount = installments_value = installments_total_value = 0
        interest_rate = ''

        if len(products.get('items')) > 0:
            for product in products.get('items'):
                ean = 0 if not product.get('ean') \
                    else clean_ean(product.get('ean'))
                sku = '' if not product.get('itemId') \
                    else product.get('itemId')
                measurement_unit = '' if not product.get('measurementUnit') \
                    else product.get('measurementUnit')
                unit_multiplier = 0 if not product.get('unitMultiplier') \
                    else product.get('unitMultiplier')
                is_kit = 'S' if product.get('isKit') is True else 'N'

                # Image Info
                image_info = cls.get_image(product)
                for seller in product.get('sellers'):
                    seller_id = 'NA' if not seller.get('sellerId') \
                        else seller.get('sellerId')
                    seller_name = 'NA' if not seller.get('sellerName') \
                        else clean_html(seller.get('sellerName'))
                    seller_default = 'S' \
                        if seller.get('sellerDefault') is True else 'N'

                    if seller_id == "1":
                        seller_type = 'LP'
                    elif seller_id != "1" and seller_default == 'S':
                        seller_type = 'VP'
                    else:
                        seller_type = 'V'

                    offer = {} if not seller.get('commertialOffer') \
                        else seller.get('commertialOffer')
                    if not offer:
                        available_quantity = price_from = price_to = \
                            price_without_discount = reward_value = tax = 0
                        available = 'N'
                    else:
                        available_quantity = 0 if not offer.get('AvailableQuantity') \
                            else offer.get('AvailableQuantity')
                        available = 'S' if offer.get('IsAvailable') is True else 'N'
                        price_from = 0 if not offer.get('ListPrice') \
                            else offer.get('ListPrice')
                        price_to = 0 if not offer.get('Price') \
                            else offer.get('Price')
                        price_without_discount = 0 if not offer.get('PriceWithoutDiscount') \
                            else offer.get('PriceWithoutDiscount')
                        reward_value = 0 if not offer.get('RewardValue') \
                            else offer.get('RewardValue')
                        tax = 0 if not offer.get('Tax') \
                            else offer.get('Tax')

                    commertial_offer = {} if not seller.get('commertialOffer') \
                        else seller.get('commertialOffer')
                    if commertial_offer and len(commertial_offer.get('Installments')) > 0:
                        installment_info = cls.get_installments(
                            commertial_offer.get('Installments')
                        )
                        installments_amount = installment_info.get('installments_amount')
                        installments_value = installment_info.get('installments_value')
                        interest_rate = installment_info.get('interest_rate')
                        installments_total_value = installment_info.get('installments_total_value')

                    data = {
                        'ean': ean,
                        'sku': sku,
                        'measurement_unit': measurement_unit,
                        'unit_multiplier': unit_multiplier,
                        'is_kit': is_kit,
                        'image': image_info.get('image'),
                        'seller_id': seller_id,
                        'seller_name': seller_name,
                        'seller_default': seller_default,
                        'seller_type': seller_type,
                        'available_quantity': available_quantity,
                        'available': available,
                        'price_from': price_from,
                        'price_to': price_to,
                        'price_without_discount': price_without_discount,
                        'reward_value': reward_value,
                        'tax': tax,
                        'installments_amount': installments_amount,
                        'installments_value': installments_value,
                        'interest_rate': interest_rate,
                        'installments_total_value': installments_total_value
                    }
                    seller_info.append(data)
        return seller_info

    @staticmethod
    def get_installments(installments: list) -> dict:
        """
        Get Installments
        :param installments:
        :return: dict
        """
        installments_info = []
        for row in installments:
            if re.search(r'Mastercard', row.get('PaymentSystemName'), re.IGNORECASE):
                installments_amount = 0 if not row.get('NumberOfInstallments') \
                    else row.get('NumberOfInstallments')
                installments_value = 0 if not row.get('Value') else row.get('Value')
                interest_rate = 'com juros' \
                    if not row.get('InterestRate') and row.get('InterestRate') > 0 \
                    else 'sem juros'
                installments_total_value = 0 if not row.get('TotalValuePlusInterestRate') \
                    else row.get('TotalValuePlusInterestRate')

                data = {
                    'installments_amount': installments_amount,
                    'installments_value': installments_value,
                    'interest_rate': interest_rate,
                    'installments_total_value': installments_total_value,
                }
                installments_info.append(data)
        return installments_info.pop()

    @classmethod
    async def get_data(
        cls,
        domain: str,
        subdomain: str,
        search_name: str,
        _from: int,
        _to: int,
        data: list
    ):
        """
        Get Data
        :param domain:
        :param subdomain:
        :param search_name:
        :param _from:
        :param _to:
        :param data:
        :return: list
        """
        try:
            now = datetime.now()
            search_term_list = []
            store_url = f"https://www.{domain}/" \
                if not subdomain else f"https://{subdomain}.{domain}/"

            for product in data:
                product_detail = cls.product_detail(store_url, product)
                sellers = cls.get_seller(product)

                for seller_info in sellers:
                    price_from = seller_info.get('price_from')
                    price_to = seller_info.get('price_to')
                    discount = product_detail.get('discount')
                    if (price_from > 0 and price_to > 0) and (price_from == price_to):
                        price_from = 0

                    if seller_info.get('available') == 'N':
                        price_from = 0
                        price_to = 0

                    if price_to > 0 and discount > 0:
                        discount_value = abs((price_to * discount) / 100)
                        price_pix = round(abs(price_to - discount_value), 2)
                    else:
                        price_pix = price_to

                    fields = {
                        'name': product_detail.get('product_name'),
                        'product_title': product_detail.get('product_title'),
                        'ean': seller_info.get('ean'),
                        'sku': seller_info.get('sku'),
                        'product_ref': product_detail.get('product_ref'),
                        'search_name': search_name,
                        'brand_id': product_detail.get('brand_id'),
                        'measurement_unit': seller_info.get('measurement_unit'),
                        'unit_multiplier': seller_info.get('unit_multiplier'),
                        'is_kit': seller_info.get('is_kit'),
                        'seller_id': seller_info.get('seller_id'),
                        'seller_name': seller_info.get('seller_name'),
                        'seller_default': seller_info.get('seller_default'),
                        'seller_type': seller_info.get('seller_type'),
                        'available_quantity': seller_info.get('available_quantity'),
                        'available': seller_info.get('available'),
                        'price_from': price_from,
                        'price_to': price_to,
                        'price_pix': price_pix,
                        'price_without_discount': seller_info.get('price_without_discount'),
                        'discount': discount,
                        'installments_amount': seller_info.get('installments_amount'),
                        'installments_value': seller_info.get('installments_value'),
                        'interest_rate': seller_info.get('interest_rate'),
                        'installments_total_value': seller_info.get('installments_total_value'),
                        'reward_value': seller_info.get('reward_value'),
                        'tax': seller_info.get('tax'),
                        'url': product_detail.get('product_slug'),
                        'image': seller_info.get('image'),
                        'created_at': now.strftime("%Y-%m-%d"),
                        'hour': now.strftime("%H:%M:%S")
                    }
                    log.info(fields)
                    try:
                        search_term_model = SearchTermModel(**fields)
                        search_term_list.append(search_term_model)
                    except ValidationError as e:
                        log.info(e)
                        return HTTPException(
                            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                            detail=str(e)
                        )

            # Pagination Info
            records_per_page = 20
            items = 2500
            pages = 130

            result = SearchTermHeader(
                records_per_page=records_per_page,
                items=items,
                pages=pages,
                offset=_from,
                limit=_to,
                data=search_term_list
            )
            return result
        except Exception as e:
            log.info(e.args)
