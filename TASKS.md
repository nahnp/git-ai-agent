# TASKS.md — Backlog

> Regra fixa: **uma tarefa por vez**. Nunca iniciar a próxima Task antes de concluir (implementação + testes + docs) a atual.

Hierarquia: Epic → Feature → Story → Task → Subtask.

---

## EPIC 1 — Fundação do Projeto

### Feature 1.1 — Documentação Inicial
- **Story 1.1.1**: Como mantenedor, quero toda a documentação base criada antes do código.
  - **Task 1.1.1.1** — Criar CLAUDE.md, PROJECT_SPEC.md, ARCHITECTURE.md ✅ *(esta entrega)*
    - Critério de aceite: arquivos completos, sem placeholders, revisados.
    - Prioridade: P0 | Dependências: nenhuma | Estimativa: concluída | Status: **Done**
  - **Task 1.1.1.2** — Criar TASKS.md, ROADMAP.md, DECISIONS.md, CHANGELOG.md ✅ *(esta entrega)*
    - Status: **Done**
  - **Task 1.1.1.3** — Criar README.md, CONTRIBUTING.md, SECURITY.md, CODE_OF_CONDUCT.md, LICENSE ✅ *(esta entrega)*
    - Status: **Done**
  - **Task 1.1.1.4** — Criar esqueleto de `docs/`, `examples/`, `.github/`, `.devcontainer/`, `.claude/`, `config/` ✅ *(esta entrega)*
    - Status: **Done**

### Feature 1.2 — Bootstrap do Pacote Python
- **Story 1.2.1**: Como contribuidor, quero um pacote instalável e configurado para qualidade desde o primeiro commit.
  - **Task 1.2.1.1** — Criar `pyproject.toml` (build system, dependências, ruff, mypy, pytest config)
    - Critério de aceite: `pip install -e .` funciona; `ruff`, `mypy`, `pytest` configurados.
    - Prioridade: P0 | Dependências: 1.1 | Estimativa: 1 entrega | Status: **Próxima tarefa**
  - **Task 1.2.1.2** — Criar estrutura `src/git_ai_agent/` (pacotes vazios com `__init__.py` documentado, sem lógica)
    - Status: **Backlog**
  - **Task 1.2.1.3** — Configurar `pre-commit` (ruff, mypy, pytest rápido, detect-secrets)
    - Status: **Backlog**
  - **Task 1.2.1.4** — Configurar GitHub Actions CI (lint, types, tests, build) em `.github/workflows/ci.yml`
    - Status: **Backlog**

---

## EPIC 2 — Domain & Configuração

### Feature 2.1 — Modelagem de Domínio
- **Task 2.1.1** — Definir entidades `Commit`, `Diff`, `FileChange`, `Severity`, `ReviewFinding`, `ReviewReport` (Pydantic, imutáveis)
- **Task 2.1.2** — Definir interfaces (Protocols): `GitRepository`, `AIReviewer`, `GitHostProvider`, `SecretScanner`, `TestRunner`

### Feature 2.2 — Sistema de Configuração
- **Task 2.2.1** — Schema de configuração YAML (`config/default.yaml`) + loader Pydantic com validação e override por env vars
- **Task 2.2.2** — Documentar todas as chaves de configuração em `docs/configuration.md`

---

## EPIC 3 — Git Engine + CLI Básica

- **Task 3.1** — Implementar `GitPythonRepository` (status, diff, add, commit, push, pull)
- **Task 3.2** — Implementar `git status` / `git diff` como comandos CLI (Typer) + saída Rich
- **Task 3.3** — Implementar checkout, merge, stash, revert, restore, reset, fetch, log, cherry-pick, branch
- **Task 3.4** — Testes de integração com repositórios Git reais em `tmp_path`

---

## EPIC 4 — Camada MCP

- **Task 4.1** — Setup do servidor FastMCP (`mcp/server.py`), transporte stdio
- **Task 4.2** — Expor as operações Git do Epic 3 como ferramentas MCP
- **Task 4.3** — Documentar contrato de cada tool em `docs/mcp-tools.md`
- **Task 4.4** — Testes de integração via cliente MCP de teste

---

## EPIC 5 — Review Engine

- **Task 5.1** — `CodeReviewAnalyzer` (qualidade, estilo, complexidade)
- **Task 5.2** — `SecurityReviewAnalyzer` (padrões inseguros, injeção, segredos no diff)
- **Task 5.3** — `ArchitectureReviewAnalyzer` (violação de camadas, acoplamento)
- **Task 5.4** — `PerformanceReviewAnalyzer` (padrões custosos conhecidos: N+1, loops ineficientes)
- **Task 5.5** — Agregador de findings + relatório Markdown/JSON

---

## EPIC 6 — Security & Testing Engine

- **Task 6.1** — Scanner de segredos (regex + entropia, baseado em padrões conhecidos)
- **Task 6.2** — Detector de linguagem por diff
- **Task 6.3** — Runner de testes/lint multi-linguagem (Python primeiro; extensível)

---

## EPIC 7 — GitHub Engine

- **Task 7.1** — `GitHubCliProvider` (PR create, release create, issue list)
- **Task 7.2** — `GitHubApiProvider` (fallback httpx, para CI sem `gh`)
- **Task 7.3** — `GenerateChangelogUseCase` a partir do histórico de commits
- **Task 7.4** — `CreateReleaseUseCase` (tag + release notes + publicação)

---

## EPIC 8 — Pipeline de Commit Completo (Integração)

- **Task 8.1** — `CommitWorkflowUseCase` orquestrando todas as etapas do fluxo descrito em CLAUDE.md §7
- **Task 8.2** — Modo interativo (aprovação humana) e modo `--yes`/`--ci`
- **Task 8.3** — Testes end-to-end do pipeline completo

---

## EPIC 9 — Hardening e Release v1.0

- **Task 9.1** — Auditoria de cobertura (≥85%) e gaps de teste
- **Task 9.2** — Revisão de documentação completa (README, docs/, exemplos)
- **Task 9.3** — Publicação no PyPI + primeira GitHub Release v1.0.0

---

## Status Atual

✅ Epic 1 / Feature 1.1 — concluída nesta entrega.
➡️ **Próxima tarefa: Task 1.2.1.1 — `pyproject.toml`.**
