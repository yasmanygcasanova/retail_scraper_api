"""Router"""

from typing import Any, Dict

import httpx
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from loguru import logger

from models.vipcommerce.assortment import AssortmentHeader
from models.vipcommerce.category import CategoryHeader
from models.vipcommerce.department import DepartmentHeader
from models.vipcommerce.distribution_center import DistributionCenterHeader
from src.market.vipcommerce.domain.web.assortment import Assortment
from src.market.vipcommerce.domain.web.category import Category
from src.market.vipcommerce.domain.web.department import Department
from src.market.vipcommerce.domain.web.distribution_center import DistributionCenter

router = APIRouter()


async def get_client() -> httpx.AsyncClient:
    """Dependency to get the HTTP client."""
    async with httpx.AsyncClient(timeout=httpx.Timeout(10.0)) as client:
        yield client


async def process_request(
    client: httpx.AsyncClient,
    domain: str,
    branch_id: int,
    request_waiting: int,
    processor: Any,
    *args: Any
) -> Dict[str, Any]:
    """Generic function to process requests."""
    data = await processor.request(client, domain, branch_id, *args, request_waiting)
    if not data:
        return {'data': []}
    try:
        return await processor.get_data(branch_id, *args, data)
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        raise HTTPException(
            detail=str(e),
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        ) from e


@router.get(
    "/market/distribution-center",
    summary="Distribution Center List",
    status_code=status.HTTP_200_OK,
    response_model=DistributionCenterHeader
)
async def distribution_center(
    domain: str = Query(
        ..., example="supermercadosmais.com.br",
        description="Inform the domain."
    ),
    branch_id: int = Query(
        ..., example=1,
        ge=1,
        description="Inform the branch."
    ),
    zip_code: str = Query(
        ..., example='04268040',
        min_length=8,
        max_length=8,
        description="Inform the zip code."
    ),
    request_waiting: int = Query(
        ..., example=5,
        ge=3,
        description="Inform the request waiting."
    ),
    client: httpx.AsyncClient = Depends(get_client)
):
    """Endpoint to get distribution center information."""
    result = await process_request(
        client,
        domain,
        branch_id,
        request_waiting,
        DistributionCenter(),
        zip_code
    )
    return JSONResponse(content=jsonable_encoder(result))


@router.get(
    "/market/department",
    summary="Department List",
    status_code=status.HTTP_200_OK,
    response_model=DepartmentHeader
)
async def department(
    domain: str = Query(..., example="supermercadosmais.com.br", description="Inform the domain."),
    branch_id: int = Query(..., example=1, ge=1, description="Inform the branch."),
    distribution_center_id: int = Query(..., example=1, ge=1, description="Inform the distribution center."),
    request_waiting: int = Query(..., example=5, ge=3, description="Inform the request waiting."),
    client: httpx.AsyncClient = Depends(get_client)
):
    """Endpoint to get department information."""
    result = await process_request(client, domain, branch_id, request_waiting, Department(), distribution_center_id)
    return JSONResponse(content=jsonable_encoder(result))


@router.get(
    "/market/category",
    summary="Category List",
    status_code=status.HTTP_200_OK,
    response_model=CategoryHeader
)
async def category(
    domain: str = Query(..., example="supermercadosmais.com.br", description="Inform the domain."),
    branch_id: int = Query(..., example=1, ge=1, description="Inform the branch."),
    distribution_center_id: int = Query(..., example=1, ge=1, description="Inform the distribution center."),
    request_waiting: int = Query(..., example=5, ge=3, description="Inform the request waiting."),
    client: httpx.AsyncClient = Depends(get_client)
):
    """Endpoint to get category information."""
    result = await process_request(client, domain, branch_id, request_waiting, Category(), distribution_center_id)
    return JSONResponse(content=jsonable_encoder(result))


@router.get(
    "/market/assortment",
    summary="Assortment List",
    status_code=status.HTTP_200_OK,
    response_model=AssortmentHeader
)
async def assortment(
    domain: str = Query(..., example="supermercadosmais.com.br", description="Inform the domain."),
    branch_id: int = Query(..., example=1, ge=1, description="Inform the branch."),
    distribution_center_id: int = Query(..., example=1, ge=1, description="Inform the distribution center."),
    category_id: int = Query(..., example=61, ge=1, description="Inform the category id."),
    page: str = Query(..., example='1', description="Inform the page."),
    request_waiting: int = Query(..., example=5, ge=3, description="Inform the request waiting."),
    client: httpx.AsyncClient = Depends(get_client)
):
    """Endpoint to get assortment information."""
    a = Assortment()
    data = await a.request(client, domain, branch_id, distribution_center_id, category_id, page, request_waiting)

    if not data.get('data'):
        result = {
            'records_per_page': 0,
            'items': 0,
            'pages': 0,
            'data': []
        }
    else:
        try:
            result = await a.get_data(domain, branch_id, distribution_center_id, category_id, data)
        except Exception as e:
            logger.error(f"Error processing assortment data: {str(e)}")
            raise HTTPException(
                detail=str(e),
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
            ) from e
    return JSONResponse(content=jsonable_encoder(result))


@router.on_event("startup")
async def app_startup():
    """Application startup event."""
    logger.info("Starting application.")


@router.on_event("shutdown")
async def app_shutdown():
    """Application shutdown event."""
    logger.info("Shutting down application.")
