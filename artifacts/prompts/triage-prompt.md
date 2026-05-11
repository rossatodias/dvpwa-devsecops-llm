# Prompt de Triagem — Análise de Segurança DVPWA

Atue como analista de segurança de software. Vou fornecer relatórios de Bandit, Semgrep, pip-audit e Gitleaks executados sobre o DVPWA (Damn Vulnerable Python Web Application).

## Tarefas

1. **Agrupe achados duplicados ou equivalentes** entre as ferramentas.
2. **Identifique prováveis falsos positivos** e explique brevemente.
3. **Priorize achados que parecem exploráveis** no DVPWA.
4. **Selecione 5 vulnerabilidades candidatas** para correção:
   - SQL Injection
   - Stored XSS
   - Session Fixation
   - Armazenamento fraco de senhas (MD5)
   - Cross-Site Request Forgery (CSRF)
5. Para cada vulnerabilidade escolhida, indique:
   - Evidência nos relatórios
   - Arquivo/linha afetado
   - Causa raiz provável
   - Estratégia de correção

## Formato de saída

Tabela com colunas:

| ID | Ferramenta | Arquivo | Severidade | Decisão | Justificativa |
|----|-----------|---------|------------|---------|---------------|

Seguida de uma seção final: **Vulnerabilidades selecionadas para remediação**, com detalhes de cada uma.

## Relatórios de entrada

Anexe os seguintes arquivos do diretório `artifacts/scan-before/`:
- `bandit.json`
- `semgrep.json`
- `pip-audit.json`
- `gitleaks.json`
