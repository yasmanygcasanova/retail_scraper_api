""" Store """
from schematics.models import Model
from schematics.types import FloatType, IntType, StringType


class StoreModel(Model):
    """ Class Store Model """
    name = StringType(required=True)
    segment = StringType(required=True)
    store_type = StringType(required=True)
    store_id = StringType(required=True)
    store_slug = StringType(required=True)
    url = StringType(required=True)
    available = StringType(required=True)
    distance = FloatType(required=True)
    user_rating = FloatType(required=True)
    fee = IntType(required=True)
    time_min_minutes = IntType(required=True)
    time_max_minutes = IntType(required=True)
    latitude = StringType(required=True)
    longitude = StringType(required=True)
    zip_code = StringType(required=True)
    region = StringType(required=True)
    alias = StringType(required=True)

    class Options:
        """ Class Options """
        serialize_when_none = False
