"""
Testes para as ferramentas externas
"""

import pytest
from src.tools import *

class TestViaCEPTool:
    """Testes para ferramenta ViaCEP"""
    
    @pytest.fixture
    def viacep(self):
        return ViaCEPTool()
    
    def test_initialization(self, viacep):
        """Testa inicialização"""
        assert viacep.name == "consulta_cep"
        assert len(viacep.description) > 0
    
    def test_valid_cep(self, viacep):
        """Testa consulta com CEP válido"""
        result = viacep.execute("01310-100")
        
        assert not result.get("error")
        assert "cep" in result
        assert "logradouro" in result
        assert "localidade" in result
    
    def test_invalid_cep_format(self, viacep):
        """Testa CEP com formato inválido"""
        result = viacep.execute("123")
        
        assert result.get("error")
        assert "inválido" in result.get("message", "").lower()
    
    def test_nonexistent_cep(self, viacep):
        """Testa CEP inexistente"""
        result = viacep.execute("99999-999")
        
        assert result.get("error")
    
    def test_format_result(self, viacep):
        """Testa formatação de resultado"""
        result = {"error": False, "cep": "01310-100", "logradouro": "Avenida Paulista"}
        formatted = viacep.format_result(result)
        
        assert isinstance(formatted, str)
        assert "01310-100" in formatted
        assert "Avenida Paulista" in formatted

class TestPokemonTool:
    """Testes para ferramenta PokéAPI"""
    
    @pytest.fixture
    def pokemon(self):
        return PokemonTool()
    
    def test_initialization(self, pokemon):
        """Testa inicialização"""
        assert pokemon.name == "consulta_pokemon"
        assert len(pokemon.description) > 0
    
    def test_valid_pokemon_name(self, pokemon):
        """Testa consulta com nome válido"""
        result = pokemon.execute("pikachu")
        
        assert not result.get("error")
        assert result.get("name") == "Pikachu"
        assert "types" in result
        assert len(result["types"]) > 0
    
    def test_valid_pokemon_number(self, pokemon):
        """Testa consulta com número válido"""
        result = pokemon.execute("25")  # Pikachu
        
        assert not result.get("error")
        assert result.get("id") == 25
        assert result.get("name") == "Pikachu"
    
    def test_invalid_pokemon(self, pokemon):
        """Testa Pokémon inexistente"""
        result = pokemon.execute("pokemonnaoexiste123")
        
        assert result.get("error")
        assert "não encontrado" in result.get("message", "").lower()
    
    def test_format_result(self, pokemon):
        """Testa formatação de resultado"""
        result = {
            "error": False,
            "id": 25,
            "name": "Pikachu",
            "types": ["Electric"],
            "height": 0.4,
            "weight": 6.0,
            "abilities": ["Static"],
            "stats": {"hp": 35}
        }
        formatted = pokemon.format_result(result)
        
        assert isinstance(formatted, str)
        assert "Pikachu" in formatted
        assert "Electric" in formatted

class TestIBGETool:
    """Testes para ferramenta IBGE"""
    
    @pytest.fixture
    def ibge(self):
        return IBGETool()
    
    def test_initialization(self, ibge):
        """Testa inicialização"""
        assert ibge.name == "consulta_ibge"
        assert len(ibge.description) > 0
    
    def test_valid_state_uf(self, ibge):
        """Testa consulta de estado por UF"""
        result = ibge.execute("SP")
        
        assert not result.get("error")
        assert result.get("type") == "estado"
        assert "nome" in result
        assert "sigla" in result
        assert result["sigla"] == "SP"
    
    def test_valid_state_name(self, ibge):
        """Testa consulta de estado por nome"""
        result = ibge.execute("São Paulo")
        
        assert not result.get("error")
        assert result.get("type") == "estado"
        assert "São Paulo" in result.get("nome", "")
    
    def test_valid_city(self, ibge):
        """Testa consulta de município"""
        result = ibge.execute("Campinas")
        
        assert not result.get("error")
        assert result.get("type") == "municipio"
        assert "nome" in result
        assert "codigo_ibge" in result
    
    def test_invalid_query(self, ibge):
        """Testa consulta inválida"""
        result = ibge.execute("LocalInexistente12345XYZ")
        
        assert result.get("error")
        assert "não encontrado" in result.get("message", "").lower()
    
    def test_format_result(self, ibge):
        """Testa formatação de resultado"""
        result = {
            "error": False,
            "type": "estado",
            "id": 35, 
            "nome": "São Paulo",
            "sigla": "SP",
            "regiao": {
                "nome": "Sudeste",
                "sigla": "SE"
            }
        }
        formatted = ibge.format_result(result)
        
        assert isinstance(formatted, str)
        assert "São Paulo" in formatted
        assert "SP" in formatted

