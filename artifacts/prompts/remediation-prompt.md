# Prompt de Remediação — Correções de Segurança DVPWA

Com base no relatório de triagem (`artifacts/llm/llm-triage.md`), proponha correções seguras para as 5 vulnerabilidades priorizadas.

## Tarefas

Para cada falha selecionada, forneça:

1. **Causa raiz**: Explique tecnicamente por que a vulnerabilidade existe.
2. **Patch proposto**: Código corrigido mínimo e seguro (diff ou bloco de código).
3. **Teste de regressão**: Descreva um teste que prove que o exploit não funciona mais.
4. **Como confirmar no segundo scan**: Indique o que esperar nos relatórios da segunda esteira (Bandit, Semgrep, etc.) após a correção.
5. **Evite correções que apenas escondem o alerta** da ferramenta sem corrigir a causa.

## Formato de saída

Para cada vulnerabilidade:

```
### [ID] — [Nome da Vulnerabilidade]
- **Causa raiz**: ...
- **Patch proposto**: ...
- **Teste de regressão**: ...
- **Como confirmar no segundo scan**: ...
```

## Contexto

- Aplicação: DVPWA (aiohttp + PostgreSQL + Redis + Jinja2)
- Linguagem: Python 3
- Relatório de triagem: `artifacts/llm/llm-triage.md`
