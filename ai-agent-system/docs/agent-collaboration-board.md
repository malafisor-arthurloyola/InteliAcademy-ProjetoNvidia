# Agent Collaboration Board

Este arquivo funciona como um quadro compartilhado para Codex e Opencode colaborarem no projeto NVIDIA Startup AI Radar sem depender apenas de copia-e-cola manual.

Ele nao substitui o handoff unico do Obsidian. Use este arquivo como canal de trabalho curto entre agentes.

## Como usar

1. Antes de trabalhar, leia:
   - `ai-agent-system/docs/Projeto_ NVIDIA Startup AI Radar (1).md`
   - `C:\Users\Inteli\Desktop\Projeto Nvidia\Sessao 2026-06-14 - Handoff para Proximo Agente.md`
   - `AGENTS.md`
   - `ai-agent-system/docs/agent-collaboration-board.md` (este quadro)
2. Consulte as skills do projeto:
   - `ai-agent-system/skills/SKILLS_INDEX.md`
   - Leia a SKILL.md da skill relevante antes de codificar.
3. Leia este quadro inteiro.
4. Atualize apenas a sua area ou a area explicitamente combinada.
5. Declare quais arquivos pretende tocar antes de editar codigo.
6. Firecrawl autorizado com `RADAR_ENABLE_EXTERNAL_PROVIDERS=true`. Outras APIs externas sem autorizacao explicita do usuario.
7. Use sempre o Python do venv do projeto.
8. Nao commite segredos, `.env`, `venv`, caches ou arquivos sensiveis.

## Papeis sugeridos

### Codex

Responsavel preferencial por:

- implementacao;
- testes;
- commits e push;
- atualizacao do Obsidian e handoff;
- organizacao do repo e validacao final.

### Opencode

Responsavel preferencial por:

- revisao tecnica;
- arquitetura;
- riscos;
- alinhamento com documento-fonte;
- sugestoes de melhoria;
- avaliacao de diffs antes/depois de mudancas maiores.

## Regras de colaboracao

- Evitar dois agentes editando os mesmos arquivos ao mesmo tempo.
- Se um agente precisar editar arquivo de codigo, registrar antes em `Arquivos reservados`.
- Se houver conflito entre sugestoes, priorizar:
  1. documento-fonte do projeto;
  2. `AGENTS.md`;
  3. handoff unico;
  4. testes existentes;
  5. decisao explicita do usuario.
- Placeholders deterministicos devem continuar existindo como mocks/fallbacks de teste.
- APIs externas estao fail-closed por padrao.
- Se um agente precisar de acao do usuario, deve atualizar `Acao necessaria do usuario` e tambem avisar no chat.
- Pedidos de API key, autorizacao de rede, custo, MCP/plugin, provider externo ou decisao de arquitetura nao devem ficar escondidos apenas neste arquivo.

## Estado atual resumido

O projeto ja possui:

- LangGraph com pipeline principal;
- schemas internos;
- adapters e normalizers;
- validacao de evidencia;
- retry policy;
- erros estruturados de coleta;
- caveats no briefing;
- safety switch para providers externos;
- testes automatizados;
- FastAPI CRUD com SQLite + Qdrant;
- RAG enricher com trafilatura;
- Frontend React (Toph) com 7 paginas API-driven;
- Providers externos autorizados: Firecrawl, Groq, OpenAI, Gemini.

Fase concluida:

```text
Fase 1: Estrutura base, schemas, LangGraph, validacao, testes.        ✅
Fase 2: Scraping real (Firecrawl, Playwright/trafilatura).             ✅
Fase 3: LLM no Extractor/Classifier (Groq + fallback Gemini/OpenAI).   ✅
Fase 4a: RAG NVIDIA (Qdrant + sentence-transformers).                  ✅
Fase 4b: Frontend dashboard completo com API real.                     ✅
```


## Status para o usuario

Resumo atual:

```text
Pipeline em background estabilizado na main.
Backend FastAPI, SQLite/Alembic, LangGraph, RAG NVIDIA e frontend /pipeline validados juntos por testes automatizados e build.
A pagina /pipeline agora mostra steps reais via GET /runs/{id}; VITE_API_BASE_URL e respeitado no frontend.
Profile permanece mock (baixa prioridade); producao ainda pede worker/fila e PostgreSQL.
```

Ultima atualizacao:

```text
2026-06-29 - Codex corrigiu contrato de progresso do pipeline, persistencia de status terminal e validou pytest/build/alembic.
```
Proxima verificacao sugerida:

```text
Subir backend + frontend localmente e fazer smoke test manual com uma query real autorizada, observando progresso por step e recomendacoes.
```

## Acao necessaria do usuario

Status: nenhuma no momento.

Usuario autorizou Firecrawl/LLM configurados no .env local para testes controlados. Nao usar outras APIs externas, custos ou providers novos sem nova autorizacao explicita.

Use esta secao quando algo depender diretamente do usuario.

Modelo de preenchimento:

