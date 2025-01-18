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
    "domain": "supermercadosmais.com.br",
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


def test_distribution_center():
    url = f"{BASE_URL}/api/v1/vipcommerce/market/distribution-center"

    PAYLOAD.update({
        "branch_id": 1,
        "zip_code": "04268040"
    })

    response = request(url, PAYLOAD)
    data = json.loads(response.text)
    assert response.status_code == 200
    assert len(data) > 0


def test_department():
    url = f"{BASE_URL}/api/v1/vipcommerce/market/department"

    PAYLOAD.update({
        "branch_id": 1,
        "distribution_center_id": 1
    })

    response = request(url, PAYLOAD)
    data = json.loads(response.text)
    assert response.status_code == 200
    assert len(data) > 0


def test_category():
    url = f"{BASE_URL}/api/v1/vipcommerce/market/category"

    PAYLOAD.update({
        "branch_id": 1,
        "distribution_center_id": 1
    })

    response = request(url, PAYLOAD)
    data = json.loads(response.text)
    assert response.status_code == 200
    assert len(data) > 0


def test_assortment():
    url = f"{BASE_URL}/api/v1/vipcommerce/market/assortment"

    PAYLOAD.update(
        {
            "branch_id": 1,
            "distribution_center_id": 1,
            "category_id": 61,
            "page": "1"
        }
    )

    response = request(url, PAYLOAD)
    data = json.loads(response.text)
    assert response.status_code == 200
    assert len(data) > 0
