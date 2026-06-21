---
title: "Relatorio de Progresso - NVIDIA Startup AI Radar"
projeto: "NVIDIA Startup AI Radar"
autor_git: "malafisor-arthurloyola <malafisor.es@gmail.com>"
---

# Relatorio de Progresso - NVIDIA Startup AI Radar

Este relatorio consolida o historico completo de progresso do projeto.
Cada sessao adiciona um bloco cronologico ao final.

---

## 2026-06-13 a 2026-06-14

### Resumo executivo

Entre 2026-06-13 e 2026-06-14, o projeto saiu de uma base inicial de organizacao e setup para uma arquitetura funcional de MVP com LangGraph, testes automatizados, ambiente Python validado e um sistema de aprendizado documentado no Obsidian.

O foco nao foi usar APIs externas ainda. A prioridade foi construir uma base confiavel: ambiente reprodutivel, grafo multiagente deterministico, schemas internos, validacao de evidencias e registro didatico do que foi feito.

### 2026-06-13 - O que foi feito

#### Organizacao inicial do projeto

Foi estruturado o repositorio principal em:

```text
C:\Users\Inteli\Desktop\Ligas\InteliAcademy\ProjetoNvidia\InteliAcademy-ProjetoNvidia
```

Tambem foi consolidado o documento `AGENTS.md`, que define regras importantes para o projeto, incluindo:

- seguir o documento oficial do case como fonte principal de verdade;
- nao inventar dados sobre startups;
- preservar rastreabilidade de evidencias;
- separar responsabilidades entre scraping, extracao, validacao, RAG, recomendacao e briefing.

#### Setup Python e base de ambiente

Foram iniciadas as configuracoes de runtime Python e dependencias do projeto.

Commits relacionados:

```text
f3fee2f chore: bootstrap skills and python environment
9f4eb11 chore: set python 3.12 as project runtime
973582c fix: novas implementacoes relacionadas ao venv, mas ainda nao foram concluidas
```

O objetivo dessa etapa foi evitar que o projeto dependesse do Python global da maquina e preparar uma base mais previsivel para testes e execucao.

#### Instalacao e organizacao de skills

Foram adicionadas skills locais e de apoio para orientar o desenvolvimento:

- `multi-agent-orchestration`;
- `frontend-design`;
- `langgraph-nvidia-startup-radar`;
- outras skills auxiliares de criacao e instalacao.

Commits relacionados:

```text
a66906a chore: add multi-agent orchestration skill
9f760a0 chore: add frontend design skill
```

#### Bootstrap da arquitetura do Radar

Foi criada a primeira arquitetura do sistema multiagente em:

```text
ai-agent-system/src/radar/
```

Principais partes criadas:

- `agents/`: agentes determiniscos iniciais;
- `graph/`: estado, nodes, edges e builder do LangGraph;
- `schemas/`: contratos Pydantic para fontes, claims, startups, recomendacoes e briefing;
- `scraping/`: coletor inicial;
- `api/`: FastAPI minima;
- `tests/`: testes iniciais do MVP.

Commit relacionado:

```text
061a81c chore: bootstrap radar architecture
```

### 2026-06-14 - O que foi feito

#### Finalizacao do ambiente Python

O ambiente virtual foi validado em:

```text
C:\Users\Inteli\Desktop\Ligas\InteliAcademy\ProjetoNvidia\InteliAcademy-ProjetoNvidia\venv
```

Python usado:

```text
Python 3.12.10
```

Comando correto para executar tarefas do projeto:

```powershell
& 'C:\Users\Inteli\Desktop\Ligas\InteliAcademy\ProjetoNvidia\InteliAcademy-ProjetoNvidia\venv\Scripts\python.exe'
```

Validacoes feitas:

```text
pip check -> No broken requirements found.
pytest -> passou
```

Restricao mantida: nao usar Python global.

#### Configuracao do autor Git correto

O autor local do Git foi ajustado para:

```text
malafisor-arthurloyola <malafisor.es@gmail.com>
```

#### Criacao do MOC de aprendizados no Obsidian

Foi criado um MOC especifico para aprendizado no cofre Obsidian:

```text
C:\Users\Inteli\Desktop\Projeto Nvidia\MOC - Aprendizados NVIDIA Startup AI Radar.md
```

A ideia desse MOC e registrar:

