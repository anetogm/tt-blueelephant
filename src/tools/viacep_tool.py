"""
Ferramenta de consulta de CEP usando a API ViaCEP
"""

import logging
import requests
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class ViaCEPTool:
    """Ferramenta para consultar informações de CEP brasileiro"""
    
    BASE_URL = "https://viacep.com.br/ws"
    
    def __init__(self):
        """Inicializa a ferramenta ViaCEP"""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'ChatbotIA/1.0'
        })
    
    @property
    def name(self) -> str:
        """Nome da ferramenta"""
        return "consulta_cep"
    
    @property
    def description(self) -> str:
        """Descrição da ferramenta"""
        return """Consulta informações de endereço a partir de um CEP brasileiro.
        
Parâmetros:
- cep: CEP brasileiro (8 dígitos, com ou sem hífen)

Retorna informações como:
- Logradouro (rua/avenida)
- Bairro
- Cidade
- Estado (UF)
- DDD
- Complemento

Exemplo de uso: consultar o CEP 01310-100"""
    
    def execute(self, cep: str) -> Dict:
        """
        Executa consulta de CEP
        
        Args:
            cep: CEP a ser consultado (formato: 00000-000 ou 00000000)
            
        Returns:
            Dicionário com informações do endereço
        """
        try:
            # Remove caracteres não numéricos
            cep_clean = ''.join(filter(str.isdigit, cep))
            
            # Valida formato
            if len(cep_clean) != 8:
                return {
                    "error": True,
                    "message": "CEP inválido. Deve conter 8 dígitos.",
                    "cep": cep
                }
            
            # Faz requisição
            url = f"{self.BASE_URL}/{cep_clean}/json/"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Verifica se CEP foi encontrado
            if data.get("erro"):
                return {
                    "error": True,
                    "message": "CEP não encontrado.",
                    "cep": cep
                }
            
            # Formata resposta
            result = {
                "error": False,
                "cep": data.get("cep", cep),
                "logradouro": data.get("logradouro", ""),
                "complemento": data.get("complemento", ""),
                "bairro": data.get("bairro", ""),
                "localidade": data.get("localidade", ""),
                "uf": data.get("uf", ""),
                "ddd": data.get("ddd", ""),
                "ibge": data.get("ibge", ""),
                "gia": data.get("gia", ""),
                "siafi": data.get("siafi", "")
            }
            
            logger.info(f"CEP {cep} consultado com sucesso")
            return result
            
        except requests.Timeout:
            logger.error(f"Timeout ao consultar CEP {cep}")
            return {
                "error": True,
                "message": "Timeout na consulta. Tente novamente.",
                "cep": cep
            }
        except requests.RequestException as e:
            logger.error(f"Erro na requisição para CEP {cep}: {e}")
            return {
                "error": True,
                "message": f"Erro na consulta: {str(e)}",
                "cep": cep
            }
        except Exception as e:
            logger.error(f"Erro inesperado ao consultar CEP {cep}: {e}")
            return {
                "error": True,
                "message": f"Erro inesperado: {str(e)}",
                "cep": cep
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
            return f"❌ {result.get('message', 'Erro desconhecido')}"
        
        output = f"📍 **Informações do CEP {result['cep']}**\n\n"
        
        if result.get("logradouro"):
            output += f"**Logradouro:** {result['logradouro']}\n"
        
        if result.get("complemento"):
            output += f"**Complemento:** {result['complemento']}\n"
        
        if result.get("bairro"):
            output += f"**Bairro:** {result['bairro']}\n"
        
        if result.get("localidade"):
            output += f"**Cidade:** {result['localidade']}\n"
        
        if result.get("uf"):
            output += f"**Estado:** {result['uf']}\n"
        
        if result.get("ddd"):
            output += f"**DDD:** {result['ddd']}\n"
        
        return output.strip()
