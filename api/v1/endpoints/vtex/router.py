""" Router """
import httpx
from fastapi import APIRouter, HTTPException, Query, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from loguru import logger

from models.vtex.assortment import AssortmentHeader
from models.vtex.brand import BrandHeader
from models.vtex.category import CategoryHeader
from models.vtex.department import DepartmentHeader
from models.vtex.intelligent_search import IntelligentSearchHeader
from models.vtex.search_term import SearchTermHeader
from models.vtex.subcategory import SubCategoryHeader
from src.market.vtex.domain.web.assortment import Assortment
from src.market.vtex.domain.web.brand import Brand
from src.market.vtex.domain.web.category import Category
from src.market.vtex.domain.web.department import Department
from src.market.vtex.domain.web.intelligent_search import IntelligentSearch
from src.market.vtex.domain.web.search_term import SearchTerm
from src.market.vtex.domain.web.subcategory import SubCategory

router = APIRouter()
client = httpx.AsyncClient(timeout=httpx.Timeout(10.0))


@router.get(
    "/market/intelligent-search",
    summary="Intelligent Search List",
    status_code=status.HTTP_200_OK,
    response_model=IntelligentSearchHeader
)
async def intelligent_search(
    subdomain: str = Query(
        ..., example="mambodelivery",
        description="""(Inform the subdomain.)"""
    ),
    request_waiting: int = Query(
        ..., example=5,
        ge=3,
        description="""(Inform the request waiting.)"""
    )
):
    i = IntelligentSearch()
    data = await i.request(
        client,
        subdomain,
        request_waiting
    )
    if not data:
        result = {
            'data': []
        }
    else:
        try:
            result = await i.get_data(
                data
            )
        except Exception as e:
            raise HTTPException(
                detail=str(e),
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
            ) from e
    return JSONResponse(content=jsonable_encoder(result))


@router.get(
    "/market/department",
    summary="Department List",
    status_code=status.HTTP_200_OK,
    response_model=DepartmentHeader
)
async def department(
    subdomain: str = Query(
        ..., example="mambodelivery",
        description="""(Inform the subdomain.)"""
    ),
    request_waiting: int = Query(
        ..., example=5,
        ge=3,
        description="""(Inform the request waiting.)"""
    )
):
    d = Department()
    data = await d.request(
        client,
        subdomain,
        request_waiting
    )
    if not data:
        result = {
            'data': []
        }
    else:
        try:
            result = await d.get_data(
                data
            )
        except Exception as e:
            raise HTTPException(
                detail=str(e),
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
            ) from e
    return JSONResponse(content=jsonable_encoder(result))


@router.get(
    "/market/category",
    summary="Category List",
    status_code=status.HTTP_200_OK,
    response_model=CategoryHeader
)
async def category(
    subdomain: str = Query(
        ..., example="mambodelivery",
        description="""(Inform the subdomain.)"""
    ),
    request_waiting: int = Query(
        ..., example=5,
        ge=3,
        description="""(Inform the request waiting.)"""
    )
):
    c = Category()
    data = await c.request(
        client,
        subdomain,
        request_waiting
    )
    if not data:
        result = {
            'data': []
        }
    else:
        try:
            result = await c.get_data(
                data
            )
        except Exception as e:
            raise HTTPException(
                detail=str(e),
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
            ) from e
    return JSONResponse(content=jsonable_encoder(result))


@router.get(
    "/market/subcategory",
    summary="SubCategory List",
    status_code=status.HTTP_200_OK,
    response_model=SubCategoryHeader
)
async def subcategory(
    subdomain: str = Query(
        ..., example="mambodelivery",
        description="""(Inform the subdomain.)"""
    ),
    request_waiting: int = Query(
        ..., example=5,
        ge=3,
        description="""(Inform the request waiting.)"""
    )
):
    s = SubCategory()
    data = await s.request(
        client,
        subdomain,
        request_waiting
    )
    if not data:
        result = {
            'data': []
        }
    else:
        try:
            result = await s.get_data(
                data
            )
        except Exception as e:
            raise HTTPException(
                detail=str(e),
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
            ) from e
    return JSONResponse(content=jsonable_encoder(result))


