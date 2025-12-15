"""
Interface Streamlit para o Chatbot com IA e Sistema de Feedback
"""

import streamlit as st
import logging
import os
from datetime import datetime
from pathlib import Path

from src.agent import Chatbot, PromptManager
from src.feedback import FeedbackProcessor

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/app.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Configuração da página
st.set_page_config(
    page_title="Chatbot com Feedback Inteligente",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        text-align: center;
        margin-bottom: 2rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        color: #000000;  /* Texto preto */
    }
    .user-message {
        background-color: #E3F2FD;
        border-left: 4px solid #1E88E5;
    }
    .user-message strong {
        color: #1565C0;  /* Azul escuro para "Você:" */
    }
    .assistant-message {
        background-color: #E8F5E9;  /* Verde claro em vez de cinza */
        border-left: 4px solid #4CAF50;
    }
    .assistant-message strong {
        color: #2E7D32;  /* Verde escuro para "Assistente:" */
    }
    .tool-output {
        background-color: #FFF3E0;
        border-left: 4px solid #FF9800;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
        color: #000000;  /* Texto preto */
    }
    .tool-output strong {
        color: #E65100;  /* Laranja escuro para "Ferramentas:" */
    }
    .stats-box {
        background-color: #F8F9FA;
        padding: 1rem;
        border-radius: 0.5rem;
        border: 1px solid #DEE2E6;
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Inicializa estado da sessão"""
    if 'initialized' not in st.session_state:
        # Verifica API key
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            st.error("GEMINI_API_KEY não configurada! Configure a variável de ambiente.")
            st.stop()
        
        # Inicializa componentes
        st.session_state.chatbot = Chatbot(api_key)
        st.session_state.feedback_processor = FeedbackProcessor(api_key)
        st.session_state.prompt_manager = st.session_state.chatbot.prompt_manager
        
        # Estado da interface
        st.session_state.messages = []
        st.session_state.feedback_history = []
        st.session_state.initialized = True
        
        logger.info("Sessão inicializada")


def render_sidebar():
    """Renderiza barra lateral com informações e controles"""
    with st.sidebar:
        st.markdown("### Informações do Sistema")
        
        # Estatísticas
        stats = st.session_state.chatbot.get_statistics()
        prompt_stats = st.session_state.prompt_manager.get_statistics()
        feedback_stats = st.session_state.feedback_processor.get_statistics()
        
        st.markdown("#### Estatísticas")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Mensagens", stats["messages_count"])
            st.metric("Versão Prompt", prompt_stats["current_version"])
        with col2:
            st.metric("Feedbacks", feedback_stats["total_feedbacks"])
            st.metric("Avaliação Média", f"{feedback_stats['average_rating']:.1f}/5")
        
        st.markdown("---")
        
        # Controles
        st.markdown("#### Controles")
        
        if st.button("Limpar Conversa", use_container_width=True):
            st.session_state.chatbot.clear_history()
            st.session_state.messages = []
            st.success("Conversa limpa!")
            st.rerun()
        
        if st.button("Atualizar Estatísticas", use_container_width=True):
            st.rerun()
        
        st.markdown("---")
        
        # Ferramentas disponíveis
        st.markdown("#### Ferramentas Disponíveis")
        st.markdown("""
        - **ViaCEP**: Consulta de CEPs brasileiros
        - **PokéAPI**: Informações sobre Pokémon
        - **IBGE**: Dados de estados e municípios do Brasil
        - **Open-Meteo**: Clima atual e previsão do tempo
        - **Open Library**: Informações sobre livros e autores
        - **TVMaze**: Informações sobre séries de TV
        - **Lyrics.ovh**: Letras de músicas
        """)
        
        st.markdown("---")
        st.markdown("#### Sobre")
        st.markdown("""
        Sistema de chatbot com IA desenvolvido com:
        - **LLM**: Google Gemini
        - **Vector Store**: ChromaDB
        - **Interface**: Streamlit
        - **APIs**: ViaCEP, PokéAPI, IBGE, Open-Meteo, Open Library, TVMaze, Lyrics.ovh
        """)


def render_chat_area():
    """Renderiza área principal do chat"""
    st.markdown('<div class="main-header">Chat com Agente IA</div>', 
                unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Converse com o assistente virtual inteligente</div>', 
                unsafe_allow_html=True)
    
    # Container para mensagens
    chat_container = st.container()
    
    # Exibe histórico
    with chat_container:
        for i, msg in enumerate(st.session_state.messages):
            if msg["role"] == "user":
                st.markdown(f"""
                <div class="chat-message user-message">
                    <strong>Você:</strong><br>
                    {msg["content"]}
                </div>
                """, unsafe_allow_html=True)
            else:
                # Mostra resposta do assistente
                st.markdown(f"""
                <div class="chat-message assistant-message">
                    <strong>Assistente:</strong><br>
                    {msg["content"]}
                </div>
                """, unsafe_allow_html=True)
                
                # Se houver ferramentas usadas, mostra em expander
                if msg.get("tools_output"):
                    tools_used_names = [tool[0] for tool in msg.get("tools_used", [])]
                    tools_label = ", ".join(tools_used_names) if tools_used_names else "Ferramentas"
                    
                    with st.expander(f"Ver detalhes da ferramenta: {tools_label}", expanded=False):
                        st.markdown(msg["tools_output"])
    
    # Input do usuário
    st.markdown("---")
    user_input = st.chat_input("Digite sua mensagem aqui...")
    
    if user_input:
        # Adiciona mensagem do usuário
        st.session_state.messages.append({
            "role": "user",
            "content": user_input,
            "timestamp": datetime.now().isoformat()
        })
        
        # Processa com o chatbot
        with st.spinner("Pensando..."):
            response_data = st.session_state.chatbot.chat(user_input)
        
        # Adiciona resposta do assistente
        st.session_state.messages.append({
            "role": "assistant",
            "content": response_data["response"],
            "tools_output": response_data.get("tools_output", ""),
            "tools_used": response_data.get("tools_used", []),
            "timestamp": datetime.now().isoformat()
        })
        
        st.rerun()


def render_feedback_area():
    """Renderiza área de feedback e melhorias"""
    st.markdown('<div class="main-header">Feedback e Melhorias</div>', 
                unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Ajude a melhorar o assistente com seu feedback</div>', 
                unsafe_allow_html=True)
    
    # Tabs para organizar conteúdo
    tab1, tab2, tab3 = st.tabs(["Dar Feedback", "Histórico", "Prompt Atual"])
    
    with tab1:
        st.markdown("### Enviar Feedback")
        
        if len(st.session_state.messages) < 2:
            st.info("Converse com o assistente primeiro para poder dar feedback!")
        else:
            # Seleção da mensagem para feedback
            recent_messages = [
                msg for msg in st.session_state.messages 
                if msg["role"] == "assistant"
            ][-5:]
            
            if recent_messages:
                st.markdown("**Selecione a resposta sobre a qual deseja dar feedback:**")
                
                selected_idx = st.selectbox(
                    "Escolha uma resposta:",
                    range(len(recent_messages)),
                    format_func=lambda i: f"Resposta {len(recent_messages)-i}: {recent_messages[-(i+1)]['content'][:50]}...",
                    key="feedback_select"
                )
                
                selected_msg = recent_messages[-(selected_idx+1)]
                
                # Encontra mensagem do usuário correspondente
                msg_idx = st.session_state.messages.index(selected_msg)
                user_msg = st.session_state.messages[msg_idx - 1] if msg_idx > 0 else None
                
                # Exibe contexto
                if user_msg:
                    st.markdown("**Contexto:**")
                    st.info(f"**Você perguntou:** {user_msg['content']}")
                    st.success(f"**Assistente respondeu:** {selected_msg['content'][:200]}...")
                
                with st.form("feedback_form"):
                    st.markdown("**Avalie a resposta:**")
                    rating = st.slider("Avaliação", 1, 5, 3, 
                                     help="1 = Muito ruim, 5 = Excelente")
                    
                    feedback_text = st.text_area(
                        "Seu feedback (o que pode melhorar?):",
                        placeholder="Exemplo: A resposta foi muito genérica, poderia ser mais específica...",
                        height=100
                    )
                    
                    submit = st.form_submit_button("Enviar Feedback", 
                                                  use_container_width=True,
                                                  type="primary")
                
                # Processa feedback fora do form
                if submit:
                    if not feedback_text.strip():
                        st.error("Por favor, escreva seu feedback!")
                    else:
                        # Registra feedback
                        feedback_data = st.session_state.feedback_processor.add_feedback(
                            user_message=user_msg["content"] if user_msg else "",
                            agent_response=selected_msg["content"],
                            feedback_text=feedback_text,
                            rating=rating
                        )
                        
                        st.session_state.feedback_history.append(feedback_data)
                        st.session_state.prompt_manager.increment_feedback_count()
                        
                        st.success("Feedback enviado com sucesso!")
                        
                        if feedback_data.get("auto_process", False):
                            with st.spinner("Processando feedbacks automaticamente..."):
                                current_prompt = st.session_state.prompt_manager.get_current_prompt()
                                new_prompt, improvements = st.session_state.feedback_processor.analyze_feedbacks(
                                    current_prompt,
                                    recent_count=3
                                )
                                
                                if new_prompt != current_prompt:
                                    new_version = st.session_state.prompt_manager.update_prompt(
                                        new_prompt,
                                        improvements
                                    )
                                    
                                    st.session_state.last_update_result = {
                                        'success': True,
                                        'version': new_version,
                                        'improvements': improvements,
                                        'auto': True
                                    }
                        
                        st.rerun()

                # Mostra resultado do processamento automático
                if 'last_update_result' in st.session_state:
                    result = st.session_state.last_update_result
                    
                    if result.get('success'):
                        auto_text = " (automático)" if result.get('auto') else ""
                        st.success(f"Prompt atualizado para versão {result['version']}{auto_text}!")
                        
                        with st.expander("Ver melhorias aplicadas", expanded=True):
                            for imp in result.get('improvements', []):
                                st.markdown(f"- {imp}")
                    else:
                        st.info(result.get('message', 'Processamento concluído'))
                    
                    # Limpa resultado após mostrar
                    del st.session_state.last_update_result
    with tab2:
        st.markdown("### Histórico de Feedbacks")
        
        feedback_stats = st.session_state.feedback_processor.get_statistics()
        
        if not st.session_state.feedback_processor.feedbacks:
            st.info("Nenhum feedback registrado ainda.")
        else:
            # Estatísticas
            st.markdown(f"**Total de feedbacks:** {feedback_stats['total_feedbacks']}")
            st.markdown(f"**Avaliação média:** {feedback_stats['average_rating']:.1f}/5")
            
            # Controle de quantidade a exibir
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown("---")
            with col2:
                show_all = st.checkbox("Mostrar todos", value=False)
            
            # Determina quantos mostrar
            if show_all:
                recent_feedbacks = st.session_state.feedback_processor.feedbacks
            else:
                recent_feedbacks = st.session_state.feedback_processor.get_recent_feedbacks(10)
            
            # Mostra feedbacks (mais recentes primeiro)
            for fb in reversed(recent_feedbacks):
                with st.expander(
                    f"Feedback #{fb['id']} - "
                    f"{'⭐' * fb['rating']} ({fb['rating']}/5) - "
                    f"{'Processado' if fb.get('processed') else '⏳ Pendente'}"
                ):
                    st.markdown(f"**Data:** {fb['timestamp']}")
                    st.markdown(f"**Usuário perguntou:** {fb['user_message']}")
                    st.markdown(f"**Agente respondeu:** {fb['agent_response'][:200]}...")
                    st.markdown(f"**Feedback:** {fb['feedback_text']}")
        
    with tab3:
        st.markdown("### Prompt Atual do Sistema")
        
        prompt_stats = st.session_state.prompt_manager.get_statistics()
        current_prompt = st.session_state.prompt_manager.get_current_prompt()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Versão Atual", prompt_stats["current_version"])
        with col2:
            st.metric("Total de Versões", prompt_stats["total_versions"])
        with col3:
            st.metric("Feedbacks Recebidos", prompt_stats["total_feedbacks"])
        
        st.markdown("---")
        st.markdown("#### Prompt em Uso:")
        st.code(current_prompt, language="markdown")
        
        st.markdown("---")
        st.markdown("#### Histórico de Versões:")
        
        history = st.session_state.prompt_manager.get_history()
        for prompt_data in reversed(history):
            with st.expander(
                f"Versão {prompt_data['version']} - "
                f"{prompt_data['timestamp'][:10]} - "
                f"{prompt_data['feedback_count']} feedbacks"
            ):
                st.markdown("**Melhorias aplicadas:**")
                for imp in prompt_data.get("improvements", []):
                    st.markdown(f"- {imp}")
                
                st.markdown("**Prompt:**")
                st.code(prompt_data["prompt"], language="markdown")


def main():
    """Função principal da aplicação"""
    # Inicializa sessão
    initialize_session_state()
    
    # Renderiza sidebar
    render_sidebar()
    
    # Layout principal com duas colunas
    col1, col2 = st.columns([1.2, 1])
    
    with col1:
        render_chat_area()
    
    with col2:
        render_feedback_area()


if __name__ == "__main__":
    main()
