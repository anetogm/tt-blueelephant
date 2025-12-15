# Chatbot IA com Feedback Inteligente

Sistema de chatbot com inteligência artificial que inclui funcionalidades de feedback em tempo real para melhorias contínuas do prompt. Desenvolvido como teste técnico para vaga de estágio em desenvolvimento.

## Descrição

Este projeto implementa um assistente virtual inteligente que:

- Conversa naturalmente com usuários usando IA (Google Gemini 2.5 Flash)
- Utiliza function calling nativo para integração automática com ferramentas externas
- Aprende e melhora continuamente através de feedbacks dos usuários
- Armazena contexto em vector store para respostas mais relevantes

## Funcionalidades Principais

### Chat Interativo

- Interface de chat moderna e responsiva
- Histórico de mensagens persistente
- Respostas contextualizadas usando vector store (ChromaDB)
- Integração automática com ferramentas externas

### Ferramentas Integradas

O sistema utiliza **function calling nativo do Google Gemini**, que permite ao modelo decidir automaticamente quando usar cada ferramenta:

1. **ViaCEP** - Consulta de CEPs brasileiros

   - Retorna endereço completo a partir do CEP
   - Informações: logradouro, bairro, cidade, UF, DDD

2. **PokéAPI** - Informações sobre Pokémon

   - Consulta por nome ou número da Pokédex
   - Dados: tipos, habilidades, estatísticas, altura, peso

3. **IBGE** - Dados geográficos do Brasil

   - Informações sobre estados brasileiros
   - Dados de municípios e regiões
   - Códigos IBGE e divisões administrativas

4. **Open-Meteo** - Clima e previsão do tempo

   - Clima atual de qualquer cidade do mundo
   - Previsão para os próximos 3 dias
   - Temperatura, umidade, vento e precipitação

5. **TVMaze** - Informações sobre séries de TV

   - Dados detalhados sobre séries
   - Gêneros, status, ratings e sinopse
   - Informações de rede e horário de exibição

6. **Open Library** - Informações sobre livros

   - Busca por título ou autor
   - ISBN, editora, ano de publicação
   - Categorias e número de páginas

7. **Lyrics.ovh** - Letras de músicas
   - Busca por artista e música
   - Letras completas de músicas

### Sistema de Feedback Inteligente

- Captura feedback do usuário em tempo real
- **Processamento automático**: atualiza o prompt automaticamente quando:
  - Acumula 3 ou mais feedbacks pendentes
  - Recebe feedbacks muito negativos (média < 3.0)
- Análise automática de feedbacks usando IA
- Processamento manual também disponível (botão)
- Atualização dinâmica do prompt do sistema
- Histórico completo de versões de prompt
- Visualização de melhorias aplicadas

### Vector Store

- Armazenamento de contexto usando ChromaDB
- Busca semântica de conversas anteriores
- Base de conhecimento sobre capacidades do sistema
- Recuperação de informações relevantes para contexto

## Arquitetura do Projeto

```
tt-blueelephant/
├── src/
│   ├── agent/
│   │   ├── chatbot.py              # Agente principal com LLM e function calling
│   │   └── prompt_manager.py       # Gerenciador de prompts e versionamento
│   ├── feedback/
│   │   └── feedback_processor.py   # Processador inteligente de feedback
│   ├── tools/
│   │   ├── viacep_tool.py          # Ferramenta ViaCEP
│   │   ├── pokemon_tool.py         # Ferramenta PokéAPI
│   │   ├── ibge_tool.py            # Ferramenta IBGE
│   │   ├── balldontlie_tool.py     # Ferramenta NBA
│   │   ├── openmeteo_tool.py       # Ferramenta Open-Meteo
│   │   ├── tvmaze_tool.py          # Ferramenta TVMaze
│   │   ├── openlibrary_tool.py     # Ferramenta Open Library
│   │   └── lyricsovh_tool.py       # Ferramenta Lyrics.ovh
│   └── vectorstore/
│       └── chroma_store.py         # Vector store ChromaDB
├── data/                         # Dados persistentes (criado automaticamente)
├── tests/                        # Testes unitários
├── app.py                        # Aplicação Streamlit
├── requirements.txt              # Dependências Python
├── Dockerfile                    # Container Docker
├── docker-compose.yml            # Orquestração Docker
├── .env.example                  # Exemplo de variáveis de ambiente
└── README.md                     # Este arquivo
```

## Instalação e Execução

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

## Como Usar

### 1. Chat com o Assistente

Digite suas perguntas no campo de entrada. O assistente responderá usando IA e ferramentas quando apropriado.

**Exemplos de uso:**

- "Qual o endereço do CEP 01310-100?"
- "Me fale sobre o Pikachu"
- "Como está o clima em São Paulo?"
- "Informações sobre o estado de SP"
- "Quem é LeBron James?"
- "Me fale sobre a série Breaking Bad"
- "Informações sobre o livro 1984"
- "Letra de Bohemian Rhapsody do Queen"

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

## Testes

```bash
# Instalar dependências de teste
pip install pytest pytest-cov

# Executar testes
pytest

# Com cobertura
pytest --cov=src tests/
```

## APIs Utilizadas

Todas as APIs utilizadas são **gratuitas e sem necessidade de autenticação** (exceto Google Gemini):

### Google Gemini API

