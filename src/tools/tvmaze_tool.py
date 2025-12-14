"""
Ferramenta de consulta de séries de TV usando a API TVMaze
"""

import logging
import requests
from typing import Dict, Optional, List

logger = logging.getLogger(__name__)


class TVMazeTool:
    """Ferramenta para consultar informações sobre séries de TV"""
    
    BASE_URL = "https://api.tvmaze.com"
    
    def __init__(self):
        """Inicializa a ferramenta TVMaze"""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'ChatbotIA/1.0'
        })
    
    @property
    def name(self) -> str:
        """Nome da ferramenta"""
        return "consulta_serie"
    
    @property
    def description(self) -> str:
        """Descrição da ferramenta"""
        return """Consulta informações sobre séries de TV usando a API TVMaze.
        
Parâmetros:
- query: Nome da série de TV

Retorna informações como:
- Nome e ano de estreia
- Gêneros
- Status (em exibição, cancelada, etc)
- Sinopse
- Rede/Plataforma
- Rating
- Horário de exibição

Exemplos de uso:
- "Breaking Bad"
- "Game of Thrones"
- "The Office"
- "Stranger Things"""
    
    def execute(self, query: str) -> Dict:
        """
        Executa consulta de série
        
        Args:
            query: Nome da série
            
        Returns:
            Dicionário com informações da série
        """
        try:
            query_clean = query.strip()
            logger.info(f"Buscando série: {query_clean}")
            
            # Busca série
            series_result = self._search_series(query_clean)
            
            if series_result and not series_result.get("error"):
                return series_result
            
            return {
                "error": True,
                "message": f"Série '{query}' não encontrada. Verifique a ortografia."
            }
            
        except requests.exceptions.Timeout:
            logger.error("Timeout ao consultar API TVMaze")
            return {
                "error": True,
                "message": "Tempo esgotado ao consultar séries. Tente novamente."
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao consultar TVMaze: {e}")
            return {
                "error": True,
                "message": f"Erro ao consultar séries: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Erro inesperado na ferramenta TVMaze: {e}", exc_info=True)
            return {
                "error": True,
                "message": f"Erro inesperado: {str(e)}"
            }
    
    def _search_series(self, name: str) -> Optional[Dict]:
        """Busca série pelo nome"""
        try:
            url = f"{self.BASE_URL}/search/shows"
            params = {"q": name}
            
            logger.info(f"Fazendo request: {url} com params: {params}")
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            if not data:
                logger.warning(f"Nenhuma série encontrada para: {name}")
                return None
            
            logger.info(f"Encontradas {len(data)} séries")
            
            # Se encontrou múltiplas, busca match exato ou retorna primeira
            name_lower = name.lower()
            
            # Tenta match exato primeiro
            for item in data:
                show = item.get("show", {})
                show_name = show.get("name", "").lower()
                if show_name == name_lower:
                    logger.info(f"Match exato encontrado: {show.get('name')}")
                    return self._format_series(show)
            
            # Se tem múltiplas sem match exato
            if len(data) > 3:
                return {
                    "error": False,
                    "type": "multiple_series",
                    "message": f"Encontradas {len(data)} séries. Seja mais específico.",
                    "series": [
                        f"{item['show'].get('name')} ({item['show'].get('premiered', 'N/A')[:4]})"
                        for item in data[:5]
                    ]
                }
            
            # Retorna primeira série (mais relevante)
            logger.info(f"Retornando primeira série: {data[0]['show'].get('name')}")
            return self._format_series(data[0]["show"])
            
        except Exception as e:
            logger.error(f"Erro ao buscar série: {e}", exc_info=True)
            return None
    
    def _format_series(self, show: Dict) -> Dict:
        """Formata dados da série"""
        # Remove tags HTML da sinopse
        summary = show.get("summary", "")
        if summary:
            import re
            summary = re.sub(r'<[^>]+>', '', summary)
        
        # Extrai informações de network/webChannel
        network_info = None
        if show.get("network"):
            network = show["network"]
            network_info = {
                "name": network.get("name"),
                "country": network.get("country", {}).get("name")
            }
        elif show.get("webChannel"):
            channel = show["webChannel"]
            network_info = {
                "name": channel.get("name"),
                "country": channel.get("country", {}).get("name") if channel.get("country") else "Streaming"
            }
        
        # Extrai informações de horário
        schedule_info = show.get("schedule", {})
        schedule_text = None
        if schedule_info.get("days") and schedule_info.get("time"):
            days = ", ".join(schedule_info["days"])
            time = schedule_info["time"]
            schedule_text = f"{days} às {time}"
        
        return {
            "error": False,
            "type": "series",
            "id": show.get("id"),
            "name": show.get("name"),
            "type": show.get("type"),
            "language": show.get("language"),
            "genres": show.get("genres", []),
            "status": show.get("status"),
            "premiered": show.get("premiered"),
            "ended": show.get("ended"),
            "rating": show.get("rating", {}).get("average"),
            "network": network_info,
            "schedule": schedule_text,
            "summary": summary,
            "official_site": show.get("officialSite"),
            "image": show.get("image", {}).get("medium")
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
        
        if result_type == "series":
            # Título e ano
            year = ""
            if result.get("premiered"):
                year = f" ({result['premiered'][:4]})"
            
            output = f"""📺 **{result['name']}{year}**\n"""
            
            # Gêneros
            if result.get("genres"):
                genres = ", ".join(result["genres"])
                output += f"\n• **Gêneros**: {genres}"
            
            # Status
            status_emoji = {
                "Running": "✅ Em exibição",
                "Ended": "🏁 Finalizada",
                "To Be Determined": "❓ A ser determinado",
                "In Development": "🔧 Em desenvolvimento"
            }
            status = status_emoji.get(result.get("status"), result.get("status", "N/A"))
            output += f"\n• **Status**: {status}"
            
            # Rating
            if result.get("rating"):
                stars = "⭐" * int(result["rating"] / 2)
                output += f"\n• **Avaliação**: {result['rating']}/10 {stars}"
            
            # Rede/Plataforma
            if result.get("network"):
                net = result["network"]
                output += f"\n• **Exibição**: {net['name']}"
                if net.get("country"):
                    output += f" ({net['country']})"
            
            # Horário
            if result.get("schedule"):
                output += f"\n• **Horário**: {result['schedule']}"
            
            # Datas
            if result.get("premiered"):
                output += f"\n• **Estreia**: {result['premiered']}"
            if result.get("ended"):
                output += f"\n• **Fim**: {result['ended']}"
            
            # Sinopse
            if result.get("summary"):
                summary = result["summary"]
                if len(summary) > 300:
                    summary = summary[:300] + "..."
                output += f"\n\n**Sinopse**: {summary}"
            
            return output
        
        elif result_type == "multiple_series":
            series_list = '\n'.join([f"  - {s}" for s in result['series']])
            return f"""🔍 **Múltiplas séries encontradas**

{result['message']}

**Opções:**
{series_list}"""
        
        return str(result)