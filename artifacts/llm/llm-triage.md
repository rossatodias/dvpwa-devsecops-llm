# Relatório de Triagem LLM — DVPWA

## 1. Análise Consolidada dos Relatórios

### 1.1 Achados Agrupados e Deduplicados

| ID | Ferramenta(s) | Arquivo | Severidade | Decisão | Justificativa |
|----|--------------|---------|------------|---------|---------------|
| T-01 | Bandit (B608) | `sqli/dao/student.py:46-47` | **ALTA** | ✅ Corrigir | SQL Injection via string formatting no `Student.create()`. A query usa `%` do Python para interpolar `name` diretamente na string SQL, permitindo injeção arbitrária. |
| T-02 | Bandit (B303), Semgrep | `sqli/dao/user.py:45` | **ALTA** | ✅ Corrigir | Uso de MD5 (`hashlib.md5`) para armazenar/verificar senhas. MD5 é criptograficamente fraco, suscetível a rainbow tables e brute-force. |
| T-03 | Semgrep | `sqli/app.py:39` | **ALTA** | ✅ Corrigir | Jinja2 configurado com `autoescape=False`. Todo conteúdo renderizado nos templates não é escapado, permitindo Stored XSS via reviews de cursos. |
| T-04 | Semgrep, Bandit | `sqli/app.py:31` | **MÉDIA** | ✅ Corrigir | CSRF middleware comentado (`# csrf_middleware`). Todas as rotas POST ficam desprotegidas contra ataques CSRF. A infraestrutura de tokens CSRF existe mas está desativada. |
| T-05 | Semgrep | `sqli/views.py:46`, `sqli/middlewares.py:24` | **MÉDIA** | ✅ Corrigir | Session Fixation: sessão não é regenerada após login. Além disso, cookies de sessão configurados com `httponly=False`, expondo-os a acesso via JavaScript. |
| T-06 | pip-audit | `requirements.txt` (várias deps) | **MÉDIA** | ⚠️ Informativo | CVEs em dependências desatualizadas (aiohttp 3.5.3, jinja2 2.10, pyyaml 3.13, psycopg2 2.7.6.1). São vulnerabilidades de dependência, não da aplicação — documentar mas fora do escopo de patches. |
| T-07 | Bandit (B105) | `config/dev.yaml` | **BAIXA** | ❌ Falso positivo | Credenciais hardcoded no config de desenvolvimento. Esperado em ambiente de dev/Docker. Não é um achado explorable em produção. |
| T-08 | Gitleaks | N/A | **NENHUMA** | ❌ Nenhum achado | Nenhum segredo (tokens, chaves, credenciais de produção) detectado no código-fonte. |

### 1.2 Falsos Positivos Identificados

- **T-07 (Bandit B105)**: As credenciais em `config/dev.yaml` (`postgres:postgres`) são configurações padrão para o ambiente Docker de desenvolvimento. Não representam risco real.
- **T-08 (Gitleaks)**: Sem achados — o repositório não contém segredos vazados.

### 1.3 Achados Duplicados

- **T-02**: Detectado tanto pelo Bandit (B303 — uso de MD5) quanto pelo Semgrep (regra de hash inseguro). Mesmo achado, duas ferramentas.
- **T-04**: O CSRF é identificado parcialmente pelo Semgrep (middleware desativado) e pelo Bandit (análise de fluxo).

---

## 2. Vulnerabilidades Selecionadas para Remediação

### VULN-01: SQL Injection (T-01)
- **Arquivo**: `sqli/dao/student.py`, linhas 46-47
- **Evidência**: `"VALUES ('%(name)s')" % {'name': name}` — interpolação direta do input do usuário na query SQL
- **Exploração**: Inserir `Robert'); DROP TABLE students CASCADE; --` como nome de aluno destrói a tabela
- **Causa raiz**: Uso de string formatting do Python em vez de queries parametrizadas do psycopg2
- **Estratégia**: Substituir por query parametrizada com `%s` placeholder

### VULN-02: Stored XSS (T-03)
- **Arquivo**: `sqli/app.py`, linha 39
- **Evidência**: `autoescape=False` na configuração do Jinja2
- **Exploração**: Submeter `<script>alert(document.cookie)</script>` como review de curso — o JavaScript é executado para todos os visitantes
- **Causa raiz**: Jinja2 renderiza HTML sem escapar caracteres especiais
- **Estratégia**: Alterar para `autoescape=True`

### VULN-03: Session Fixation (T-05)
- **Arquivo**: `sqli/views.py`, linha 46; `sqli/middlewares.py`, linha 24
- **Evidência**: `session['user_id'] = user.id` sem regenerar o identificador de sessão; `httponly=False` no storage
- **Exploração**: Atacante obtém cookie de sessão, fixa-o no navegador da vítima, vítima faz login, atacante herda a sessão autenticada
- **Causa raiz**: Ausência de rotação de identidade de sessão no login/logout
- **Estratégia**: Limpar e regenerar identidade da sessão no login; definir `httponly=True`

### VULN-04: Armazenamento Fraco de Senhas (T-02)
- **Arquivo**: `sqli/dao/user.py`, linha 45
- **Evidência**: `md5(password.encode('utf-8')).hexdigest()` — uso de MD5 sem salt
- **Exploração**: Hashes MD5 podem ser revertidos com rainbow tables (ex: CrackStation) em segundos
- **Causa raiz**: Uso de função de hash genérica (MD5) em vez de KDF para senhas (bcrypt, argon2)
- **Estratégia**: Substituir por bcrypt; atualizar fixtures com hashes bcrypt pré-computados

### VULN-05: CSRF (T-04)
- **Arquivo**: `sqli/app.py`, linha 31
- **Evidência**: `# csrf_middleware` — middleware comentado
- **Exploração**: Site malicioso pode criar formulário POST apontando para `/students/` ou `/courses/{id}/review` e submeter ações em nome do usuário autenticado
- **Causa raiz**: Middleware de validação CSRF deliberadamente desativado
- **Estratégia**: Descomentar `csrf_middleware` na lista de middlewares e adicionar import
