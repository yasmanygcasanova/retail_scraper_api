""" Product """
from schematics.models import Model
from schematics.types import FloatType, IntType, StringType


class ProductModel(Model):
    """ Product Model """
    name = StringType(required=True)
    ean = IntType(required=True)
    sku = StringType(required=True)
    store_id = IntType(required=True)
    category_id = IntType(required=True)
    search_term = StringType(required=True)
    brand = StringType(required=True)
    available = StringType(required=True)
    sale_unit = StringType(required=False)
    qty_sale = IntType(required=False)
    price_from = FloatType(required=True)
    price_to = FloatType(required=True)
    discount = IntType(required=True)
    in_stock = IntType(required=True)
    slug = StringType(required=True)
    image = StringType(required=False)
    created_at = StringType(required=True)
    hour = StringType(required=True)

    class Options:
        """ Class Options """
        serialize_when_none = False
