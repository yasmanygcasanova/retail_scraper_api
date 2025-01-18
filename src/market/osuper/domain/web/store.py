""" Store """
import asyncio
import json
from typing import List, Dict, Any

from loguru import logger as log
from user_agent import generate_user_agent

from core.util.strings import check_subdomain, clean_html
from models.osuper.store import StoreHeader, StoreModel
from src.market.osuper.domain.web.account import Account


class Store:
    """ Class Store """
    @staticmethod
    async def request(
        client: object,
        domain: str,
        request_waiting: int
    ) -> List[Dict[str, Any]]:
        """
        Fetch store data from the API.
        :param client: HTTP client for making requests.
        :param domain: The domain for API requests.
        :param request_waiting: Time to wait between requests.
        :return: List of store data.
        """
        try:
            url = f"https://api.{domain}/graphql"
            log.info(f"{url}: Fetching store data")

            payload = {
                "query": """
                fragment StoreFields on PublicViewerStore {
                  id
                  name
                  alias
                  timezone
                  cnpj
                  messageConfig
                  alertConfig {
                    id
                    active
                    backgroundColor
                    text
                    textColor
                    time
                    icon
                    __typename
                  }
                  id
                  popUpConfig {
                    id
                    active
                    backgroundColor
                    text
                    textColor
                    title
                    icon
                    __typename
                  }
                  antifraudConfig {
                    type
                    enabled
                    fingerprint
                    __typename
                  }
                  deliveryMapTool {
                    apiKey
                    defaultCenter {
                      lat
                      lng
                      __typename
                    }
                    defaultZoom
                    email
                    __typename
                  }
                  couponConfig {
                    active
                    __typename
                  }
                  categoriesConfigurations {
                    ordering
                    enableHighlighting
                    __typename
                  }
                  fullAddress {
                    id
                    complete
                    __typename
                  }
                  contacts {
                    identification
                    type
                    value
                    __typename
                  }
                  deliveryConfig {
                    id
                    active
                    daysToCollect
                    preparationTime
                    maxDeliveriesBySchedule
                    maxDeadlineExpressDelivery
                    __typename
                  }
                  selfCollectConfig {
                    id
                    active
                    daysToCollect
                    preparationPrice
                    preparationTime
                    __typename
                  }
                  orderConfiguration {
                    id
                    minOrderValue
                    minOrderValueEnabled
                    minValueForFreeDelivery
                    paymentNotice
                    registrationMessage
                    replacementOption
                    deliveryNotice
                    freeDeliveryEnabled
                    freeDeliveryEnabledForExpressDelivery
                    displayFreeDeliveryStatus
                    freeDeliveryPeriodStart
                    freeDeliveryPeriodEnd
                    minOrderValueForExpress
                    minOrderValueForFreeDeliveryExpress
                    __typename
                  }
                  productConfig {
                    id
                    displayNormalPrice
                    displayPercentageOfDiscount
                    displayPromotionBox
                    displayUnitContent
                    stockDisplayMethod
                    minimumStockToDisplay
                    minimumStockToDisplayWeighable
                    displayProductsOutOfStock
                    displayPromotionLimit
                    __typename
                  }
                  adwordsConfig {
                    awConversionId
                    awConversionLabel
                    __typename
                  }
                  recipeConfig {
                    displayParallax
                    subTitle
                    title
                    ordering
                    __typename
                  }
                  disableLeads
                  footerText
                  chatEmbed
                  chatEnabled
                  facebookPixelCode
                  allowedCustomerType
                  socialMediaConfig {
                    facebook
                    instagram
                    twitter
                    youtube
                    linkedin
                    __typename
                  }
                  openingHours {
                    weekdays {
                      start
                      end
                      __typename
                    }
                    sundays {
                      end
                      start
                      __typename
                    }
                    saturdays {
                      start
                      end
                      __typename
                    }
                    __typename
                  }
                  googleAdsConfig {
                    tagId
                    events {
                      addToCart
                      contact
                      viewProduct
                      registration
                      __typename
                    }
                    __typename
                  }
                  __typename
                }
                query OnlineStoresQuery($storeId: ID!) {
                  publicViewer(storeId: $storeId) {
                    id
                    onlineStores {
                      ...StoreFields
                      __typename
                    }
                    __typename
                  }
                }
                """,
                "variables": {
                    "storeId": "",
                }
            }

            headers = Store._build_headers(domain)
            await asyncio.sleep(request_waiting)
            response = await client.post(
                url,
                headers=headers,
                json=payload,
                timeout=None
            )

            response.raise_for_status()  # Raise an error for HTTP codes >= 400
            return Store._extract_store_data(response)
        except Exception as e:
            log.error(f"Error fetching store data: {e}")
            return []

    @staticmethod
    def _build_headers(domain: str) -> Dict[str, str]:
        """
        Build headers for the API request.
        :param domain: Domain of the request.
        :return: Headers as a dictionary.
        """
        origin = check_subdomain(domain)
        return {
            'User-Agent': generate_user_agent(),
            'Accept': '*/*',
            'Accept-Language': 'pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate, br',
            'content-type': 'application/json',
            'Origin': origin,
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'Pragma': 'no-cache',
            'Cache-Control': 'no-cache',
            'TE': 'trailers'
        }

    @staticmethod
    def _extract_store_data(response: Any) -> List[Dict[str, Any]]:
        """
        Extract store data from the API response.
        :param response: The HTTP response.
        :return: Extracted store data.
        """
        try:
            data = response.json()
            return data.get('data', {}).get('publicViewer', {}).get('onlineStores', [])
        except json.JSONDecodeError:
            log.error("Failed to parse JSON response")
            return []

    @staticmethod
    async def get_data(
        client: object,
        domain: str,
        request_waiting: int,
        data: List[Dict[str, Any]]
    ) -> StoreHeader:
        """
        Process raw store data into structured models.
        :param client: HTTP client for making requests.
        :param domain: The domain for API requests.
        :param request_waiting: Time to wait between requests.
        :param data: Raw store data from the API.
        :return: StoreHeader with processed data.
        """
        try:
            account_id = await Account.get_id(client, domain, request_waiting)
            store_list = [Store._build_store_model(row, account_id) for row in data]
            return StoreHeader(data=store_list)
        except Exception as e:
            log.error(f"Error processing store data: {e}")
            return StoreHeader(data=[])

    @staticmethod
    def _build_store_model(row: Dict[str, Any], account_id: int) -> StoreModel:
        """
        Build a StoreModel instance from raw data.
        :param row: A dictionary containing store data.
        :param account_id: The account ID associated with the store.
        :return: A StoreModel instance.
        """
        return StoreModel(
            name=clean_html(row.get('name', 'NA')),
            store_id=int(row.get('id', 0)),
            alias=clean_html(row.get('alias', 'NA')),
            cnpj=row.get('cnpj', 'NA'),
            address=clean_html(row.get('fullAddress', {}).get('complete', 'NA')),
            account_id=account_id,
            contacts=row.get('contacts', [])
        )
