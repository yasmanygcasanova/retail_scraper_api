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
    "subdomain": "mambodelivery",
    "request_waiting": 5
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


def test_intelligent_search():
    url = f"{BASE_URL}/api/v1/vtex/market/intelligent-search"

    response = request(url, PAYLOAD)
    data = json.loads(response.text)
    assert response.status_code == 200
    assert len(data) > 0


def test_department():
    url = f"{BASE_URL}/api/v1/vtex/market/department"

    response = request(url, PAYLOAD)
    data = json.loads(response.text)
    assert response.status_code == 200
    assert len(data) > 0


def test_category():
    url = f"{BASE_URL}/api/v1/vtex/market/category"

    response = request(url, PAYLOAD)
    data = json.loads(response.text)
    assert response.status_code == 200
    assert len(data) > 0


def test_subcategory():
    url = f"{BASE_URL}/api/v1/vtex/market/subcategory"

    response = request(url, PAYLOAD)
    data = json.loads(response.text)
    assert response.status_code == 200
    assert len(data) > 0


def test_brand():
    url = f"{BASE_URL}/api/v1/vtex/market/brand"

    response = request(url, PAYLOAD)
    data = json.loads(response.text)
    assert response.status_code == 200
    assert len(data) > 0


def test_assortment():
    url = f"{BASE_URL}/api/v1/vtex/market/assortment"

    PAYLOAD.update(
        {
            "domain": "mambo.com.br",
            "alias": "mambodelivery",
            "department_id": 731,
            "category_id": 732,
            "_from": 0,
            "_to": 20
        }
    )

    response = request(url, PAYLOAD)
    data = json.loads(response.text)
    assert response.status_code == 200
    assert len(data) > 0


def test_search_term():
    url = f"{BASE_URL}/api/v1/vtex/market/search-term"

    PAYLOAD.update(
        {
            "domain": "mambo.com.br",
            "alias": "mambodelivery",
            "search_name": "azeite",
            "_from": 0,
            "_to": 20
        }
    )

    response = request(url, PAYLOAD)
    data = json.loads(response.text)
    assert response.status_code == 200
    assert len(data) > 0
