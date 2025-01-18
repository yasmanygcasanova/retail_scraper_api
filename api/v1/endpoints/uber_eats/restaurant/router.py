""" Router """
import httpx
from fastapi import APIRouter, HTTPException, Query, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from loguru import logger
from cachetools import TTLCache

from models.uber_eats.restaurant.assortment import AssortmentHeader
from models.uber_eats.restaurant.store_info import StoreInfoHeader
from src.delivery.uber_eats.restaurant.domain.web.assortment import Assortment
from src.delivery.uber_eats.restaurant.domain.web.store_info import StoreInfo

router = APIRouter()

# Global HTTP client and cache configuration
client = None
cache = TTLCache(maxsize=100, ttl=300)  # Cache with a time-to-live of 5 minutes


@router.on_event("startup")
async def app_startup():
    global client
    client = httpx.AsyncClient(timeout=httpx.Timeout(10.0))
    logger.info("Starting application and initializing HTTP client.")


@router.on_event("shutdown")
async def app_shutdown():
    await client.aclose()
    logger.info("Shutting down application and closing HTTP client.")


async def fetch_data(service, store_id: str, request_waiting: int):
    """
    Helper function to fetch data from a specific service.

    :param service: Service to be used (StoreInfo or Assortment)
    :param store_id: Store ID to fetch the data
    :param request_waiting: Time to wait before processing the request
    :return: Processed data as JSON response
    """

    # Check if the result is in the cache
    if store_id in cache:
        logger.info(f"Cache hit for store: {store_id}")
        return JSONResponse(content=jsonable_encoder(cache[store_id]), status_code=status.HTTP_200_OK)

    logger.info(f"Fetching data for store: {store_id}")

    try:
        response = await service.request(
            client=client,
            store_id=store_id,
            request_waiting=request_waiting
        )

        data = response.get('data', [])
        if not data:
            logger.warning(f"No data found for store: {store_id}")
            return JSONResponse(content={"data": []}, status_code=status.HTTP_200_OK)

        result = await service.get_data(store_id, data)

        # Store the result in cache
        cache[store_id] = result

        return JSONResponse(content=jsonable_encoder(result), status_code=status.HTTP_200_OK)

    except httpx.HTTPStatusError as http_exc:
        logger.error(f"HTTP error occurred: {http_exc.response.status_code} - {http_exc.response.text}")
        raise HTTPException(status_code=http_exc.response.status_code, detail=http_exc.response.text)

    except Exception as e:
        logger.exception(f"Unexpected error while fetching data for store: {store_id}")
        raise HTTPException(
            detail=f"Internal server error: {str(e)}",
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        ) from e


@router.get(
    "/delivery/store-info",
    summary="Store Info",
    status_code=status.HTTP_200_OK,
    response_model=StoreInfoHeader,
)
async def get_store_info(
        store_id: str = Query(
            ...,
            example="a6961a93-7682-40a0-8e05-ce4bb8bfbfe4", description="(Provide the store ID.)"
        ),
        request_waiting: int = Query(
            ...,
            example=5, ge=3, description="(Time to wait between requests in seconds.)"
        )
):
    """
    Endpoint to retrieve info for a given store.
    """
    store_info_service = StoreInfo()
    return await fetch_data(store_info_service, store_id, request_waiting)


@router.get(
    "/delivery/assortment",
    summary="Product Assortment",
    status_code=status.HTTP_200_OK,
    response_model=AssortmentHeader,
)
async def get_assortment(
        store_id: str = Query(
            ...,
            example="a6961a93-7682-40a0-8e05-ce4bb8bfbfe4", description="(Provide the store ID.)"
        ),
        request_waiting: int = Query(
            ...,
            example=5, ge=3, description="(Time to wait between requests in seconds.)"
        )
):
    """
    Endpoint to retrieve product assortment for a given store.
    """
    assortment_service = Assortment()
    return await fetch_data(assortment_service, store_id, request_waiting)
