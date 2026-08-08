# Estudo consolidado do projeto

## Síntese

Os documentos originais descrevem um produto maior que o protótipo: uma camada inteligente sobre Git/GitHub, consumível por pessoas e agentes via CLI e MCP, com review, segurança, testes, changelog e releases. O princípio que diferencia o projeto não é “usar IA”, mas combinar automação com controle humano, explicabilidade e falha segura.

## O melhor preservado dos documentos

1. **Human-in-the-loop verificável:** operações de escrita não dependem de uma promessa textual; a aprovação referencia um snapshot do estado.
2. **Clean Architecture pragmática:** regras e contratos ficam separados de Git, terminal e protocolo MCP.
3. **Degradação local:** o fluxo funciona sem credencial, provedor remoto ou envio de código.
4. **Segurança não opcional:** segredo detectado bloqueia commit; não há force-push ou comandos destrutivos no MVP.
5. **Paridade de interfaces:** CLI e MCP expõem o mesmo núcleo de casos de uso.
6. **Documentação como contrato:** decisões, configuração, ferramentas, riscos e evolução têm fontes explícitas.

## Leitura técnica

O adapter Git usa subprocessos com argumentos, `shell=False`, timeout e saída limitada. O review agrega diff, linguagens, estatísticas, findings e resultados de comandos. O scanner observa apenas linhas adicionadas e redige valores. A aplicação prepara uma sessão com UUID, branch, fingerprint SHA-256, arquivos, mensagem, comandos planejados e validade. A execução refaz o review e recusa qualquer divergência antes de `git add` e `git commit`. Push é outro caso de uso e outra confirmação.

## Leitura para desenvolvimento

O caminho de extensão é estável: novos modelos/ports em `domain`; orquestração em `application`; integração concreta em `infrastructure`; análise especializada em `engines`; exposição fina em `cli` e `mcp`. Testes unitários cobrem regras e contratos; integração usa Git real. Antes de contribuir, rode a mesma matriz da CI e atualize documentação/CHANGELOG quando o comportamento mudar.

## Leitura de negócio

O MVP reduz variabilidade e risco no intervalo entre terminar código e publicar uma alteração. Ele é útil para profissionais individuais, equipes com padrões de commit e organizações que desejam agentes de desenvolvimento com limites auditáveis. O ganho deve ser medido por tempo de ciclo, falhas antecipadas, segredos bloqueados e retrabalho evitado — não por volume de chamadas de IA.

## Inconsistências resolvidas

- O escopo original de v1 incluía muitas operações destrutivas; o MVP foi deliberadamente limitado ao fluxo seguro solicitado.
- A antiga possibilidade de ignorar achados críticos por `--force` não se aplica a segredos e não existe neste protótipo.
- IA remota aparece como direção futura, nunca como dependência para funcionamento.
- `stdio` é o transporte do MVP; SSE e integrações GitHub avançadas permanecem no roadmap.

## Próximas decisões recomendadas

Priorizar Gitleaks como defesa em profundidade; definir allowlist auditável; escolher backend de sessões para uso concorrente; testar Linux/macOS/WSL2 na CI; e somente depois adicionar adapters remotos de IA/GitHub com consentimento e threat model próprios.
