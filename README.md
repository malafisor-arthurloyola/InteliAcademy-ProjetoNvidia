# InteliAcademy-ProjetoNvidia

Projeto NVIDIA Startup AI Radar.

## Ambiente Python

Versao oficial: Python 3.12.

As instrucoes de ambiente ficam em:

`ai-agent-system/docs/ENVIRONMENT.md`

## Arquitetura

A arquitetura inicial dos entregaveis 1 e 2 fica em:

`ai-agent-system/docs/ARCHITECTURE.md`

O codigo Python principal fica em:

`ai-agent-system/src/radar/`

## Configuração de API Externa (Firecrawl)

O Radar usa **Firecrawl** como provider de busca (Search) e scraping de páginas (Scrape) para coleta real de dados.

### 1. Obter API Key

1. Criar conta em [firecrawl.dev](https://www.firecrawl.dev/)
2. No dashboard, habilitar **Scrape**, **Search**, **Crawl**
3. Copiar a API key

### 2. Configurar `.env`

Criar arquivo `.env` na **raiz do repositório** (gitignorado):

```env
RADAR_ENABLE_EXTERNAL_PROVIDERS=true
RADAR_SEARCH_PROVIDER=firecrawl
RADAR_PAGE_PROVIDER=firecrawl
FIRECRAWL_API_KEY=fc-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

> [!IMPORTANT]
> **Nunca commitar o `.env`.**

### 3. Safety Switch

`RADAR_ENABLE_EXTERNAL_PROVIDERS=false` (padrão) → Firecrawl não roda.

Os adapters levantam `ExternalProviderDisabledError` quando `RADAR_ENABLE_EXTERNAL_PROVIDERS=false`.

### 4. Ativar ambiente e rodar

```powershell
# Ativar venv
.\venv\Scripts\Activate.ps1

# Ou usar direto:
.\venv\Scripts\python.exe -m pytest
```

### 5. Testar integração real

```powershell
cd ai-agent-system
$env:RADAR_ENABLE_EXTERNAL_PROVIDERS='true'
$env:RADAR_SEARCH_PROVIDER='firecrawl'
$env:RADAR_PAGE_PROVIDER='firecrawl'
$env:FIRECRAWL_API_KEY='fc-...'
python -m pytest tests/test_scraping_adapters.py -v -k firecrawl
```

### 6. Providers suportados

| Provider | Search | Page | Status |
|---|---|---|---|
| `fixture` | StaticSeedCollector (mock) | HtmlPageContentAdapter (mock) | Sempre disponível |
| `firecrawl` | FirecrawlSearchAdapter | FirecrawlPageAdapter | Requer API key |
| `serpapi` | SerpApiSearchAdapter | — | Alternativo (fallback) |

## Testes

Com as dependencias instaladas no ambiente Python 3.12:

```powershell
cd ai-agent-system
python -m pytest
```
