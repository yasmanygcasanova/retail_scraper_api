"""Category"""

import asyncio
from typing import List, Dict, Any

from loguru import logger as log
from user_agent import generate_user_agent

from core.util.strings import check_subdomain, clean_html
from models.osuper.category import CategoryHeader, CategoryModel


class Category:
    """Class Category."""

    @staticmethod
    async def request(
        client: Any,
        domain: str,
        store_id: int,
        request_waiting: int
    ) -> List[Dict[str, Any]]:
        """
        Sends a request to fetch category data from the API.

        Args:
            client: HTTP client instance.
            domain: The domain to scrape.
            store_id: The store's ID.
            request_waiting: Delay in seconds before making the request.

        Returns:
            A list of categories or an empty list in case of failure.
        """
        url = f"https://api.{domain}/graphql"
        log.info(f"Scraping data from {url}")

        payload = Category._build_payload(store_id)
        headers = Category._generate_headers(domain)

        await asyncio.sleep(request_waiting)

        try:
            response = await client.post(
                url, headers=headers, json=payload, timeout=None
            )
            response.raise_for_status()

            response_data = response.json()
            categories = (
                response_data.get("data", {})
                .get("publicViewer", {})
                .get("categories", [])
            )
            return categories
        except Exception as e:
            log.error(f"Error fetching data: {e}")
            return []

    @staticmethod
    def _build_payload(store_id: int) -> Dict[str, Any]:
        """Constructs the GraphQL payload for the request."""
        return {
            "query": """
            query AllCategoriesPageQuery($storeId: ID!) {
              publicViewer(storeId: $storeId) {
                id
                categories(storeId: $storeId) {
                  id
                  name
                  slug
                  imageCategoryPage {
                    url
                    thumborized
                    __typename
                  }
                  children(active: true, group: true) {
                    id
                    name
                    slug
                    __typename
                  }
                  __typename
                }
                __typename
              }
            }
            """,
            "variables": {"storeId": str(store_id)},
        }

    @staticmethod
    def _generate_headers(domain: str) -> Dict[str, str]:
        """Generates HTTP headers for the API request."""
        origin = check_subdomain(domain)
        return {
            "User-Agent": generate_user_agent(),
            "Accept": "*/*",
            "Accept-Language": "pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3",
            "Accept-Encoding": "gzip, deflate, br",
            "Content-Type": "application/json",
            "Origin": origin,
            "Connection": "keep-alive",
            "Sec-Fetch-Dest": "empty",
            "Sec-Fetch-Mode": "cors",
            "Sec-Fetch-Site": "same-site",
            "Pragma": "no-cache",
            "Cache-Control": "no-cache",
        }

    @staticmethod
    async def get_data(store_id: int, data: List[Dict[str, Any]]) -> CategoryHeader:
        """
        Processes and maps raw category data into a CategoryHeader object.

        Args:
            store_id: The store's ID.
            data: List of raw category data.

        Returns:
            A CategoryHeader object with the processed category list.
        """
        category_list = []

        for row in data:
            department_id = int(row.get("id", 0))
            children = row.get("children", [])

            for child in children:
                category_list.append(
                    Category._process_category(store_id, department_id, row, child)
                )

        return CategoryHeader(data=category_list)

    @staticmethod
    def _process_category(
        store_id: int, department_id: int, parent: Dict[str, Any], child: Dict[str, Any]
    ) -> CategoryModel:
        """Processes a single category and maps it into a CategoryModel."""
        name = clean_html(child.get("name", "NA"))
        search_term = f"{parent.get('name', 'NA')} > {child.get('name', 'NA')}"
        return CategoryModel(
            name=name,
            category_id=int(child.get("id", 0)),
            department_id=department_id,
            store_id=store_id,
            slug=child.get("slug", "NA"),
            search_term=search_term,
        )
