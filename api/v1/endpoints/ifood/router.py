""" Router """
import httpx
from fastapi import APIRouter, HTTPException, Query, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from loguru import logger

from models.ifood.assortment import AssortmentHeader
from models.ifood.department import DepartmentHeader
from models.ifood.postal_code import PostalCodeHeader
from models.ifood.segment import SegmentHeader
from models.ifood.store import MarketHeader
from models.ifood.store_info import StoreInfoHeader
from src.delivery.ifood.domain.web.assortment import Assortment
from src.delivery.ifood.domain.web.department import Department
from src.delivery.ifood.domain.web.postal_code import PostalCode
from src.delivery.ifood.domain.web.segment import Segment
from src.delivery.ifood.domain.web.store import Store
from src.delivery.ifood.domain.web.store_info import StoreInfo

router = APIRouter()
client = httpx.AsyncClient(timeout=httpx.Timeout(10.0))


@router.get(
    "/delivery/postal-code",
    summary="Postal Code",
    status_code=status.HTTP_200_OK,
    response_model=PostalCodeHeader
)
async def postal_code(
    zip_code: str = Query(
        ..., example='04268040',
        min_length=8,
        max_length=8,
        description="""(Inform the zip code.)"""
    )
):
    pc = PostalCode()
    zip_code = zip_code.replace('-', '')
    if len(zip_code) < 8:
        raise HTTPException(
            detail='Por favor, preencha o CEP corretamente.',
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
        )

    response = await pc.request(zip_code)

    if not response:
        result = {
            'data': {}
        }
    else:
        try:
            result = await pc.get_data(
                zip_code,
                response.get('address')
            )
        except Exception as e:
            raise HTTPException(
                detail=str(e),
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
            ) from e
    return JSONResponse(content=jsonable_encoder(result))


@router.get(
    "/delivery/segment",
    summary="Segment List",
    status_code=status.HTTP_200_OK,
    response_model=SegmentHeader
)
async def segment(
    latitude: str = Query(
        ..., example='-23.5942581',
        description="""(Inform the latitude.)"""

    ),
    longitude: str = Query(
        ..., example='-46.6107278',
        description="""(Inform the longitude.)"""

    ),
    request_waiting: int = Query(
        ..., example=5,
        ge=3,
        description="""(Inform the request waiting.)"""
    )
):
    s = Segment()
    response = await s.request(
        client,
        latitude,
        longitude,
        request_waiting
    )
    data = [] if response.get('code') == '102' or not response.get('categories') \
        else response.get('categories')
    if response.get('code') == '102':
        raise HTTPException(
            detail='Acesso não permitido.',
            status_code=status.HTTP_401_UNAUTHORIZED
        )

    if not data:
        result = {
            'data': []
        }
    else:
        try:
            result = await s.get_data(
                latitude=latitude,
                longitude=longitude,
                data=data
            )
        except Exception as e:
            raise HTTPException(
                detail=str(e),
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
            ) from e
    return JSONResponse(content=jsonable_encoder(result))


@router.get(
    "/delivery/store",
    summary="Store List",
    status_code=status.HTTP_200_OK,
    response_model=MarketHeader
)
async def store(
    alias: str = Query(
        ..., example='HOME_MERCADO_BR',
        description="""(Inform the alias.)"""
    ),
    latitude: str = Query(
        ..., example='-23.5942581',
        description="""(Inform the latitude.)"""

    ),
    longitude: str = Query(
        ..., example='-46.6107278',
        description="""(Inform the longitude.)"""

    ),
    zip_code: str = Query(
        ..., example='04268040',
        min_length=8,
        max_length=8,
        description="""(Inform the zip code.)"""
    ),
    request_waiting: int = Query(
        ..., example=5,
        ge=3,
        description="""(Inform the request waiting.)"""
    )
):
    s = Store()
    response = await s.request(
        client,
        alias,
        latitude,
        longitude,
        request_waiting
    )
    data = [] if response.get('code') == '102' or \
        not response.get('sections') \
        else response.get('sections')[0].get('cards')
    if response.get('code') == '102':
        raise HTTPException(
            detail='Acesso não permitido.',
            status_code=status.HTTP_401_UNAUTHORIZED
        )

    if not data:
        result = {
            'data': []
        }
    else:
        try:
            result = await s.get_data(
                latitude,
                longitude,
                zip_code,
                alias,
                data
            )
        except Exception as e:
            raise HTTPException(
                detail=str(e),
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
            ) from e
    return JSONResponse(content=jsonable_encoder(result))


