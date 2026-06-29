# ROADMAP.md

## v0.1 — Fundação (atual)
- Documentação completa do projeto (CLAUDE.md, PROJECT_SPEC.md, ARCHITECTURE.md, TASKS.md, ROADMAP.md, DECISIONS.md, CHANGELOG.md, CONTRIBUTING.md, SECURITY.md, CODE_OF_CONDUCT.md, LICENSE).
- Estrutura de pastas e arquivos de configuração de ambiente (`.devcontainer/`, `.claude/`, `.github/`).

## v0.2 — Bootstrap + Git Engine
- `pyproject.toml`, lint/types/test configurados, CI básico.
- Domain layer (entidades + interfaces).
- Git Engine completo + CLI espelhando todas as operações Git suportadas.

## v0.3 — Camada MCP
- Servidor FastMCP funcional via stdio.
- Todas as ferramentas Git expostas via MCP.
- Documentação de tools MCP.

## v0.4 — Review Engine
- 4 analisadores de review (code/security/architecture/performance).
- Relatórios consolidados Markdown + JSON.

## v0.5 — Security & Testing Engine
- Scanner de segredos.
- Detecção de linguagem e execução de testes/lint multi-linguagem.

## v0.6 — GitHub Engine
- Integração com `gh` CLI e fallback via API.
- Geração de changelog e criação de releases.

## v0.7 — Pipeline de Commit Completo
- `CommitWorkflowUseCase` ponta a ponta, modo interativo e modo CI.
- Testes end-to-end.

## v1.0 — Hardening e Publicação
- Cobertura ≥ 85%, documentação revisada, exemplos completos.
- Publicação no PyPI e primeira GitHub Release oficial.

## Pós v1.0 (exploratório, não comprometido)
- Suporte a GitLab/Bitbucket via `GitHostProvider` adicional.
- Suporte a múltiplos provedores de IA (`AIProvider` plugável).
- Modo "watch": revisão contínua em background durante desenvolvimento.
- Plugin/extension para IDEs além do protocolo MCP padrão.
