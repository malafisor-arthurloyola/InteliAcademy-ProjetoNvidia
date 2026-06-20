# AGENTS.md

# AGENTS

Antes de executar qualquer tarefa, leia:

InteliAcademy-ProjetoNvidia\ai-agent-system\docs\Projeto_ NVIDIA Startup AI Radar (1).md

Este documento contém:

- Objetivos do projeto
- Escopo
- Definições
- Fontes recomendadas
- Tecnologias NVIDIA
- Critérios de classificação
- Arquitetura conceitual
- Regras de negócio

Considere esse documento a fonte principal de verdade do projeto.

## Estado Operacional Atual

Antes de continuar em um novo chat, leia tambem o handoff unico:

`C:\Users\Inteli\Desktop\Projeto Nvidia\Sessao 2026-06-14 - Handoff para Proximo Agente.md`

Esse arquivo deve ser mantido atualizado no lugar de criar varios handoffs por sessao.

Codigo Python real do projeto deve ficar em:

`InteliAcademy-ProjetoNvidia\ai-agent-system\src\radar\`

Nao recrie scaffolds antigos na raiz de `ai-agent-system` como `agent/`, `api/`, `config/`, `llm/` ou `memory/` sem uma necessidade concreta. Essas bases vazias foram removidas para evitar ambiguidade.

Use sempre o Python do venv do projeto:

`InteliAcademy-ProjetoNvidia\venv\Scripts\python.exe`


Ao lidar com falhas do sandbox Windows, edicoes via PowerShell, encoding, validacao com venv ou higiene de git, use a skill local:

`ai-agent-system\skills\windows-powershell-repo-hygiene`

Ao documentar aprendizado, explicacoes de codigo, fluxos do LangGraph ou atualizacoes do handoff, use a skill local:

`ai-agent-system\skills\obsidian-learning-notes`

Nao usar APIs externas sem autorizacao explicita do usuario. Nao commitar segredos, `.env`, caches ou o `venv`.

## Safety Switch para APIs Externas

APIs externas estao protegidas por uma camada fail-closed:

```python
# src/radar/settings.py
RADAR_ENABLE_EXTERNAL_PROVIDERS=false  # mude para true apenas com autorizacao
RADAR_SEARCH_PROVIDER=fixture          # ou "serpapi"
RADAR_PAGE_PROVIDER=fixture            # ou "firecrawl"
```

Se algum código tentar usar provedor externo sem habilitar, levanta:
- `ExternalProviderDisabledError` (se RADAR_ENABLE_EXTERNAL_PROVIDERS=false)
- `ExternalProviderCredentialsError` (se habilitado mas sem API key)

ConfiguredSerpApiSearchAdapter e ConfiguredFirecrawlPageAdapter em
`src/radar/scraping/adapters.py` implementam esse padrao.

Nao remover os adapters mockados/fixture — eles sao a bancada de testes
permanente do projeto.

## Ordem Alinhada de Implementacao

```text
Fase 1: Scraping real (RADAR_ENABLE_EXTERNAL_PROVIDERS=true)
Fase 2: LLM no Extractor e Classifier
Fase 3: RAG NVIDIA real (Qdrant)
Fase 4: Persistencia (SQLite) e frontend
```

Scraping real primeiro porque dados reais validam os schemas antes de IA
tentar interpretar. Placeholders continuam existindo como mocks de teste.

Ao implementar funcionalidades:

1. Preserve alinhamento com o documento.
2. Não invente critérios de classificação.
3. Não invente tecnologias NVIDIA.
4. Priorize modularidade e rastreabilidade.
5. Cite fontes sempre que possível.

## Missão do Projeto

Você está trabalhando no projeto NVIDIA Startup AI Radar.

O objetivo é construir uma plataforma multiagente capaz de:

* Encontrar startups brasileiras com sinais de uso intensivo de IA.
* Coletar informações públicas sobre essas empresas.
* Estruturar e validar evidências encontradas.
* Diagnosticar o nível de maturidade AI-native da startup.
* Identificar possíveis gaps técnicos.
* Consultar uma base de conhecimento sobre tecnologias NVIDIA.
* Gerar recomendações personalizadas para o NVIDIA Inception.
* Produzir briefings executivos para abordagem comercial e técnica.

---

## Problema de Negócio

Grandes laboratórios de IA (OpenAI, Anthropic, Google DeepMind, Meta e outros) estão subindo na cadeia de valor e ameaçando startups que dependem apenas de wrappers de LLM.

O sistema deve ajudar a NVIDIA a identificar startups que possuem potencial para evoluir para AI-native services e que possam se beneficiar do ecossistema NVIDIA.

---

## Pergunta Norteadora

Como a NVIDIA pode identificar, atrair e nutrir startups brasileiras AI-native em um contexto no qual grandes laboratórios de IA ameaçam empresas que dependem apenas de wrappers de LLM?

---

## Definições Importantes

### AI-Native

Empresa cujo produto depende profundamente de IA para entregar valor.

Características comuns:

* Uso intensivo de IA.
* Fluxos automatizados por agentes.
* Dados proprietários.
* Integração de IA ao processo operacional.
* Diferenciação além do uso de APIs.

### AI-Enabled

Empresa que utiliza IA como apoio operacional, mas não depende dela como núcleo do negócio.

### Non-AI

Empresa sem uso relevante de IA em seu produto ou operação.

---

## Pipeline Esperada

1. Search Planner Agent
2. Scraper Agent
3. Extractor Agent
4. Startup Classifier Agent
5. Evidence Validator Agent
6. NVIDIA RAG Agent
7. Recommendation Agent
8. Briefing Agent

Fluxo:

Consulta
→ Busca
→ Coleta
→ Extração
→ Validação
→ Classificação
→ Diagnóstico
→ Consulta RAG NVIDIA
→ Recomendação
→ Briefing

---

## Responsabilidades dos Agentes

### Search Planner Agent

Transforma a consulta do usuário em estratégias de busca.

Saída esperada:

* palavras-chave
* fontes prioritárias
* plano de coleta

### Scraper Agent

Coleta informações públicas.

Fontes prioritárias:

* Site oficial
* Blog
* Página de carreiras
* Notícias
* Diretórios de startups

Sempre preservar URL da evidência.

### Extractor Agent

Extrai:

* nome
* setor
* produto
* founders
* clientes
* funding
* tecnologias citadas
* uso de IA

Converter texto não estruturado em schema estruturado.

### Startup Classifier Agent

Classificar:

* AI-Native
* AI-Enabled
* Non-AI

Toda classificação deve possuir justificativa.

### Evidence Validator Agent

Validar:

* quantidade de evidências
* qualidade da fonte
* consistência entre fontes

Nunca permitir recomendações sem evidências.

### NVIDIA RAG Agent

Consultar:

* NVIDIA Inception
* NIM
* NeMo
* NeMo Guardrails
* Triton
* TensorRT-LLM
* RAPIDS
* cuDF
* cuML
* CUDA
* Riva
* Omniverse
* Isaac
* Clara
* Morpheus
* AI Enterprise

### Recommendation Agent

Relacionar:

* perfil da startup
* problemas encontrados
* tecnologias NVIDIA relevantes

Produzir:

* recomendação
* justificativa técnica
* justificativa de negócio
* prioridade
* complexidade
* próxima ação sugerida

### Briefing Agent

Gerar relatório executivo contendo:

* resumo da startup
* diagnóstico AI-native
* evidências encontradas
* gaps identificados
* recomendações NVIDIA
* plano de abordagem

---

## Tecnologias Preferenciais

### Orquestração

* LangGraph

### Backend

* Python
* FastAPI

### Dados

* PostgreSQL

### Vetorial

Preferência:

1. Qdrant
2. pgvector
3. ChromaDB

### Scraping

* Playwright
* BeautifulSoup
* Scrapy
* Firecrawl
* trafilatura

### Busca

* Busca vetorial
* BM25
* Busca híbrida

### Reranking

* Cohere Rerank

---

## Regras de Desenvolvimento

* Código modular.
* Tipagem explícita.
* Responsabilidades separadas.
* Funções pequenas.
* Não misturar scraping, RAG e regras de negócio.
* Não criar arquivos gigantes.
* Preservar rastreabilidade.
* Salvar URLs de origem.
* Nunca inventar informações sobre startups.
* Toda recomendação deve apontar evidências utilizadas.

---

## Estrutura Atual do Codigo

```text
ai-agent-system/src/radar/
  agents/           # agentes como arquivos planos (search_planner.py, scraper.py, ...)
  api/              # FastAPI (health + /runs)
  database/         # placeholder para SQLite
  graph/            # state, nodes, edges, builder, retry_policy
  rag/              # placeholder para Qdrant real
  schemas/          # contratos Pydantic (base, search, evidence, startup, pipeline, recommendation, briefing)
  scraping/         # collectors, normalizers, adapters
  services/         # placeholder
  utils/            # placeholder
