""" Department """
import asyncio
import json
from typing import Dict, List, Optional, Any

from loguru import logger as log
from user_agent import generate_user_agent

from core.util.strings import clean_html
from models.ifood.department import DepartmentHeader, DepartmentModel


class Department:
    """ Classe para gerenciar departamentos do iFood """
    
    # Constantes da classe
    host = 'marketplace.ifood.com.br'
    base_url = 'https://www.ifood.com.br'
    access_key = "69f181d5-0046-4221-b7b2-deef62bd60d5"
    secret_key = "9ef4fb4f-7a1d-4e0d-a9b1-9b82873297d8"

    @classmethod
    def _get_default_headers(cls) -> Dict[str, str]:
        """
        Retorna os headers padrão para as requisições
        :return: Headers da requisição
        """
        return {
            'User-Agent': generate_user_agent(),
            'Accept': "application/json, text/plain, */*",
            'Accept-Language': "pt-BR,pt;q=1",
            'Accept-Encoding': "gzip, deflate, br",
            'Referer': cls.base_url,
            'Cache-Control': "no-cache, no-store",
            'access_key': cls.access_key,
            'secret_key': cls.secret_key,
            'platform': "Desktop",
            'app_version': "9.94.6",
            'Origin': cls.base_url,
            'Sec-Fetch-Dest': "empty",
            'Sec-Fetch-Mode': "cors",
            'Sec-Fetch-Site': "same-site",
            'Connection': "keep-alive",
            'Pragma': "no-cache",
            'TE': "trailers",
            'cache-control': "no-cache"
        }

    @classmethod
    async def request(
        cls,
        client: object,
        store_id: str,
        request_waiting: int
    ) -> Dict[str, Any]:
        """
        Realiza requisição para obter dados dos departamentos
        :param client: Cliente HTTP
        :param store_id: ID da loja
        :param request_waiting: Tempo de espera entre requisições
        :return: Dados dos departamentos
        """
        url = f"https://{cls.host}/v1/merchants/{store_id}/taxonomies"
        log.info(f"{url}: scraping data for store {store_id}")

        try:
            await asyncio.sleep(request_waiting)
            response = await client.get(
                url,
                headers=cls._get_default_headers()
            )
            response.raise_for_status()
            data = json.loads(response.text)
            return {} if not data else data
            
        except Exception as e:
            log.error(f"Erro ao buscar departamentos da loja {store_id}: {str(e)}")
            return {}

    @staticmethod
    async def get_category(categories: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """
        Processa dados das categorias
        :param categories: Lista de categorias
        :return: Lista de categorias processadas
        """
        category_list = []
        for row in categories:
            category_list.append({
                'name': row.get('name', 'NA')
            })
        return category_list

    @classmethod
    async def get_data(
        cls, 
        store_id: str,
        latitude: str,
        longitude: str,
        segment_type: str,
        data: List[Dict[str, Any]]
    ) -> Optional[DepartmentHeader]:
        """
        Processa e valida dados dos departamentos
        :param store_id: ID da loja
        :param latitude: Latitude
        :param longitude: Longitude
        :param segment_type: Tipo do segmento
        :param data: Dados brutos
        :return: Dados processados e validados
        """
        try:
            department_list = []
            
            for row in data:
                # Processa categorias
                categories = row.get("parentTaxonomies", [])
                category_list = await cls.get_category(categories) if categories else []

                # Monta campos do departamento
                fields = {
                    'name': clean_html(row.get('name', 'NA')),
                    'department_id': row.get('id', 'NA'),
                    'categories': category_list,
                    'segment_type': segment_type,
                    'store_id': store_id,
                    'latitude': latitude,
                    'longitude': longitude
                }

                # Valida e adiciona departamento
                department = DepartmentModel(**fields)
                department_list.append(department)

            return DepartmentHeader(data=department_list)
            
        except Exception as e:
            log.error(f"Erro ao processar departamentos: {str(e)}")
            return None
