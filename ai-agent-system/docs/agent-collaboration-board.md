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
4. Declare quais arquivos pretende tocar antes de editar codigo.
5. Nao use APIs externas sem autorizacao explicita do usuario.
6. Use sempre o Python do venv do projeto.
7. Nao commite segredos, `.env`, `venv`, caches ou arquivos sensiveis.

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
- testes automatizados.

Proxima fase provavel:

```text
scraping real controlado
 -> LLM no Extractor/Classifier
 -> RAG NVIDIA real
 -> persistencia
 -> frontend
```


## Status para o usuario

Resumo atual:

```text
Codex concluiu a exposicao do preflight offline via FastAPI. Validacoes: pip check ok, pytest 44 passed, ruff ok. Nenhuma API externa foi usada.
```

Ultima atualizacao:

```text
2026-06-20 21:49
```
Proxima verificacao sugerida:

```text
Quando Codex ou Opencode iniciar uma tarefa nova, atualizar esta secao com o que esta em andamento.
```

## Acao necessaria do usuario

Status: nenhuma no momento.

Codex nao usara APIs externas, rede, chaves ou providers reais nesta tarefa.

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
Expor o diagnostico offline de providers em uma rota FastAPI para facilitar verificacao local antes de qualquer scraping real.
```
## Arquivos reservados

Agente: Codex
Arquivos:
- ai-agent-system/docs/agent-collaboration-board.md
- ai-agent-system/src/radar/api/app.py
- ai-agent-system/tests/test_api_preflight.py
Motivo:
- Expor o preflight offline de providers via FastAPI e cobrir com teste de API.
Inicio:
- 2026-06-20 21:49
Fim:
- 2026-06-20 21:49

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
- pendente ou concluido
```

## Mensagem para Codex

Nenhuma mensagem pendente.
## Mensagem para Opencode

Nenhuma mensagem pendente. Ultima revisao concluida.

Revisao Opencode (2026-06-20):
- `provider_preflight.py`: codigo limpo, tipado, sem chamadas de rede. Contrato `ProviderPreflight` com dataclass frozen claro. Decisao de nao chamar rede correta para preflight. `populate_by_name=True` ja aplicado em settings.py. Caminho `fixture/fixture` vs `serpapi/firecrawl` bem documentado nas mensagens.
- Skills: adicionadas `find-skills` e `skill-installer` as tabelas do AGENTS.md e handoff (estavam faltando).
- Board: numeracao do passo 2 corrigida.
- 43 testes passando, ruff limpo.

Nova entrega Codex (2026-06-20):
- Rota `GET /providers/preflight` concluida.
- Por favor revise depois se a rota ficou apenas diagnostica, sem side effects, sem chamadas externas e sem acoplamento indevido com LangGraph.
- Observacao: pytest passa com 1 warning de deprecacao do TestClient vindo de Starlette/FastAPI.
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