```

## Historico de Progresso

O diario completo do que foi feito em cada sessao esta em:

```text
InteliAcademy-ProjetoNvidia\Documents\Relatorio de Progresso.md
```

Esse arquivo contem todos os dias de desenvolvimento, arquivos alterados,
validacoes, notas de aprendizado criadas e commits. Consulte antes de
comecar uma nova tarefa para saber o que ja foi tentado.

## Comandos uteis

```powershell
# Rodar testes
cd ai-agent-system
..\venv\Scripts\python.exe -m pytest

# Lint
..\venv\Scripts\python.exe -m ruff check src/radar/ tests/

# Ver ultimo commit
git log -1 --oneline
```

---

## Critérios de Qualidade

Uma entrega é considerada boa quando:

* Possui fontes rastreáveis.
* Estrutura dados corretamente.
* Classifica maturidade AI-native.
* Recupera conhecimento NVIDIA relevante.
* Justifica recomendações.
* Produz briefing executivo utilizável.
* Mantém arquitetura modular.

---

## O que NÃO fazer

* Criar apenas um chatbot.
* Fazer scraping sem armazenar evidências.
* Recomendar tecnologias sem justificativa.
* Acoplar todos os agentes em um único arquivo.
* Ignorar validação de evidências.
* Usar LangGraph apenas como sequência linear de prompts.
* Inventar dados de startups.
