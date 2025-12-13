"""
Processador de Feedback Inteligente
Analisa feedbacks e gera melhorias automáticas para o prompt
"""

import logging
from typing import List, Dict, Tuple
import google.generativeai as genai
from datetime import datetime
import json
from pathlib import Path

logger = logging.getLogger(__name__)


class FeedbackProcessor:
    """Processa feedbacks e gera melhorias inteligentes para prompts"""
    
    def __init__(self, api_key: str, data_dir: str = "data"):
        """
        Inicializa o processador de feedback
        
        Args:
            api_key: Chave da API Gemini
            data_dir: Diretório para armazenar feedbacks
        """
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.feedbacks_file = self.data_dir / "feedbacks.json"
        self.feedbacks: List[Dict] = []
        self._load_feedbacks()
    
    def _load_feedbacks(self):
        """Carrega histórico de feedbacks"""
        try:
            if self.feedbacks_file.exists():
                with open(self.feedbacks_file, 'r', encoding='utf-8') as f:
                    self.feedbacks = json.load(f)
                logger.info(f"Carregados {len(self.feedbacks)} feedbacks")
        except Exception as e:
            logger.error(f"Erro ao carregar feedbacks: {e}")
            self.feedbacks = []
    
    def _save_feedbacks(self):
        """Salva feedbacks no arquivo"""
        try:
            with open(self.feedbacks_file, 'w', encoding='utf-8') as f:
                json.dump(self.feedbacks, f, ensure_ascii=False, indent=2)
            logger.info("Feedbacks salvos com sucesso")
        except Exception as e:
            logger.error(f"Erro ao salvar feedbacks: {e}")
    
    def add_feedback(self, user_message: str, agent_response: str, 
                    feedback_text: str, rating: int = 3) -> Dict:
        """
        Adiciona um novo feedback ao sistema
        
        Args:
            user_message: Mensagem do usuário
            agent_response: Resposta do agente
            feedback_text: Texto do feedback
            rating: Avaliação de 1-5 (opcional)
            
        Returns:
            Dicionário com o feedback registrado
        """
        feedback = {
            "id": len(self.feedbacks) + 1,
            "timestamp": datetime.now().isoformat(),
            "user_message": user_message,
            "agent_response": agent_response,
            "feedback_text": feedback_text,
            "rating": rating,
            "processed": False
        }
        
        self.feedbacks.append(feedback)
        self._save_feedbacks()
        
        logger.info(f"Feedback #{feedback['id']} adicionado")
        return feedback
    
    def get_recent_feedbacks(self, limit: int = 10) -> List[Dict]:
        """
        Retorna feedbacks recentes
        
        Args:
            limit: Número máximo de feedbacks a retornar
            
        Returns:
            Lista de feedbacks
        """
        return self.feedbacks[-limit:] if self.feedbacks else []
    
    def analyze_feedbacks(self, current_prompt: str, 
                         recent_count: int = 5) -> Tuple[str, List[str]]:
        """
        Analisa feedbacks recentes e gera prompt melhorado
        
        Args:
            current_prompt: Prompt atual do agente
            recent_count: Número de feedbacks recentes a considerar
            
        Returns:
            Tupla (novo_prompt, lista_de_melhorias)
        """
        if not self.feedbacks:
            logger.warning("Nenhum feedback disponível para análise")
            return current_prompt, ["Nenhuma melhoria aplicada - sem feedbacks"]
        
        # Pega feedbacks recentes não processados
        recent_feedbacks = [f for f in self.feedbacks[-recent_count:] 
                          if not f.get("processed", False)]
        
        if not recent_feedbacks:
            logger.info("Todos os feedbacks recentes já foram processados")
            return current_prompt, ["Feedbacks já processados anteriormente"]
        
        # Prepara contexto para análise
        feedbacks_text = "\n\n".join([
            f"Feedback {f['id']}:\n"
            f"Usuário disse: {f['user_message']}\n"
            f"Agente respondeu: {f['agent_response']}\n"
            f"Feedback: {f['feedback_text']}\n"
            f"Avaliação: {f['rating']}/5"
            for f in recent_feedbacks
        ])
        
        # Prompt para o modelo analisar e melhorar
        analysis_prompt = f"""Você é um especialista em melhorar prompts de sistemas de IA.

Analise os feedbacks abaixo sobre as respostas de um assistente virtual e sugira melhorias específicas para o prompt do sistema.

PROMPT ATUAL:
{current_prompt}

FEEDBACKS RECEBIDOS:
{feedbacks_text}

Sua tarefa:
1. Identifique padrões e problemas nos feedbacks
2. Sugira melhorias específicas e acionáveis
3. Reescreva o prompt incorporando essas melhorias
4. Mantenha a estrutura e funcionalidades existentes
5. Seja específico sobre o que mudou

Forneça sua resposta no seguinte formato:

MELHORIAS APLICADAS:
- [Lista de melhorias específicas, uma por linha]

NOVO PROMPT:
[O prompt reescrito e melhorado]
"""
        
        try:
            # Gera análise usando Gemini
            response = self.model.generate_content(analysis_prompt)
            result_text = response.text
            
            # Parseia a resposta
            improvements, new_prompt = self._parse_analysis_response(result_text)
            
            # Marca feedbacks como processados
            for f in recent_feedbacks:
                f["processed"] = True
            self._save_feedbacks()
            
            logger.info(f"Análise concluída: {len(improvements)} melhorias identificadas")
            return new_prompt, improvements
            
        except Exception as e:
            logger.error(f"Erro ao analisar feedbacks: {e}")
            return current_prompt, [f"Erro na análise: {str(e)}"]
    
    def _parse_analysis_response(self, response_text: str) -> Tuple[List[str], str]:
        """
        Parseia a resposta do modelo de análise
        
        Args:
            response_text: Texto da resposta do modelo
            
        Returns:
            Tupla (lista_de_melhorias, novo_prompt)
        """
        improvements = []
        new_prompt = ""
        
        try:
            # Separa melhorias e novo prompt
            if "MELHORIAS APLICADAS:" in response_text and "NOVO PROMPT:" in response_text:
                parts = response_text.split("NOVO PROMPT:")
                improvements_section = parts[0].split("MELHORIAS APLICADAS:")[1].strip()
                new_prompt = parts[1].strip()
                
                # Extrai lista de melhorias
                for line in improvements_section.split('\n'):
                    line = line.strip()
                    if line and (line.startswith('-') or line.startswith('•')):
                        improvements.append(line.lstrip('-•').strip())
            else:
                # Fallback se formato não for seguido
                improvements = ["Análise automática de feedbacks aplicada"]
                new_prompt = response_text
                
        except Exception as e:
            logger.error(f"Erro ao parsear resposta: {e}")
            improvements = ["Erro ao processar melhorias"]
            new_prompt = response_text
        
        return improvements, new_prompt
    
    def get_statistics(self) -> Dict:
        """
        Retorna estatísticas sobre feedbacks
        
        Returns:
            Dicionário com estatísticas
        """
        total = len(self.feedbacks)
        processed = sum(1 for f in self.feedbacks if f.get("processed", False))
        
        if total > 0:
            avg_rating = sum(f.get("rating", 3) for f in self.feedbacks) / total
        else:
            avg_rating = 0
        
        return {
            "total_feedbacks": total,
            "processed_feedbacks": processed,
            "pending_feedbacks": total - processed,
            "average_rating": round(avg_rating, 2)
        }
