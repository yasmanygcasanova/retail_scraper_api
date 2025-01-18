"""Router module for O'Super market API endpoints."""

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from loguru import logger
from cachetools import TTLCache
from functools import lru_cache

from models.osuper.assortment import AssortmentHeader
from models.osuper.category import CategoryHeader
from models.osuper.department import DepartmentHeader
from models.osuper.store import StoreHeader
from src.market.osuper.domain.web.assortment import Assortment
from src.market.osuper.domain.web.category import Category
from src.market.osuper.domain.web.department import Department
from src.market.osuper.domain.web.store import Store

router = APIRouter()

# Create a TTLCache with a maximum of 1000 items and a 5-minute TTL
cache = TTLCache(maxsize=1000, ttl=300)


@lru_cache()
def get_cache():
    """Returns the global cache object."""
    return cache


async def get_client():
    """Dependency to create and manage the HTTP client."""
    async with httpx.AsyncClient(timeout=httpx.Timeout(10.0)) as client:
        yield client


def validate_request_waiting(request_waiting: int = Query(..., ge=3)):
    """Validate the request_waiting parameter."""
    return request_waiting


@router.get(
    "/market/store",
    summary="Store Info",
    status_code=status.HTTP_200_OK,
    response_model=StoreHeader
)
async def get_store(
    domain: str = Query(..., example="viladasfrutas.com.br", description="Inform the domain."),
    request_waiting: int = Depends(validate_request_waiting),
    client: httpx.AsyncClient = Depends(get_client),
    cache: TTLCache = Depends(get_cache)
):
    """Endpoint to get store information."""
    cache_key = f"store:{domain}"
    if cache_key in cache:
        return JSONResponse(content=jsonable_encoder(cache[cache_key]))

    store = Store()
    try:
        data = await store.request(client, domain, request_waiting)
        if not data:
            result = {'data': {}}
        else:
            result = await store.get_data(client, domain, request_waiting, data)
        cache[cache_key] = result
        return JSONResponse(content=jsonable_encoder(result))
    except Exception as e:
        logger.error(f"Error in get_store: {str(e)}")
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)) from e


@router.get(
    "/market/department",
    summary="Department List",
    status_code=status.HTTP_200_OK,
    response_model=DepartmentHeader
)
async def get_department(
    domain: str = Query(..., example="viladasfrutas.com.br", description="Inform the domain."),
    store_id: int = Query(..., ge=1, example=253, description="Inform the store id."),
    request_waiting: int = Depends(validate_request_waiting),
    client: httpx.AsyncClient = Depends(get_client),
    cache: TTLCache = Depends(get_cache)
):
    """Endpoint to get department list."""
    cache_key = f"department:{domain}:{store_id}"
    if cache_key in cache:
        return JSONResponse(content=jsonable_encoder(cache[cache_key]))

    department = Department()
    try:
        data = await department.request(client, domain, store_id, request_waiting)
        if not data:
            result = {'data': {}}
        else:
            result = await department.get_data(store_id, data)
        cache[cache_key] = result
        return JSONResponse(content=jsonable_encoder(result))
    except Exception as e:
        logger.error(f"Error in get_department: {str(e)}")
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)) from e


@router.get(
    "/market/category",
    summary="Category List",
    status_code=status.HTTP_200_OK,
    response_model=CategoryHeader
)
async def get_category(
    domain: str = Query(..., example="viladasfrutas.com.br", description="Inform the domain."),
    store_id: int = Query(..., ge=1, example=253, description="Inform the store id."),
    request_waiting: int = Depends(validate_request_waiting),
    client: httpx.AsyncClient = Depends(get_client),
    cache: TTLCache = Depends(get_cache)
):
    """Endpoint to get category list."""
    cache_key = f"category:{domain}:{store_id}"
    if cache_key in cache:
        return JSONResponse(content=jsonable_encoder(cache[cache_key]))

    category = Category()
    try:
        data = await category.request(client, domain, store_id, request_waiting)
        if not data:
            result = {'data': {}}
        else:
            result = await category.get_data(store_id, data)
        cache[cache_key] = result
        return JSONResponse(content=jsonable_encoder(result))
    except Exception as e:
        logger.error(f"Error in get_category: {str(e)}")
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)) from e


@router.get(
    "/market/assortment",
    summary="Assortment List",
    status_code=status.HTTP_200_OK,
    response_model=AssortmentHeader
)
async def get_assortment(
    domain: str = Query(..., example="viladasfrutas.com.br", description="Inform the domain."),
    account_id: int = Query(..., ge=1, example=100, description="Inform the account id."),
    store_id: int = Query(..., ge=1, example=253, description="Inform the store id."),
    category_id: int = Query(..., ge=1, example=571970, description="Inform the category id."),
    search_term: str = Query(..., example="Bebidas > Refrigerantes", description="Inform the search term."),
    request_waiting: int = Depends(validate_request_waiting),
    client: httpx.AsyncClient = Depends(get_client),
    cache: TTLCache = Depends(get_cache)
):
    """Endpoint to get assortment list."""
    cache_key = f"assortment:{domain}:{account_id}:{store_id}:{category_id}:{search_term}"
    if cache_key in cache:
        return JSONResponse(content=jsonable_encoder(cache[cache_key]))

    assortment = Assortment()
    try:
        response = await assortment.request(
            client=client,
            domain=domain,
            page='',
            account_id=account_id,
            store_id=store_id,
            search_term=search_term,
            products=[],
            request_waiting=request_waiting
        )
        if not response:
            result = {'data': []}
        else:
            result = await assortment.get_data(
                store_id=store_id,
                category_id=category_id,
                search_term=search_term,
                data=response
            )
        cache[cache_key] = result
        return JSONResponse(content=jsonable_encoder(result))
    except Exception as e:
        logger.error(f"Error in get_assortment: {str(e)}")
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(e)) from e


@router.on_event("startup")
async def app_startup():
    """Application startup event."""
    logger.info("Starting application with TTLCache.")


@router.on_event("shutdown")
async def app_shutdown():
    """Application shutdown event."""
    logger.info("Shutting down application and clearing cache.")
    cache.clear()