```text
Status: pendente
Pedido:
- O que o usuario precisa fazer ou autorizar.

Por que:
- Motivo tecnico ou de produto.

Risco/custo:
- Custo financeiro, uso de quota, risco de segredo, risco de mudanca grande ou impacto no projeto.

Como fazer:
- Passos concretos para o usuario.

Solicitado por:
- Codex ou Opencode.

Data:
- YYYY-MM-DD.
```

Exemplo:

```text
Status: pendente
Pedido:
- Autorizar um teste controlado com SerpAPI usando 1 query.

Por que:
- Validar se o provider real gera SourceCandidate no formato esperado.

Risco/custo:
- Pode consumir quota ou gerar custo pequeno. Nenhuma chave deve ser commitada.

Como fazer:
- Adicionar SERPAPI_API_KEY apenas no .env local e confirmar no chat que autoriza o teste.

Solicitado por:
- Codex.

Data:
- 2026-06-20.
```

## Tarefa em andamento

Status: concluido por Codex.

Objetivo atual:

```text
Estabilizar UX do pipeline em background: contrato de steps, persistencia final, testes assincronos, README e validacoes.
```
## Arquivos reservados

Agente: Codex
Arquivos:
- ai-agent-system/docs/agent-collaboration-board.md
- ai-agent-system/src/radar/settings.py
- ai-agent-system/tests/test_external_provider_settings.py
Motivo:
- Garantir que o backend leia o .env da raiz do repo e permita preflight real autorizado sem imprimir segredos.
Inicio:
- 2026-06-21
Fim:
- 2026-06-22


Agente: Codex
Arquivos:
- ai-agent-system/docs/agent-collaboration-board.md
- ai-agent-system/src/radar/agents/recommendation.py
- ai-agent-system/src/radar/agents/nvidia_rag.py
- ai-agent-system/src/radar/agents/extractor.py (somente se o diagnostico confirmar mistura/nome errado de startup)
- ai-agent-system/tests/test_recommendation_mapping.py
- ai-agent-system/tests/test_rag_pipeline.py (somente se alterar RAG)
Motivo:
- Corrigir o caso real em que o pipeline encontra fontes/classifica startup, mas retorna recommendations vazio.
Inicio:
- 2026-06-22
Fim:
- 2026-06-22