- o que foi feito;
- por que foi feito;
- quais arquivos importam;
- quais trechos de codigo sao importantes;
- como cada parte se conecta no projeto;
- o que estudar depois.

Tambem foram criadas notas como:

- `Aprendizado - Venv Python`;
- `Aprendizado - Setup do Projeto`;
- `Aprendizado - Schemas e Adapters para APIs`;
- `Aprendizado - LangGraph Atual do Projeto`;
- `Aprendizado - Sistema Multiagente com LangGraph`.

#### Criacao de adapter/normalizer para fontes

Foi criada a primeira camada de protecao entre dados externos e o LangGraph:

```text
ai-agent-system/src/radar/scraping/normalizers.py
```

Antes, o coletor criava diretamente um `SourceDocument`. Agora, ele simula payloads brutos e passa por um normalizador.

Fluxo desejado:

```text
API ou scraper bruto
 -> adapter/normalizer
 -> schema interno
 -> LangGraph
```

Commit relacionado:

```text
a71b842 feat: normalize source payloads for radar pipeline
```

#### Fortalecimento da extracao e validacao de evidencias

O `Extractor Agent` foi melhorado para diferenciar tipos de claims:

```text
ai_usage
technology_signal
public_signal
```

Arquivo:

```text
ai-agent-system/src/radar/agents/extractor.py
```

O `Evidence Validator Agent` tambem foi fortalecido.

Regras atuais:

```python
MINIMUM_CLAIMS = 2
MINIMUM_AI_CLAIMS = 1
MINIMUM_CONFIDENCE = 0.5
```

Arquivo:

```text
ai-agent-system/src/radar/agents/validator.py
```

Commit relacionado:

```text
971d88a feat: strengthen evidence extraction gates
```

#### Criacao de testes novos

Foram adicionados testes para validar os novos contratos:

```text
ai-agent-system/tests/test_source_normalizers.py
ai-agent-system/tests/test_evidence_pipeline.py
```

Cobertura atual:

- payload sem URL rastreavel e rejeitado;
- payloads com formatos diferentes viram `SourceDocument`;
- evidencia fraca gera briefing limitado;
- recomendacao so aparece depois de evidencia minima validada;
- extractor cria claims de uso de IA;
- validator exige evidencias independentes.

Resultado: `7 passed`

#### Criacao da skill de aprendizado no Obsidian

Foi criada uma skill local para orientar futuras anotacoes de aprendizado:

```text
ai-agent-system/skills/obsidian-learning-notes/SKILL.md
```

Commit relacionado:

```text
c4b5d9d chore: add obsidian learning notes skill
```

---

## 2026-06-16 - Recomendacoes NVIDIA deterministicas

Foi fortalecida a etapa `nvidia_rag -> recommendation`, ainda sem APIs externas.

Arquivos alterados:

```text
ai-agent-system/src/radar/agents/nvidia_rag.py
ai-agent-system/src/radar/agents/recommendation.py
ai-agent-system/tests/test_recommendation_mapping.py
```

O `nvidia_rag.py` agora possui uma base estatica minima de conhecimento NVIDIA e recupera chunks por sinais presentes apenas em claims validadas.

O `recommendation.py` agora gera recomendacoes especificas por tecnologia, mantendo:

- gap tecnico;
- justificativa tecnica;
- justificativa de negocio;
- prioridade;
- complexidade;
- proxima acao sugerida;
- IDs de evidencia da startup;
- IDs de conhecimento NVIDIA.

Tecnologias mapeadas nesta versao:

```text
NVIDIA Inception
NVIDIA NIM
NeMo Guardrails
NVIDIA Triton Inference Server
NVIDIA RAPIDS
NVIDIA Riva
NVIDIA Clara
```

Validacao: `pytest -> 10 passed`

Nota de aprendizado: `Aprendizado - NVIDIA RAG e Recommendation Agent.md`

Commit: `157a00e feat: map validated signals to nvidia recommendations`

---

## 2026-06-16 - Matriz deterministica expandida

Foi expandida a matriz deterministica de recomendacoes antes de iniciar scraping real ou APIs externas.

Arquivos alterados:

```text
ai-agent-system/src/radar/scraping/collectors.py
ai-agent-system/src/radar/agents/nvidia_rag.py
ai-agent-system/src/radar/agents/recommendation.py
ai-agent-system/tests/test_recommendation_mapping.py
```

