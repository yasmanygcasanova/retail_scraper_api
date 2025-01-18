""" Store Info """
from schematics.models import Model
from schematics.types import FloatType, IntType, StringType


class StoreInfoModel(Model):
    """ Class Store Info Model """
    name = StringType(required=True)
    company_code = StringType(required=True)
    phone = StringType(required=True)
    main_category = StringType(required=True)
    store_id = StringType(required=True)
    store_type = StringType(required=True)
    cnpj = StringType(required=True)
    logo = StringType(required=False)
    country = StringType(required=True)
    state = StringType(required=True)
    city = StringType(required=True)
    district = StringType(required=True)
    zip_code = StringType(required=True)
    latitude = StringType(required=True)
    longitude = StringType(required=True)
    street_name = StringType(required=True)
    street_number = StringType(required=True)
    price_range = StringType(required=True)
    delivery_fee = FloatType(required=True)
    type_delivery_fee = StringType(required=True)
    takeout_time = IntType(required=True)
    delivery_time = IntType(required=True)
    minimum_order_value = IntType(required=True)
    preparation_time = IntType(required=True)
    distance = FloatType(required=True)
    available = StringType(required=True)
    user_rating = FloatType(required=True)
    user_rating_count = IntType(required=True)

    class Options:
        """ Class Options """
        serialize_when_none = False
