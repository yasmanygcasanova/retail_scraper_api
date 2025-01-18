""" Postal Code """
import brazilcep
from fastapi import HTTPException, status
from geopy.geocoders import Nominatim
from loguru import logger as log

from core.util.model_validator import validate_and_parse_model
from core.util.strings import clean_html, format_zip_code
from models.ifood.postal_code import PostalCodeHeader
from models.ifood.postal_code import PostalCodeModel as ZipCodeModel
from src.delivery.ifood.models.web.postal_code import PostalCodeModel


class PostalCode:
    """ Class Postal Code """
    @staticmethod
    async def request(
        zip_code: str
    ) -> dict:
        """
        Function Request
        :param zip_code:
        :return: dict
        """
        address = brazilcep.get_address_from_cep(format_zip_code(zip_code))
        if not address:
            data = {}
        else:
            data = {'address': address}
        return data

    @staticmethod
    async def get_data(
        zip_code: str,
        address: dict
    ):
        """
        Function Get Data
        :param zip_code:
        :param address:
        :return:
        """
        geolocator = Nominatim(user_agent="geolocation")

        # Address Info
        street = 'NA' if not address.get('street') \
            else address.get('street')
        neighborhood = 'NA' if not address.get('district') \
            else address.get('district')
        complement = 'NA' if not address.get('complement') \
            else address.get('complement')
        city = 'NA' if not address.get('city') \
            else address.get('city')
        region = 'NA' if not address.get('uf') \
            else address.get('uf')

        # Geolocator Info
        if street != 'NA' and neighborhood != 'NA' and city != 'NA':
            street = f"{street[0]}.{street[3:]}"
            location = geolocator.geocode(
                f"{street}, "
                f"{neighborhood}-{city}, "
                f"{zip_code}"
            )
        else:
            location = geolocator.geocode(f"{city}")

        latitude = 'NA' if not location \
            else str(location.latitude)
        longitude = 'NA' if not location \
            else str(location.longitude)

        fields = {
            'zip_code': zip_code,
            'address': clean_html(street),
            'neighborhood': clean_html(neighborhood),
            'complement': clean_html(complement),
            'city': clean_html(city),
            'region': clean_html(region),
            'latitude': latitude,
            'longitude': longitude
        }

        try:
            # Validate Postal Code Model
            if postal_code_model := validate_and_parse_model(
                    fields,
                    PostalCodeModel
            ):
                ZipCodeModel(**fields)
                data = PostalCodeHeader(
                    data=fields
                )
                return data
            log.info(postal_code_model)
        except ValueError as e:
            log.info(e.args)
            return HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=str(e.args),
                headers=None
            )
