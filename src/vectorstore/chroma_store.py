"""
Vector Store usando ChromaDB para armazenamento e recuperação de contexto
"""

import logging
from typing import List, Dict, Optional
import chromadb
from chromadb.config import Settings
from pathlib import Path
import hashlib

logger = logging.getLogger(__name__)


class ChromaVectorStore:
    """Gerencia armazenamento vetorial com ChromaDB"""
    
    def __init__(self, persist_directory: str = "data/chroma"):
        """
        Inicializa o vector store
        
        Args:
            persist_directory: Diretório para persistir dados
        """
        self.persist_dir = Path(persist_directory)
        self.persist_dir.mkdir(parents=True, exist_ok=True)
        
        # Inicializa ChromaDB com persistência
        self.client = chromadb.Client(Settings(
            persist_directory=str(self.persist_dir),
            anonymized_telemetry=False
        ))
        
        # Cria ou obtém coleções
        self.conversations_collection = self.client.get_or_create_collection(
            name="conversations",
            metadata={"description": "Histórico de conversas"}
        )
        
        self.knowledge_collection = self.client.get_or_create_collection(
            name="knowledge",
            metadata={"description": "Base de conhecimento"}
        )
        
        # Inicializa base de conhecimento se vazia
        if self.knowledge_collection.count() == 0:
            self._initialize_knowledge_base()
        
        logger.info("ChromaDB inicializado com sucesso")
    
    def _initialize_knowledge_base(self):
        """Inicializa base de conhecimento com informações padrão"""
        knowledge_items = [
            {
                "content": "O assistente pode consultar CEPs brasileiros usando a ferramenta ViaCEP. "
                          "Basta fornecer um CEP de 8 dígitos e o sistema retornará informações completas sobre o endereço.",
                "metadata": {"category": "tools", "type": "viacep"}
            },
            {
                "content": "O assistente possui acesso à PokéAPI para fornecer informações detalhadas sobre Pokémon. "
                          "Você pode perguntar sobre qualquer Pokémon pelo nome ou número da Pokédex.",
                "metadata": {"category": "tools", "type": "pokemon"}
            },
            {
                "content": "O assistente pode consultar dados geográficos do Brasil via IBGE. "
                          "Pergunte sobre estados, municípios, regiões e códigos IBGE.",
                "metadata": {"category": "tools", "type": "ibge"}
            },
            {
                "content": "O assistente pode consultar previsão do tempo e clima atual usando Open-Meteo. "
                          "Pergunte sobre temperatura, clima e previsão para qualquer cidade do mundo.",
                "metadata": {"category": "tools", "type": "clima"}
            },
            {
                "content": "O assistente pode consultar informações sobre séries de TV usando TVMaze. "
                          "Pergunte sobre séries, episódios, atores e ratings.",
                "metadata": {"category": "tools", "type": "series"}
            },
            {
                "content": "O assistente pode consultar informações sobre livros usando Open Library. "
                          "Pergunte sobre livros, autores, ISBN e sinopses.",
                "metadata": {"category": "tools", "type": "livros"}
            },
            {
                "content": "O assistente pode buscar letras de músicas usando Lyrics.ovh. "
                          "Pergunte sobre letras fornecendo o nome da música e do artista.",
                "metadata": {"category": "tools", "type": "letras"}
            },
            {
                "content": "Este sistema utiliza inteligência artificial com o modelo Gemini 2.5 Flash do Google. "
                          "O agente usa function calling nativo para decidir automaticamente quando usar ferramentas externas.",
                "metadata": {"category": "system", "type": "capabilities"}
            },
            {
                "content": "O sistema possui um mecanismo de feedback inteligente que permite melhorar "
                          "continuamente as respostas do assistente. Feedbacks são analisados automaticamente "
                          "e incorporados ao prompt do agente.",
                "metadata": {"category": "system", "type": "feedback"}
            }
        ]
        
        for idx, item in enumerate(knowledge_items):
            doc_id = f"kb_{idx}"
            self.knowledge_collection.add(
                documents=[item["content"]],
                metadatas=[item["metadata"]],
                ids=[doc_id]
            )
        
        logger.info(f"Base de conhecimento inicializada com {len(knowledge_items)} itens")
    
    def add_conversation(self, user_message: str, agent_response: str, 
                        metadata: Optional[Dict] = None):
        """
        Adiciona interação ao histórico
        
        Args:
            user_message: Mensagem do usuário
            agent_response: Resposta do agente
            metadata: Metadados adicionais (opcional)
        """
        try:
            # Cria ID único baseado no conteúdo
            content = f"User: {user_message}\nAgent: {agent_response}"
            doc_id = hashlib.md5(content.encode()).hexdigest()
            
            if metadata is None:
                metadata = {}
            
            metadata["type"] = "conversation"
            
            self.conversations_collection.add(
                documents=[content],
                metadatas=[metadata],
                ids=[doc_id]
            )
            
            logger.debug(f"Conversa adicionada ao vector store: {doc_id}")
            
        except Exception as e:
            logger.error(f"Erro ao adicionar conversa: {e}")
    
    def search_similar_conversations(self, query: str, n_results: int = 3) -> List[Dict]:
        """
        Busca conversas similares
        
        Args:
            query: Texto de busca
            n_results: Número de resultados a retornar
            
        Returns:
            Lista de conversas similares
        """
        try:
            results = self.conversations_collection.query(
                query_texts=[query],
                n_results=min(n_results, self.conversations_collection.count())
            )
            
            if not results["documents"] or not results["documents"][0]:
                return []
            
            similar = []
            for doc, metadata, distance in zip(
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0]
            ):
                similar.append({
                    "content": doc,
                    "metadata": metadata,
                    "similarity": 1 - distance  # Converte distância para similaridade
                })
            
            logger.debug(f"Encontradas {len(similar)} conversas similares")
            return similar
            
        except Exception as e:
            logger.error(f"Erro ao buscar conversas similares: {e}")
            return []
    
    def search_knowledge(self, query: str, n_results: int = 3) -> List[Dict]:
        """
        Busca na base de conhecimento
        
        Args:
            query: Texto de busca
            n_results: Número de resultados a retornar
            
        Returns:
            Lista de itens de conhecimento relevantes
        """
        try:
            results = self.knowledge_collection.query(
                query_texts=[query],
                n_results=min(n_results, self.knowledge_collection.count())
            )
            
            if not results["documents"] or not results["documents"][0]:
                return []
            
            knowledge = []
            for doc, metadata, distance in zip(
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0]
            ):
                knowledge.append({
                    "content": doc,
                    "metadata": metadata,
                    "similarity": 1 - distance
                })
            
            logger.debug(f"Encontrados {len(knowledge)} itens de conhecimento")
            return knowledge
            
        except Exception as e:
            logger.error(f"Erro ao buscar conhecimento: {e}")
            return []
    
    def add_knowledge(self, content: str, metadata: Optional[Dict] = None):
        """
        Adiciona item à base de conhecimento
        
        Args:
            content: Conteúdo do conhecimento
            metadata: Metadados adicionais
        """
        try:
            doc_id = hashlib.md5(content.encode()).hexdigest()
            
            if metadata is None:
                metadata = {}
            
            self.knowledge_collection.add(
                documents=[content],
                metadatas=[metadata],
                ids=[doc_id]
            )
            
            logger.info(f"Conhecimento adicionado: {doc_id}")
            
        except Exception as e:
            logger.error(f"Erro ao adicionar conhecimento: {e}")
    
    def get_statistics(self) -> Dict:
        """
        Retorna estatísticas do vector store
        
        Returns:
            Dicionário com estatísticas
        """
        return {
            "conversations_count": self.conversations_collection.count(),
            "knowledge_count": self.knowledge_collection.count(),
            "persist_directory": str(self.persist_dir)
        }
    
    def clear_conversations(self):
        """Limpa histórico de conversas"""
        try:
            self.client.delete_collection("conversations")
            self.conversations_collection = self.client.create_collection(
                name="conversations",
                metadata={"description": "Histórico de conversas"}
            )
            logger.info("Histórico de conversas limpo")
        except Exception as e:
            logger.error(f"Erro ao limpar conversas: {e}")
