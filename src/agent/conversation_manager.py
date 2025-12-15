"""
Gerenciador de Histórico de Conversas
Salva todas as conversas automaticamente no histórico
"""

import logging
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict
import uuid

logger = logging.getLogger(__name__)


class ConversationManager:
    """Gerencia histórico persistente de conversas em sessões"""
    
    def __init__(self, data_dir: str = "data"):
        """
        Inicializa o gerenciador de conversas
        
        Args:
            data_dir: Diretório para armazenar conversas
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.conversations_file = self.data_dir / "conversations.json"
        self.sessions: List[Dict] = []
        self.current_session_id = None
        self.current_session_index = None
        self._load_conversations()
    
    def _load_conversations(self):
        """Carrega histórico de conversas do arquivo"""
        try:
            if self.conversations_file.exists():
                with open(self.conversations_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.sessions = data.get("sessions", [])
                logger.info(f"Carregadas {len(self.sessions)} sessões do histórico")
        except Exception as e:
            logger.error(f"Erro ao carregar conversas: {e}")
            self.sessions = []
    
    def _save_conversations(self):
        """Salva conversas no arquivo (automático)"""
        try:
            data = {
                "sessions": self.sessions,
                "last_updated": datetime.now().isoformat()
            }
            with open(self.conversations_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Erro ao salvar conversas: {e}")
    
    def start_new_session(self):
        """Inicia uma nova sessão de conversa"""
        self.current_session_id = str(uuid.uuid4())
        
        # Cria nova sessão no histórico imediatamente
        new_session = {
            "session_id": self.current_session_id,
            "started_at": datetime.now().isoformat(),
            "messages": [],
            "message_count": 0
        }
        
        self.sessions.append(new_session)
        self.current_session_index = len(self.sessions) - 1
        self._save_conversations()
        
        logger.info(f"Nova sessão iniciada e adicionada ao histórico: {self.current_session_id}")
    
    def add_message(self, role: str, content: str, tools_used: List = None, tools_output: str = None):
        """
        Adiciona uma mensagem à sessão atual E salva automaticamente no histórico
        
        Args:
            role: Papel da mensagem ('user' ou 'assistant')
            content: Conteúdo da mensagem
            tools_used: Lista de ferramentas usadas (opcional)
            tools_output: Saída das ferramentas (opcional)
        """
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        
        if tools_used:
            message["tools_used"] = tools_used
        if tools_output:
            message["tools_output"] = tools_output
        
        # Adiciona à sessão atual no histórico
        if self.current_session_index is not None:
            self.sessions[self.current_session_index]["messages"].append(message)
            self.sessions[self.current_session_index]["message_count"] = len(
                self.sessions[self.current_session_index]["messages"]
            )
            self.sessions[self.current_session_index]["last_updated"] = datetime.now().isoformat()
            
            # Salva automaticamente
            self._save_conversations()
            logger.info(f"Mensagem adicionada e salva automaticamente ({role})")
    
    def get_current_messages(self) -> List[Dict]:
        """Retorna mensagens da sessão atual"""
        if self.current_session_index is not None:
            return self.sessions[self.current_session_index]["messages"]
        return []
    
    def get_all_sessions(self) -> List[Dict]:
        """Retorna todas as sessões salvas (exceto a atual vazia)"""
        # Retorna todas as sessões que têm pelo menos 1 mensagem
        return [s for s in self.sessions if s["message_count"] > 0]
    
    def clear_current_session(self):
        """Limpa apenas a sessão atual da tela (mantém no histórico)"""
        # Apenas inicia uma nova sessão
        self.start_new_session()
        logger.info("Nova sessão iniciada (anterior mantida no histórico)")
    
    def delete_session(self, session_id: str):
        """Remove uma sessão específica do histórico"""
        original_count = len(self.sessions)
        self.sessions = [s for s in self.sessions if s["session_id"] != session_id]
        
        # Atualiza índice da sessão atual se necessário
        if self.current_session_index >= len(self.sessions):
            self.current_session_index = len(self.sessions) - 1 if self.sessions else None
        
        if len(self.sessions) < original_count:
            self._save_conversations()
            logger.info(f"Sessão {session_id} removida do histórico")
    
    def clear_all_history(self):
        """Limpa TODO o histórico de sessões salvas"""
        self.sessions = []
        self.current_session_index = None
        self._save_conversations()
        logger.info("Todo histórico de conversas limpo")
        
        # Inicia nova sessão
        self.start_new_session()
    
    def get_statistics(self) -> Dict:
        """Retorna estatísticas do histórico"""
        sessions_with_messages = [s for s in self.sessions if s["message_count"] > 0]
        total_messages = sum(s["message_count"] for s in sessions_with_messages)
        
        return {
            "total_sessions": len(sessions_with_messages),
            "total_messages": total_messages,
            "current_session_messages": len(self.get_current_messages()),
            "has_history": len(sessions_with_messages) > 0
        }