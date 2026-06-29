# Política de Segurança

## Versões Suportadas

Enquanto o projeto estiver em `0.x`, apenas a última versão minor publicada recebe correções de segurança. A partir de `1.0`, a política de suporte será detalhada nesta seção.

## Reportando uma Vulnerabilidade

**Não abra uma issue pública.** Para reportar uma vulnerabilidade:

1. Envie um e-mail para o(s) mantenedor(es) listados no `README.md`, com o assunto `[SECURITY] git-ai-agent`.
2. Inclua: descrição do problema, passos para reprodução, versão afetada, e impacto potencial.
3. Você receberá uma confirmação de recebimento em até 5 dias úteis.
4. Um patch ou mitigação será priorizado conforme a severidade (CVSS estimado).

## Princípios de Segurança do Projeto

- O agente **nunca** executa operações destrutivas (`push`, `commit`, `reset --hard`, `force-push`, `revert`) sem confirmação explícita, exceto em modo CI explicitamente configurado para isso.
- O scanner de segredos é **obrigatório e não configurável para desligar** (ver `DECISIONS.md`, ADR-005) — apenas allowlist explícita e auditável para falsos positivos.
- Nenhuma credencial é persistida fora de variáveis de ambiente/`.env` (sempre git-ignorado).
- Toda chamada de rede possui timeout explícito e nunca expõe payloads sensíveis em logs.
- Dependências são auditadas via `pip-audit`/Dependabot no CI.

## Divulgação Responsável

Concedemos crédito público a quem reportar vulnerabilidades de forma responsável, salvo preferência contrária do relator, após o patch correspondente ser publicado.
