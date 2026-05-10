# DVPWA DevSecOps LLM — Pipeline de Segurança

Pipeline DevSecOps com triagem assistida por LLM para detecção, remediação e validação de vulnerabilidades no [DVPWA](https://github.com/anxolerd/dvpwa) (Damn Vulnerable Python Web Application).

**Disciplina**: CS-282 — Sistemas de Software Seguro  
**Projeto**: Básico de Exame

---

## Arquitetura da Pipeline

```
┌─────────────────────────────────────────────────────────────────────┐
│                        GitLab CI/CD Pipeline                        │
├──────────────┬──────────────┬─────────────────┬─────────────────────┤
│  scan_before │    prompt    │ validate_after  │     scan_after      │
├──────────────┼──────────────┼─────────────────┼─────────────────────┤
│ • Bandit     │ • Triage     │ • pytest        │ • Bandit            │
│ • Semgrep    │   prompt     │   (20 tests)    │ • Semgrep           │
│ • pip-audit  │ • Remediation│                 │ • pip-audit         │
│ • Gitleaks   │   prompt     │                 │ • Gitleaks          │
└──────────────┴──────────────┴─────────────────┴─────────────────────┘
       ▼                                               ▼
  artifacts/                                     artifacts/
  scan-before/                                   scan-after/
  ├── bandit.json                                ├── bandit.json
  ├── semgrep.json                               ├── semgrep.json
  ├── pip-audit.json                             ├── pip-audit.json
  ├── gitleaks.json                              ├── gitleaks.json
                                                 └── comparison.md
```

### Estágios

1. **scan_before** — Executa 4 ferramentas SAST/SCA sobre o código original (vulnerável)
2. **prompt** — Gera prompts para triagem e remediação via LLM
3. **validate_after** — Executa 20 testes de regressão (pytest)
4. **scan_after** — Re-executa as 4 ferramentas sobre o código corrigido

---

## Vulnerabilidades Corrigidas

| # | Vulnerabilidade | Arquivo | Correção | Commit |
|---|----------------|---------|----------|--------|
| 1 | **SQL Injection** | `sqli/dao/student.py` | Queries parametrizadas (`%s`) | `fix: remediate SQL Injection vulnerability` |
| 2 | **Stored XSS** | `sqli/app.py` | `autoescape=True` no Jinja2 | `fix: remediate Stored XSS vulnerability` |
| 3 | **Session Fixation** | `sqli/views.py`, `sqli/middlewares.py` | Regeneração de sessão no login/logout + `httponly=True` | `fix: remediate Session Fixation vulnerability` |
| 4 | **Senhas MD5** | `sqli/dao/user.py`, `migrations/001-fixtures.sql` | Substituição de MD5 por bcrypt | `fix: remediate bad choice for storing passwords` |
| 5 | **CSRF** | `sqli/app.py` | Ativação do `csrf_middleware` | `fix: remediate Cross-site request forgery (CSRF)` |

---

## Estrutura de Artefatos

```
artifacts/
├── scan-before/          # Relatórios da 1ª esteira (antes dos patches)
│   ├── bandit.json
│   ├── semgrep.json
│   ├── pip-audit.json
│   └── gitleaks.json
├── prompts/              # Prompts enviados à LLM
│   ├── triage-prompt.md
│   └── remediation-prompt.md
├── llm/                  # Saídas da LLM
│   ├── llm-triage.md
│   └── llm-remediation.md
└── scan-after/           # Relatórios da 2ª esteira (após patches)
    ├── bandit.json
    ├── semgrep.json
    ├── pip-audit.json
    ├── gitleaks.json
    └── comparison.md     # Comparativo antes/depois
```

---

## Scans Before/After — Resumo

| Vulnerabilidade | scan-before | scan-after | Status |
|----------------|-------------|------------|--------|
| SQL Injection | 🔴 Bandit B608 | 🟢 Removida | ✅ Corrigida |
| Stored XSS | 🔴 Semgrep autoescape | 🟡 Pode permanecer | ✅ Corrigida (teste prova) |
| Session Fixation | 🟡 Não detectada por SAST | 🟡 N/A | ✅ Corrigida (teste prova) |
| Senhas MD5 | 🔴 Bandit B303 | 🟢 Removida | ✅ Corrigida |
| CSRF | 🔴 Semgrep middleware | 🟢 Removida | ✅ Corrigida |
| Deps (pip-audit) | 🟡 CVEs presentes | 🟡 CVEs presentes | ⚠️ Fora do escopo |
| Segredos | 🟢 Limpo | 🟢 Limpo | ✅ OK |

> **Nota**: O pip-audit detecta CVEs em **dependências** (aiohttp, jinja2, etc.), não vulnerabilidades da aplicação. Esses findings permanecem porque a atualização de dependências está fora do escopo.

---

## Testes de Regressão

```
tests/
├── conftest.py                 # Fixtures compartilhados
├── test_sql_injection.py       # 3 testes — query parametrizada
├── test_xss.py                 # 3 testes — autoescape + payloads escapados
├── test_session_fixation.py    # 4 testes — regeneração de sessão + httponly
├── test_password_storage.py    # 6 testes — bcrypt + verificação funcional
└── test_csrf.py                # 4 testes — middleware ativo + validação de token
```

**Total: 20 testes — todos passam.**

### Execução local

```bash
pip install pytest bcrypt jinja2
pytest tests/ -v
```

---

## Prompts Utilizados

### Triagem (`artifacts/prompts/triage-prompt.md`)
Instrui a LLM a analisar os relatórios scan-before, agrupar duplicatas, identificar falsos positivos e priorizar as 5 vulnerabilidades-alvo.

### Remediação (`artifacts/prompts/remediation-prompt.md`)
Instrui a LLM a propor patches seguros para cada vulnerabilidade priorizada, incluindo causa raiz, código corrigido, teste de regressão e confirmação no segundo scan.

### Saídas LLM
- `artifacts/llm/llm-triage.md` — Tabela de triagem com decisões e justificativas
- `artifacts/llm/llm-remediation.md` — Patches propostos com código e testes

---

## Fluxo Git

```
main
 └── setup/ci-pipeline
      ├── chore: setup project directory structure
      ├── ci: create scan-before pipeline with Bandit, Semgrep, pip-audit, and Gitleaks
      ├── docs: generate LLM triage and remediation prompts and mock outputs
      └── fix/security-remediation
           ├── fix: remediate SQL Injection vulnerability
           ├── fix: remediate Stored XSS vulnerability
           ├── fix: remediate Session Fixation vulnerability
           ├── fix: remediate bad choice for storing passwords
           ├── fix: remediate Cross-site request forgery (CSRF)
           ├── test: add regression tests for remediated vulnerabilities
           └── ci: add scan-after pipeline and comparison report
```

---

## Reprodução

### Pré-requisitos
- Docker + Docker Compose
- Python 3.11+
- Git

### Passo a passo

```bash
# 1. Clonar o repositório
git clone https://gitlab.com/rossatodias/dvpwa-devsecops-llm.git
cd dvpwa-devsecops-llm

# 2. Iniciar DVPWA (Docker Compose)
docker-compose up -d

# 3. Acessar aplicação
open http://localhost:8080

# 4. Executar testes de regressão
pip install pytest bcrypt jinja2
pytest tests/ -v

# 5. Executar scan local (opcional)
pip install bandit semgrep pip-audit
bandit -r . -f json
semgrep scan --json .
```

---

## Licença

MIT — baseado em [anxolerd/dvpwa](https://github.com/anxolerd/dvpwa).