Novos cenarios mockados no `StaticSeedCollector`:

```text
LLM/agentes
Dados tabulares
Voz/call center/transcricao
Saude/healthcare
Robotica/simulacao
Latencia/inferencia
```

Tecnologias cobertas pela matriz deterministica atual:

```text
NVIDIA Inception, NVIDIA NIM, NeMo Guardrails, NVIDIA Triton Inference Server,
TensorRT-LLM, NVIDIA RAPIDS, cuDF, cuML, NVIDIA Riva, NVIDIA Clara,
NVIDIA Omniverse, NVIDIA Isaac
```

Validacao: `pytest -> 15 passed`

Nota de aprendizado: `Aprendizado - Matriz de Recomendacoes NVIDIA.md`

Commit: `8dad0c1 feat: surface collection errors in briefing`

---

## 2026-06-17 - Contratos e adapters para dados reais

Foi preparada a fronteira para futuras APIs externas, ainda sem chamar nenhuma API real.

Arquivos alterados:

```text
ai-agent-system/src/radar/schemas/search.py
ai-agent-system/src/radar/schemas/__init__.py
ai-agent-system/src/radar/scraping/normalizers.py
ai-agent-system/tests/test_source_normalizers.py
```

Novo contrato interno: `SourceCandidate` — representa um resultado de busca normalizado antes da pagina virar evidencia completa.

Campos principais: `url`, `domain`, `source_type`, `title`, `snippet`, `rank`, `provider`, `raw_payload`.

Novos normalizers: `normalize_search_result_payload`, `normalize_search_result_payloads`, `normalize_collected_page_payload`.

Fluxo preparado:

```text
payload bruto de API de busca
 -> SourceCandidate
 -> payload bruto de pagina coletada
 -> SourceDocument
 -> extractor -> validator -> classifier -> nvidia_rag -> recommendation -> briefing
```

Validacao: `pytest -> 19 passed`

Nota de aprendizado: `Aprendizado - Contratos e Adapters de Dados Reais.md`

Commit: `8dad0c1 feat: surface collection errors in briefing`

---

## 2026-06-20 - Adapters mockados de provedores

Foi criada uma camada de adapters com fixtures para simular provedores externos sem usar APIs reais, rede ou chaves.

Arquivos alterados/criados:

```text
ai-agent-system/src/radar/scraping/adapters.py
ai-agent-system/src/radar/scraping/collectors.py
ai-agent-system/tests/test_scraping_adapters.py
ai-agent-system/tests/fixtures/serpapi_ai_startups.json
ai-agent-system/tests/fixtures/page_payloads_ai_startups.json
```

Novas pecas: `SerpApiSearchAdapter`, `PageContentAdapter`, `SearchBackedCollector`.

Validacao: `pip check -> No broken requirements found.` | `pytest -> 23 passed`

Nota de aprendizado: `Aprendizado - Adapters Mockados de Provedores.md`

---

## 2026-06-20 - Erros estruturados de coleta

Foi adicionada uma camada de erros recuperaveis para a coleta, sem usar APIs externas.

Arquivos alterados:

```text
ai-agent-system/src/radar/schemas/pipeline.py
ai-agent-system/src/radar/scraping/collectors.py
ai-agent-system/src/radar/agents/scraper.py
ai-agent-system/src/radar/graph/nodes.py
ai-agent-system/tests/test_scraping_adapters.py
```

Mudancas principais:

- `PipelineError` agora guarda `source_url`, `provider` e `error_type`
- `SearchBackedCollector` ganhou `collect_with_errors()`
- `scraper_node` grava erros em `RadarState.errors` e marca `review_required`

Validacao: `pip check -> No broken requirements found.` | `pytest -> 25 passed`

Nota de aprendizado: `Aprendizado - Erros Estruturados de Coleta.md`

---

## 2026-06-20 - Skill de higiene Windows PowerShell

Foi criada uma skill local para lidar com falhas do sandbox Windows, edicoes via PowerShell, risco de encoding/BOM, validacao com venv e higiene de git.

Arquivos criados/alterados:

```text
ai-agent-system/skills/windows-powershell-repo-hygiene/SKILL.md
ai-agent-system/skills/windows-powershell-repo-hygiene/agents/openai.yaml
ai-agent-system/skills/SKILLS_INDEX.md
AGENTS.md
```

Validacao: `quick_validate.py -> Skill is valid!`

