"""
Gerenciador de Prompts com Sistema de Versionamento
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class PromptManager:
    """Gerencia prompts do agente com versionamento e histórico"""
    
    def __init__(self, data_dir: str = "data"):
        """
        Inicializa o gerenciador de prompts
        
        Args:
            data_dir: Diretório para armazenar dados de prompts
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.prompts_file = self.data_dir / "prompts_history.json"
        self.prompts_history: List[Dict] = []
        self._load_prompts()
        
        # Prompt inicial padrão
        if not self.prompts_history:
            self._initialize_default_prompt()
    
    def _initialize_default_prompt(self):
        """Inicializa com prompt padrão"""
        default_prompt = {
            "version": 1,
            "prompt": """Você é um assistente virtual inteligente e prestativo.

Suas características:
- Responda de forma clara, concisa e educada
- Use as ferramentas disponíveis quando apropriado
- Seja proativo em ajudar o usuário
- Mantenha um tom profissional mas amigável

Ferramentas disponíveis:
1. Consulta de CEP (Brasil) - use quando o usuário mencionar CEP ou endereço
2. Informações sobre Pokémon - use quando o usuário perguntar sobre Pokémon

Sempre forneça respostas completas e úteis.""",
            "timestamp": datetime.now().isoformat(),
            "feedback_count": 0,
            "improvements": ["Prompt inicial padrão"]
        }
        self.prompts_history.append(default_prompt)
        self._save_prompts()
        logger.info("Prompt padrão inicializado")
    
    def _load_prompts(self):
        """Carrega histórico de prompts do arquivo"""
        try:
            if self.prompts_file.exists():
                with open(self.prompts_file, 'r', encoding='utf-8') as f:
                    self.prompts_history = json.load(f)
                logger.info(f"Carregados {len(self.prompts_history)} prompts do histórico")
        except Exception as e:
            logger.error(f"Erro ao carregar prompts: {e}")
            self.prompts_history = []
    
    def _save_prompts(self):
        """Salva histórico de prompts no arquivo"""
        try:
            with open(self.prompts_file, 'w', encoding='utf-8') as f:
                json.dump(self.prompts_history, f, ensure_ascii=False, indent=2)
            logger.info("Histórico de prompts salvo com sucesso")
        except Exception as e:
            logger.error(f"Erro ao salvar prompts: {e}")
    
    def get_current_prompt(self) -> str:
        """
        Retorna o prompt atual (última versão)
        
        Returns:
            String com o prompt atual
        """
        if not self.prompts_history:
            self._initialize_default_prompt()
        return self.prompts_history[-1]["prompt"]
    
    def get_prompt_version(self, version: int) -> Optional[str]:
        """
        Retorna uma versão específica do prompt
        
        Args:
            version: Número da versão desejada
            
        Returns:
            String com o prompt ou None se não encontrado
        """
        for prompt_data in self.prompts_history:
            if prompt_data["version"] == version:
                return prompt_data["prompt"]
        return None
    
    def get_history(self) -> List[Dict]:
        """
        Retorna todo o histórico de prompts
        
        Returns:
            Lista com dicionários contendo dados de cada versão
        """
        return self.prompts_history.copy()
    
    def update_prompt(self, new_prompt: str, improvements: List[str]) -> int:
        """
        Cria nova versão do prompt com melhorias
        
        Args:
            new_prompt: Novo texto do prompt
            improvements: Lista de melhorias aplicadas
            
        Returns:
            Número da nova versão criada
        """
        new_version = len(self.prompts_history) + 1
        
        prompt_data = {
            "version": new_version,
            "prompt": new_prompt,
            "timestamp": datetime.now().isoformat(),
            "feedback_count": 0,
            "improvements": improvements
        }
        
        self.prompts_history.append(prompt_data)
        self._save_prompts()
        
        logger.info(f"Prompt atualizado para versão {new_version}")
        return new_version
    
    def increment_feedback_count(self):
        """Incrementa contador de feedbacks da versão atual"""
        if self.prompts_history:
            self.prompts_history[-1]["feedback_count"] += 1
            self._save_prompts()
    
    def get_current_version(self) -> int:
        """Retorna número da versão atual"""
        return len(self.prompts_history)
    
    def get_statistics(self) -> Dict:
        """
        Retorna estatísticas sobre os prompts
        
        Returns:
            Dicionário com estatísticas
        """
        total_versions = len(self.prompts_history)
        total_feedbacks = sum(p["feedback_count"] for p in self.prompts_history)
        
        return {
            "total_versions": total_versions,
            "current_version": total_versions,
            "total_feedbacks": total_feedbacks,
            "created_at": self.prompts_history[0]["timestamp"] if self.prompts_history else None,
            "last_update": self.prompts_history[-1]["timestamp"] if self.prompts_history else None
        }
