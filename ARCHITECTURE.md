# ARCHITECTURE.md

## 1. Visão Geral

`git-ai-agent` segue **Clean Architecture** com elementos de **DDD** (Domain-Driven Design) leve, organizados em camadas concêntricas. Dependências sempre apontam para dentro (em direção ao `domain`).

```mermaid
graph TD
    CLI[CLI - Typer] --> APP[Application Layer]
    MCP[MCP Layer - FastMCP] --> APP
    APP --> DOM[Domain Layer]
    APP --> ENG[Engines]
    ENG --> DOM
    ENG --> INFRA[Infrastructure]
    INFRA --> EXT1[(Git / Filesystem)]
    INFRA --> EXT2[(GitHub API / gh CLI)]
    INFRA --> EXT3[(AI Provider API)]
```

## 2. Camadas

### Domain
Entidades e regras de negócio puras, sem I/O: `Commit`, `Diff`, `ReviewFinding`, `Severity`, `ReleasePlan`. Define também as **interfaces** (Protocols) que `infrastructure` e `engines` implementam — ex.: `GitRepository`, `AIReviewer`, `GitHostProvider`.

### Application
Casos de uso que orquestram o domínio: `CommitWorkflowUseCase`, `ReviewPullRequestUseCase`, `GenerateChangelogUseCase`, `CreateReleaseUseCase`. Não conhece detalhes de Git real, GitHub real ou IA real — depende apenas das interfaces do `domain`.

### Infrastructure
Implementações concretas das interfaces: `GitPythonRepository`, `GitHubCliProvider`, `GitHubApiProvider` (fallback httpx), `AnthropicReviewer`.

### Engines
Coordenadores especializados, construídos sobre `infrastructure`, que encapsulam lógica específica de domínio técnico:
- `git_engine` — operações Git de baixo nível.
- `github_engine` — PRs, releases, issues.
- `review_engine` — orquestra os 4 analisadores (code/security/architecture/performance).
- `security_engine` — scanners de segredo (regex + entropia) e SAST leve.
- `testing_engine` — detecção de linguagem e execução de test runners/lint apropriados.

### MCP Layer
Cada caso de uso é exposto como uma `@mcp.tool()` em `mcp/tools/`. A camada MCP é fina: valida input (Pydantic), chama o `application`, formata output.

### CLI
Interface Typer espelhando 1:1 as tools MCP, para uso humano direto no terminal, com saída rica via `Rich`.

## 3. Fluxo MCP

```mermaid
sequenceDiagram
    participant Client as Cliente MCP (ex: Claude Code)
    participant MCP as MCP Server (FastMCP)
    participant App as Application Use Case
    participant Eng as Engine
    participant Ext as Sistema Externo (Git/GitHub/IA)

    Client->>MCP: tool_call(commit_workflow, args)
    MCP->>App: CommitWorkflowUseCase.execute(args)
    App->>Eng: GitEngine.status() / diff()
    App->>Eng: TestingEngine.run()
    App->>Eng: SecurityEngine.scan()
    App->>Eng: ReviewEngine.review(diff)
    Eng->>Ext: chamadas reais
    Ext-->>Eng: resultados
    Eng-->>App: resultados agregados
    App-->>MCP: relatório + commit message proposta
    MCP-->>Client: resultado estruturado (JSON)
```

## 4. Fluxo Git (pipeline de commit)

```mermaid
flowchart LR
    A[git status] --> B[git diff]
    B --> C[Detectar linguagem]
    C --> D[Executar testes]
    D --> E[Executar lint]
    E --> F[Scan de segredos]
    F --> G[Review por IA]
    G --> H[Gerar relatório]
    H --> I[Gerar Conventional Commit]
    I --> J{Aprovação do usuário?}
    J -- sim --> K[git add]
    K --> L[git commit]
    L --> M[git push]
    M --> N{Criar PR?}
    N -- sim --> O[gh pr create]
    J -- não --> P[Abortar - nada é alterado]
```

## 5. Fluxo GitHub

```mermaid
flowchart TD
    A[Use Case dispara ação GitHub] --> B{gh CLI disponível?}
    B -- sim --> C[GitHubCliProvider]
    B -- não --> D[GitHubApiProvider via httpx]
    C --> E[Resultado normalizado]
    D --> E
```

## 6. Fluxo de Revisão por IA

```mermaid
flowchart TD
    Diff[Diff segmentado por arquivo] --> Code[Code Review Analyzer]
    Diff --> Sec[Security Review Analyzer]
    Diff --> Arch[Architecture Review Analyzer]
    Diff --> Perf[Performance Review Analyzer]
    Code --> Agg[Agregador de Findings]
    Sec --> Agg
    Arch --> Agg
    Perf --> Agg
    Agg --> Report[Relatório consolidado - Markdown + JSON]
```

## 7. Decisões Arquiteturais e Motivação

| Decisão | Motivação | Trade-off |
|---|---|---|
| Clean Architecture com Domain isolado | Permite testar regras de negócio sem Git/GitHub/IA reais | Mais boilerplate inicial (interfaces) |
| FastMCP para camada MCP | Padrão emergente, integra nativamente com Claude Code e clientes MCP | Acoplamento a uma lib em evolução — mitigado por camada fina |
| `gh` CLI como integração primária com GitHub | Reaproveita autenticação já configurada do usuário, menor superfície de gerenciamento de tokens | Exige `gh` instalado — fallback via API cobre CI |
| Engines paralelas para review | Reduz latência total do pipeline | Maior complexidade de agregação de erros parciais |
| Pydantic v2 para toda fronteira de dados | Validação forte, serialização consistente para MCP | Custo de aprendizado para contribuidores novos — mitigado com exemplos em docs |

Toda nova decisão estrutural relevante deve ser registrada em `DECISIONS.md` e referenciada aqui.

## 8. Estrutura de Pastas (visão completa)

```
git-ai-agent/
├── src/git_ai_agent/
│   ├── domain/
│   ├── application/
│   ├── infrastructure/
│   ├── engines/
│   │   ├── git_engine/
│   │   ├── github_engine/
│   │   ├── review_engine/
│   │   ├── security_engine/
│   │   └── testing_engine/
│   ├── mcp/
│   │   ├── server.py
│   │   └── tools/
│   ├── cli/
│   ├── config/
│   └── logging/
├── tests/
│   ├── unit/
│   └── integration/
├── docs/
├── examples/
├── .github/workflows/
├── .devcontainer/
├── .claude/
└── config/
```
