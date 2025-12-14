"""
Chatbot principal com integração de LLM, ferramentas e vector store
"""

import logging
from typing import List, Dict, Optional
import google.generativeai as genai
from google.generativeai.types import content_types

from ..tools import ViaCEPTool, PokemonTool, IBGETool, OpenMeteoTool, TVMazeTool
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
        
        # Inicializa ferramentas
        self.tools_instances = {
            "viacep": ViaCEPTool(),
            "pokemon": PokemonTool(),
            "ibge": IBGETool(),
            "clima": OpenMeteoTool(),
            "serie": TVMazeTool()
        }
        
        # Define funções para o Gemini (formato correto)
        self.tools = [
            genai.protos.FunctionDeclaration(
                name="consultar_cep",
                description="Consulta informações de endereço a partir de um CEP brasileiro. Use quando o usuário mencionar CEP, endereço, ou fornecer um código postal de 8 dígitos.",
                parameters=genai.protos.Schema(
                    type=genai.protos.Type.OBJECT,
                    properties={
                        "cep": genai.protos.Schema(
                            type=genai.protos.Type.STRING,
                            description="CEP brasileiro com 8 dígitos (pode ter hífen ou não). Exemplo: 01310-100 ou 01310100"
                        )
                    },
                    required=["cep"]
                )
            ),
            genai.protos.FunctionDeclaration(
                name="consultar_pokemon",
                description="Consulta informações sobre um Pokémon específico da PokéAPI. Use quando o usuário perguntar sobre Pokémon, mencionar nomes de Pokémon ou números da Pokédex.",
                parameters=genai.protos.Schema(
                    type=genai.protos.Type.OBJECT,
                    properties={
                        "identificador": genai.protos.Schema(
                            type=genai.protos.Type.STRING,
                            description="Nome do Pokémon (em inglês minúsculo, ex: 'pikachu') ou número da Pokédex (ex: '25')"
                        )
                    },
                    required=["identificador"]
                )
            ),
            genai.protos.FunctionDeclaration(
                name="consultar_ibge",
                description="Consulta informações geográficas do Brasil via IBGE. Use quando o usuário perguntar sobre estados brasileiros, municípios, cidades, regiões ou siglas de UF.",
                parameters=genai.protos.Schema(
                    type=genai.protos.Type.OBJECT,
                    properties={
                        "consulta": genai.protos.Schema(
                            type=genai.protos.Type.STRING,
                            description="Nome do estado (ex: 'São Paulo' ou 'SP'), município (ex: 'Campinas') ou sigla da UF (ex: 'RJ')"
                        )
                    },
                    required=["consulta"]
                )
            ),
            genai.protos.FunctionDeclaration(
                name="consultar_clima",
                description="Consulta informações de clima atual e previsão do tempo. Use quando o usuário perguntar sobre clima, tempo, temperatura, previsão meteorológica.",
                parameters=genai.protos.Schema(
                    type=genai.protos.Type.OBJECT,
                    properties={
                        "local": genai.protos.Schema(
                            type=genai.protos.Type.STRING,
                            description="Nome da cidade ou localização (ex: 'São Paulo', 'New York', 'Tokyo', 'Paris')"
                        )
                    },
                    required=["local"]
                )
            ),
            genai.protos.FunctionDeclaration(
                name="consultar_serie",
                description="Consulta informações sobre séries de TV. Use quando o usuário perguntar sobre séries, programas de TV, shows.",
                parameters=genai.protos.Schema(
                    type=genai.protos.Type.OBJECT,
                    properties={
                        "nome": genai.protos.Schema(
                            type=genai.protos.Type.STRING,
                            description="Nome da série de TV (ex: 'Breaking Bad', 'Game of Thrones', 'The Office', 'Stranger Things')"
                        )
                    },
                    required=["nome"]
                )
            )
        ]
        
        # Inicializa modelo com function calling
        self.model = genai.GenerativeModel(
            'gemini-2.5-flash',
            tools=self.tools
        )
        
        # Inicializa componentes
        self.prompt_manager = PromptManager(data_dir)
        self.vector_store = ChromaVectorStore(f"{data_dir}/chroma")
        
        # Histórico da conversa atual
        self.chat_history: List[Dict[str, str]] = []
        
        logger.info("Chatbot inicializado com function calling")
    
    def _execute_function_call(self, function_name: str, function_args: Dict) -> str:
        """
        Executa uma função chamada pelo modelo
        
        Args:
            function_name: Nome da função a executar
            function_args: Argumentos da função
            
        Returns:
            String com resultado formatado
        """
        try:
            if function_name == "consultar_cep":
                cep = function_args.get("cep", "")
                result = self.tools_instances["viacep"].execute(cep)
                formatted = self.tools_instances["viacep"].format_result(result)
                logger.info(f"Function calling: ViaCEP executada para {cep}")
                return formatted
                
            elif function_name == "consultar_pokemon":
                identificador = function_args.get("identificador", "")
                result = self.tools_instances["pokemon"].execute(identificador)
                formatted = self.tools_instances["pokemon"].format_result(result)
                logger.info(f"Function calling: Pokemon executada para {identificador}")
                return formatted
                
            elif function_name == "consultar_ibge":
                consulta = function_args.get("consulta", "")
                result = self.tools_instances["ibge"].execute(consulta)
                formatted = self.tools_instances["ibge"].format_result(result)
                logger.info(f"Function calling: IBGE executada para {consulta}")
                return formatted
            
            elif function_name == "consultar_clima":
                local = function_args.get("local", "")
                result = self.tools_instances["clima"].execute(local)
                formatted = self.tools_instances["clima"].format_result(result)
                logger.info(f"Function calling: Clima executada para {local}")
                return formatted
            
            elif function_name == "consultar_serie":
                nome = function_args.get("nome", "")
                result = self.tools_instances["serie"].execute(nome)
                formatted = self.tools_instances["serie"].format_result(result)
                logger.info(f"Function calling: Série executada para {nome}")
                return formatted
            
            else:
                logger.warning(f"Função desconhecida: {function_name}")
                return f"Função '{function_name}' não reconhecida"
                
        except Exception as e:
            logger.error(f"Erro ao executar função {function_name}: {e}")
            return f"Erro ao executar {function_name}: {str(e)}"
    
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
                    if item["similarity"] > 0.5:
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
        Processa mensagem do usuário e gera resposta usando function calling
        
        Args:
            user_message: Mensagem do usuário
            
        Returns:
            Dicionário com resposta e informações adicionais
        """
        try:
            # Busca contexto no vector store
            vector_context = self._get_context_from_vectorstore(user_message)
            
            # Constrói prompt completo
            system_prompt = self.prompt_manager.get_current_prompt()
            
            # Prepara histórico de conversa
            history_text = "\n".join([
                f"{'Usuário' if msg['role'] == 'user' else 'Assistente'}: {msg['content']}"
                for msg in self.chat_history[-5:]
            ])
            
            # Monta prompt com contexto
            full_message = f"""{system_prompt}

