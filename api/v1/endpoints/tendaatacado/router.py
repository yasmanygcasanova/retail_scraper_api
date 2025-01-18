import httpx
from fastapi import APIRouter, HTTPException, Query, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from loguru import logger

from models.tendaatacado.assortment import AssortmentHeader
from models.tendaatacado.category import CategoryHeader
from models.tendaatacado.department import DepartmentHeader
from src.wholesale.tendaatacado.domain.web.assortment import Assortment
from src.wholesale.tendaatacado.domain.web.category import Category
from src.wholesale.tendaatacado.domain.web.department import Department

router = APIRouter()
client = httpx.AsyncClient(timeout=httpx.Timeout(10.0))


async def fetch_data(model_instance, *args):
    """Helper function to fetch data and handle potential errors."""
    try:
        data = await model_instance.request(client, *args)
        if not data:
            return {'data': []}
        return await model_instance.get_data(data)
    except Exception as e:
        logger.error(f"Error fetching data: {str(e)}")
        raise HTTPException(
            detail=str(e),
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        )


@router.get(
    "/wholesale/department",
    summary="Department List",
    status_code=status.HTTP_200_OK,
    response_model=DepartmentHeader
)
async def department(
    request_waiting: int = Query(
        ..., example=5,
        ge=3,
        description="(Inform the request waiting.)"
    )
):
    """Fetch and return the list of departments."""
    department_instance = Department()
    result = await fetch_data(department_instance, request_waiting)
    return JSONResponse(content=jsonable_encoder(result))


@router.get(
    "/wholesale/category",
    summary="Categories List",
    status_code=status.HTTP_200_OK,
    response_model=CategoryHeader
)
async def category(
    request_waiting: int = Query(
        ..., example=5,
        ge=3,
        description="(Inform the request waiting.)"
    )
):
    """Fetch and return the list of categories."""
    category_instance = Category()
    result = await fetch_data(category_instance, request_waiting)
    return JSONResponse(content=jsonable_encoder(result))


@router.get(
    "/wholesale/assortment",
    summary="Assortment List",
    status_code=status.HTTP_200_OK,
    response_model=AssortmentHeader
)
async def assortment(
    category_id: int = Query(
        ..., example=126,
        ge=1,
        description="(Inform the category id.)"
    ),
    search_term: str = Query(
        ..., example='acucar-e-adocantes',
        description="(Inform the search term.)"
    ),
    page: str = Query(
        ..., example='1',
        description="(Inform the page.)"
    ),
    request_waiting: int = Query(
        ..., example=5,
        ge=3,
        description="(Inform the request waiting.)"
    )
):
    """Fetch and return the assortment based on category and search term."""

    assortment_instance = Assortment()

    try:
        data = await assortment_instance.request(client, category_id, search_term, page, request_waiting)

        if not data.get("products"):
            return JSONResponse(content=jsonable_encoder({
                'records_per_page': 0,
                'items': 0,
                'pages': 0,
                'data': []
            }))

        result = await assortment_instance.process_data(category_id, search_term, data)

        return JSONResponse(content=jsonable_encoder(result))

    except Exception as e:
        logger.error(f"Error processing assortment data: {str(e)}")
        raise HTTPException(
            detail=str(e),
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        )


@router.on_event("startup")
async def app_startup():
    """Application startup event. Initializes the HTTP client."""
    logger.info("Starting application and initializing HTTP client.")


@router.on_event("shutdown")
async def app_shutdown():
    """Application shutdown event. Cleans up the HTTP client."""
    await client.aclose()  # Ensure proper closure of the HTTP client.
    logger.info("Shutting down application and closing HTTP client.")
