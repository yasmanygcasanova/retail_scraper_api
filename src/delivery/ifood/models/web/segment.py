""" Segment """
from schematics.models import Model
from schematics.types import StringType


class SegmentModel(Model):
    """ Class Segment Model """
    name = StringType(required=True)
    segment_type = StringType(required=True)
    alias = StringType(required=True)
    latitude = StringType(required=True)
    longitude = StringType(required=True)

    class Options:
        """ Class Options """
        serialize_when_none = False