---

## 2026-06-20 - Caveats de coleta no briefing

Foi feita a conexao entre os erros estruturados da coleta e o briefing final.

Arquivos alterados/criados:

```text
ai-agent-system/src/radar/agents/briefing.py
ai-agent-system/tests/test_briefing.py
```

Mudanca principal: `PipelineError` vindo do scraper agora aparece como caveat no `ExecutiveBriefing`.

Validacao: `pip check -> No broken requirements found.` | `pytest -> 30 passed`

Nota de aprendizado: `Aprendizado - Caveats no Briefing.md`

---

## 2026-06-20 - Politica de retry da coleta

Foi formalizada a regra de retry da coleta antes de conectar APIs reais.

Arquivos alterados/criados:

```text
ai-agent-system/src/radar/graph/retry_policy.py
ai-agent-system/src/radar/graph/edges.py
ai-agent-system/src/radar/agents/briefing.py
ai-agent-system/tests/test_retry_policy.py
ai-agent-system/tests/test_briefing.py
```

Mudanca principal: `MAX_COLLECTION_ATTEMPTS = 2`

Fluxo atualizado:

```text
validator
 -> evidencia suficiente: classifier
 -> evidencia fraca e tentativas restantes: scraper
 -> evidencia fraca e limite atingido: briefing limitado com caveat
```

Validacao: `pip check -> No broken requirements found.` | `pytest -> 30 passed`

Nota de aprendizado: `Aprendizado - Politica de Retry da Coleta.md`

Commit: `6ddcb85 feat: formalize collection retry policy`

---

## 2026-06-20 — Safety switch para provedores externos

Foi implementada uma camada de seguranca fail-closed para provedores externos, ainda sem chamar APIs reais.

Arquivos criados/alterados:

```text
ai-agent-system/.env.example                          (modificado)
ai-agent-system/src/radar/settings.py                 (criado)
ai-agent-system/src/radar/scraping/adapters.py         (modificado)
ai-agent-system/tests/test_external_provider_settings.py (criado)
```

Mudancas principais:

- `RadarSettings` com `enable_external_providers: bool = False` (desligado por padrao)
- `ConfiguredSerpApiSearchAdapter` e `ConfiguredFirecrawlPageAdapter` (fail-closed)
- Erros estruturados: `ExternalProviderDisabledError`, `ExternalProviderCredentialsError`
- `.env.example` expandido com variaveis `RADAR_*`, `SERPAPI_API_KEY`, `FIRECRAWL_API_KEY`

Correcao: `adapters.py` estava corrompido com `\r\n` literais na linha 13 (herdado de sessao anterior). Corrigido e validado.

Validacao:

```text
pip check -> No broken requirements found.
pytest -> 34 passed (30 existentes + 4 novos)
ruff -> All checks passed
```

Commit: `bc49a12 feat: add fail-closed safety switch for external providers`

Nota: `docs/guia-transicao-placeholders-para-producao.md` foi criado e depois removido por ser redundante com o handoff.

---

## 2026-06-20 — Scraping real (Firecrawl), Extractor, Classifier

### Resumo executivo

Nesta sessão, o projeto saiu dos mocks offline para scraping real com Firecrawl. O extrator e classificador foram refinados com scoring multidimensional. O pipeline end-to-end foi validado com dados reais: 7 fontes coletadas, classificação AI-Native com 95% de confiança, tecnologias NVIDIA detectadas (Clara, Riva, RAG), setor, funding e founders identificados. Total de 68 testes passando.

### Commits

```text
8119210 feat: adapt offline html page content to source document
182f3db feat: improve extractor and classifier with multidimensional scoring
17d04cc docs: record collaboration review guidance for agents
fd1b953 feat: firecrawl real search and page adapters with provider factory
53038c0 fix: firecrawl sdk api
68c9ee2 docs: update collaboration board with skills requirement
```

### O que foi feito

#### Extractor (src/radar/agents/extractor.py)

- Extração estruturada de **setor** (13 categorias: Healthcare, Fintech, Agrotech, Edtech, Logistics, Retail, Legal, Real Estate, Energy, Security, Entertainment, Developer Tools, Other)
- **Produto**: regex para product/platform/solution/produto/ferramenta
- **Founders**: padroes founder/ceo/cto/co-founder/fundador
- **Funding**: padroes raised/seed/series A-Z
- **Tecnologias**: 21 keywords (NVIDIA: CUDA, TensorRT-LLM, Triton, NeMo, RAPIDS, Omniverse, Isaac, Clara, Morpheus, Riva, AI Enterprise, Inception; Gerais: LLM, LangChain, RAG, Vector DB, PyTorch, HF, GPU Inference, etc.)
- **ai_usage_summary** gerado quando há claim de IA

