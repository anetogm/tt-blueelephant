"""
Interface Streamlit para o Chatbot com IA e Sistema de Feedback
"""

import streamlit as st
import logging
import os
from datetime import datetime
from pathlib import Path

from src.agent import Chatbot, PromptManager, ConversationManager
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

def initialize_session():
    """Inicializa ou recupera estado da sessão"""
    if "initialized" not in st.session_state:
        # Carrega variáveis de ambiente
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            st.error("GEMINI_API_KEY não encontrada!")
            st.stop()
        
        # Inicializa componentes
        st.session_state.chatbot = Chatbot(api_key)
        st.session_state.feedback_processor = FeedbackProcessor(api_key)
        st.session_state.prompt_manager = st.session_state.chatbot.prompt_manager
        st.session_state.conversation_manager = ConversationManager()
        
        # Inicia uma NOVA sessão (não carrega mensagens antigas)
        st.session_state.conversation_manager.start_new_session()
        st.session_state.messages = []  # Começa vazio
        st.session_state.feedback_history = []
        st.session_state.initialized = True
        
        logger.info("Nova sessão inicializada")


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
            st.session_state.conversation_manager.clear_current_session()
            st.session_state.messages = []
            
            st.success("Conversa limpa! Nova sessão iniciada.")
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
        st.session_state.conversation_manager.add_message("user", user_input)
        
        # Processa com o chatbot
        with st.spinner("Pensando..."):
            response_data = st.session_state.chatbot.chat(user_input)
        
        # Extrai dados da resposta
        response = response_data.get("response", "")
        tools_used = response_data.get("tools_used", [])
        tools_output = response_data.get("tools_output", "")
        
        # Adiciona resposta do assistente
        st.session_state.messages.append({
            "role": "assistant",
            "content": response,
            "timestamp": datetime.now().isoformat(),
            "tools_used": tools_used,
            "tools_output": tools_output
        })
        st.session_state.conversation_manager.add_message(
            "assistant", response, tools_used, tools_output
        )
        
        st.rerun()


def render_feedback_area():
    """Renderiza área de feedback e melhorias"""
    st.markdown('<div class="main-header">Feedback e Melhorias</div>', 
                unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Ajude a melhorar o assistente com seu feedback</div>', 
                unsafe_allow_html=True)
    
    # Tabs para organizar conteúdo
    tab1, tab2, tab3, tab4 = st.tabs(["Dar Feedback", "Histórico Feedbacks", "Histórico Conversas", "Prompt Atual"])
    
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
        st.markdown("### Histórico de Conversas")
        
        st.info("Todas as conversas são salvas automaticamente no histórico.")
        
        # Carrega todas as sessões do histórico
        all_sessions = st.session_state.conversation_manager.get_all_sessions()
        
        if not all_sessions:
            st.info("Nenhuma conversa no histórico ainda. Comece a conversar e suas mensagens serão salvas automaticamente!")
        else:
            # Estatísticas
            stats = st.session_state.conversation_manager.get_statistics()
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total de Sessões", stats["total_sessions"])
            with col2:
                st.metric("Total de Mensagens", stats["total_messages"])
            
            st.markdown("---")
            
            # Opção de limpar o histórico
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown("**Sessões Anteriores:**")
            with col2:
                if st.button("Limpar Histórico", use_container_width=True):
                    st.session_state.conversation_manager.clear_all_history()
                    st.success("Histórico limpo!")
                    st.rerun()
            
            # Mostra cada sessão (mais recentes primeiro)
            for idx, session in enumerate(reversed(all_sessions)):
                session_num = len(all_sessions) - idx
                started = session["started_at"][:19].replace("T", " ")
                msg_count = session["message_count"]
                
                # Identifica ferramentas usadas nesta sessão
                tools_in_session = set()
                for msg in session["messages"]:
                    if msg["role"] == "assistant" and msg.get("tools_used"):
                        for tool_name, _ in msg["tools_used"]:
                            tools_in_session.add(tool_name)
                
                tools_str = f" - {', '.join(tools_in_session)}" if tools_in_session else ""
                
                with st.expander(
                    f"Sessão #{session_num} - {msg_count} mensagens{tools_str} - {started}",
                    expanded=False
                ):
                    # Mostra conversas da sessão
                    messages = session["messages"]
                    
                    for i in range(0, len(messages), 2):
                        if i + 1 < len(messages):
                            user_msg = messages[i]
                            assistant_msg = messages[i + 1]
                            
                            # Pergunta
                            st.markdown("**Você:**")
                            st.info(user_msg["content"])
                            
                            # Resposta
                            st.markdown("**Assistente:**")
                            st.success(assistant_msg["content"])
                            
                            # Ferramentas usadas
                            if assistant_msg.get("tools_used"):
                                with st.expander("Ferramentas utilizadas"):
                                    for tool_name, tool_params in assistant_msg["tools_used"]:
                                        st.markdown(f"- **{tool_name}**: `{tool_params}`")
                                    
                                    if assistant_msg.get("tools_output"):
                                        st.markdown("---")
                                        st.markdown(assistant_msg["tools_output"])
                            
                            if i + 2 < len(messages):
                                st.markdown("---")
                    
                    # Botão para deletar esta sessão
                    st.markdown("---")
                    if st.button(f"Deletar Sessão #{session_num}", key=f"del_{session['session_id']}"):
                        st.session_state.conversation_manager.delete_session(session["session_id"])
                        st.success(f"Sessão #{session_num} removida!")
                        st.rerun()
    
    with tab4:
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
    initialize_session()
    
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
