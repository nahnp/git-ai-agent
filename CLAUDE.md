# CLAUDE.md — Memória Permanente do Projeto

> Este arquivo é a fonte de verdade operacional do **git-ai-agent**. Qualquer agente (humano ou IA) que trabalhe neste repositório deve ler este documento antes de tocar em qualquer linha de código.

## 1. Objetivo

`git-ai-agent` é uma ferramenta CLI + servidor MCP (Model Context Protocol) que automatiza e eleva a qualidade do fluxo de trabalho Git/GitHub usando IA: revisão de código, segurança, performance, geração de commits semânticos, changelogs e releases — com o desenvolvedor sempre no controle final (human-in-the-loop).

## 2. Escopo

**Dentro do escopo:**
- Wrapper inteligente sobre Git (status, diff, add, commit, push, pull, branch, merge, stash, revert, restore, reset, fetch, log, cherry-pick).
- Integração com GitHub via `gh` CLI / API (PRs, releases, issues).
- Motor de revisão por IA (código, segurança, arquitetura, performance).
- Execução orquestrada de testes, lint e scanners de segredo.
- Geração de Conventional Commits e changelogs.
- Exposição de todas as capacidades acima como **ferramentas MCP**, consumíveis por qualquer cliente MCP (Claude Code, Claude Desktop, IDEs compatíveis).

**Fora do escopo (v1):**
- Suporte a outros provedores de Git hosting (GitLab, Bitbucket) — planejado, não v1.
- UI gráfica própria.
- Hospedagem de modelos de IA — o projeto consome modelos via API, não treina nem serve modelos.

## 3. Princípios

1. **Human-in-the-loop sempre** — nenhuma operação destrutiva (push, commit, reset --hard, force) executa sem confirmação explícita.
2. **Nada de mágica silenciosa** — toda decisão da IA é explicada e logada.
3. **Fail-safe, não fail-silent** — erros nunca são engolidos; sempre reportados com contexto acionável.
4. **Composability** — cada ferramenta MCP é independente e testável isoladamente.
5. **Zero TODOs em código mergeado** — código incompleto não entra na branch principal.
6. **Documentação é código** — PRs que mudam comportamento sem atualizar docs são rejeitados.

## 4. Arquitetura (resumo — ver ARCHITECTURE.md)

```
git_ai_agent/
├── domain/          # Entidades e regras de negócio puras (sem I/O)
├── application/     # Casos de uso, orquestração dos fluxos (ex: fluxo de commit)
├── infrastructure/  # Adapters: GitPython, httpx (GitHub API), filesystem, subprocess
├── engines/
│   ├── git_engine/
│   ├── github_engine/
│   ├── review_engine/      # code/security/architecture/performance review
│   ├── security_engine/    # scanners de segredo, SAST leve
│   └── testing_engine/     # runners de pytest/lint
├── mcp/             # Camada MCP — exposição das tools via FastMCP
├── cli/             # Interface Typer
├── config/          # Carregamento e validação de configuração (Pydantic + YAML)
└── logging/         # Logging estruturado
```

Camadas seguem Clean Architecture: `domain` não depende de nada; `application` depende de `domain`; `infrastructure`/`engines` implementam interfaces definidas em `domain`/`application`; `mcp` e `cli` são pontos de entrada (entrypoints) que orquestram `application`.

## 5. Regras Permanentes

- Python ≥ 3.12, tipagem estrita (`mypy --strict`).
- 100% das funções públicas com type hints e docstring (Google style).
- Toda nova ferramenta MCP exige: implementação + teste unitário + teste de integração + entrada em `docs/mcp-tools.md`.
- Nenhum `print()` em código de produção — usar o logger estruturado.
- Nenhuma chamada de rede sem timeout explícito.
- Segredos nunca em código ou em commits — sempre via variáveis de ambiente / `.env` (git-ignorado).

## 6. Padrões de Código

- Formatação e lint: `ruff` (substitui black + flake8 + isort).
- Tipagem: `mypy --strict`.
- Commits: Conventional Commits (`feat:`, `fix:`, `docs:`, `refactor:`, `test:`, `chore:`, `perf:`, `ci:`).
- Branches: `feature/<slug>`, `fix/<slug>`, `chore/<slug>`, partindo sempre de `main`.
- Um Pull Request = uma entrega funcional, testada e documentada.

