# 🤖 Chatbot IA com Feedback Inteligente

Sistema de chatbot com inteligência artificial que inclui funcionalidades de feedback em tempo real para melhorias contínuas do prompt. Desenvolvido como teste técnico para vaga de estágio em desenvolvimento.

## 📋 Descrição

Este projeto implementa um assistente virtual inteligente que:

- Conversa naturalmente com usuários usando IA (Google Gemini)
- Utiliza ferramentas externas (APIs) para fornecer informações específicas
- Aprende e melhora continuamente através de feedbacks dos usuários
- Armazena contexto em vector store para respostas mais relevantes

## ✨ Funcionalidades Principais

### 🗣️ Chat Interativo

- Interface de chat moderna e responsiva
- Histórico de mensagens persistente
- Respostas contextualizadas usando vector store (ChromaDB)
- Integração automática com ferramentas externas

### 🛠️ Ferramentas Integradas

1. **ViaCEP** - Consulta de CEPs brasileiros

   - Retorna endereço completo a partir do CEP
   - Informações: logradouro, bairro, cidade, UF, DDD

2. **PokéAPI** - Informações sobre Pokémon
   - Consulta por nome ou número da Pokédex
   - Dados: tipos, habilidades, estatísticas, altura, peso

### 📝 Sistema de Feedback Inteligente

- Captura feedback do usuário sobre respostas do agente
- Análise automática de feedbacks usando IA
- Atualização dinâmica do prompt do sistema
- Histórico completo de versões de prompt
- Visualização de melhorias aplicadas

### 💾 Vector Store

- Armazenamento de contexto usando ChromaDB
- Busca semântica de conversas anteriores
- Base de conhecimento sobre capacidades do sistema
- Recuperação de informações relevantes para contexto

## 🏗️ Arquitetura do Projeto

```
tt-blueelephant/
├── src/
│   ├── agent/
│   │   ├── chatbot.py           # Agente principal com LLM
│   │   └── prompt_manager.py    # Gerenciador de prompts
│   ├── feedback/
│   │   └── feedback_processor.py # Processador inteligente de feedback
│   ├── tools/
│   │   ├── viacep_tool.py       # Ferramenta ViaCEP
│   │   └── pokemon_tool.py      # Ferramenta PokéAPI
│   └── vectorstore/
│       └── chroma_store.py      # Vector store ChromaDB
├── data/                         # Dados persistentes (criado automaticamente)
├── tests/                        # Testes unitários
├── app.py                        # Aplicação Streamlit
├── requirements.txt              # Dependências Python
├── Dockerfile                    # Container Docker
├── docker-compose.yml            # Orquestração Docker
├── .env.example                  # Exemplo de variáveis de ambiente
└── README.md                     # Este arquivo
```

## 🚀 Instalação e Execução

### Pré-requisitos

