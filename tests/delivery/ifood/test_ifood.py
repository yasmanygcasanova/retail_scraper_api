import json
import os

import httpx
import pytest
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv('API_KEY')
BASE_URL = os.getenv('BASE_URL')

HEADERS = {
    'accept': "application/json",
    'x-api-key': API_KEY,
    'cache-control': "no-cache"
}

PAYLOAD = {
    "latitude": "-23.5942581",
    "longitude": "-46.6107278",
    "request_waiting": 3
}


def request(url: str, payload: dict):
    with httpx.Client() as client:
        response = client.get(
            url,
            headers=HEADERS,
            params=payload,
            timeout=None
        )
        return response


def test_segment():
    url = f"{BASE_URL}/api/v1/ifood/delivery/segment"

    response = request(url, PAYLOAD)
    data = json.loads(response.text)
    assert response.status_code == 200
    assert len(data) > 0


def test_store():
    url = f"{BASE_URL}/api/v1/ifood/delivery/store"

    PAYLOAD.update({
        "alias": "HOME_MERCADO_BR",
        "zip_code": "04268040"
    })

    response = request(url, PAYLOAD)
    data = json.loads(response.text)
    assert response.status_code == 200
    assert len(data) > 0


def test_store_info():
    url = f"{BASE_URL}/api/v1/ifood/delivery/store-info"

    PAYLOAD.update({"store_id": "ee4559e2-6c68-429c-9dad-89796c13315e"})

    response = request(url, PAYLOAD)
    data = json.loads(response.text)
    assert response.status_code == 200
    assert len(data) > 0


def test_department():
    url = f"{BASE_URL}/api/v1/ifood/delivery/department"

    PAYLOAD.update({
        "segment_type": "MERCADOS",
        "store_id": "ee4559e2-6c68-429c-9dad-89796c13315e"
    })

    response = request(url, PAYLOAD)
    data = json.loads(response.text)
    assert response.status_code == 200
    assert len(data) > 0


def test_assortment():
    url = f"{BASE_URL}/api/v1/ifood/delivery/assortment"

    PAYLOAD.update({
        "segment_type": "MERCADOS",
        "region": "sao-paulo-sp",
        "store_slug": "carrefour-hiper---imigrantes-bosque-da-saude",
        "store_id": "ee4559e2-6c68-429c-9dad-89796c13315e",
        "department_id": "f9845b8a-efe4-48a0-a9aa-c45b50eafafe",
        "search_term": "Grãos",
        "page": "1"
    })

    response = request(url, PAYLOAD)
    data = json.loads(response.text)
    assert response.status_code == 200
    assert len(data) > 0
