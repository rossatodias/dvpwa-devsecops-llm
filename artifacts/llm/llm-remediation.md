# Relatório de Remediação LLM — DVPWA

Baseado na triagem (`artifacts/llm/llm-triage.md`), seguem as correções propostas para as 5 vulnerabilidades priorizadas.

---

### VULN-01 — SQL Injection

- **Causa raiz**: Em `sqli/dao/student.py:46-47`, o método `Student.create()` usa Python string formatting (`%`) para interpolar o parâmetro `name` diretamente na string SQL. Isso permite que um atacante injete SQL arbitrário via o campo de nome.

- **Patch proposto**:
```python
# ANTES (vulnerável):
@staticmethod
async def create(conn: Connection, name: str):
    q = ("INSERT INTO students (name) "
         "VALUES ('%(name)s')" % {'name': name})
    async with conn.cursor() as cur:
        await cur.execute(q)

# DEPOIS (corrigido):
@staticmethod
async def create(conn: Connection, name: str):
    q = "INSERT INTO students (name) VALUES (%s)"
    async with conn.cursor() as cur:
        await cur.execute(q, (name,))
```

- **Teste de regressão**: Inserir o payload `Robert'); DROP TABLE students CASCADE; --` como nome de aluno. Verificar que o nome é armazenado literalmente no banco de dados e que a tabela `students` continua existindo.

- **Como confirmar no segundo scan**: O Bandit (B608) não deve mais reportar achado de SQL injection em `sqli/dao/student.py`, pois a query agora usa parâmetros separados.

---

### VULN-02 — Stored XSS

- **Causa raiz**: Em `sqli/app.py:39`, o Jinja2 está configurado com `autoescape=False`. Isso significa que qualquer conteúdo inserido por usuários (como reviews de cursos) é renderizado como HTML bruto, sem escapar tags como `<script>`.

- **Patch proposto**:
```python
# ANTES:
setup_jinja(app, loader=PackageLoader('sqli', 'templates'),
            context_processors=[csrf_processor, auth_user_processor],
            autoescape=False)

# DEPOIS:
setup_jinja(app, loader=PackageLoader('sqli', 'templates'),
            context_processors=[csrf_processor, auth_user_processor],
            autoescape=True)
```

- **Teste de regressão**: Submeter `<script>alert('XSS')</script>` como texto de review. Verificar que o HTML renderizado contém `&lt;script&gt;` (escapado) e não executa JavaScript.

- **Como confirmar no segundo scan**: O Semgrep pode continuar acusando regras genéricas sobre templates Jinja2. Isso é aceitável — a correção efetiva é comprovada pelo teste de regressão, não pela ausência total de findings do Semgrep.

---

### VULN-03 — Session Fixation

- **Causa raiz**: Em `sqli/views.py:46`, após login bem-sucedido, a aplicação apenas define `session['user_id'] = user.id` sem regenerar o identificador da sessão. Um atacante que conheça o ID de sessão (cookie) antes do login herda a sessão autenticada. Agravante: em `sqli/middlewares.py:24`, `httponly=False` permite que JavaScript leia o cookie de sessão.

- **Patch proposto**:
```python
# Em sqli/views.py — no login:
session = await get_session(request)
session.clear()           # Limpa dados antigos
session._changed = True   # Marca como modificada
session._identity = None  # Remove identidade anterior
session._new = True       # Força criação de nova identidade
session['user_id'] = user.id

# Em sqli/views.py — no logout:
session = await get_session(request)
session.clear()
session._changed = True
session._identity = None
session._new = True

# Em sqli/middlewares.py:
storage = RedisStorage(app['redis'], httponly=True)  # era False
```

- **Teste de regressão**: Obter o cookie de sessão antes do login, fazer login, verificar que o cookie mudou (nova identidade de sessão gerada).

- **Como confirmar no segundo scan**: Bandit e Semgrep geralmente não detectam Session Fixation diretamente. A confirmação vem pelo teste de regressão funcional.

---

### VULN-04 — Armazenamento Fraco de Senhas

- **Causa raiz**: Em `sqli/dao/user.py:45`, `check_password()` usa `md5(password.encode()).hexdigest()` para comparar com o hash armazenado. MD5 é criptograficamente fraco, sem salt, e vulnerável a rainbow tables.

- **Patch proposto**:
```python
# Em sqli/dao/user.py:
# ANTES:
from hashlib import md5

def check_password(self, password: str):
    return self.pwd_hash == md5(password.encode('utf-8')).hexdigest()

# DEPOIS:
import bcrypt

def check_password(self, password: str):
    return bcrypt.checkpw(
        password.encode('utf-8'),
        self.pwd_hash.encode('utf-8')
    )
```

```
# Em requirements.txt — adicionar:
bcrypt
```

```sql
-- Em migrations/001-fixtures.sql — substituir md5() por hashes bcrypt pré-computados:
-- md5('superadmin') → '$2b$12$...'  (hash bcrypt de 'superadmin')
-- md5('password')   → '$2b$12$...'  (hash bcrypt de 'password')
-- md5('spidey')     → '$2b$12$...'  (hash bcrypt de 'spidey')
```

- **Teste de regressão**: Verificar que `check_password` valida corretamente as senhas conhecidas contra hashes bcrypt. Verificar que `hashlib.md5` não é mais importado em `user.py`.

- **Como confirmar no segundo scan**: O Bandit (B303) não deve mais reportar uso de MD5 em `sqli/dao/user.py`.

---

### VULN-05 — Cross-Site Request Forgery (CSRF)

- **Causa raiz**: Em `sqli/app.py:31`, o `csrf_middleware` está comentado na lista de middlewares da aplicação. A infraestrutura completa de CSRF existe (geração de token em `jinja2.py`, validação em `middlewares.py`, campos hidden nos templates), mas está desativada.

- **Patch proposto**:
```python
# Em sqli/app.py:
# ANTES:
from sqli.middlewares import session_middleware, error_middleware

app = Application(
    debug=True,
    middlewares=[
        session_middleware,
        # csrf_middleware,
        error_middleware,
    ]
)

# DEPOIS:
from sqli.middlewares import session_middleware, csrf_middleware, error_middleware

app = Application(
    debug=True,
    middlewares=[
        session_middleware,
        csrf_middleware,
        error_middleware,
    ]
)
```

- **Teste de regressão**: Enviar requisição POST para uma rota protegida sem incluir o token `_csrf_token` no formulário. A resposta deve ser HTTP 403 Forbidden.

- **Como confirmar no segundo scan**: O Semgrep não deve mais reportar middleware CSRF desativado. Caso regras genéricas permaneçam, a confirmação vem pelo teste funcional.
