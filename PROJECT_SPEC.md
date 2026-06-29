# PROJECT_SPEC.md — Especificação Funcional

## 1. Objetivos

- Reduzir o tempo entre "código escrito" e "código commitado com qualidade verificada".
- Padronizar revisão de código (estilo, segurança, arquitetura, performance) usando IA, de forma auditável.
- Tornar o fluxo Git/GitHub acessível via linguagem natural e via protocolo MCP, sem abrir mão de controle humano.

## 2. Casos de Uso

| ID | Caso de Uso | Ator | Descrição |
|----|-------------|------|-----------|
| UC-01 | Commit assistido | Dev | Dev pede "faça commit"; agente roda pipeline completo (status→diff→testes→lint→scan→review→commit-msg→aprovação→commit→push). |
| UC-02 | Revisão de PR | Dev/CI | Agente analisa diff de uma branch contra `main` e gera relatório de review (qualidade, segurança, arquitetura, performance). |
| UC-03 | Geração de changelog | Maintainer | Agente lê histórico de commits desde a última tag e gera changelog categorizado. |
| UC-04 | Criação de release | Maintainer | Agente cria tag, gera notas de release e publica via `gh release create`. |
| UC-05 | Scan de segredos | Dev/CI | Agente varre diff/working tree por credenciais expostas antes de permitir commit. |
| UC-06 | Rollback assistido | Dev | Agente identifica commit problemático e propõe `revert` seguro, com plano de ação. |
| UC-07 | Consumo via MCP | Cliente MCP (Claude Code etc.) | Qualquer cliente MCP pode invocar as ferramentas do agente como tools nativas. |

## 3. Requisitos Funcionais

- RF-01: O sistema deve expor cada operação Git suportada como ferramenta MCP individual e como comando CLI individual.
- RF-02: O sistema deve nunca executar `commit`, `push`, `reset --hard`, `force-push` ou `revert` sem confirmação explícita do usuário, salvo modo `--yes` explicitamente configurado.
- RF-03: O sistema deve gerar mensagens de commit no formato Conventional Commits a partir do diff analisado.
- RF-04: O sistema deve detectar a(s) linguagem(ns) predominante(s) no diff para selecionar lint/test runners apropriados.
- RF-05: O sistema deve produzir um relatório estruturado (Markdown + JSON) por execução de review, contendo achados categorizados por severidade.
- RF-06: O sistema deve permitir configuração declarativa (YAML) de quais etapas do pipeline são obrigatórias, opcionais ou desabilitadas.
- RF-07: O sistema deve registrar log estruturado de cada execução, com identificador único de sessão.
- RF-08: O sistema deve suportar execução tanto interativa (CLI) quanto não interativa (CI, modo `--yes`/`--ci`).

## 4. Requisitos Não Funcionais

- RNF-01: Tempo de resposta do pipeline de commit (sem chamadas de IA) ≤ 3s para repositórios de até 10k arquivos.
- RNF-02: Nenhuma credencial deve ser persistida em disco fora de variáveis de ambiente/`.env` git-ignorado.
- RNF-03: Cobertura de testes mínima de 85% por módulo.
- RNF-04: Compatibilidade com Linux, macOS e WSL2 (Windows nativo: best-effort).
- RNF-05: Todas as chamadas de rede devem ter timeout e retry com backoff exponencial.
- RNF-06: O sistema deve degradar graciosamente se a API de IA estiver indisponível (pipeline continua sem a etapa de review por IA, com aviso explícito).

## 5. Fluxos Completos

### 5.1 Fluxo de Commit (UC-01)
`git status` → `git diff` → detectar linguagem → testes → lint → scan de segredos → review por IA → relatório → gerar Conventional Commit → aprovação do usuário → `git add` → `git commit` → `git push` → criar PR (opcional).

### 5.2 Fluxo de Review de PR (UC-02)
Buscar diff via `gh pr diff` ou Git local → segmentar por arquivo → rodar engines de review em paralelo (code/security/architecture/performance) → consolidar relatório → opcionalmente publicar como comentário no PR via GitHub API.

### 5.3 Fluxo de Release (UC-04)
Validar `main` verde → gerar changelog desde última tag → criar tag semântica → `gh release create` com notas → (opcional) publicar pacote.

## 6. Usuários

- **Desenvolvedor individual** usando a CLI localmente.
- **Equipe** usando o agente em CI (GitHub Actions) para revisão automática de PRs.
- **Maintainer de projeto open source** usando para changelog/release.
- **Agentes de IA** (Claude Code e similares) consumindo as ferramentas via MCP.

## 7. Restrições

- Não deve depender de serviços proprietários além de: API do modelo de IA configurado e GitHub API/CLI.
- Não deve assumir presença de Docker para uso básico (Docker é opcional, para ambiente isolado).
- Licença MIT — todo código e dependências diretas devem ser compatíveis com MIT.

## 8. Regras de Negócio

- Nenhuma etapa do pipeline de commit pode ser pulada silenciosamente; etapas desabilitadas aparecem explicitamente no relatório como "skipped (config)".
- Um relatório de review com achados de severidade `critical` bloqueia o commit por padrão, exigindo `--force` explícito do usuário para prosseguir.
- Segredos detectados sempre bloqueiam o commit, sem exceção configurável (segurança não é "opt-out").

## 9. Integrações

- **Git** via GitPython + subprocess (fallback).
- **GitHub** via `gh` CLI (preferencial) e GitHub REST API via `httpx` (fallback/CI).
- **IA** via API de modelo configurável (Anthropic API por padrão; arquitetura permite outros provedores via adapter).
- **MCP** via FastMCP, expondo todas as tools sobre stdio e SSE.

## 10. Critérios de Aceite (v1.0)

- Todas as operações Git listadas implementadas como CLI + MCP tool.
- Pipeline de commit completo funcional ponta a ponta, com testes de integração.
- Review engine cobrindo as 4 dimensões (code/security/architecture/performance) com pelo menos um analisador real por dimensão.
- Documentação completa (este conjunto de arquivos) publicada e mantida atualizada.
- CI verde, cobertura ≥ 85%, pacote publicável no PyPI.

## 11. Métricas

- Tempo médio do pipeline de commit.
- Taxa de achados críticos bloqueados antes do merge.
- Cobertura de testes do próprio projeto.
- Número de ferramentas MCP expostas e adotadas (telemetria opt-in, nunca por padrão).

## 12. Roadmap (resumo — ver ROADMAP.md)

v0.1 Documentação e fundação → v0.2 Git Engine + CLI básica → v0.3 MCP Layer → v0.4 Review Engine → v0.5 Security/Testing Engine → v0.6 GitHub Engine (PR/Release) → v1.0 Hardening, docs finais, publicação PyPI.

## 13. Escalabilidade

- Engines projetadas para execução paralela (revisões independentes por dimensão).
- Suporte futuro a múltiplos provedores de Git hosting via interface `GitHostProvider`.
- Suporte futuro a múltiplos provedores de modelo de IA via interface `AIProvider`.