class TestOpenMeteoTool:
    """Testes para ferramenta Open-Meteo"""
    
    @pytest.fixture
    def weather(self):
        return OpenMeteoTool()
    
    def test_initialization(self, weather):
        """Testa inicialização"""
        assert weather.name == "consulta_clima"
        assert len(weather.description) > 0
    
    def test_valid_city(self, weather):
        """Testa consulta de clima para cidade válida"""
        result = weather.execute("São Paulo")
        
        assert not result.get("error")
        assert "location" in result
        assert "current" in result
        assert "temperature" in result["current"]
    
    def test_international_city(self, weather):
        """Testa consulta para cidade internacional"""
        result = weather.execute("London")
        
        assert not result.get("error")
        assert "location" in result
        # API pode retornar nome traduzido (Londres) ou original (London)
        assert "london" in result["location"].lower() or "londres" in result["location"].lower()
    
    def test_invalid_location(self, weather):
        """Testa localização inexistente"""
        result = weather.execute("CidadeInexistente12345XYZ")
        
        assert result.get("error")
        assert "não encontrada" in result.get("message", "").lower()
    
    def test_format_result(self, weather):
        """Testa formatação de resultado"""
        result = {
            "error": False,
            "location": "São Paulo",
            "country": "BR",
            "coordinates": {"latitude": -23.5, "longitude": -46.6},
            "current": {
                "temperature": 25.5,
                "apparent_temperature": 26.0,
                "wind_speed": 10.0,
                "humidity": 65,
                "weather_description": "☀️ Céu limpo",
                "precipitation": 0 
            },
            "forecast": {
                "dates": [],
                "max_temp": [],
                "min_temp": [],
                "precipitation": [],
                "weather_codes": []
            }
        }
        formatted = weather.format_result(result)
        
        assert isinstance(formatted, str)
        assert "São Paulo" in formatted
        assert "25.5" in formatted or "25,5" in formatted

class TestTVMazeTool:
    """Testes para ferramenta TVMaze"""
    
    @pytest.fixture
    def tvmaze(self):
        return TVMazeTool()
    
    def test_initialization(self, tvmaze):
        """Testa inicialização"""
        assert tvmaze.name == "consulta_serie"
        assert len(tvmaze.description) > 0
    
    def test_valid_show(self, tvmaze):
        """Testa consulta de série válida"""
        result = tvmaze.execute("Breaking Bad")
        
        assert not result.get("error")
        assert "name" in result
        assert "Breaking Bad" in result["name"]
        assert "genres" in result
    
    def test_show_with_info(self, tvmaze):
        """Testa se retorna informações completas"""
        result = tvmaze.execute("Game of Thrones")
        
        if not result.get("error"):
            assert "name" in result
            assert "status" in result
            assert "summary" in result
    
    def test_invalid_show(self, tvmaze):
        """Testa série inexistente"""
        result = tvmaze.execute("SerieInexistente12345XYZ")
        
        assert result.get("error")
        assert "não encontrada" in result.get("message", "").lower()
    
    def test_format_result(self, tvmaze):
        """Testa formatação de resultado"""
        result = {
            "error": False,
            "name": "Breaking Bad",
            "genres": ["Drama", "Crime"],
            "status": "Ended",
            "rating": 9.5
        }
        formatted = tvmaze.format_result(result)
        
        assert isinstance(formatted, str)
        assert "Breaking Bad" in formatted
        assert "Drama" in formatted

