# Ferramentas MCP

Servidor: `git-ai-agent-mcp`, transporte `stdio`. Logs não são escritos em stdout.

| Tool | Entrada principal | Efeito |
|---|---|---|
| `git_status` | `repo` | Leitura |
| `git_diff` | `repo` | Leitura e fingerprint |
| `git_review` | `repo` | Review local estruturado |
| `prepare_commit` | `repo`, `message?` | Cria sessão; não altera Git |
| `execute_commit` | `session_id`, `repo`, `approved=true`, `message?` | Revalida e commita |
| `execute_push` | `repo`, `approved=true` | Push separado |
| `git_log` | `repo`, `limit` | Histórico resumido |
| `git_branch` | `repo` | Branch e remotes |

Erros são acionáveis e serializados pelo protocolo. `execute_commit` falha se sessão, repositório, branch, diff, mensagem, testes ou scan não coincidirem. `execute_push` não oferece force-push.
