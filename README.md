# git-ai-agent

Ferramenta local de revisão e aprovação segura de alterações Git, disponível como CLI e servidor MCP. O protótipo lê status, branch, remotes, histórico e diff; detecta linguagens e riscos; executa lint/testes configurados; gera relatório estruturado e mensagem Conventional Commit; e só altera o repositório mediante aprovações verificáveis.

## Para quem e por quê

- **Negócio:** reduz falhas operacionais entre código pronto e código publicado, mantendo rastreabilidade e decisão humana.
- **Tecnologia:** oferece uma fronteira comum, extensível e local-first para automação Git via terminal ou MCP.
- **Desenvolvimento:** padroniza review, checks, commit e push sem esconder etapas ou exigir uma API de IA.

## Arquitetura

`domain` contém contratos puros; `application` orquestra a aprovação; `infrastructure` fala com Git; `engines` fazem review, segurança e testes; `cli` e `mcp` apenas traduzem entradas e saídas. A direção das dependências preserva o domínio independente de Typer, FastMCP e subprocessos.

Fluxo seguro: `review → prepare-commit → sessão imutável → aprovação explícita → revalidação → add/commit`. O `push` é separado e pede nova aprovação.

## Requisitos e instalação

- Python 3.12+
- Git disponível no `PATH`
- Repositório alvo confiável

```bash
python -m venv .venv
# Linux/macOS: source .venv/bin/activate
# Windows: .venv\Scripts\activate
python -m pip install -e ".[dev]"
git-ai-agent config-check
```

## Uso via CLI

```bash
git-ai-agent status --repo .
git-ai-agent diff --repo .
git-ai-agent branch --repo .
git-ai-agent log --repo . --limit 10
git-ai-agent review --repo . --json
git-ai-agent prepare-commit --repo . --message "feat(cli): add safe workflow"
git-ai-agent commit --repo . --session-id ID_RETORNADO --approve
git-ai-agent push --repo . --approve
```

`status`, `diff`, `branch`, `log`, `review` e `prepare-commit` não modificam o Git. O commit é recusado se a sessão não existir, expirar, apontar para outro repositório ou branch, se o diff/mensagem mudar, se um check falhar ou se um segredo for detectado. O push nunca é implícito e não há force-push.

## Uso via MCP

Inicie com:

```bash
git-ai-agent-mcp
```

Configure o cliente MCP para executar esse comando por `stdio`. Tools: `git_status`, `git_diff`, `git_review`, `prepare_commit`, `execute_commit`, `execute_push`, `git_log` e `git_branch`. Consulte [docs/mcp-tools.md](docs/mcp-tools.md).

## Configuração

Use `config/default.yaml` como base e passe um arquivo com `--config` nos comandos que aceitam configuração. Lint e testes são listas de argumentos, por exemplo `[["pytest", "-q"]]`; não há execução por shell. Etapas vazias aparecem como `skipped (config)`. Veja [docs/configuration.md](docs/configuration.md).

Por padrão, o review é local e determinístico. Nenhum diff é enviado a APIs. `AIReviewer` é uma interface de extensão, mas o protótipo não inclui adapter remoto nem armazena credenciais.

## Relatórios

O review retorna JSON serializável com repositório, branch, fingerprint SHA-256, arquivos, linguagens, estatísticas, findings, checks e estado do review de IA. A saída CLI legível usa Rich; `--json` atende automações. O conteúdo sensível encontrado é mascarado: o relatório identifica a regra, não repete o valor.

## Segurança e limitações

O scanner cobre chaves privadas, URLs com credenciais, variáveis suspeitas, tokens GitHub e chaves AWS comuns. É uma barreira preventiva simples, não substitui Gitleaks, scanners de CI, rotação de credenciais ou revisão especializada. Se um segredo real já foi exposto, considere-o comprometido e rotacione-o.

Lint e testes podem executar código arbitrário do projeto. Use-os somente em repositórios confiáveis e, para terceiros, prefira isolamento. O protótipo limita tempo, tamanho do diff e saída dos comandos; valida diretórios permitidos quando configurados; não implementa reset, clean, restore, revert, force-push, pull automático, PRs ou releases.

## Desenvolvimento e testes

```bash
ruff check .
ruff format --check .
mypy --strict src/
pytest --cov=src --cov-report=term-missing
python -m build
```

Os testes de integração criam repositórios Git reais em diretórios temporários e cobrem status, diff, branch, commit, push para remote local, mudança após preparação, segredo e falha de testes.

## Estrutura

```text
src/git_ai_agent/
├── domain/          # modelos e ports
├── application/     # sessão e workflow de commit
├── infrastructure/  # adapter Git seguro
├── engines/         # review, segurança e testes
├── cli/             # Typer + Rich
├── mcp/             # FastMCP stdio
└── config/          # YAML + ambiente
tests/{unit,integration}/
docs/  config/  examples/  output/
```

## Roadmap

Próximos incrementos: integração opcional com Gitleaks; adapter de IA explicitamente consentido; análise semântica adicional; allowlist auditável; suporte GitHub a PRs/releases; sessões concorrentes com backend configurável; e hardening multiplataforma. Consulte [ROADMAP.md](ROADMAP.md).

## Governança

Veja [ARCHITECTURE.md](ARCHITECTURE.md), [DECISIONS.md](DECISIONS.md), [CONTRIBUTING.md](CONTRIBUTING.md), [SECURITY.md](SECURITY.md) e [docs/business-overview.md](docs/business-overview.md). Licença MIT.