#### Classifier (src/radar/agents/classifier.py)

Classificação deterministica refinada com scoring multidimensional:

- **AI-Native score**: dados proprietários, fine-tuning, multi-agent, NVIDIA techs
- **AI-Enabled score**: uso de API/LLM, automação, workflow, techs genéricas
- **Evidence quality score**: quantidade e tipos de claims e sources
- **Business maturity score**: funding, founders, setor identificado
- Thresholds: AI-Enabled a partir de 1.5 combinado ou NVIDIA techs presentes
- **Caveats dinâmicos**: alerta se startup já cita tecnologias NVIDIA

#### Firecrawl real

- `FirecrawlSearchAdapter`: busca real via `firecrawl.Firecrawl().search()`, normaliza em `SourceCandidate`
- `FirecrawlPageAdapter`: scrape real via `firecrawl.Firecrawl().scrape_url()`, extrai markdown/HTML, normaliza em `SourceDocument`
- `provider_factory.py`: suporta `firecrawl/firecrawl` como configuração primária; `serpapi/firecrawl` mantido como fallback
- `provider_preflight.py`: atualizado para verificar credenciais apenas do provider configurado (não ambos); suporta combinação `firecrawl/firecrawl`
- `settings.py`: `SearchProviderName` agora inclui `"firecrawl"`; `.env` movido para raiz do repositório (evita poluição no CWD dos testes)
- Pipeline end-to-end com Firecrawl real: 7 fontes coletadas, classificação AI-Native 95%

#### Agentes e grafo

- **Evidence Validator** (src/radar/agents/validator.py): `MINIMUM_CLAIMS=2`, `MINIMUM_AI_CLAIMS=1`, `MINIMUM_CONFIDENCE=0.5`
- **Recommendation** (src/radar/agents/recommendation.py): mapeia 12 tecnologias NVIDIA com gap técnico, justificativas, prioridade, complexidade, próxima ação
- **NVIDIA RAG** (src/radar/agents/nvidia_rag.py): contexto determinístico de NVIDIA Inception se startup não for Non-AI
- **Briefing** (src/radar/agents/briefing.py): briefing final com caveats quando evidência é fraca
- **API** (src/radar/api/app.py): FastAPI com GET /health e GET /providers/preflight

#### Testes

```text
tests/test_extractor.py: 11 tests (setor, produto, founders, funding, tecnologias, dedup, summary)
tests/test_classifier.py: 7 tests (AI-Native, AI-Enabled, Non-AI, NVIDIA caveats, funding boost, rationale, confidence bounds)
tests/test_provider_factory.py: 5 tests
tests/test_provider_preflight.py: 7 tests (multi-provider, firecrawl config, varredura)
tests/test_scraping_adapters.py: firecrawl real + firecrawl safety switch
tests/test_graph_mvp.py, test_source_normalizers.py, test_evidence_pipeline.py,
test_recommendation_mapping.py, test_retry_policy.py, test_briefing.py,
test_external_provider_settings.py, test_api_preflight.py

Total: 68 tests passing, ruff clean
```

#### Skills

- `firecrawl-skill` criada em `ai-agent-system/skills/firecrawl-skill/SKILL.md`
- `SKILLS_INDEX.md` atualizado com `firecrawl-skill` na tabela

#### Obsidian e documentação

- Nota `Firecrawl Setup.md` criada no vault com setup, safety switch, exemplos de uso
- `README.md` atualizado com seção de configuração de API externa, tabela de providers
- `Handoff` atualizado com progresso do Firecrawl real

### Experimentos e decisões

- Firecrawl escolhido como **provider único** (search + page) por ser gratuito e estar no documento-fonte
- `.env` movido para **raiz do repositório** (não mais dentro de `ai-agent-system/`) porque pytest roda de `ai-agent-system/` mas o `BaseSettings` busca no CWD
- SerpAPI mantido como fallback alternativo, mas não como primary
- Placeholders (StaticSeedCollector, HtmlPageContentAdapter) mantidos como mocks permanentes de teste
- Safety switch continua fail-closed: só Firecrawl roda com autorização explícita

