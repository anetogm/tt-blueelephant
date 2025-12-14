"""
Ferramenta de consulta de letras de músicas usando a API Lyrics.ovh
"""

import logging
import requests
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class LyricsOvhTool:
    """Ferramenta para consultar letras de músicas"""
    
    BASE_URL = "https://api.lyrics.ovh/v1"
    
    def __init__(self):
        """Inicializa a ferramenta Lyrics.ovh"""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'ChatbotIA/1.0'
        })
    
    @property
    def name(self) -> str:
        """Nome da ferramenta"""
        return "consulta_letra_musica"
    
    @property
    def description(self) -> str:
        """Descrição da ferramenta"""
        return """Consulta letras de músicas usando a API Lyrics.ovh.
        
Parâmetros:
- artist: Nome do artista/banda
- song: Nome da música

Retorna:
- Letra completa da música
- Nome do artista
- Nome da música

Exemplos de uso:
- Artista: "Coldplay", Música: "Yellow"
- Artista: "The Beatles", Música: "Hey Jude"
- Artista: "Legião Urbana", Música: "Faroeste Caboclo"
- Artista: "Queen", Música: "Bohemian Rhapsody"""
    
    def execute(self, artist: str, song: str) -> Dict:
        """
        Executa consulta de letra de música
        
        Args:
            artist: Nome do artista/banda
            song: Nome da música
            
        Returns:
            Dicionário com letra da música
        """
        try:
            artist_clean = artist.strip()
            song_clean = song.strip()
            
            logger.info(f"Buscando letra: '{song_clean}' de '{artist_clean}'")
            
            # Busca letra
            lyrics_result = self._get_lyrics(artist_clean, song_clean)
            
            if lyrics_result and not lyrics_result.get("error"):
                return lyrics_result
            
            return {
                "error": True,
                "message": f"Letra da música '{song}' de '{artist}' não encontrada. Verifique a ortografia do artista e música."
            }
            
        except requests.exceptions.Timeout:
            logger.error("Timeout ao consultar API Lyrics.ovh")
            return {
                "error": True,
                "message": "Tempo esgotado ao consultar letras. Tente novamente."
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao consultar Lyrics.ovh: {e}")
            return {
                "error": True,
                "message": f"Erro ao consultar letras: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Erro inesperado na ferramenta Lyrics: {e}", exc_info=True)
            return {
                "error": True,
                "message": f"Erro inesperado: {str(e)}"
            }
    
    def _get_lyrics(self, artist: str, song: str) -> Optional[Dict]:
        """Busca letra da música"""
        try:
            # URL: /v1/{artist}/{song}
            url = f"{self.BASE_URL}/{artist}/{song}"
            
            logger.info(f"Fazendo request: {url}")
            response = self.session.get(url, timeout=15)
            
            # Se não encontrou, retorna None
            if response.status_code == 404:
                logger.warning(f"Letra não encontrada: {artist} - {song}")
                return None
            
            response.raise_for_status()
            
            data = response.json()
            lyrics = data.get("lyrics")
            
            if not lyrics:
                logger.warning("Resposta sem letra")
                return None
            
            logger.info(f"Letra encontrada: {len(lyrics)} caracteres")
            
            return {
                "error": False,
                "type": "lyrics",
                "artist": artist,
                "song": song,
                "lyrics": lyrics.strip()
            }
            
        except Exception as e:
            logger.error(f"Erro ao buscar letra: {e}", exc_info=True)
            return None
    
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
        
        if result_type == "lyrics":
            lyrics = result.get("lyrics", "")
            
            # Limita o tamanho da letra para não ficar muito longo
            max_length = 2000
            if len(lyrics) > max_length:
                lyrics = lyrics[:max_length] + "\n\n... (letra completa muito longa, mostrando apenas o início)"
            
            output = f"""**{result['song']}**\n"""
            output += f"**Artista**: {result['artist']}\n"
            output += f"\n**Letra:**\n\n{lyrics}"
            
            return output
        
        return str(result)