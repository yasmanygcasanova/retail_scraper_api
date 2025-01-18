""" Category """
import asyncio
from typing import Any, Dict, List

from fastapi import HTTPException, status
from loguru import logger
from user_agent import generate_user_agent

from core.util.strings import clean_html
from models.tendaatacado.category import CategoryHeader, CategoryModel


class Category:
    """ Class Category """
    domain = 'api.tendaatacado.com.br'
    base_url = f'https://{domain}'

    @classmethod
    async def request(
        cls,
        client: object,
        request_waiting: int
    ) -> List[Dict[str, Any]]:
        """
        Makes a request to fetch category data.
        :param client: HTTP client instance
        :param request_waiting: Delay before the request
        :return: List of categories as dictionaries
        """
        headers = {
            'User-Agent': generate_user_agent(),
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.5',
            'Origin': 'https://www.tendaatacado.com.br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'TE': 'trailers'
        }

        url = f"{cls.base_url}/api/public/store/departments"
        logger.info(f"Fetching data from: {url}")
        try:
            await asyncio.sleep(request_waiting)
            response = await client.get(
                url,
                headers=headers,
                timeout=None
            )
            # Raise HTTP errors if status != 200
            response.raise_for_status()
            data = response.json()
            if not data:
                logger.warning("No data received.")
                return []

            logger.info("Data fetched successfully.")
            return data
        except HTTPException as e:
            logger.error(f"HTTP exception: {e.detail}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error while fetching data: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while fetching category data."
        )

    @staticmethod
    async def get_data(data: List[Dict[str, Any]]) -> CategoryHeader:
        """
        Processes raw category data into structured models.
        :param data: Raw data received from API
        :return: CategoryHeader object containing processed categories
        """
        try:
            category_list = []

            for row in data:
                if row.get("hasChildren") and row.get("children"):
                    for child in row["children"]:
                        category_model = Category.process_child_data(child, row["id"])
                        category_list.append(category_model)

            logger.info(f"Processed {len(category_list)} categories.")
            return CategoryHeader(data=category_list)
        except KeyError as e:
            logger.error(f"Missing key in category data: {e}")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Key error in data: {e}"
            )
        except Exception as e:
            logger.error(f"Error processing category data: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="An error occurred while processing category data."
            )

    @staticmethod
    def process_child_data(child: Dict[str, Any], parent_id: int) -> CategoryModel:
        """
        Processes a single child category.
        :param child: Child category data
        :param parent_id: ID of the parent category
        :return: CategoryModel instance
        """
        name = clean_html(child.get('name', 'NA'))
        category_id = int(child.get('id', 0))
        search_term = child.get('link', 'NA')

        return CategoryModel(
            name=name,
            category_id=category_id,
            department_id=parent_id,
            search_term=search_term
        )
