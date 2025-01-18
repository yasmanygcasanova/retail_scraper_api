# api/v1/config.py
from typing import List, Dict, Any

from api.v1.endpoints.ifood import router as ifood_router
from api.v1.endpoints.uber_eats.restaurant import router as uber_eats_restaurant_router
from api.v1.endpoints.osuper import router as osuper_router
from api.v1.endpoints.tendaatacado import router as tendaatacado_router
from api.v1.endpoints.vipcommerce import router as vipcommerce_router
from api.v1.endpoints.vtex import router as vtex_router

EndpointConfig = Dict[str, Any]
ENDPOINTS: List[EndpointConfig] = [
    {
        'prefix': 'ifood',
        'tag': 'Ifood',
        'router': ifood_router
    },
    {
        'prefix': 'uber-eats-restaurant',
        'tag': 'Uber Eats - Restaurant',
        'router': uber_eats_restaurant_router
    },
    {
        'prefix': 'tendaatacado',
        'tag': 'Tenda Atacado',
        'router': tendaatacado_router
    },
    {
        'prefix': 'vipcommerce',
        'tag': 'VipCommerce',
        'router': vipcommerce_router
    },
    {
        'prefix': 'osuper',
        'tag': 'OSuper',
        'router': osuper_router
    },
    {
        'prefix': 'vtex',
        'tag': 'Vtex',
        'router': vtex_router
    },
]