@router.get(
    "/market/brand",
    summary="Brand List",
    status_code=status.HTTP_200_OK,
    response_model=BrandHeader
)
async def brand(
    subdomain: str = Query(
        ..., example="mambodelivery",
        description="""(Inform the subdomain.)"""
    ),
    request_waiting: int = Query(
        ..., example=5,
        ge=3,
        description="""(Inform the request waiting.)"""
    )
):
    b = Brand()
    data = await b.request(
        client,
        subdomain,
        request_waiting
    )
    if not data:
        result = {
            'data': []
        }
    else:
        try:
            result = await b.get_data(
                data
            )
        except Exception as e:
            raise HTTPException(
                detail=str(e),
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
            ) from e
    return JSONResponse(content=jsonable_encoder(result))


@router.get(
    "/market/assortment",
    summary="Assortment List",
    status_code=status.HTTP_200_OK,
    response_model=AssortmentHeader
)
async def assortment(
    domain: str = Query(
        ..., example="mambo.com.br",
        description="""(Inform the domain.)"""
    ),
    subdomain: str = Query(
        "", example="",
        description="""(Inform the subdomain.)"""
    ),
    alias: str = Query(
        ..., example="mambodelivery",
        description="""(Inform the subdomain.)"""
    ),
    department_id: int = Query(
        ..., example=731,
        ge=1,
        description="""(Inform the department id.)"""
    ),
    category_id: int = Query(
        ..., example=732,
        ge=1,
        description="""(Inform the category id.)"""
    ),
    _from: int = Query(
        ..., example=0,
        description="""(Inform the _from.)"""
    ),
    _to: int = Query(
        ..., example=20,
        description="""(Inform the _to.)"""
    ),
    request_waiting: int = Query(
        ..., example=5,
        ge=3,
        description="""(Inform the request waiting.)"""
    )
):
    a = Assortment()
    data = await a.request(
        client,
        alias,
        department_id,
        category_id,
        _from,
        _to,
        request_waiting
    )

    if not data:
        result = {
            'records_per_page': 0,
            'items': 0,
            'pages': 0,
            'data': []
        }
    elif data[0].get('status_code') == status.HTTP_429_TOO_MANY_REQUESTS:
        raise HTTPException(
            detail='Too Many Requests.',
            status_code=status.HTTP_429_TOO_MANY_REQUESTS
        )
    else:
        try:
            result = await a.get_data(
                domain,
                subdomain,
                department_id,
                category_id,
                _from,
                _to,
                data
            )
        except Exception as e:
            raise HTTPException(
                detail=str(e),
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
            ) from e
    return JSONResponse(content=jsonable_encoder(result))


@router.get(
    "/market/search-term",
    summary="Search Term",
    status_code=status.HTTP_200_OK,
    response_model=SearchTermHeader
)
async def search_term(
    domain: str = Query(
        ..., example="mambo.com.br",
        description="""(Inform the domain.)"""
    ),
    subdomain: str = Query(
        "", example="",
        description="""(Inform the subdomain.)"""
    ),
    alias: str = Query(
        ..., example="mambodelivery",
        description="""(Inform the subdomain.)"""
    ),
    search_name: str = Query(
        ..., example="azeite",
        description="""(Inform the search name.)"""
    ),
    _from: int = Query(
        ..., example=0,
        description="""(Inform the _from.)"""
    ),
    _to: int = Query(
        ..., example=20,
        description="""(Inform the _to.)"""
    ),
    request_waiting: int = Query(
        ..., example=5,
        ge=3,
        description="""(Inform the request waiting.)"""
    )
):
    s = SearchTerm()
    data = await s.request(
        client,
        alias,
        search_name.lower(),
        _from,
        _to,
        request_waiting
    )

    if not data:
        result = {
            'records_per_page': 0,
            'items': 0,
            'pages': 0,
            'data': []
        }
    elif data[0].get('status_code') == status.HTTP_429_TOO_MANY_REQUESTS:
        raise HTTPException(
            detail='Too Many Requests.',
            status_code=status.HTTP_429_TOO_MANY_REQUESTS
        )
    else:
        try:
            result = await s.get_data(
                domain,
                subdomain,
                search_name.lower(),
                _from,
                _to,
                data
            )
        except Exception as e:
            raise HTTPException(
                detail=str(e),
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
            ) from e
    return JSONResponse(content=jsonable_encoder(result))


@router.on_event("startup")
async def app_startup():
    """
    Application startup event.
    Initializes the HTTP client.
    """
    logger.info("Starting application and initializing HTTP client.")


@router.on_event("shutdown")
async def app_shutdown():
    """
    Application shutdown event.
    Cleans up the HTTP client.
    """
    logger.info("Shutting down application and closing HTTP client.")
