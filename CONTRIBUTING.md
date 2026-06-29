# Contribuindo com git-ai-agent

Obrigado por considerar contribuir! Este projeto segue padrões estritos de qualidade — leia este guia antes de abrir seu primeiro PR.

## Antes de começar

1. Leia `CLAUDE.md` (memória/regras do projeto) e `ARCHITECTURE.md`.
2. Verifique `TASKS.md` para ver a tarefa atual em andamento — **uma tarefa por vez, por contribuidor, por PR**.
3. Abra ou comente em uma issue antes de começar trabalho substancial, para evitar esforço duplicado.

## Ambiente de desenvolvimento

```bash
git clone https://github.com/nahnp/git-ai-agent.git
cd git-ai-agent
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pre-commit install
```

Alternativamente, use o Dev Container fornecido em `.devcontainer/`.

## Fluxo de contribuição

1. Crie uma branch a partir de `main`: `feature/<slug>`, `fix/<slug>` ou `chore/<slug>`.
2. Implemente **uma única tarefa** do backlog.
3. Escreva testes (unitários e, quando aplicável, de integração).
4. Rode localmente:
   ```bash
   ruff check .
   ruff format --check .
   mypy --strict src/
   pytest --cov=src --cov-report=term-missing
   ```
5. Atualize a documentação relevante (`README.md`, `docs/`, `ARCHITECTURE.md` se a arquitetura mudou).
6. Atualize `CHANGELOG.md` na seção `[Unreleased]`.
7. Faça commit usando [Conventional Commits](https://www.conventionalcommits.org/).
8. Abra o Pull Request com descrição estruturada: contexto, mudança, testes, impacto.

## Padrões de código

- Tipagem estrita obrigatória (`mypy --strict`).
- Sem `print()` em código de produção — use o logger estruturado do projeto.
- Sem `TODO`/`FIXME` em código mergeado.
- Cobertura mínima de 85% para módulos novos.

## Decisões arquiteturais

Se sua contribuição envolve uma escolha arquitetural relevante (nova dependência, novo padrão, mudança de contrato), registre-a em `DECISIONS.md` **antes** de abrir o PR, explicando alternativas consideradas e impacto.

## Código de Conduta

Ao contribuir, você concorda em seguir o `CODE_OF_CONDUCT.md`.

## Relatando problemas de segurança

Não abra issues públicas para vulnerabilidades — siga o processo descrito em `SECURITY.md`.
