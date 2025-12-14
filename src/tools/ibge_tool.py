"""
Ferramenta de consulta de dados do IBGE
"""

import logging
import requests
from typing import Dict, Optional, List

logger = logging.getLogger(__name__)


class IBGETool:
    """Ferramenta para consultar informações do IBGE (estados, municípios, etc)"""
    
    BASE_URL = "https://servicodados.ibge.gov.br/api/v1"
    
    def __init__(self):
        """Inicializa a ferramenta IBGE"""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'ChatbotIA/1.0'
        })
    
    @property
    def name(self) -> str:
        """Nome da ferramenta"""
        return "consulta_ibge"
    
    @property
    def description(self) -> str:
        """Descrição da ferramenta"""
        return """Consulta informações geográficas do Brasil via IBGE.
        
Parâmetros:
- query: Nome do estado (sigla ou nome completo) ou município

Retorna informações como:
- Estados: nome, sigla, região
- Municípios: nome, código IBGE, microrregião, mesorregião

Exemplo de uso: 
- "SP" ou "São Paulo" para info do estado
- "Campinas" para info do município"""
    
    def execute(self, query: str) -> Dict:
        """
        Executa consulta no IBGE
        
        Args:
            query: Estado (UF ou nome) ou município a ser consultado
            
        Returns:
            Dicionário com informações geográficas
        """
        try:
            query_clean = query.strip()
            
            # Tenta como UF primeiro (2 letras)
            if len(query_clean) == 2:
                return self._get_state_info(query_clean.upper())
            
            # Verifica se é nome de estado
            state_info = self._search_state_by_name(query_clean)
            if state_info:
                return state_info
            
            # Se não, busca como município
            return self._search_municipality(query_clean)
            
        except requests.exceptions.Timeout:
            logger.error("Timeout ao consultar API do IBGE")
            return {
                "error": True,
                "message": "Tempo esgotado ao consultar IBGE. Tente novamente."
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao consultar IBGE: {e}")
            return {
                "error": True,
                "message": f"Erro ao consultar IBGE: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Erro inesperado na ferramenta IBGE: {e}")
            return {
                "error": True,
                "message": f"Erro inesperado: {str(e)}"
            }
    
    def _get_state_info(self, uf: str) -> Dict:
        """Busca informações de um estado pela sigla"""
        url = f"{self.BASE_URL}/localidades/estados/{uf}"
        response = self.session.get(url, timeout=10)
        
        if response.status_code == 404:
            return {
                "error": True,
                "message": f"Estado '{uf}' não encontrado."
            }
        
        response.raise_for_status()
        data = response.json()
        
        return {
            "error": False,
            "type": "estado",
            "id": data.get("id"),
            "sigla": data.get("sigla"),
            "nome": data.get("nome"),
            "regiao": {
                "id": data.get("regiao", {}).get("id"),
                "sigla": data.get("regiao", {}).get("sigla"),
                "nome": data.get("regiao", {}).get("nome")
            }
        }
    
    def _search_state_by_name(self, name: str) -> Optional[Dict]:
        """Busca estado pelo nome"""
        url = f"{self.BASE_URL}/localidades/estados"
        response = self.session.get(url, timeout=10)
        response.raise_for_status()
        
        states = response.json()
        name_lower = name.lower()
        
        for state in states:
            if state.get("nome", "").lower() == name_lower:
                return {
                    "error": False,
                    "type": "estado",
                    "id": state.get("id"),
                    "sigla": state.get("sigla"),
                    "nome": state.get("nome"),
                    "regiao": {
                        "id": state.get("regiao", {}).get("id"),
                        "sigla": state.get("regiao", {}).get("sigla"),
                        "nome": state.get("regiao", {}).get("nome")
                    }
                }
        
        return None
    
    def _search_municipality(self, name: str) -> Dict:
        """Busca município pelo nome"""
        url = f"{self.BASE_URL}/localidades/municipios"
        response = self.session.get(url, timeout=15)
        response.raise_for_status()
        
        municipalities = response.json()
        name_lower = name.lower()
        
        # Busca exata primeiro
        for mun in municipalities:
            if mun.get("nome", "").lower() == name_lower:
                return self._format_municipality(mun)
        
        # Busca parcial
        matches = []
        for mun in municipalities:
            if name_lower in mun.get("nome", "").lower():
                matches.append(mun)
        
        if len(matches) == 1:
            return self._format_municipality(matches[0])
        elif len(matches) > 1:
            # Retorna lista de opções
            options = [f"{m.get('nome')} ({m.get('microrregiao', {}).get('mesorregiao', {}).get('UF', {}).get('sigla')})" 
                      for m in matches[:5]]
            return {
                "error": False,
                "type": "municipios_multiplos",
                "message": f"Encontrados {len(matches)} municípios. Seja mais específico.",
                "opcoes": options,
                "total": len(matches)
            }
        else:
            return {
                "error": True,
                "message": f"Município '{name}' não encontrado."
            }
    
    def _format_municipality(self, data: Dict) -> Dict:
        """Formata dados do município"""
        return {
            "error": False,
            "type": "municipio",
            "id": data.get("id"),
            "nome": data.get("nome"),
            "codigo_ibge": data.get("id"),
            "microrregiao": {
                "id": data.get("microrregiao", {}).get("id"),
                "nome": data.get("microrregiao", {}).get("nome")
            },
            "mesorregiao": {
                "id": data.get("microrregiao", {}).get("mesorregiao", {}).get("id"),
                "nome": data.get("microrregiao", {}).get("mesorregiao", {}).get("nome")
            },
            "estado": {
                "id": data.get("microrregiao", {}).get("mesorregiao", {}).get("UF", {}).get("id"),
                "sigla": data.get("microrregiao", {}).get("mesorregiao", {}).get("UF", {}).get("sigla"),
                "nome": data.get("microrregiao", {}).get("mesorregiao", {}).get("UF", {}).get("nome"),
                "regiao": {
                    "id": data.get("microrregiao", {}).get("mesorregiao", {}).get("UF", {}).get("regiao", {}).get("id"),
                    "sigla": data.get("microrregiao", {}).get("mesorregiao", {}).get("UF", {}).get("regiao", {}).get("sigla"),
                    "nome": data.get("microrregiao", {}).get("mesorregiao", {}).get("UF", {}).get("regiao", {}).get("nome")
                }
            }
        }
    
    def format_result(self, result: Dict) -> str:
        """
        Formata resultado para exibição
        
        Args:
            result: Dicionário com resultado da consulta
            
        Returns:
            String formatada para exibição
        """
        if result.get("error"):
            return f"❌ **Erro**: {result.get('message', 'Erro desconhecido')}"
        
        result_type = result.get("type")
        
        if result_type == "estado":
            return f"""📍 **{result['nome']} ({result['sigla']})**

• **Região**: {result['regiao']['nome']}
• **Sigla da Região**: {result['regiao']['sigla']}
• **Código IBGE**: {result['id']}"""
        
        elif result_type == "municipio":
            return f"""🏙️ **{result['nome']} - {result['estado']['sigla']}**

• **Código IBGE**: {result['codigo_ibge']}
• **Estado**: {result['estado']['nome']} ({result['estado']['sigla']})
• **Região**: {result['estado']['regiao']['nome']}
• **Mesorregião**: {result['mesorregiao']['nome']}
• **Microrregião**: {result['microrregiao']['nome']}"""
        
        elif result_type == "municipios_multiplos":
            opcoes = '\n'.join([f"  - {opt}" for opt in result['opcoes']])
            return f"""🔍 **Múltiplos municípios encontrados**

{result['message']}

**Opções encontradas ({result['total']}):**
{opcoes}"""
        
        return str(result)