"""Department"""
import asyncio
from typing import List, Dict, Any

from loguru import logger as log
from user_agent import generate_user_agent

from core.util.strings import check_subdomain, clean_html
from models.osuper.department import DepartmentHeader, DepartmentModel


class Department:
    """Class Department"""

    @staticmethod
    async def request(
        client: Any,
        domain: str,
        store_id: int,
        request_waiting: int,
    ) -> List[Dict[str, Any]]:
        """
        Fetches department data from the API.

        Args:
            client: The HTTP client instance.
            domain: The domain to scrape.
            store_id: The ID of the store.
            request_waiting: Time to wait before making the request.

        Returns:
            A list of departments or an empty list in case of failure.
        """
        url = f"https://api.{domain}/graphql"
        log.info(f"Scraping data from {url}")

        payload = {
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
            "variables": {"storeId": f"{store_id}"},
        }

        headers = Department._generate_headers(domain)

        await asyncio.sleep(request_waiting)

        try:
            response = await client.post(url, headers=headers, json=payload, timeout=None)
            response.raise_for_status()

            response_data = response.json()
            categories = (
                response_data.get("data", {})
                .get("publicViewer", {})
                .get("categories", [])
            )
            return categories
        except Exception as e:
            log.error(f"Error while requesting data: {e}")
            return []

    @staticmethod
    def _generate_headers(domain: str) -> Dict[str, str]:
        """Generates HTTP headers for the request."""
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
    async def get_data(store_id: int, data: List[Dict[str, Any]]) -> DepartmentHeader:
        """
        Processes and maps raw department data into DepartmentHeader.

        Args:
            store_id: The ID of the store.
            data: Raw data fetched from the API.

        Returns:
            A DepartmentHeader object containing the parsed department list.
        """
        department_list = []

        for row in data:
            department_model = DepartmentModel(
                name=clean_html(row.get("name", "NA")),
                department_id=int(row.get("id", 0)),
                store_id=store_id,
                slug=row.get("slug", "NA"),
                search_term=row.get("name", "NA"),
            )
            department_list.append(department_model)

        return DepartmentHeader(data=department_list)
