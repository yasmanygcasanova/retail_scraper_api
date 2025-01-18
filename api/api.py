from fastapi import APIRouter
from api.config import ENDPOINTS

api_router = APIRouter()

for endpoint in ENDPOINTS:
    api_router.include_router(
        endpoint.get('router').router,
        prefix=f'/{endpoint.get("prefix")}',
        tags=[endpoint.get('tag')]
    )
