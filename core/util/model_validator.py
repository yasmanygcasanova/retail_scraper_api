""" Model Validator"""
from typing import Dict, List, Type, Union

from schematics import Model
from schematics.exceptions import DataError


def validate_and_parse_model(data: dict, cls: Type[Model]) -> Union[Dict, None]:
    """
    Function Validate and Parse Model
    :param data:
    :param cls:
    :return:
    """
    try:
        model = cls(data)
        model.validate()
        return model.to_primitive()
    except DataError as e:
        return e.messages


def validate_and_parse_model_many(data: list, cls: Type[Model]) -> Union[List, None]:
    """
    Function Validate and Parse Model Many
    :param data:
    :param cls:
    :return:
    """
    try:
        data_list = []
        for value in data:
            model = cls(value)
            model.validate()
            data_list.append(model.to_primitive())
        return data_list
    except DataError as e:
        return e.messages