{f'CONTEXTO DA BASE DE CONHECIMENTO:{chr(10)}{vector_context}' if vector_context else ''}

{f'HISTÓRICO RECENTE:{chr(10)}{history_text}' if history_text else ''}

MENSAGEM DO USUÁRIO:
{user_message}"""
            
            # Primeira chamada ao modelo (pode retornar function calls)
            response = self.model.generate_content(full_message)
            
            # Verifica se há function calls
            tools_used = []
            tools_output = ""
            
            if response.candidates and response.candidates[0].content.parts:
                for part in response.candidates[0].content.parts:
                    # Se há function call
                    if hasattr(part, 'function_call') and part.function_call:
                        function_call = part.function_call
                        function_name = function_call.name
                        function_args = dict(function_call.args)
                        
                        logger.info(f"Model solicitou function call: {function_name} com args {function_args}")
                        
                        # Executa a função
                        function_result = self._execute_function_call(function_name, function_args)
                        tools_output += function_result + "\n\n"
                        tools_used.append((function_name, str(function_args)))
            
            # Se houve function calls, faz segunda chamada com os resultados
            if tools_used:
                # Constrói mensagem com resultados das ferramentas
                second_prompt = f"""{full_message}

RESULTADOS DAS FERRAMENTAS:
{tools_output}

Agora responda ao usuário de forma natural, incorporando essas informações:"""
                
                # Segunda chamada ao modelo sem function calling
                model_no_tools = genai.GenerativeModel('gemini-2.5-flash')
                final_response = model_no_tools.generate_content(second_prompt)
                agent_response = final_response.text
            else:
                # Não houve function calls, usa resposta direta
                agent_response = response.text if hasattr(response, 'text') else "Desculpe, não consegui processar sua mensagem."
            
            # Adiciona ao histórico
            self.chat_history.append({"role": "user", "content": user_message})
            self.chat_history.append({"role": "assistant", "content": agent_response})
            
            # Salva no vector store
            self.vector_store.add_conversation(
                user_message,
                agent_response,
                metadata={
                    "tools_used": [t[0] for t in tools_used],
                    "has_context": bool(vector_context)
                }
            )
            
            logger.info(f"Resposta gerada com sucesso (function calls: {len(tools_used)})")
            
            return {
                "response": agent_response,
                "tools_used": tools_used,
                "has_tools_output": bool(tools_output),
                "tools_output": tools_output.strip(),
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
            "messages_count": len(user_messages),
            "prompt_version": self.prompt_manager.get_current_version(),
            "vector_store": self.vector_store.get_statistics()
        }