- **Descrição**: Modelo de linguagem para geração de respostas e function calling
- **Documentação**: https://ai.google.dev/docs
- **Requer API Key**: Sim (gratuita com limites)

### ViaCEP

- **Descrição**: Consulta de CEPs brasileiros
- **Documentação**: https://viacep.com.br/
- **Exemplo**: `https://viacep.com.br/ws/01310100/json/`

### PokéAPI

- **Descrição**: Informações sobre Pokémon
- **Documentação**: https://pokeapi.co/docs/v2
- **Exemplo**: `https://pokeapi.co/api/v2/pokemon/pikachu`

### IBGE API

- **Descrição**: Dados geográficos do Brasil
- **Documentação**: https://servicodados.ibge.gov.br/api/docs
- **Exemplo**: `https://servicodados.ibge.gov.br/api/v1/localidades/estados/SP`

### Open-Meteo API

- **Descrição**: Previsão do tempo e clima
- **Documentação**: https://open-meteo.com/
- **Exemplo**: `https://api.open-meteo.com/v1/forecast`

### TVMaze API

- **Descrição**: Informações sobre séries de TV
- **Documentação**: https://www.tvmaze.com/api
- **Exemplo**: `https://api.tvmaze.com/search/shows?q=breaking+bad`

### Open Library API

- **Descrição**: Informações sobre livros
- **Documentação**: https://openlibrary.org/developers/api
- **Exemplo**: `https://openlibrary.org/search.json?q=1984`

### Lyrics.ovh API

- **Descrição**: Letras de músicas
- **Documentação**: https://lyricsovh.docs.apiary.io/
- **Exemplo**: `https://api.lyrics.ovh/v1/coldplay/yellow`

## Tecnologias Utilizadas

### Backend

- **Python 3.11**: Linguagem principal
- **Google Gemini 2.5 Flash**: Modelo de linguagem com function calling
- **ChromaDB**: Vector store para embeddings e busca semântica
- **Requests**: Cliente HTTP para APIs externas

### Frontend

- **Streamlit**: Framework para interface web interativa

### DevOps

- **Docker**: Containerização da aplicação
- **Docker Compose**: Orquestração de containers

### Testes

- **pytest**: Framework de testes
- **pytest-cov**: Cobertura de código

## Estrutura de Dados

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

## Diferenciais Implementados

**Requisitos Obrigatórios**

- Interface Streamlit com separação clara de áreas
- LLM Google Gemini integrado
- Vector Store ChromaDB para contexto
- 8 ferramentas externas via APIs gratuitas
- Sistema de feedback inteligente funcional
- Atualização automática de prompts
- Dockerização completa (Dockerfile + docker-compose.yml)
- Python 3.9+

**Diferenciais**

- Testes unitários com pytest e cobertura
- Documentação clara e completa do código
- README estruturado com exemplos
- Tratamento robusto de erros em todas as operações
- Logs estruturados para debugging
- Function calling nativo do Gemini (mais preciso que regex)
- Base de conhecimento inicializada automaticamente
- Persistência de dados entre sessões

## Segurança e Boas Práticas

- API keys em variáveis de ambiente (.env)
- .gitignore configurado para dados sensíveis
- Timeout em todas as requisições HTTP
- Validação de inputs do usuário
- Tratamento de exceções em operações críticas
- Health checks no Docker
- Logs estruturados para auditoria
- Separação de responsabilidades (SRP)
- Type hints em todo o código Python

## Melhorias Futuras

- Autenticação de usuários multi-tenant
- Persistência de sessões entre reloads
- Cache de respostas de APIs externas
- Suporte a múltiplos idiomas
- Análise de sentimento dos feedbacks
- Exportação de conversas (PDF/JSON)
- API REST para integração externa
- Testes end-to-end com Selenium
- Dashboard de analytics
- Rate limiting para APIs

## Decisões de Design

### Function Calling vs Regex

Optei por usar **function calling nativo do Google Gemini** ao invés de detecção manual (regex) porque:

- O LLM entende contexto e decide quando usar cada ferramenta
- Elimina ~150 linhas de código de detecção manual
- Mais preciso e flexível
- Fácil adicionar novas ferramentas (apenas declaração)
- Reduz manutenção

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

- Usuário escolhe quando processar (imediato ou acumulado)
- Análise considera múltiplos feedbacks para melhor contexto
- Prompt é atualizado incrementalmente
- Histórico completo de versões mantido

## Contribuindo

Contribuições são bem-vindas! Por favor:

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/MinhaFeature`)
3. Commit suas mudanças (`git commit -m 'Adiciona MinhaFeature'`)
4. Push para a branch (`git push origin feature/MinhaFeature`)
5. Abra um Pull Request

## Licença

Este projeto foi desenvolvido como teste técnico e está disponível para fins educacionais.

## Autor

Desenvolvido como teste técnico para processo seletivo de estágio em desenvolvimento.

## Suporte

Para dúvidas ou problemas:

- Abra uma issue no GitHub
- Verifique os logs em `data/app.log`
- Revise a documentação das APIs utilizadas
- Consulte a documentação do Google Gemini

---

**Nota**: Este projeto atende a todos os requisitos obrigatórios e diferenciais do teste técnico, incluindo funcionalidades extras como function calling nativo, 8 ferramentas integradas e base de conhecimento automática.