- Python 3.9+ ou Docker
- Chave de API do Google Gemini ([obter aqui](https://makersuite.google.com/app/apikey))

### Opção 1: Execução Local com Python

1. **Clone o repositório**

```bash
git clone https://github.com/seu-usuario/tt-blueelephant.git
cd tt-blueelephant
```

2. **Crie um ambiente virtual**

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. **Instale as dependências**

```bash
pip install -r requirements.txt
```

4. **Configure a API Key**

```bash
# Copie o arquivo de exemplo
cp .env.example .env

# Edite .env e adicione sua chave:
# GEMINI_API_KEY=sua_chave_aqui
```

Ou defina diretamente no terminal:

```bash
# Windows
set GEMINI_API_KEY=sua_chave_aqui

# Linux/Mac
export GEMINI_API_KEY=sua_chave_aqui
```

5. **Execute a aplicação**

```bash
streamlit run app.py
```

A aplicação estará disponível em `http://localhost:8501`

### Opção 2: Execução com Docker (Recomendado)

1. **Clone o repositório**

```bash
git clone https://github.com/seu-usuario/tt-blueelephant.git
cd tt-blueelephant
```

2. **Configure a API Key**

```bash
# Crie arquivo .env
cp .env.example .env

# Edite .env e adicione sua chave do Gemini
```

3. **Execute com Docker Compose**

```bash
docker-compose up -d
```

4. **Acesse a aplicação**

```
http://localhost:8501
```

5. **Para parar a aplicação**

```bash
docker-compose down
```

### Comandos Docker Úteis

```bash
# Ver logs
docker-compose logs -f

# Rebuild após mudanças no código
docker-compose up -d --build

# Remover volumes (limpar dados)
docker-compose down -v
```

## 📖 Como Usar

### 1. Chat com o Assistente

- Digite sua pergunta no campo de entrada
- O assistente responderá usando IA e ferramentas quando necessário
- Exemplos de uso:
  - "Qual o endereço do CEP 01310-100?"
  - "Me fale sobre o Pikachu"
  - "Quais são as estatísticas do Charizard?"
  - "Como está o tempo hoje?"

### 2. Dar Feedback

- Navegue até a aba "Feedback e Melhorias"
- Selecione uma resposta recente do assistente
- Avalie de 1 a 5 estrelas
- Escreva sugestões de melhoria
- Envie o feedback

### 3. Atualizar Prompt

- Após enviar feedback, marque a opção "Processar feedback agora"
- O sistema analisará os feedbacks e atualizará o prompt automaticamente
- Visualize as melhorias aplicadas
- Verifique a nova versão do prompt na aba "Prompt Atual"

### 4. Visualizar Histórico

- Aba "Histórico": veja todos os feedbacks enviados
- Aba "Prompt Atual": veja versões anteriores do prompt
- Estatísticas na barra lateral: métricas em tempo real

## 🧪 Testes

```bash
# Instalar dependências de teste
pip install pytest pytest-cov

# Executar testes
pytest

# Com cobertura
pytest --cov=src tests/
```

## 📚 APIs Utilizadas

### Google Gemini API

- **Descrição**: Modelo de linguagem para geração de respostas
- **Documentação**: https://ai.google.dev/docs
- **Gratuita**: Sim (com limites)

### ViaCEP

- **Descrição**: Consulta de CEPs brasileiros
- **Documentação**: https://viacep.com.br/
- **Gratuita**: Sim
- **Exemplo**: `https://viacep.com.br/ws/01310100/json/`

### PokéAPI

- **Descrição**: Informações sobre Pokémon
- **Documentação**: https://pokeapi.co/docs/v2
- **Gratuita**: Sim
- **Exemplo**: `https://pokeapi.co/api/v2/pokemon/pikachu`

## 🔧 Tecnologias Utilizadas

- **Python 3.11**: Linguagem principal
- **Streamlit**: Framework para interface web
- **Google Gemini**: Modelo de linguagem (LLM)
- **ChromaDB**: Vector store para embeddings
- **Docker**: Containerização
- **Requests**: Cliente HTTP para APIs externas

## 📊 Estrutura de Dados

### Prompts History (`data/prompts_history.json`)

```json
[
  {
    "version": 1,
    "prompt": "Você é um assistente...",
    "timestamp": "2024-12-13T10:00:00",
    "feedback_count": 5,
    "improvements": ["Melhoria 1", "Melhoria 2"]
  }
]
```

### Feedbacks (`data/feedbacks.json`)

```json
[
  {
    "id": 1,
    "timestamp": "2024-12-13T10:30:00",
    "user_message": "Qual o CEP...",
    "agent_response": "O CEP é...",
    "feedback_text": "Resposta muito boa!",
    "rating": 5,
    "processed": false
  }
]
```

## 🎯 Diferenciais Implementados

✅ **Testes Unitários**: Cobertura de componentes principais  
✅ **Documentação Clara**: Código comentado e docstrings  
✅ **README Completo**: Instruções detalhadas de uso  
✅ **Tratamento de Erros**: Try-catch em operações críticas  
✅ **Logs Estruturados**: Sistema de logging configurável  
✅ **Dockerização Completa**: Dockerfile + docker-compose  
✅ **Vector Store**: ChromaDB para contexto semântico  
✅ **Feedback Inteligente**: Análise automática com IA

## 🔐 Segurança e Boas Práticas

- ✅ API keys em variáveis de ambiente
- ✅ `.gitignore` configurado para dados sensíveis
- ✅ Timeout em requisições HTTP
- ✅ Validação de inputs
- ✅ Tratamento de exceções
- ✅ Health checks no Docker

## 🚧 Melhorias Futuras

- [ ] Autenticação de usuários
- [ ] Persistência de sessões entre reloads
- [ ] Mais ferramentas externas (clima, notícias, etc.)
- [ ] Suporte a múltiplos idiomas
- [ ] Análise de sentimento dos feedbacks
- [ ] Exportação de conversas
- [ ] API REST para integração externa
- [ ] Testes end-to-end

## 📝 Decisões de Design

### Organização da Interface

Optei por usar **colunas lado a lado** ao invés de abas ou páginas separadas porque:

- Permite visualizar chat e feedback simultaneamente
- Facilita dar feedback imediato durante a conversa
- Melhor aproveitamento do espaço em telas grandes

### Vector Store

Escolhi **ChromaDB** porque:

- Fácil integração com Python
- Não requer servidor externo
- Suporta persistência local
- Boa performance para o escopo do projeto

### Processamento de Feedback

O sistema processa feedbacks de forma **semi-automática**:

- Usuário pode escolher processar imediatamente ou acumular
- Análise considera múltiplos feedbacks para melhor contexto
- Prompt é atualizado de forma incremental

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor:

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/MinhaFeature`)
3. Commit suas mudanças (`git commit -m 'Adiciona MinhaFeature'`)
4. Push para a branch (`git push origin feature/MinhaFeature`)
5. Abra um Pull Request

## 📄 Licença

Este projeto foi desenvolvido como teste técnico e está disponível para fins educacionais.

## 👨‍💻 Autor

Desenvolvido como teste técnico para processo seletivo de estágio em desenvolvimento.

## 📞 Suporte

Para dúvidas ou problemas:

- Abra uma issue no GitHub
- Verifique a documentação das APIs utilizadas
- Revise os logs em `data/app.log`

---

**Nota**: Este projeto foi desenvolvido seguindo todas as especificações do teste técnico, incluindo funcionalidades obrigatórias e diferenciais.
