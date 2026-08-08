# Visão de negócio

## Problema

Entre terminar uma alteração e publicá-la existem passos repetitivos e sujeitos a falhas: revisar o diff, procurar credenciais, executar qualidade, escrever um commit consistente e confirmar o destino. O git-ai-agent transforma esse intervalo em um fluxo verificável, sem retirar a decisão final da pessoa desenvolvedora.

## Valor entregue pelo MVP

- Reduz inconsistência operacional com um mesmo fluxo na CLI e em clientes MCP.
- Evita commits acidentais por meio de preparação sem escrita e aprovação vinculada a fingerprint.
- Bloqueia padrões básicos de segredo antes do commit e não envia código a serviços externos.
- Produz resultados JSON adequados a automações e auditoria.
- Funciona em qualquer repositório Git confiável, independentemente da linguagem principal.

## Limites e risco residual

O scanner baseado em padrões reduz risco, mas não substitui Gitleaks, secret managers, revisão humana ou segurança de CI. Executar lint e testes significa executar código do repositório; use apenas em projetos confiáveis. O MVP não inclui telemetria, interface gráfica, force-push, rollback automático nem integração GitHub avançada.

## Indicadores recomendados

Tempo entre alteração e commit aprovado; percentual de pipelines aprovados sem retrabalho; segredos bloqueados; falhas de teste encontradas antes do commit; adoção das tools MCP; e falsos positivos do scanner.
