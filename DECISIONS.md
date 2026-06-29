# DECISIONS.md — Registro de Decisões Arquiteturais (ADR Log)

Formato de cada entrada: Data | Contexto | Decisão | Alternativas consideradas | Impacto.

---

## ADR-001 — Adoção de Clean Architecture com Domain isolado
- **Data**: 2026-06-29
- **Contexto**: Necessidade de testar regras de negócio sem depender de Git, GitHub ou IA reais, e de permitir trocar implementações (ex.: outro provedor Git host) sem reescrever casos de uso.
- **Decisão**: Separar `domain` (puro), `application` (casos de uso), `infrastructure`/`engines` (implementações), com `mcp`/`cli` como entrypoints finos.
- **Alternativas consideradas**: Estrutura "flat" por feature (mais simples, menos testável isoladamente); arquitetura hexagonal pura (overhead similar, nomenclatura menos familiar à comunidade Python).
- **Impacto**: Mais arquivos/interfaces no início; testes de domínio extremamente rápidos e isolados; facilita extensão futura (multi-provider).

## ADR-002 — FastMCP como camada de exposição MCP
- **Data**: 2026-06-29
- **Contexto**: O projeto precisa ser consumível nativamente por clientes MCP (Claude Code, Claude Desktop, IDEs compatíveis).
- **Decisão**: Usar FastMCP para implementar o servidor MCP, com camada fina que apenas valida input/output e delega para `application`.
- **Alternativas consideradas**: Implementar o protocolo MCP manualmente (mais controle, muito mais esforço de manutenção e risco de divergência do spec).
- **Impacto**: Acoplamento à evolução do FastMCP, mitigado por isolar toda a integração em `mcp/`, sem permear `application`/`domain`.

## ADR-003 — `gh` CLI como integração primária com GitHub, com fallback via API
- **Data**: 2026-06-29
- **Contexto**: Usuários frequentemente já têm `gh` instalado e autenticado; reimplementar autenticação OAuth seria redundante e arriscado para um projeto open source gerenciar segredos de terceiros.
- **Decisão**: `GitHubCliProvider` como caminho padrão; `GitHubApiProvider` (httpx) como fallback automático quando `gh` não está disponível (ex.: alguns ambientes de CI).
- **Alternativas consideradas**: Apenas API REST direta (exige gerenciar token explicitamente em todo ambiente, pior DX local).
- **Impacto**: Dois caminhos de código a manter e testar, mitigado por uma interface comum `GitHostProvider` e testes de contrato compartilhados.

## ADR-004 — Pydantic v2 em todas as fronteiras de dados
- **Data**: 2026-06-29
- **Contexto**: Entidades de domínio, configuração e payloads MCP precisam de validação forte e serialização previsível.
- **Decisão**: Usar Pydantic v2 (`BaseModel`/`dataclasses` imutáveis onde aplicável) em domínio, configuração e schemas de tools MCP.
- **Alternativas consideradas**: `dataclasses` puro (sem validação automática); `attrs` (boa opção, mas menos integrado ao ecossistema FastMCP/Typer).
- **Impacto**: Curva de aprendizado para contribuidores novos, mitigada com exemplos em `docs/`.

## ADR-005 — Segurança não é opt-out
- **Data**: 2026-06-29
- **Contexto**: Definir comportamento padrão quando o scanner de segredos encontra uma credencial exposta.
- **Decisão**: Bloqueio de commit por segredo detectado é **sempre obrigatório**, sem flag de configuração para desabilitar — apenas allowlist explícita por padrão de falso-positivo conhecido, documentada e auditável.
- **Alternativas consideradas**: Tornar configurável (`security.secret_scan.enabled: false`) — rejeitado por risco de uso indevido silencioso em ambientes de CI mal configurados.
- **Impacto**: Maior segurança por padrão; exige mecanismo de allowlist bem documentado para evitar fricção legítima.

---

> Toda nova decisão estrutural relevante deve ser adicionada aqui **antes** de ser implementada, e referenciada em `ARCHITECTURE.md` quando aplicável.
