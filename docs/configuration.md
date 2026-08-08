# Configuração

O arquivo YAML é validado antes do uso. Comandos são listas de argumentos, nunca strings de shell.

| Chave | Uso |
|---|---|
| `default_repository` | Repositório usado por padrão |
| `protected_branches` | Branches sinalizadas como protegidas |
| `command_timeout_seconds` | Tempo máximo de subprocessos |
| `lint_commands`, `test_commands` | Listas de comandos; vazio aparece como `skipped (config)` |
| `minimum_coverage` | Meta de cobertura documentada |
| `blocking_severity` | Severidade mínima de achados gerais |
| `max_diff_bytes` | Limite antes de recusar análise |
| `approval_ttl_seconds` | Validade da sessão preparada |
| `push_enabled` | Habilita push, ainda sujeito a aprovação separada |
| `ai_provider` | `local` no protótipo; nenhum código sai da máquina |
| `allowed_repository_roots` | Raízes permitidas; vazio aceita qualquer Git local explícito |

Overrides: `GIT_AI_AGENT_DEFAULT_REPOSITORY`, `GIT_AI_AGENT_AI_PROVIDER` e `GIT_AI_AGENT_PUSH_ENABLED`.
O scanner de segredos não possui chave para desligamento.
