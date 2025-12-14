"""
Chatbot principal com integração de LLM, ferramentas e vector store
"""

import logging
import re
from typing import List, Dict, Optional, Tuple
import google.generativeai as genai

from ..tools import ViaCEPTool, PokemonTool, IBGETool
from ..vectorstore import ChromaVectorStore
from .prompt_manager import PromptManager

logger = logging.getLogger(__name__)


class Chatbot:
    """Agente conversacional com IA e ferramentas externas"""
    
    def __init__(self, api_key: str, data_dir: str = "data"):
        """
        Inicializa o chatbot
        
        Args:
            api_key: Chave da API Gemini
            data_dir: Diretório para armazenar dados
        """
        # Configura Gemini
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        
        # Inicializa componentes
        self.prompt_manager = PromptManager(data_dir)
        self.vector_store = ChromaVectorStore(f"{data_dir}/chroma")
        
        # Inicializa ferramentas
        self.tools = {
            "viacep": ViaCEPTool(),
            "pokemon": PokemonTool(),
            "ibge": IBGETool()
        }
        
        # Histórico da conversa atual
        self.chat_history: List[Dict[str, str]] = []
        
        logger.info("Chatbot inicializado com sucesso")
    
    def _detect_tool_usage(self, user_message: str) -> List[Tuple[str, str]]:
        """
        Detecta se ferramentas devem ser usadas na mensagem
        
        Args:
            user_message: Mensagem do usuário
            
        Returns:
            Lista de tuplas (nome_ferramenta, parâmetro)
        """
        tools_to_use = []
        message_lower = user_message.lower()
        
        # Detecta CEP (formato: 00000-000 ou 00000000)
        cep_pattern = r'\b\d{5}-?\d{3}\b'
        ceps = re.findall(cep_pattern, user_message)
        for cep in ceps:
            tools_to_use.append(("viacep", cep))
        
        # Detecta menções a CEP/endereço
        cep_keywords = ["cep", "endereço", "endereco", "logradouro", "rua"]
        if any(keyword in message_lower for keyword in cep_keywords) and not ceps:
            # Tenta extrair números que podem ser CEP
            numbers = re.findall(r'\b\d{5,8}\b', user_message)
            for num in numbers:
                if len(num) in [5, 8]:
                    tools_to_use.append(("viacep", num))
        
        # Detecta menções a Pokémon
        pokemon_keywords = ["pokemon", "pokémon", "pikachu", "charizard", 
                          "bulbasaur", "pokedex", "pokédex"]
        if any(keyword in message_lower for keyword in pokemon_keywords):
            # Tenta extrair nome ou número do Pokémon
            # Remove palavras comuns
            words = message_lower.split()
            for word in words:
                # Se for número pequeno, pode ser número da pokédex
                if word.isdigit() and int(word) < 1000:
                    tools_to_use.append(("pokemon", word))
                    break
            else:
                # Tenta encontrar nome de Pokémon comum
                common_pokemon = ["pikachu", "charizard", "bulbasaur", "squirtle",
                                "charmander", "mewtwo", "mew", "eevee", "snorlax"]
                for pokemon in common_pokemon:
                    if pokemon in message_lower:
                        tools_to_use.append(("pokemon", pokemon))
                        break
                    
        ibge_keywords = ["estado", "município", "municipio", "cidade", "ibge", 
                        "região", "regiao", "uf", "brasil"]
        
        # Lista de UFs e alguns estados comuns
        ufs = ["ac", "al", "ap", "am", "ba", "ce", "df", "es", "go", "ma", 
               "mt", "ms", "mg", "pa", "pb", "pr", "pe", "pi", "rj", "rn", 
               "rs", "ro", "rr", "sc", "sp", "se", "to"]
        
        estados_comuns = ["são paulo", "rio de janeiro", "minas gerais", "bahia",
                         "paraná", "santa catarina", "rio grande do sul"]
        
        # Verifica se menciona IBGE ou conceitos geográficos
        if any(keyword in message_lower for keyword in ibge_keywords):
            # Procura por UF
            words = message_lower.split()
            for word in words:
                clean_word = word.strip('.,!?')
                if clean_word in ufs:
                    tools_to_use.append(("ibge", clean_word.upper()))
                    break
            
            # Procura por nome de estado/cidade
            for estado in estados_comuns:
                if estado in message_lower:
                    tools_to_use.append(("ibge", estado.title()))
                    break
            
            # Se não encontrou mas tem keywords, tenta extrair possível nome
            if not any(t[0] == "ibge" for t in tools_to_use):
                # Pega palavras capitalizadas que podem ser cidades/estados
                words_orig = user_message.split()
                for word in words_orig:
                    if word and word[0].isupper() and len(word) > 3:
                        clean = word.strip('.,!?')
                        if clean.lower() not in ibge_keywords:
                            tools_to_use.append(("ibge", clean))
                            break
        
        return tools_to_use
    
    def _execute_tools(self, tools_to_use: List[Tuple[str, str]]) -> str:
        """
        Executa ferramentas detectadas
        
        Args:
            tools_to_use: Lista de ferramentas a executar
            
        Returns:
            String com resultados formatados
        """
        results = []
        
        for tool_name, param in tools_to_use:
            try:
                if tool_name == "viacep":
                    result = self.tools["viacep"].execute(param)
                    formatted = self.tools["viacep"].format_result(result)
                    results.append(formatted)
                    logger.info(f"Ferramenta ViaCEP executada: {param}")
                    
                elif tool_name == "pokemon":
                    result = self.tools["pokemon"].execute(param)
                    formatted = self.tools["pokemon"].format_result(result)
                    results.append(formatted)
                    logger.info(f"Ferramenta Pokémon executada: {param}")
                    
                elif tool_name == "ibge":
                    result = self.tools["ibge"].execute(param)
                    formatted = self.tools["ibge"].format_result(result)
                    results.append(formatted)
                    logger.info(f"Ferramenta IBGE executada: {param}")
                    
            except Exception as e:
                logger.error(f"Erro ao executar ferramenta {tool_name}: {e}")
                results.append(f"Erro ao executar {tool_name}: {str(e)}")
        
        return "\n\n".join(results) if results else ""
    
    def _get_context_from_vectorstore(self, user_message: str) -> str:
        """
        Busca contexto relevante no vector store
        
        Args:
            user_message: Mensagem do usuário
            
        Returns:
            String com contexto relevante
        """
        try:
            # Busca conhecimento relevante
            knowledge = self.vector_store.search_knowledge(user_message, n_results=2)
            
            # Busca conversas similares
            similar_convs = self.vector_store.search_similar_conversations(
                user_message, n_results=1
            )
            
            context_parts = []
            
            if knowledge:
                context_parts.append("Conhecimento relevante:")
                for item in knowledge:
                    if item["similarity"] > 0.5:  # Apenas itens relevantes
                        context_parts.append(f"- {item['content']}")
            
            if similar_convs:
                context_parts.append("\nConversas anteriores similares:")
                for conv in similar_convs:
                    if conv["similarity"] > 0.6:
                        context_parts.append(f"- {conv['content'][:200]}...")
            
            return "\n".join(context_parts) if context_parts else ""
            
        except Exception as e:
            logger.error(f"Erro ao buscar contexto: {e}")
            return ""
    
    def chat(self, user_message: str) -> Dict:
        """
        Processa mensagem do usuário e gera resposta
        
        Args:
            user_message: Mensagem do usuário
            
        Returns:
            Dicionário com resposta e informações adicionais
        """
        try:
            # Detecta ferramentas a usar
            tools_to_use = self._detect_tool_usage(user_message)
            
            # Executa ferramentas se necessário
            tools_output = ""
            if tools_to_use:
                tools_output = self._execute_tools(tools_to_use)
            
            # Busca contexto no vector store
            vector_context = self._get_context_from_vectorstore(user_message)
            
            # Constrói prompt completo
            system_prompt = self.prompt_manager.get_current_prompt()
            
            # Prepara histórico de conversa
            history_text = "\n".join([
                f"{'Usuário' if msg['role'] == 'user' else 'Assistente'}: {msg['content']}"
                for msg in self.chat_history[-5:]  # Últimas 5 mensagens
            ])
            
            # Monta prompt final
            full_prompt = f"""{system_prompt}

{'CONTEXTO DA BASE DE CONHECIMENTO:' + chr(10) + vector_context if vector_context else ''}

{'RESULTADOS DAS FERRAMENTAS:' + chr(10) + tools_output if tools_output else ''}

{'HISTÓRICO RECENTE:' + chr(10) + history_text if history_text else ''}

MENSAGEM DO USUÁRIO:
{user_message}

Responda de forma natural e útil, incorporando as informações das ferramentas se disponíveis:"""
            
            # Gera resposta com Gemini
            response = self.model.generate_content(full_prompt)
            agent_response = response.text
            
            # Adiciona ao histórico
            self.chat_history.append({"role": "user", "content": user_message})
            self.chat_history.append({"role": "assistant", "content": agent_response})
            
            # Salva no vector store
            self.vector_store.add_conversation(
                user_message,
                agent_response,
                metadata={
                    "tools_used": [t[0] for t in tools_to_use],
                    "has_context": bool(vector_context)
                }
            )
            
            logger.info(f"Resposta gerada com sucesso (ferramentas: {len(tools_to_use)})")
            
            return {
                "response": agent_response,
                "tools_used": tools_to_use,
                "has_tools_output": bool(tools_output),
                "tools_output": tools_output,
                "has_context": bool(vector_context)
            }
            
        except Exception as e:
            logger.error(f"Erro ao processar mensagem: {e}")
            error_response = f"Desculpe, ocorreu um erro ao processar sua mensagem: {str(e)}"
            
            return {
                "response": error_response,
                "tools_used": [],
                "has_tools_output": False,
                "tools_output": "",
                "has_context": False,
                "error": str(e)
            }
    
    def clear_history(self):
        """Limpa histórico da conversa atual"""
        self.chat_history = []
        logger.info("Histórico de conversa limpo")
    
    def get_history(self) -> List[Dict[str, str]]:
        """Retorna histórico da conversa"""
        return self.chat_history.copy()
    
    def get_statistics(self) -> Dict:
        """Retorna estatísticas do chatbot"""
        user_messages = [msg for msg in self.chat_history if msg["role"] == "user"]
    
        return {
            "messages_count": len(user_messages),  # Agora conta só perguntas do usuário
            "prompt_version": self.prompt_manager.get_current_version(),
            "vector_store": self.vector_store.get_statistics()
        }
