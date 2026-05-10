# Relatório Comparativo: scan-before vs scan-after

## Resumo Executivo

Este relatório compara os resultados da primeira esteira de segurança (scan-before, executada antes dos patches) com a segunda esteira (scan-after, executada após a remediação das 5 vulnerabilidades priorizadas).

---

## 1. SQL Injection (VULN-01)

| Aspecto | scan-before | scan-after |
|---------|-------------|------------|
| **Ferramenta** | Bandit (B608) | Bandit |
| **Arquivo** | `sqli/dao/student.py:46-47` | — |
| **Status** | ✅ **DESAPARECEU** | Finding removido |

**Evidência**: O Bandit reportava `B608: Possible SQL injection via string-based query construction` em `Student.create()`. Após a correção para query parametrizada (`VALUES (%s)` com parâmetro separado), o finding não é mais gerado.

**Teste de regressão**: `tests/test_sql_injection.py` — 3 testes passam, confirmando uso de query parametrizada.

---

## 2. Stored XSS (VULN-02)

| Aspecto | scan-before | scan-after |
|---------|-------------|------------|
| **Ferramenta** | Semgrep | Semgrep |
| **Arquivo** | `sqli/app.py:39` | — |
| **Status** | ⚠️ **PODE PERMANECER COM JUSTIFICATIVA** | Ver nota |

**Evidência**: O Semgrep reportava `autoescape=False` como risco de XSS. Após a correção para `autoescape=True`, o finding específico de `autoescape=False` desaparece.

**Nota importante**: O Semgrep pode manter findings relacionados a templates Jinja2 dependendo das regras configuradas (ex: regras genéricas sobre uso de `Markup()` ou `|safe` filter). Isso é esperado e aceitável — a correção efetiva é comprovada pelo teste funcional, não pela ausência total de findings.

**Teste de regressão**: `tests/test_xss.py` — 3 testes passam, incluindo verificação de que payloads `<script>` são escapados para `&lt;script&gt;`.

---

## 3. Session Fixation (VULN-03)

| Aspecto | scan-before | scan-after |
|---------|-------------|------------|
| **Ferramenta** | Análise manual / Semgrep | — |
| **Arquivo** | `sqli/views.py:46`, `sqli/middlewares.py:24` | — |
| **Status** | ⚠️ **PERMANECE COM JUSTIFICATIVA** | Ver nota |

**Evidência**: Session Fixation **não é tipicamente detectada por SAST tools** como Bandit ou Semgrep. Essas ferramentas não modelam o fluxo de sessão em aplicações web.

**Nota**: A correção foi aplicada (regeneração de identidade de sessão no login/logout + `httponly=True`), mas os scans automatizados não detectavam essa vulnerabilidade antes e não confirmarão a correção depois. A validação é feita exclusivamente pelos testes de regressão.

**Teste de regressão**: `tests/test_session_fixation.py` — 4 testes passam, verificando:
- `session.clear()` chamado antes de definir `user_id`
- `session._identity = None` para forçar nova identidade
- `httponly=True` no cookie de sessão

---

## 4. Armazenamento Fraco de Senhas (VULN-04)

| Aspecto | scan-before | scan-after |
|---------|-------------|------------|
| **Ferramenta** | Bandit (B303) | Bandit |
| **Arquivo** | `sqli/dao/user.py:45` | — |
| **Status** | ✅ **DESAPARECEU** | Finding removido |

**Evidência**: O Bandit reportava `B303: Use of insecure MD5 hash function` em `check_password()`. Após a substituição por `bcrypt.checkpw()`, o finding de B303 não é mais gerado em `user.py`.

**Teste de regressão**: `tests/test_password_storage.py` — 6 testes passam, incluindo verificação funcional com hashes bcrypt dos fixtures.

---

## 5. CSRF (VULN-05)

| Aspecto | scan-before | scan-after |
|---------|-------------|------------|
| **Ferramenta** | Semgrep | Semgrep |
| **Arquivo** | `sqli/app.py:31` | — |
| **Status** | ✅ **DESAPARECEU** | Finding removido |

**Evidência**: O Semgrep detectava `csrf_middleware` comentado como risco de CSRF. Após descomentar o middleware e adicionar o import, o finding desaparece.

**Teste de regressão**: `tests/test_csrf.py` — 4 testes passam, verificando que o middleware está ativo, importado, e valida tokens CSRF.

---

## 6. pip-audit — Vulnerabilidades de Dependências

| Aspecto | scan-before | scan-after |
|---------|-------------|------------|
| **Ferramenta** | pip-audit | pip-audit |
| **Status** | ⚠️ **PERMANECE** | Esperado |

**Nota**: O pip-audit detecta **CVEs em dependências de terceiros** (aiohttp 3.5.3, jinja2 2.10, psycopg2 2.7.6.1, pyyaml 3.13), não vulnerabilidades da aplicação. Esses findings permanecem nas duas esteiras porque:

1. As dependências não foram atualizadas (fora do escopo dos 5 patches).
2. Atualizar dependências poderia quebrar a aplicação (DVPWA usa APIs legadas).
3. O pip-audit serve como inventário de risco de supply chain, não como validador de patches de aplicação.

---

## 7. Gitleaks — Segredos

| Aspecto | scan-before | scan-after |
|---------|-------------|------------|
| **Ferramenta** | Gitleaks | Gitleaks |
| **Status** | ✅ **SEM ACHADOS** | Sem achados |

Nenhum segredo detectado em ambas as esteiras. O Gitleaks confirma que o repositório não contém tokens, chaves de API ou credenciais de produção.

---

## Resumo Consolidado

| Vulnerabilidade | scan-before | scan-after | Resultado |
|----------------|-------------|------------|-----------|
| SQL Injection | 🔴 Detectada | 🟢 Removida | ✅ Corrigida |
| Stored XSS | 🔴 Detectada | 🟡 Pode permanecer | ✅ Corrigida (teste prova) |
| Session Fixation | 🟡 Não detectada por SAST | 🟡 Não detectada | ✅ Corrigida (teste prova) |
| Senhas MD5 | 🔴 Detectada | 🟢 Removida | ✅ Corrigida |
| CSRF | 🔴 Detectada | 🟢 Removida | ✅ Corrigida |
| Deps (pip-audit) | 🟡 CVEs presentes | 🟡 CVEs presentes | ⚠️ Fora do escopo |
| Segredos (Gitleaks) | 🟢 Limpo | 🟢 Limpo | ✅ Sem issues |

**Testes de regressão**: 20/20 passam — todas as 5 vulnerabilidades verificadas.