class TestOpenLibraryTool:
    """Testes para ferramenta Open Library"""
    
    @pytest.fixture
    def library(self):
        return OpenLibraryTool()
    
    def test_initialization(self, library):
        """Testa inicialização"""
        assert library.name == "consulta_livro"
        assert len(library.description) > 0
    
    def test_valid_book_title(self, library):
        """Testa consulta por título de livro"""
        result = library.execute("The Lord of the Rings")
        
        assert not result.get("error")
        assert "title" in result
        assert "authors" in result
    
    def test_valid_book_author(self, library):
        """Testa consulta por autor"""
        result = library.execute("J.K. Rowling")
        
        assert not result.get("error")
        assert "title" in result or "authors" in result
    
    def test_portuguese_book(self, library):
        """Testa consulta de livro em português"""
        result = library.execute("Dom Casmurro")
        
        if not result.get("error"):
            assert "title" in result
    
    def test_invalid_book(self, library):
        """Testa livro inexistente"""
        result = library.execute("LivroTotalmenteInexistente12345XYZ")
        
        assert result.get("error")
        assert "não encontrado" in result.get("message", "").lower()
    
    def test_format_result(self, library):
        """Testa formatação de resultado"""
        result = {
            "error": False,
            "title": "Harry Potter",
            "authors": ["J.K. Rowling"],
            "first_publish_year": 1997,
            "isbn": ["123456789"]
        }
        formatted = library.format_result(result)
        
        assert isinstance(formatted, str)
        assert "Harry Potter" in formatted
        assert "J.K. Rowling" in formatted
        
class TestLyricsOvhTool:
    """Testes para ferramenta Lyrics.ovh"""
    
    @pytest.fixture
    def lyrics(self):
        return LyricsOvhTool()
    
    def test_initialization(self, lyrics):
        """Testa inicialização"""
        assert lyrics.name == "consulta_letra_musica"
        assert len(lyrics.description) > 0
    
    def test_valid_song(self, lyrics):
        """Testa consulta de letra válida"""
        result = lyrics.execute("Coldplay", "Yellow")
        
        # API pode estar indisponível ou música não encontrada
        if not result.get("error"):
            assert "lyrics" in result
            assert "artist" in result
            assert "song" in result
            assert len(result["lyrics"]) > 0
    
    def test_famous_song(self, lyrics):
        """Testa música famosa"""
        result = lyrics.execute("The Beatles", "Hey Jude")
        
        if not result.get("error"):
            assert "lyrics" in result
            assert "Hey Jude" in result.get("song", "")
    
    def test_invalid_song(self, lyrics):
        """Testa música inexistente"""
        result = lyrics.execute("ArtistaInexistente123", "MusicaInexistente456")
        
        assert result.get("error")
        assert "não encontrada" in result.get("message", "").lower()
    
    def test_format_result(self, lyrics):
        """Testa formatação de resultado"""
        result = {
            "error": False,
            "artist": "Queen",
            "song": "Bohemian Rhapsody",
            "lyrics": "Is this the real life?\nIs this just fantasy?"
        }
        formatted = lyrics.format_result(result)
        
        assert isinstance(formatted, str)
        assert "Queen" in formatted
        assert "Bohemian Rhapsody" in formatted
        assert "Is this the real life?" in formatted

# Teste de integração básico
class TestToolsIntegration:
    """Testes de integração entre ferramentas"""
    
    def test_all_tools_have_name(self):
        """Verifica que todas as ferramentas têm nome"""
        tools = [
            ViaCEPTool(),
            PokemonTool(),
            IBGETool(),
            OpenMeteoTool(),
            TVMazeTool(),
            OpenLibraryTool(),
            LyricsOvhTool()
        ]
        
        for tool in tools:
            assert hasattr(tool, 'name')
            assert len(tool.name) > 0
    
    def test_all_tools_have_description(self):
        """Verifica que todas as ferramentas têm descrição"""
        tools = [
            ViaCEPTool(),
            PokemonTool(),
            IBGETool(),
            OpenMeteoTool(),
            TVMazeTool(),
            OpenLibraryTool(),
            LyricsOvhTool()
        ]
        
        for tool in tools:
            assert hasattr(tool, 'description')
            assert len(tool.description) > 0
    
    def test_all_tools_have_execute(self):
        """Verifica que todas as ferramentas têm método execute"""
        tools = [
            ViaCEPTool(),
            PokemonTool(),
            IBGETool(),
            OpenMeteoTool(),
            TVMazeTool(),
            OpenLibraryTool(),
            LyricsOvhTool()
        ]
        
        for tool in tools:
            assert hasattr(tool, 'execute')
            assert callable(tool.execute)
    
    def test_all_tools_return_dict(self):
        """Verifica que todas as ferramentas retornam dicionário"""
        # Testes rápidos com dados válidos
        tests = [
            (ViaCEPTool(), "01310-100"),
            (PokemonTool(), "pikachu"),
            (IBGETool(), "SP"),
        ]
        
        for tool, param in tests:
            if isinstance(param, tuple):
                result = tool.execute(*param)
            else:
                result = tool.execute(param)
            assert isinstance(result, dict)
            assert "error" in result