## 7. Fluxo Git do Projeto

1. Criar branch a partir de `main`.
2. Implementar uma única tarefa do `TASKS.md`.
3. Rodar `ruff check`, `mypy`, `pytest` localmente.
4. Abrir PR com descrição estruturada (contexto, mudança, testes, impacto).
5. CI deve passar (lint + types + tests + build).
6. Merge via squash, mensagem final em Conventional Commits.

## 8. Como Adicionar uma Nova Ferramenta MCP

1. Definir o contrato (input/output) em `domain/` se introduzir novo conceito de negócio.
2. Implementar o caso de uso em `application/`.
3. Implementar o adapter necessário em `infrastructure/` ou `engines/`.
4. Expor via decorator `@mcp.tool()` em `mcp/tools/<nome>.py`.
5. Escrever testes unitários (`tests/unit/`) e de integração (`tests/integration/`).
6. Documentar em `docs/mcp-tools.md` (nome, descrição, schema de input/output, exemplo).
7. Atualizar `CHANGELOG.md`.

## 9. Como Escrever Testes

- Framework: `pytest`.
- Estrutura: `tests/unit/<camada>/test_<modulo>.py`, `tests/integration/test_<fluxo>.py`.
- Mínimo de cobertura por módulo novo: 85%.
- Testes de integração com Git usam repositórios temporários reais (`tmp_path` + `git init`), nunca mocks de `git` em si.
- Chamadas a APIs externas (GitHub) sempre mockadas via `respx`/`httpx` mock transport.

## 10. Como Executar Lint e CI Localmente

```bash
ruff check .
ruff format --check .
mypy --strict src/
pytest --cov=src --cov-report=term-missing
```

Pre-commit hook (`pre-commit run --all-files`) executa as quatro etapas acima automaticamente.

## 11. Como Publicar Releases

1. Garantir que `main` está verde no CI.
2. Gerar changelog incremental via ferramenta `generate_changelog` do próprio agente (dogfooding).
3. Criar tag semântica (`vMAJOR.MINOR.PATCH`).
4. `gh release create` com changelog como corpo.
5. Publicar pacote no PyPI (`twine upload`) — automatizado via GitHub Actions na tag.

## 12. Como Contribuir

Ver `CONTRIBUTING.md`. Resumo: uma issue/tarefa por PR, testes obrigatórios, descrição clara, sem quebra de compatibilidade sem registro em `DECISIONS.md`.

## 13. Stack

Python 3.12+, FastMCP, GitPython, Pydantic v2, Typer, Rich, PyYAML, httpx, pytest, ruff, mypy, pre-commit, Docker, GitHub Actions, GitHub CLI (`gh`).

## 14. Checklist — Antes de Cada Commit

- [ ] `ruff check .` sem erros
- [ ] `mypy --strict` sem erros
- [ ] `pytest` 100% verde
- [ ] Nenhum `TODO`/`FIXME`/`print` introduzido
- [ ] Mensagem de commit em Conventional Commits

## 15. Checklist — Antes de Abrir Pull Request

- [ ] Branch atualizada com `main`
- [ ] Documentação relevante atualizada (`README`, `docs/`, `ARCHITECTURE.md` se aplicável)
- [ ] `CHANGELOG.md` atualizado
- [ ] Testes novos cobrindo o comportamento adicionado
- [ ] Descrição do PR explica contexto, decisão e trade-offs

## 16. Checklist — Antes de Publicar Release

- [ ] Todos os PRs do milestone mergeados
- [ ] CI verde em `main`
- [ ] `CHANGELOG.md` finalizado para a versão
- [ ] Tag semântica criada
- [ ] Release notes publicadas no GitHub
- [ ] Pacote publicado no PyPI

## 17. Atualização deste Documento

Este arquivo deve ser atualizado **imediatamente** sempre que uma decisão estrutural for tomada. Toda atualização aqui deve ter uma entrada correspondente em `DECISIONS.md`.
