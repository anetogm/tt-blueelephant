"""
Ferramenta de consulta de Pokémon usando a PokéAPI
"""

import logging
import requests
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class PokemonTool:
    """Ferramenta para consultar informações sobre Pokémon"""
    
    BASE_URL = "https://pokeapi.co/api/v2"
    
    def __init__(self):
        """Inicializa a ferramenta PokéAPI"""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'ChatbotIA/1.0'
        })
    
    @property
    def name(self) -> str:
        """Nome da ferramenta"""
        return "consulta_pokemon"
    
    @property
    def description(self) -> str:
        """Descrição da ferramenta"""
        return """Consulta informações sobre Pokémon usando nome ou número da Pokédex.
        
Parâmetros:
- identifier: Nome do Pokémon (em inglês) ou número da Pokédex

Retorna informações como:
- Nome e número da Pokédex
- Tipos (Fire, Water, Grass, etc.)
- Altura e peso
- Habilidades
- Estatísticas base (HP, Attack, Defense, etc.)

Exemplos de uso:
- pikachu
- charizard
- 25 (número do Pikachu)
- 1 (Bulbasaur)"""
    
    def execute(self, identifier: str) -> Dict:
        """
        Executa consulta de Pokémon
        
        Args:
            identifier: Nome ou número do Pokémon
            
        Returns:
            Dicionário com informações do Pokémon
        """
        try:
            # Normaliza o identificador
            identifier = str(identifier).lower().strip()
            
            # Faz requisição
            url = f"{self.BASE_URL}/pokemon/{identifier}"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Extrai informações relevantes
            result = {
                "error": False,
                "id": data.get("id"),
                "name": data.get("name", "").title(),
                "height": data.get("height", 0) / 10,  # Converte para metros
                "weight": data.get("weight", 0) / 10,  # Converte para kg
                "types": [t["type"]["name"].title() for t in data.get("types", [])],
                "abilities": [a["ability"]["name"].title().replace("-", " ") 
                            for a in data.get("abilities", [])],
                "stats": {
                    stat["stat"]["name"]: stat["base_stat"]
                    for stat in data.get("stats", [])
                },
                "sprite": data.get("sprites", {}).get("front_default", "")
            }
            
            logger.info(f"Pokémon {identifier} consultado com sucesso")
            return result
            
        except requests.HTTPError as e:
            if e.response.status_code == 404:
                logger.warning(f"Pokémon {identifier} não encontrado")
                return {
                    "error": True,
                    "message": f"Pokémon '{identifier}' não encontrado. Verifique o nome ou número.",
                    "identifier": identifier
                }
            else:
                logger.error(f"Erro HTTP ao consultar Pokémon {identifier}: {e}")
                return {
                    "error": True,
                    "message": f"Erro na consulta: {str(e)}",
                    "identifier": identifier
                }
        except requests.Timeout:
            logger.error(f"Timeout ao consultar Pokémon {identifier}")
            return {
                "error": True,
                "message": "Timeout na consulta. Tente novamente.",
                "identifier": identifier
            }
        except requests.RequestException as e:
            logger.error(f"Erro na requisição para Pokémon {identifier}: {e}")
            return {
                "error": True,
                "message": f"Erro na consulta: {str(e)}",
                "identifier": identifier
            }
        except Exception as e:
            logger.error(f"Erro inesperado ao consultar Pokémon {identifier}: {e}")
            return {
                "error": True,
                "message": f"Erro inesperado: {str(e)}",
                "identifier": identifier
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
            return f"{result.get('message', 'Erro desconhecido')}"
        
        output = f"**{result['name']} (#{result['id']:03d})**\n\n"
        
        # Tipos
        types_str = " / ".join(result.get("types", []))
        output += f"**Tipo:** {types_str}\n\n"
        
        # Características físicas
        output += f"**Altura:** {result['height']:.1f}m\n"
        output += f"**Peso:** {result['weight']:.1f}kg\n\n"
        
        # Habilidades
        if result.get("abilities"):
            abilities_str = ", ".join(result["abilities"])
            output += f"**Habilidades:** {abilities_str}\n\n"
        
        # Estatísticas base
        if result.get("stats"):
            output += "**Estatísticas Base:**\n"
            stats_map = {
                "hp": "HP",
                "attack": "Ataque",
                "defense": "Defesa",
                "special-attack": "Atq. Especial",
                "special-defense": "Def. Especial",
                "speed": "Velocidade"
            }
            for stat_name, stat_value in result["stats"].items():
                display_name = stats_map.get(stat_name, stat_name.title())
                output += f"- {display_name}: {stat_value}\n"
        
        return output.strip()
    
    def search_by_type(self, type_name: str) -> Dict:
        """
        Busca Pokémon por tipo
        
        Args:
            type_name: Nome do tipo (fire, water, grass, etc.)
            
        Returns:
            Dicionário com lista de Pokémon daquele tipo
        """
        try:
            type_name = type_name.lower().strip()
            url = f"{self.BASE_URL}/type/{type_name}"
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            pokemon_list = [p["pokemon"]["name"].title() 
                          for p in data.get("pokemon", [])[:20]]  # Limita a 20
            
            return {
                "error": False,
                "type": type_name.title(),
                "pokemon": pokemon_list,
                "total": len(data.get("pokemon", []))
            }
            
        except Exception as e:
            logger.error(f"Erro ao buscar Pokémon do tipo {type_name}: {e}")
            return {
                "error": True,
                "message": f"Erro ao buscar tipo: {str(e)}"
            }
