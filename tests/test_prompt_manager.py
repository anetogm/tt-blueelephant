"""
Testes para o gerenciador de prompts
"""

import pytest
import json
import tempfile
from pathlib import Path
from src.agent.prompt_manager import PromptManager


@pytest.fixture
def temp_dir():
    """Cria diretório temporário para testes"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def prompt_manager(temp_dir):
    """Cria instância do PromptManager para testes"""
    return PromptManager(data_dir=temp_dir)


def test_initialization(prompt_manager):
    """Testa inicialização do gerenciador"""
    assert prompt_manager is not None
    assert len(prompt_manager.prompts_history) > 0
    assert prompt_manager.get_current_version() == 1


def test_get_current_prompt(prompt_manager):
    """Testa recuperação do prompt atual"""
    current = prompt_manager.get_current_prompt()
    assert isinstance(current, str)
    assert len(current) > 0
    assert "assistente" in current.lower() or "você é" in current.lower()


def test_update_prompt(prompt_manager):
    """Testa atualização de prompt"""
    new_prompt = "Novo prompt de teste"
    improvements = ["Melhoria 1", "Melhoria 2"]
    
    old_version = prompt_manager.get_current_version()
    new_version = prompt_manager.update_prompt(new_prompt, improvements)
    
    assert new_version == old_version + 1
    assert prompt_manager.get_current_prompt() == new_prompt


def test_get_prompt_version(prompt_manager):
    """Testa recuperação de versão específica"""
    version_1 = prompt_manager.get_prompt_version(1)
    assert version_1 is not None
    assert isinstance(version_1, str)
    
    version_999 = prompt_manager.get_prompt_version(999)
    assert version_999 is None


def test_increment_feedback_count(prompt_manager):
    """Testa incremento de contador de feedback"""
    initial_count = prompt_manager.prompts_history[-1]["feedback_count"]
    
    prompt_manager.increment_feedback_count()
    
    new_count = prompt_manager.prompts_history[-1]["feedback_count"]
    assert new_count == initial_count + 1


def test_get_history(prompt_manager):
    """Testa recuperação do histórico"""
    history = prompt_manager.get_history()
    assert isinstance(history, list)
    assert len(history) > 0
    assert "version" in history[0]
    assert "prompt" in history[0]


def test_get_statistics(prompt_manager):
    """Testa estatísticas"""
    stats = prompt_manager.get_statistics()
    
    assert "total_versions" in stats
    assert "current_version" in stats
    assert "total_feedbacks" in stats
    assert stats["total_versions"] >= 1


def test_persistence(temp_dir):
    """Testa persistência de dados entre instâncias"""
    # Primeira instância
    pm1 = PromptManager(data_dir=temp_dir)
    pm1.update_prompt("Test prompt", ["Test improvement"])
    version1 = pm1.get_current_version()
    
    # Segunda instância (deve carregar dados salvos)
    pm2 = PromptManager(data_dir=temp_dir)
    version2 = pm2.get_current_version()
    
    assert version1 == version2
    assert pm2.get_current_prompt() == "Test prompt"


def test_multiple_updates(prompt_manager):
    """Testa múltiplas atualizações sequenciais"""
    for i in range(3):
        new_prompt = f"Prompt versão {i+2}"
        improvements = [f"Melhoria {i+1}"]
        version = prompt_manager.update_prompt(new_prompt, improvements)
        assert version == i + 2
    
    assert prompt_manager.get_current_version() == 4
    assert len(prompt_manager.get_history()) == 4
