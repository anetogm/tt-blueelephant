"""
Testes para as ferramentas externas
"""

import pytest
from src.tools import ViaCEPTool, PokemonTool


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
    
    def test_format_error(self, viacep):
        """Testa formatação de erro"""
        result = {"error": True, "message": "Erro de teste"}
        formatted = viacep.format_result(result)
        
        assert isinstance(formatted, str)
        assert "Erro de teste" in formatted


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
    
    def test_search_by_type(self, pokemon):
        """Testa busca por tipo"""
        result = pokemon.search_by_type("electric")
        
        if not result.get("error"):
            assert "type" in result
            assert "pokemon" in result
            assert isinstance(result["pokemon"], list)
