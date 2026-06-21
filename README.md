# InteliAcademy-ProjetoNvidia

Projeto NVIDIA Startup AI Radar — plataforma multiagente para encontrar, classificar e recomendar tecnologias NVIDIA para startups brasileiras AI-native.

## Status do Projeto

| Fase | O que | Status |
|---|---|---|
| 1 | Scraping real (Firecrawl + Playwright) | ✅ CONCLUIDO |
| 2 | LLM no Extractor e Classifier (Groq/OpenAI/Gemini) | ✅ CONCLUIDO |
| 3 | RAG NVIDIA real (Qdrant in-memory) | 🔜 PROXIMO |
| 4 | Persistência (SQLite) e frontend | 🔜 PROXIMO |

## Ambiente Python

Versao oficial: Python 3.12.

As instrucoes de ambiente ficam em:

`ai-agent-system/docs/ENVIRONMENT.md`

## Arquitetura

A arquitetura inicial dos entregaveis 1 e 2 fica em:

`ai-agent-system/docs/ARCHITECTURE.md`

O codigo Python principal fica em:

`ai-agent-system/src/radar/`

## Configuração de API Externa

### 1. Provedores de Scraping (Firecrawl)

Criar conta em [firecrawl.dev](https://www.firecrawl.dev/), habilitar **Scrape**, **Search**, **Crawl**.

```env
RADAR_ENABLE_EXTERNAL_PROVIDERS=true
RADAR_SEARCH_PROVIDER=firecrawl
RADAR_PAGE_PROVIDER=firecrawl
FIRECRAWL_API_KEY=fc-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### 2. Provedores de LLM (Groq primario + OpenAI/Gemini fallback)

```env
RADAR_LLM_PROVIDER=groq
RADAR_LLM_FALLBACKS='["openai","gemini"]'
GROQ_API_KEY=gsk_...
OPENAI_API_KEY=sk-...
GEMINI_API_KEY=AIza...
```

### 3. Safety Switch

`RADAR_ENABLE_EXTERNAL_PROVIDERS=false` (padrão) → **nenhuma API externa roda**. Extractor/Classifier usam código determinístico (regex/scoring).

### 4. Providers suportados

| Provider | Search | Page | LLM | Custo |
|---|---|---|---|---|
| `fixture` | StaticSeedCollector (mock) | HtmlPageContentAdapter (mock) | Deterministico (regex/scoring) | Sempre disponivel |
| `firecrawl` | FirecrawlSearchAdapter | FirecrawlPageAdapter | — | Requer API key |
| `playwright` | — | PlaywrightPageAdapter (fallback) | — | Gratuito (local) |
| `serpapi` | SerpApiSearchAdapter | — | — | Alternativo (fallback) |
| `groq` | — | — | GroqProvider (Llama 3.3 70B) | Gratuito |
| `openai` | — | — | OpenAIProvider (GPT-4o-mini) | Pago |
| `gemini` | — | — | GeminiProvider (Gemini 2.0 Flash) | Gratuito |

## Testes

### Offline (sem APIs externas)

Testa todo o pipeline com mocks. Não requer `.env` configurado:

```powershell
cd ai-agent-system
..\venv\Scripts\python.exe -m pytest
```

92 testes:

| Suite | O que testa | Tests |
|---|---|---|
| `test_extractor.py` | Extracao deterministica (regex): setor, produto, founders, funding, tecnologias | 11 |
| `test_classifier.py` | Classificacao deterministica: AI-Native, AI-Enabled, Non-AI, NVIDIA caveats | 7 |
| `test_llm_adapters.py` | LLM adapter: safety switch, providers, prompts, fallback chain, preflight | 15 |
| `test_playwright_adapter.py` | Playwright adapter: safety switch, factory, preflight | 9 |
| `test_provider_factory.py` | Provider factory: fixture, firecrawl, serpapi, playwright | 6 |
| `test_provider_preflight.py` | Preflight offline: fixture, firecrawl, serpapi, playwright, LLM | 7 |
| `test_scraping_adapters.py` | Adaptadores de scraping: SerpAPI, PageContent, HTML bruto, Firecrawl | 8 |
| `test_source_normalizers.py` | Normalizacao de payloads: URL, formato, batch | 6 |
| `test_graph_mvp.py` | Pipeline completo do LangGraph | 3 |
| `test_evidence_pipeline.py` | Pipeline de evidencias: extracao + validacao | 2 |
| `test_recommendation_mapping.py` | Mapeamento de sinais para tecnologias NVIDIA | 8 |
| `test_retry_policy.py` | Politica de retry da coleta | 3 |
| `test_briefing.py` | Briefing final com caveats | 2 |
| `test_external_provider_settings.py` | Safety switch: providers desligados por padrao | 4 |
| `test_api_preflight.py` | Endpoint FastAPI GET /providers/preflight | 1 |

### Integração com Firecrawl (requer API key)

```powershell
$env:RADAR_ENABLE_EXTERNAL_PROVIDERS='true'
$env:RADAR_SEARCH_PROVIDER='firecrawl'
$env:RADAR_PAGE_PROVIDER='firecrawl'
$env:FIRECRAWL_API_KEY='fc-...'
python -m pytest tests/test_scraping_adapters.py -v -k firecrawl
```

### Integração com Playwright (fallback)

```powershell
$env:RADAR_ENABLE_EXTERNAL_PROVIDERS='true'
$env:RADAR_SEARCH_PROVIDER='firecrawl'
$env:RADAR_PAGE_PROVIDER='playwright'
$env:FIRECRAWL_API_KEY='fc-...'
python -m pytest tests/test_playwright_adapter.py -v
```

### Pipeline completo com LLM real

```powershell
$env:RADAR_ENABLE_EXTERNAL_PROVIDERS='true'
$env:PYTHONPATH='src'
..\venv\Scripts\python.exe -c "
from radar.graph.builder import build_graph
r = build_graph().invoke({'query': 'startup brasileira de IA', 'collection_attempts': 0})
print('Sources:', len(r['sources']))
print('Profile:', r.get('extracted_startups'))
print('Classification:', r.get('classification'))
"
```

### Testar LLM adapter direto

```powershell
$env:RADAR_ENABLE_EXTERNAL_PROVIDERS='true'
$env:PYTHONPATH='src'
..\venv\Scripts\python.exe -c "
from radar.llm.adapters import run_llm_with_fallback
from radar.llm.prompts import EXTRACTION_PROMPT
result = run_llm_with_fallback(EXTRACTION_PROMPT, 'Extract info about a startup')
print(result)
"
```
