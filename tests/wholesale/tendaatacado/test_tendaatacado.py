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


def test_department():
    url = f"{BASE_URL}/api/v1/tendaatacado/wholesale/department"

    response = request(url, PAYLOAD)
    data = json.loads(response.text)
    assert response.status_code == 200
    assert len(data) > 0


def test_category():
    url = f"{BASE_URL}/api/v1/tendaatacado/wholesale/category"

    response = request(url, PAYLOAD)
    data = json.loads(response.text)
    assert response.status_code == 200
    assert len(data) > 0


def test_assortment():
    url = f"{BASE_URL}/api/v1/tendaatacado/wholesale/assortment"

    PAYLOAD.update({
        "category_id": 126,
        "search_term": "acucar-e-adocantes",
        "page": "1"
    })

    response = request(url, PAYLOAD)
    data = json.loads(response.text)
    assert response.status_code == 200
    assert len(data) > 0
