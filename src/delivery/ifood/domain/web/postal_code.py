""" Postal Code """
import brazilcep
import httpx
from fastapi import HTTPException, status
from loguru import logger as log
from typing import Dict, Optional

from core.util.model_validator import validate_and_parse_model
from core.util.strings import clean_html, format_zip_code
from models.ifood.postal_code import PostalCodeHeader
from models.ifood.postal_code import PostalCodeModel as ZipCodeModel
from src.delivery.ifood.models.web.postal_code import PostalCodeModel


class PostalCode:
    """ Class Postal Code """
    NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
    DEFAULT_TIMEOUT = 10.0
    
    @staticmethod
    async def _get_coordinates(client: httpx.AsyncClient, zip_code: str) -> tuple[str, str]:
        """
        Função auxiliar para obter coordenadas do Nominatim
        :param client: Cliente HTTP
        :param zip_code: CEP
        :return: Tupla com (latitude, longitude)
        """
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (compatible; MyApp/1.0)'
            }
            response = await client.get(
                PostalCode.NOMINATIM_URL,
                params={
                    "format": "json",
                    "q": f"{zip_code},Brazil"
                },
                headers=headers,
                timeout=PostalCode.DEFAULT_TIMEOUT
            )
            response.raise_for_status()
            nominatim_data = response.json()

            if nominatim_data and len(nominatim_data) > 0:
                return nominatim_data[0]['lat'], nominatim_data[0]['lon']
            
        except (httpx.RequestError, KeyError) as e:
            log.error(f"Erro ao obter coordenadas: {str(e)}")
        
        return 'NA', 'NA'

    @staticmethod
    async def request(zip_code: str) -> Dict[str, Optional[dict]]:
        """
        Function Request
        :param zip_code: CEP a ser consultado
        :return: Dicionário com dados do endereço
        """
        formatted_zip = format_zip_code(zip_code)
        address = brazilcep.get_address_from_cep(formatted_zip)

        if not address:
            return {}

        async with httpx.AsyncClient(verify=False) as client:
            latitude, longitude = await PostalCode._get_coordinates(client, formatted_zip)
            address['latitude'] = latitude
            address['longitude'] = longitude

        return {'address': address}

    @staticmethod
    async def get_data(zip_code: str, address: dict):
        """
        Function Get Data
        :param zip_code: CEP
        :param address: Dicionário com dados do endereço
        :return: Dados formatados do endereço
        """
        fields = {
            'zip_code': zip_code,
            'address': clean_html(address.get('street', 'NA')),
            'neighborhood': clean_html(address.get('district', 'NA')),
            'complement': clean_html(address.get('complement', 'NA')),
            'city': clean_html(address.get('city', 'NA')),
            'region': clean_html(address.get('uf', 'NA')),
            'latitude': str(address.get('latitude', 'NA')),
            'longitude': str(address.get('longitude', 'NA'))
        }

        try:
            if postal_code_model := validate_and_parse_model(fields, PostalCodeModel):
                ZipCodeModel(**fields)
                return PostalCodeHeader(data=fields)
                
            log.info(postal_code_model)
            return None
            
        except ValueError as e:
            log.info(e.args)
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=str(e.args)
            )