### Próximos passos

```text
Fase 1: Scraping real (FINALIZADA — Firecrawl + Playwright)
Fase 2: LLM no Extractor e Classifier (FINALIZADA — Groq/OpenAI/Gemini)
Fase 3: RAG NVIDIA real (Qdrant in-memory + sentence-transformers) ← PROXIMO
Fase 4: Persistência (SQLite) e frontend
```

---

## 2026-06-20 (continuacao) — PlaywrightPageAdapter

### O que foi feito

- `settings.py`: adicionado `"playwright"` ao `PageProviderName`
- `adapters.py`: criado `PlaywrightPageAdapter` — usa Chromium headless + trafilatura para extrair texto de paginas com JS pesado
- `provider_factory.py`: suporta combos `firecrawl/playwright` e `serpapi/playwright`
- `provider_preflight.py`: detecta se Chromium esta instalado
- `test_playwright_adapter.py`: 9 testes (unitario, factory, preflight)
- Handoff atualizado com plano claro de proximos passos em tabelas

### Commits

```text
a1916a1 feat: PlaywrightPageAdapter as fallback page provider
b96eba4 docs: firecrawl skill, README setup, relatorio, handoff, board update
```

### Validacao

```text
pytest -> 77 passed (era 68)
ruff -> All checks passed
```

---

## 2026-06-20 (continuacao) — LLM no Extractor e Classifier

### O que foi feito

#### src/radar/llm/ (novo modulo)

- `adapters.py`: tres providers com fallback chain:
  - `GroqProvider` (Llama 3.3 70B — primario)
  - `OpenAIProvider` (GPT-4o-mini — primeiro fallback)
  - `GeminiProvider` (Gemini 2.0 Flash — segundo fallback)
- `prompts.py`: `EXTRACTION_PROMPT` + `CLASSIFICATION_PROMPT` com saida JSON estruturada
- `run_llm_with_fallback()`: tenta provedores em ordem, propaga erro se todos falharem
- Safety switch: se `RADAR_ENABLE_EXTERNAL_PROVIDERS=false`, levanta `ExternalProviderDisabledError`

#### Extractor (src/radar/agents/extractor.py)

- `_build_profile()` agora tenta `_llm_extract()` primeiro se providers habilitados
- Se LLM falhar, cai no `_deterministic_extract()` (regex/scoring original)
- `_llm_extract()`: chama `run_llm_with_fallback()` com `EXTRACTION_PROMPT`, faz parse do JSON retornado
- `_parse_llm_json()`: trata markdown ```json ``` e JSON puro

#### Classifier (src/radar/agents/classifier.py)

- `classify_startup()` agora tenta `_llm_classify()` primeiro se providers habilitados
- Se LLM falhar, cai no `_deterministic_classify()` (scoring multidimensional)
- `_llm_classify()`: monta profile + textos das fontes, chama `run_llm_with_fallback()` com `CLASSIFICATION_PROMPT`
- Adiciona caveats automaticos se tecnologias NVIDIA detectadas

#### settings.py

- `LLMProviderName = Literal["groq", "openai", "gemini"]`
- `llm_provider: LLMProviderName = "groq"`
- `llm_fallbacks: list[LLMProviderName] = ["openai", "gemini"]`
- `groq_api_key`, `openai_api_key`, `gemini_api_key`

#### Provider Preflight

- `ProviderPreflight` agora inclui `llm_provider`, `llm_fallbacks`, `llm_ready`
- `_check_llm_ready()`: retorna True se pelo menos 1 API key estiver configurada

#### .env (gitignorado)

Configurado com as 3 chaves fornecidas pelo usuario.

### Commits

```text
48c601d feat: LLM adapter with Groq primary + OpenAI/Gemini fallback chain
```

### Testes

```text
tests/test_llm_adapters.py: 15 tests
  - safety switch (3): disabled error, fallback disabled, missing key
  - factories (4): Groq/OpenAI/Gemini instantiation, unknown provider
  - prompts (2): extraction fields, classification labels
  - preflight (5): no keys, groq key, openai key, full preflight, preflight no keys
  - fallback chain (1): all providers fail → RuntimeError

Total: 92 tests passing (era 77)
ruff -> All checks passed
```
