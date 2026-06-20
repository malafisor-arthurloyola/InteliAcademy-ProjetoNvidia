# Guia de Transição: Placeholders → Produção

## Filosofia adotada

A decisão de implementar o LangGraph e os contratos primeiro, sem APIs
reais, foi intencional e correta. Isso permitiu:

- Validar o fluxo completo (query → briefing) com 30 testes automatizados
- Garantir que estados, nós, arestas condicionais e tratamento de erros
  funcionam antes de introduzir dependências externas
- Separar a orquestração (LangGraph) da implementação concreta de cada
  agente

Agora que a arquitetura está sólida, cada implementação provisória
("placeholder") deve ser substituída por uma versão real seguindo as
interfaces já definidas nos módulos.

## Mapa de Substituição

### 1. Scraper Agent: StaticSeedCollector → Scraping real

**Arquivo:** `agents/scraper.py` + `scraping/collectors.py`

**Hoje:** Gera dados falsos baseados em palavras-chave da query.
Nunca fez uma requisição HTTP real.

**O que precisa mudar:** Criar `PlaywrightCollector` ou
`TrafilaturaCollector` que implemente a ABC `WebCollector` e faça
scraping real de sites. Controlar por flag de configuração para
poder rodar testes ainda com dados mockados.

**Schema de saída:** `SourceDocument` (já definido, não muda).

**Testes:** Já existem 6 testes em `test_scraping_adapters.py` que
validam os adapters com fixtures.

### 2. Extractor Agent: keyword matching → LLM estruturado

**Arquivo:** `agents/extractor.py`

**Hoje:** Detecta claims usando listas fixas como `AI_MARKERS = ("ai",
"ia", "llm", "machine learning", "agents")`. Trunca texto em 500
chars.

**O que precisa mudar:** Substituir `_infer_claim_type()` por chamada
a LLM que recebe o texto completo da `SourceDocument` e retorna claims
estruturadas com tipo (`ai_usage`, `technology_signal`,
`public_signal`), confiança e justificativa.

**Schema de saída:** `EvidenceClaim` (já definido, não muda).

### 3. Classifier Agent: determinístico → LLM com 3 labels

**Arquivo:** `agents/classifier.py`

**Hoje:** Retorna apenas "AI-Enabled" ou "Non-AI". **NUNCA** retorna
"AI-Native". Usa `if "ai" in text.lower()`.

**O que precisa mudar:** Chamada a LLM com prompt que diferencia:

- **AI-Native:** produto depende profundamente de IA, dados
  proprietários, agentes, diferenciação além de API wrapper
- **AI-Enabled:** usa IA como apoio, mas não é o núcleo do negócio
- **Non-AI:** sem uso relevante de IA

**Schema de saída:** `StartupClassification` (já definido, não muda).

### 4. NVIDIA RAG Agent: base inline → Qdrant

**Arquivo:** `agents/nvidia_rag.py`

**Hoje:** Base de conhecimento fixa no código com 12 tecnologias
NVIDIA e keywords hardcoded.

**O que precisa mudar:** Popular uma coleção Qdrant (ou pgvector) com
chunks reais da documentação NVIDIA. Substituir o matching de keywords
por busca vetorial + reranking (Cohere já está no requirements.txt).

**Schema de saída:** `NvidiaKnowledgeChunk` (já definido, não muda).

**Dependências:** `qdrant-client` e `cohere` já estão em
requirements.txt.

### 5. Recommendation Agent: guidance fixo → dinâmico

**Arquivo:** `agents/recommendation.py`

**Hoje:** `TECHNOLOGY_GUIDANCE` inline com gaps, justificativas e
prioridades fixas. `severity` é "high" para exatamente 3 tecnologias
e "medium" para todas as outras.

**O que precisa mudar:** Usar os chunks reais recuperados do Qdrant
para montar recomendações contextualizadas por startup. Mover
guidance para um arquivo de configuração ou base de conhecimento.

**Schema de saída:** `NvidiaRecommendation` (já definido, não muda).

### 6. API: endpoint simples → endpoints completos

**Arquivo:** `api/app.py`

**Hoje:** `GET /health` e `POST /runs` que compila o grafo do zero
em toda requisição. Sem autenticação, logging, ou documentação.

**O que precisa mudar:**
- Cachear o grafo compilado
- Adicionar `GET /runs/{id}` para consultar análise anterior
- Adicionar logging estruturado
- Adicionar schema de request/response com Pydantic
- (Opcional) autenticação via API key

### 7. Persistência: zero → SQLite

**Arquivo:** `database/` (hoje vazio)

**O que precisa mudar:** Adicionar SQLAlchemy com SQLite para salvar
resultados de execução, fontes coletadas e briefings gerados.
Usar `sqlalchemy` e `psycopg` (já em requirements.txt), mas começar
com SQLite para desenvolvimento.

## O que NÃO precisa mudar (está bom)

- Schemas Pydantic (`schemas/`)
- Normalizadores (`scraping/normalizers.py`)
- Estrutura do grafo (`graph/builder.py`, `graph/edges.py`)
- Estado do grafo (`graph/state.py`)
- Política de retry (`graph/retry_policy.py`)
- Agente de briefing (`agents/briefing.py`)
- Agente de validação (`agents/validator.py`)
- Adapters de provedor (`scraping/adapters.py`)
- Testes existentes (30 passando)

## Ordem recomendada de implementação

### Fase 1 — Base (1-2 dias)

1. Adicionar persistência SQLite
2. Expandir API com caching do grafo e GET /runs/{id}

### Fase 2 — Inteligência (2-3 dias)

3. Substituir Extractor por LLM
4. Substituir Classifier por LLM

### Fase 3 — Dados reais (2-3 dias)

5. Substituir StaticSeedCollector por scraping real (flag opt-in)
6. Popular Qdrant com documentação NVIDIA

### Fase 4 — Recomendação (1-2 dias)

7. Conectar Recommendation ao Qdrant
8. Mover TECHNOLOGY_GUIDANCE para config

### Fase 5 — Polimento (2 dias)

9. Testes de integração
10. CI/CD com GitHub Actions
11. MyPy + lint em CI
12. Frontend básico

## Critérios de "pronto" para cada substituição

- Código antigo removido (ou mantido como fallback com flag)
- Testes novos passando
- Testes antigos ainda passam (regressão zero)
- Pipeline completa executável sem placeholders
- Erros de provedor/scraping tratados como `PipelineError`