@router.get(
    "/delivery/store-info",
    summary="Store Info",
    status_code=status.HTTP_200_OK,
    response_model=StoreInfoHeader
)
async def store_info(
    store_id: str = Query(
        ..., example='ee4559e2-6c68-429c-9dad-89796c13315e',
        description="""(Inform the store id.)"""

    ),
    latitude: str = Query(
        ..., example='-23.5942581',
        description="""(Inform the latitude.)"""

    ),
    longitude: str = Query(
        ..., example='-46.6107278',
        description="""(Inform the longitude.)"""

    ),
    request_waiting: int = Query(
        ..., example=5,
        ge=3,
        description="""(Inform the request waiting.)"""
    )
):
    s = StoreInfo()
    response = await s.request(
        client,
        store_id,
        latitude,
        longitude,
        request_waiting
    )
    data = [] if response.get('code') == '102' \
        or not response.get('data') \
        else response.get('data')
    if response.get('code') == '102':
        raise HTTPException(
            detail='Acesso não permitido.',
            status_code=status.HTTP_401_UNAUTHORIZED
        )

    if not data:
        result = {
            'data': {}
        }
    else:
        try:
            result = await s.get_data(
                store_id,
                data
            )
        except Exception as e:
            raise HTTPException(
                detail=str(e),
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
            ) from e
    return JSONResponse(content=jsonable_encoder(result))


@router.get(
    "/delivery/department",
    summary="Department List",
    status_code=status.HTTP_200_OK,
    response_model=DepartmentHeader
)
async def department(
    segment_type: str = Query(
        ..., example='MERCADOS',
        description="""(Inform the segment.)"""
    ),
    store_id: str = Query(
        ..., example='ee4559e2-6c68-429c-9dad-89796c13315e',
        description="""(Inform the store id.)"""
    ),
    latitude: str = Query(
        ..., example='-23.5942581',
        description="""(Inform the latitude.)"""

    ),
    longitude: str = Query(
        ..., example='-46.6107278',
        description="""(Inform the longitude.)"""

    ),
    request_waiting: int = Query(
        ..., example=5,
        ge=3,
        description="""(Inform the request waiting.)"""
    )
):
    d = Department()
    response = await d.request(
        client,
        store_id,
        request_waiting
    )
    data = [] if response.get('code') == '102' \
        or not response.get('data') \
        else response.get('data').get('categories')
    if response.get('code') == '102':
        raise HTTPException(
            detail='Acesso não permitido.',
            status_code=status.HTTP_401_UNAUTHORIZED
        )

    if not data:
        result = {
            'data': []
        }
    else:
        try:
            result = await d.get_data(
                segment_type=segment_type,
                store_id=store_id,
                latitude=latitude,
                longitude=longitude,
                data=data
            )
        except Exception as e:
            raise HTTPException(
                detail=str(e),
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
            ) from e
    return JSONResponse(content=jsonable_encoder(result))


@router.get(
    "/delivery/assortment",
    summary="Assortment List",
    status_code=status.HTTP_200_OK,
    response_model=AssortmentHeader
)
async def assortment(
    segment_type: str = Query(
        ..., example='MERCADOS',
        description="""(Inform the segment.)"""
    ),
    region: str = Query(
        ..., example='sao-paulo-sp',
        description="""(Inform the region.)"""
    ),
    store_slug: str = Query(
        ..., example='carrefour-hiper---imigrantes-bosque-da-saude',
        description="""(Inform the store slug.)"""
    ),
    store_id: str = Query(
        ..., example='ee4559e2-6c68-429c-9dad-89796c13315e',
        description="""(Inform the store id.)"""
    ),
    department_id: str = Query(
        ..., example='f9845b8a-efe4-48a0-a9aa-c45b50eafafe',
        description="""(Inform the department id.)"""
    ),
    search_term: str = Query(
        ..., example='Grãos',
        description="""(Inform the search term.)"""
    ),
    latitude: str = Query(
        ..., example='-23.5942581',
        description="""(Inform the latitude.)"""

    ),
    longitude: str = Query(
        ..., example='-46.6107278',
        description="""(Inform the longitude.)"""

    ),
    page: str = Query(
        ..., example='1',
        description="""(Inform the page.)"""

    ),
    request_waiting: int = Query(
        ..., example=2,
        ge=2,
        description="""(Inform the request waiting.)"""
    )
):
    a = Assortment()
    response = await a.request(
        client,
        store_id,
        department_id,
        page,
        request_waiting
    )
    data = [] if response.get('code') == '102' \
        or not response.get('data') \
        else response.get('data')
    if response.get('code') == '102':
        raise HTTPException(
            detail='Acesso não permitido.',
            status_code=status.HTTP_401_UNAUTHORIZED
        )

    if not data:
        result = {
            'records_per_page': 0,
            'items': 0,
            'pages': 0,
            'data': []
        }
    else:
        try:
            result = await a.get_data(
                client=client,
                segment_type=segment_type,
                region=region,
                store_slug=store_slug,
                store_id=store_id,
                department_id=department_id,
                search_term=search_term,
                latitude=latitude,
                longitude=longitude,
                data=data
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
