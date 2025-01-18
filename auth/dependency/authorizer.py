""" Authorizer """
import os
import typing

from dotenv import find_dotenv, load_dotenv
from fastapi import Header, HTTPException


def api_keys_in_env(
    key_pattern: typing.Optional[str] = None,
) -> typing.List[typing.Optional[str]]:
    """
    Function Api Keys in Env
    :param key_pattern:
    :return:
    """
    api_keys = []
    load_dotenv(find_dotenv())

    for i in os.environ.keys():
        if i.startswith(key_pattern if key_pattern else "API_KEY"):
            api_keys.append(os.getenv(i))
    return api_keys


class AuthorizerDependency:
    """ Class AuthorizerDependency """
    def __init__(self, key_pattern: typing.Optional[str] = None):
        self.key_pattern = key_pattern

    def __call__(self, x_api_key: typing.Optional[str] = Header(...)):
        if x_api_key not in api_keys_in_env(self.key_pattern):
            raise HTTPException(status_code=401, detail="Unauthorized")
        return x_api_key
