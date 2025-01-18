""" Product """
from schematics.models import Model
from schematics.types import FloatType, IntType, StringType


class ProductModel(Model):
    """ Class Product Model """
    name = StringType(required=True)
    ean = IntType(required=True)
    sku = StringType(required=True)
    department = StringType(required=True)
    category = StringType(required=True)
    sub_category = StringType(required=True)
    department_id = StringType(required=True)
    category_id = StringType(required=True)
    search_term = StringType(required=True)
    details = StringType(required=False)
    availability = StringType(required=True)
    price_from = FloatType(required=True)
    price_to = FloatType(required=True)
    discount = IntType(required=False)
    segment_type = StringType(required=True)
    store_id = StringType(required=True)
    latitude = StringType(required=True)
    longitude = StringType(required=True)
    image = StringType(required=False)
    url = StringType(required=False)
    created_at = StringType(required=True)
    hour = StringType(required=True)

    class Options:
        """ Class Options """
        serialize_when_none = False