Agente: Codex
Branch:
- feat/frontend-pages
Arquivos:
- ai-agent-system/docs/agent-collaboration-board.md
- frontend/src/routes/startup.$id.tsx
- frontend/src/routes/briefing.tsx
- frontend/src/routes/contacts.tsx
- frontend/src/lib/api.ts (somente se faltar tipo/helper)
- frontend/src/lib/hooks/* (somente se precisar hook auxiliar)
- frontend/src/routeTree.gen.ts (se build atualizar)
- Documents/Relatorio de Progresso.md
Motivo:
- Migrar paginas frontend combinadas para dados reais da FastAPI, usando associacao temporaria por nome/query enquanto startup_id no run ainda vem nulo.
Inicio:
- 2026-06-22
Fim:
- pendente

Agente: Codex
Branch:
- feat/frontend-pages
Arquivos:
- ai-agent-system/docs/agent-collaboration-board.md
- frontend/src/routes/startup.$id.tsx
- frontend/src/routes/briefing.tsx
- frontend/src/routes/contacts.tsx
- frontend/src/lib/api.ts (somente se faltar tipo/helper)
- frontend/src/lib/hooks/* (somente se precisar hook auxiliar)
- frontend/src/routeTree.gen.ts (se build atualizar)
- Documents/Relatorio de Progresso.md
Motivo:
- Migrar paginas frontend combinadas para dados reais da FastAPI, usando associacao temporaria por nome/query enquanto startup_id no run ainda vem nulo.
Inicio:
- 2026-06-22
Fim:
- pendente
Quando um agente for editar, registrar assim:

```text
Agente: Codex ou Opencode
Arquivos:
- caminho/do/arquivo.py
Motivo:
- resumo curto
Inicio:
- YYYY-MM-DD HH:MM
Fim:
- 2026-06-21 ou concluido
```

## Mensagem para Codex

Resultado Codex (2026-06-21):
- Inventario de API real vs dados mockados registrado no Relatorio e handoff.
- `.gitignore` atualizado para ignorar `ai-agent-system/src/radar/database/radar.db` e arquivos auxiliares.
- Proximo commit deve expor fontes/evidencias reais no backend reaproveitando `source_documents` e `evidence_claims`.


Resultado Codex (2026-06-21):
- `nvidia_rag.py`: normalizacao/cast explicito de chunks vindos do Qdrant antes de montar `NvidiaKnowledgeChunk`.
- `api/app.py`: retorno de `/runs` tipado como `dict[str, Any]` e serializado com `jsonable_encoder`.
- Validacoes: `pip check` ok, `ruff check src/radar tests` ok, `pytest` 145 passed, 2 warnings conhecidos.

Resultado Opencode (2026-06-22):
- Branch `feat/frontend-features`:
  - `ranking.tsx`: ordenacao por coluna + paginacao (10/25/50) + export CSV
  - `sources.tsx`: export CSV
  - `lib/export-csv.ts` (novo): utility de CSV com UTF-8 BOM
- npm run build ok, merged em main (commit `a6a7939`).

Resultado Opencode (2026-06-22, Fase 5):
- Branch `feat/alembic-deploy`:
  - Alembic setup: `alembic.ini`, `env.py`, `script.py.mako`, migracao `0001_initial_schema.py`
  - `app.py`: lifespan executa `alembic upgrade head` via API Python
  - `GET /health/db`: retorna tabelas + tamanho do banco
  - `start.ps1`: script de setup local (ativa venv → migra → instrucoes)
- pytest 129 passed, upgrade/downgrade alembic OK.

## Mensagem para agentes

Ambas as branches concluidas e merged em main.
Nenhum conflito registrado em todo o ciclo.
Proximas fases: features faltantes (Fase 7) ou producao (Fase 8).
## Decisoes tomadas

- Primeiro estruturar base, schemas, LangGraph, validacao e testes.
- Conectar scraping real antes de LLMs.
- Manter mocks/fixtures como bancada permanente de testes.
- Nao usar APIs externas sem autorizacao explicita.
- Usar ferramentas recomendadas no documento-fonte: LangGraph, Python/FastAPI, PostgreSQL, Qdrant, Playwright/BeautifulSoup/Scrapy/Firecrawl/trafilatura, busca hibrida/BM25/vetorial e Cohere Rerank.

## Bloqueios

Nenhum bloqueio ativo.

## Perguntas abertas

- Qual provider real de busca/coleta sera usado primeiro?
- O primeiro teste real sera com SerpAPI, Firecrawl, Playwright/trafilatura ou outra opcao?
- Persistencia entrara com PostgreSQL direto ou SQLite apenas como MVP local documentado?

## Proxima acao sugerida

1. Codex propoe uma pequena mudanca tecnica.
2. Opencode revisa riscos e alinhamento.
3. Codex implementa se aprovado.
4. Rodar validacoes:

```powershell
cd ai-agent-system
..\venv\Scripts\python.exe -m pip check
..\venv\Scripts\python.exe -m pytest
```

5. Atualizar Obsidian/handoff quando houver progresso relevante.
6. Commitar e fazer push se houver mudanca de repo relevante.

## Log curto de colaboracao

- 2026-06-20: Quadro criado para permitir colaboracao assincrona entre Codex e Opencode via arquivo compartilhado.
- 2026-06-20: Adicionadas secoes de status para o usuario e acao necessaria do usuario.
- 2026-06-20: Codex concluiu preflight offline de providers (`provider_preflight.py`) com `pytest -> 43 passed`, `pip check` ok e `ruff` ok.
- 2026-06-20: Codex expos `GET /providers/preflight` na API, com `pytest -> 44 passed`, `pip check` ok e `ruff` ok; nenhuma API externa usada.
- 2026-06-20: Opencode revisou e aprovou rota, teste e warning. Numeracao do board corrigida definitivamente.
- 2026-06-20: Codex adicionou adapter offline de HTML bruto com BeautifulSoup; validacoes: pip check ok, pytest 46 passed, ruff ok; nenhuma API externa usada.
- 2026-06-20: Agente unico melhorou Extractor (setor, produto, founders, funding, tecnologias) e Classifier (scoring multidimensional, thresholds) — pytest 64 passed, ruff ok, 18 novos testes.
- 2026-06-20: FirecrawlSearchAdapter e FirecrawlPageAdapter reais implementados. Pipeline end-to-end testado com dados reais: 7 fontes, classificacao AI-Native 95%. pytest 68 passed, ruff ok.
- 2026-06-20: skill `firecrawl-skill` criada, README atualizado com setup de env/API keys/safety switch, Relatorio de Progresso atualizado, Handoff atualizado, .env.example atualizado com firecrawl provider options, Obsidian note "Firecrawl Setup.md" criada.
- 2026-06-20: PlaywrightPageAdapter implementado (Chromium headless + trafilatura). `settings.py`, `provider_factory.py`, `provider_preflight.py` atualizados. 9 novos testes. pytest 77 passed, ruff ok.
- 2026-06-20: LLM adapter system implementado (Groq primario + OpenAI/Gemini fallback). `src/radar/llm/` criado com adapters e prompts. Extractor e Classifier com LLM + fallback deterministico. 15 novos testes. pytest 92 passed, ruff ok. Handoff, Relatorio, README, Obsidian atualizados.
- 2026-06-29: Codex estabilizou progresso real do pipeline em background, corrigiu status terminal/persistencia SQLite, alinhou frontend `completed -> done`, validou `ruff`, `pip check`, `pytest 155 passed`, `npm run build`, Alembic upgrade/downgrade e smoke backend+frontend `/pipeline`.
