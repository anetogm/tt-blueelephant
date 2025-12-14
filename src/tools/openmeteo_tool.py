"""
Ferramenta de consulta de clima usando a API Open-Meteo
"""

import logging
import requests
from typing import Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class OpenMeteoTool:
    """Ferramenta para consultar informações de clima"""
    
    GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
    WEATHER_URL = "https://api.open-meteo.com/v1/forecast"
    
    def __init__(self):
        """Inicializa a ferramenta Open-Meteo"""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'ChatbotIA/1.0'
        })
    
    @property
    def name(self) -> str:
        """Nome da ferramenta"""
        return "consulta_clima"
    
    @property
    def description(self) -> str:
        """Descrição da ferramenta"""
        return """Consulta informações de clima atual e previsão usando Open-Meteo.
        
Parâmetros:
- location: Nome da cidade ou local

Retorna informações como:
- Temperatura atual
- Sensação térmica
- Velocidade do vento
- Umidade relativa
- Condições climáticas
- Previsão para os próximos dias

Exemplos de uso:
- "São Paulo"
- "New York"
- "Tokyo"
- "London"""
    
    def execute(self, location: str) -> Dict:
        """
        Executa consulta de clima
        
        Args:
            location: Nome da cidade/local
            
        Returns:
            Dicionário com informações do clima
        """
        try:
            location_clean = location.strip()
            logger.info(f"Buscando clima para: {location_clean}")
            
            # Primeiro, busca coordenadas da localização
            coords = self._get_coordinates(location_clean)
            if not coords or coords.get("error"):
                return coords or {
                    "error": True,
                    "message": f"Localização '{location}' não encontrada."
                }
            
            # Depois busca dados do clima
            weather_data = self._get_weather(coords)
            if weather_data.get("error"):
                return weather_data
            
            # Combina informações
            result = {
                "error": False,
                "location": coords["name"],
                "country": coords["country"],
                "latitude": coords["latitude"],
                "longitude": coords["longitude"],
                **weather_data
            }
            
            logger.info(f"Clima encontrado para {coords['name']}")
            return result
            
        except requests.exceptions.Timeout:
            logger.error("Timeout ao consultar API Open-Meteo")
            return {
                "error": True,
                "message": "Tempo esgotado ao consultar clima. Tente novamente."
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao consultar Open-Meteo: {e}")
            return {
                "error": True,
                "message": f"Erro ao consultar clima: {str(e)}"
            }
        except Exception as e:
            logger.error(f"Erro inesperado na ferramenta clima: {e}", exc_info=True)
            return {
                "error": True,
                "message": f"Erro inesperado: {str(e)}"
            }
    
    def _get_coordinates(self, location: str) -> Optional[Dict]:
        """Busca coordenadas da localização usando geocoding"""
        try:
            params = {
                "name": location,
                "count": 1,
                "language": "pt",
                "format": "json"
            }
            
            logger.info(f"Buscando coordenadas: {self.GEOCODING_URL}")
            response = self.session.get(self.GEOCODING_URL, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            results = data.get("results", [])
            
            if not results:
                logger.warning(f"Nenhuma localização encontrada para: {location}")
                return {
                    "error": True,
                    "message": f"Localização '{location}' não encontrada. Tente ser mais específico."
                }
            
            # Pega o primeiro resultado (mais relevante)
            loc = results[0]
            logger.info(f"Localização encontrada: {loc.get('name')}, {loc.get('country')}")
            
            return {
                "error": False,
                "name": loc.get("name"),
                "country": loc.get("country"),
                "latitude": loc.get("latitude"),
                "longitude": loc.get("longitude"),
                "timezone": loc.get("timezone")
            }
            
        except Exception as e:
            logger.error(f"Erro ao buscar coordenadas: {e}", exc_info=True)
            return {
                "error": True,
                "message": f"Erro ao buscar localização: {str(e)}"
            }
    
    def _get_weather(self, coords: Dict) -> Dict:
        """Busca dados do clima para as coordenadas"""
        try:
            params = {
                "latitude": coords["latitude"],
                "longitude": coords["longitude"],
                "current": "temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,weather_code,wind_speed_10m",
                "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,weather_code",
                "timezone": "auto",
                "forecast_days": 3
            }
            
            logger.info(f"Buscando clima: {self.WEATHER_URL}")
            response = self.session.get(self.WEATHER_URL, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            # Extrai dados atuais
            current = data.get("current", {})
            daily = data.get("daily", {})
            
            return {
                "error": False,
                "current": {
                    "temperature": current.get("temperature_2m"),
                    "apparent_temperature": current.get("apparent_temperature"),
                    "humidity": current.get("relative_humidity_2m"),
                    "wind_speed": current.get("wind_speed_10m"),
                    "precipitation": current.get("precipitation"),
                    "weather_code": current.get("weather_code"),
                    "weather_description": self._get_weather_description(current.get("weather_code")),
                    "time": current.get("time")
                },
                "forecast": {
                    "dates": daily.get("time", []),
                    "max_temp": daily.get("temperature_2m_max", []),
                    "min_temp": daily.get("temperature_2m_min", []),
                    "precipitation": daily.get("precipitation_sum", []),
                    "weather_codes": daily.get("weather_code", [])
                }
            }
            
        except Exception as e:
            logger.error(f"Erro ao buscar clima: {e}", exc_info=True)
            return {
                "error": True,
                "message": f"Erro ao buscar dados do clima: {str(e)}"
            }
    
    def _get_weather_description(self, code: Optional[int]) -> str:
        """Converte código do clima para descrição"""
        if code is None:
            return "Desconhecido"
        
        weather_codes = {
            0: "☀️ Céu limpo",
            1: "🌤️ Principalmente limpo",
            2: "⛅ Parcialmente nublado",
            3: "☁️ Nublado",
            45: "🌫️ Névoa",
            48: "🌫️ Névoa com geada",
            51: "🌦️ Chuvisco leve",
            53: "🌦️ Chuvisco moderado",
            55: "🌧️ Chuvisco intenso",
            61: "🌧️ Chuva leve",
            63: "🌧️ Chuva moderada",
            65: "🌧️ Chuva forte",
            71: "🌨️ Neve leve",
            73: "🌨️ Neve moderada",
            75: "❄️ Neve forte",
            77: "🌨️ Grãos de neve",
            80: "🌦️ Pancadas de chuva leves",
            81: "⛈️ Pancadas de chuva moderadas",
            82: "⛈️ Pancadas de chuva fortes",
            85: "🌨️ Pancadas de neve leves",
            86: "❄️ Pancadas de neve fortes",
            95: "⛈️ Tempestade",
            96: "⛈️ Tempestade com granizo leve",
            99: "⛈️ Tempestade com granizo forte"
        }
        
        return weather_codes.get(code, f"Código {code}")
    
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
        
        current = result.get("current", {})
        forecast = result.get("forecast", {})
        
        # Formata clima atual
        current_weather = f"""🌍 **{result['location']}, {result['country']}**

**Clima Atual:**
• {current['weather_description']}
• **Temperatura**: {current['temperature']}°C
• **Sensação térmica**: {current['apparent_temperature']}°C
• **Umidade**: {current['humidity']}%
• **Vento**: {current['wind_speed']} km/h"""
        
        if current.get('precipitation', 0) > 0:
            current_weather += f"\n• **Precipitação**: {current['precipitation']} mm"
        
        # Adiciona previsão
        if forecast.get("dates"):
            current_weather += "\n\n**Previsão próximos dias:**"
            for i in range(min(3, len(forecast["dates"]))):
                date = forecast["dates"][i]
                max_t = forecast["max_temp"][i]
                min_t = forecast["min_temp"][i]
                precip = forecast["precipitation"][i]
                code = forecast["weather_codes"][i]
                desc = self._get_weather_description(code)
                
                # Formata data
                try:
                    date_obj = datetime.fromisoformat(date)
                    date_str = date_obj.strftime("%d/%m")
                except:
                    date_str = date
                
                current_weather += f"\n• **{date_str}**: {desc} | {min_t}°C - {max_t}°C"
                if precip > 0:
                    current_weather += f" | 🌧️ {precip}mm"
        
        return current_weather