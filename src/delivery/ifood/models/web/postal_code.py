""" Postal Code """
from schematics.models import Model
from schematics.types import StringType


class PostalCodeModel(Model):
    """ Class Postal Code Model """
    zip_code = StringType(required=True)
    address = StringType(required=True)
    neighborhood = StringType(required=True)
    complement = StringType(required=True)
    city = StringType(required=True)
    region = StringType(required=True)
    latitude = StringType(required=True)
    longitude = StringType(required=True)

    class Options:
        """ Class Options """
        serialize_when_none = False
