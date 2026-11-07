# Pruebas de seguridad, concurrencia y estrés — microblog

- **Fecha:** 2026-11-07
- **Commit de correcciones:** `b189d6a`
- **Entorno:** Python 3.14, Flask 3.1.3, SQLite temporal, Gunicorn 2 workers × 4 hilos
- **Alcance:** suite funcional, dependencias, OWASP Top 10, concurrencia y carga HTTP.
- **Importante:** todas las pruebas se hicieron sobre bases temporales. No se modificó `instance/database.db`.

## Resumen

| Área | Resultado |
|---|---|
| Suite funcional | **55/55 tests OK** |
| Dependencias (`pip-audit`) | **0 vulnerabilidades conocidas** |
| `pip check` | Sin conflictos |
| Bandit | 1 hallazgo medio, falso positivo (`Markup` tras `bleach.clean`) |
| OWASP dinámico | **59/59 comprobaciones OK** |
| Concurrencia | 1 carrera crítica encontrada y corregida |
| Estrés HTTP | 3.900 peticiones, **0 fallos**, **0 respuestas 500** |

---

## 1. Suite funcional

```bash
.venv/bin/pytest -q
```

Resultado:

```text
55 passed
```

Cubre autenticación, 2FA, posts, páginas, tags, categorías, galerías, AJAX del buscador, temas, configuración del sitio, seguridad de cabeceras y sanitización.

---

## 2. Dependencias y análisis estático

```bash
.venv/bin/pip check
.venv/bin/pip-audit -r requirements.txt
.venv/bin/bandit -q -r blog main.py
```

Resultados:

- `pip check`: sin dependencias rotas.
- `pip-audit`: **No known vulnerabilities found**.
- Bandit: `B704:markupsafe_markup_xss` en `main.py:93`.
  - Es un **falso positivo**: `Markup` se aplica al resultado de `bleach.clean(...)` con etiquetas, atributos, protocolos y CSS ya restringidos.

---

## 3. OWASP Top 10 — comprobaciones dinámicas

Se ejecutaron **59 comprobaciones** contra una app Flask con base temporal.

### Acceso y sesión

| Prueba | Resultado |
|---|---|
| `/admin/`, `/admin/posts`, `/admin/settings`, `/gallery`, `/admin/gallery/browser` sin sesión | 302 a login |
| Post y página en borrador sin sesión | 404 |
| Borrado sin sesión | 302 a login |
| `/install` cuando ya existe usuario | 302 a login |
| Login con `?next=http://evil.example` | Redirige a `/admin/`, no a `evil.example` |

### CSRF y rate limiting

| Prueba | Resultado |
|---|---|
| POST `/login` sin token CSRF | **400** |
| POST `/login` con token CSRF | 302 |
| 11 intentos de login fallidos | 10 × 200 + **1 × 429** |
| 6 intentos de recuperación | 5 × 302 + **1 × 429** |

### XSS / inyección

| Prueba | Resultado |
|---|---|
| `<script>alert(1)</script>` en contenido | Eliminado |
| `<img onerror=...>` | Eliminado |
| `href="javascript:..."` | Eliminado |
| iframe de dominio no permitido | Eliminado |
| iframe de YouTube permitido | Conservado |
| `style="position:fixed"` | Propiedad eliminada por el saneador CSS |
| Comentario con `<script>` | Escapado |
| Búsqueda con `<script>` | Escapada |
| Búsqueda `' OR 1=1 --` | 200, sin error SQL |
| `/post/1' OR '1'='1` y `/category/...` | 404 |

### Cookies y cabeceras

| Prueba | Resultado |
|---|---|
| `X-Content-Type-Options` | `nosniff` |
| `X-Frame-Options` | `DENY` |
| `Referrer-Policy` | `strict-origin-when-cross-origin` |
| `Permissions-Policy` | geolocation/microphone/camera deshabilitados |
| CSP | `frame-ancestors 'none'`, `object-src 'none'`, `frame-src` solo YouTube |
| HSTS | Presente solo sobre HTTPS |
| Cookie de sesión | `HttpOnly`, `SameSite=Lax` |
| Cookie `remember_token` | `HttpOnly`, `SameSite=Lax`; `Secure` en producción (**corregido**) |

### Uploads y archivos

| Prueba | Resultado |
|---|---|
| Subida `.php` | Rechazada, sin registro en BD |
| Nombre `../../evil.jpg` | Guardado como `uploads/imgs/<uuid>.jpg`, sin traversal |
| Archivo > 20 MB | Rechazado por `FileSize` |
| Upload anónimo | 302 a login |

### Recuperación de contraseña y 2FA

| Prueba | Resultado |
|---|---|
| Token inválido | 302 a `/recover` |
| Token válido | Cambia contraseña y permite login |
| Reutilizar el mismo token | Rechazado (**corregido**: token de un solo uso) |
| 2FA sin código | Rechazado |
| 2FA con código incorrecto | Rechazado |
| 2FA con código TOTP válido | Acceso a `/admin/` |

### Host header y configuración

| Prueba | Resultado |
|---|---|
| `Host: evil.example` en `/recover` | Rechazado por `TRUSTED_HOSTS` (**corregido**) |
| Ajustes `/admin/settings` | No muestra `MAIL_PASSWORD` ni `SECRET_KEY` |
| Tema inválido | Rechazado |

---

## 4. Concurrencia

Pruebas con `ThreadPoolExecutor` y clientes Flask independientes sobre SQLite temporal.

### Instalación simultánea (hallazgo crítico)

**Antes:** 4 peticiones simultáneas a `/install` creaban **4 usuarios administradores**.

**Después:** 5 iteraciones × 4 hilos → **1 usuario** en todas las iteraciones.

Corrección aplicada:

- Modelo `InstallState` con fila única `id=1`.
- El usuario y el registro de instalación se insertan en la misma transacción.
- Si dos peticiones compiten, una recibe `IntegrityError`, hace rollback y redirige a login.
- Migración: `migrations/versions/b7f1c9d2a4e6_install_state.py`.

### Tags en paralelo

- 10 posts simultáneos con `new_tags="compartido"`.
- Resultado: **10 posts, 1 tag, 10 relaciones**, todos 302, sin errores.
- No se reprodujo la carrera, aunque el patrón podría requerir reintento en otros motores/isolation levels.

### Comentarios en paralelo

- 10 comentarios simultáneos.
- Resultado: **10 comentarios**, todos 302, sin errores.

### Rate limit en paralelo

- 20 intentos de login simultáneos desde la misma IP.
- Resultado: **10 × 200** y **10 × 429**. El lock de `blog/core/ratelimit.py` funciona.

---

## 5. Estrés HTTP

Servidor: Gunicorn con **2 workers × 4 hilos**, SQLite temporal, ApacheBench con keep-alive.

| Endpoint | Peticiones | Concurrencia | RPS | Media | Fallos | 500 |
|---|---:|---:|---:|---:|---:|---:|
| `/` | 1.500 | 50 | 190,94 | 261,86 ms | 0 | 0 |
| `/post/1` | 800 | 40 | 248,07 | 161,24 ms | 0 | 0 |
| `/search?q=prueba` | 800 | 40 | 256,96 | 155,66 ms | 0 | 0 |
| `/theme.css` | 800 | 40 | 2.326,47 | 17,19 ms | 0 | 0 |

Conclusión: sin errores ni 500 bajo carga concurrente. El cuello de botella es SQLite para escrituras; para producción con más carga conviene MySQL/PostgreSQL.

---

## Migraciones multi-motor (MySQL/MariaDB/PostgreSQL)

Se revisó toda la cadena de migraciones. El fallo en MariaDB (`1060 Duplicate column name 'status'`) venía de aplicar una migración sobre un esquema que ya tenía `status` (creado fuera de Alembic).

Correcciones:

- `9e178187db95`:
  - Añade `status` a `page`/`post` solo si no existe.
  - Altera `totp_secret` a `VARCHAR(255)` solo si su longitud es menor.
  - Cifra secretos TOTP solo si están en texto plano; los ya cifrados se dejan intactos.
  - Usa `identifier_preparer.quote_identifier('user')`: backticks en MySQL/MariaDB y comillas dobles en PostgreSQL/SQLite.
- `0cc0f3a789b4`, `34aef1adb0dd`, `710da5fe58f0`, `b7f1c9d2a4e6`: idempotentes (comprueban columnas/tablas antes de crearlas).
- `0cc0f3a789b4`: `server_default=sa.false()` en lugar de `sa.text('0')` para portabilidad del booleano.
- La migración inicial `3572661ab018` sigue asumiendo un esquema vacío, como es estándar; si la base fue creada con `db.create_all`, hay que sellar la revisión correspondiente o usar las migraciones idempotentes posteriores.

Validación realizada:

- Cadena completa desde cero en SQLite: **OK**.
- Esquema “adelantado” con `status` ya presente y TOTP en texto plano + ya cifrado: **upgrade OK**, sin columnas duplicadas y cifrando solo lo necesario.
- Suite completa: **55/55 tests OK**.

---

## 6. Hallazgos y correcciones

| Severidad | Hallazgo | Estado |
|---|---|---|
| Crítica | Carrera en `/install` permitía crear varios administradores | **Corregido** con `InstallState` |
| Media | Token de recuperación reutilizable | **Corregido**: token ligado al hash actual de contraseña |
| Media | Host header poisoning en el enlace de recuperación | **Corregido** con `TRUSTED_HOSTS` |
| Media | Cookie `remember_token` sin `Secure`/`SameSite` | **Corregido** |
| Baja | `DEBUG=True` en `.env` | **Pendiente para producción**: usar `DEBUG=False` y HTTPS |
| Baja/Media | CSP con `unsafe-inline` y `unsafe-eval` | **Pendiente**: requerido por CKEditor/scripts inline; endurecer con nonces/hashes |
| Baja | Rate limiting en memoria por proceso | **Pendiente**: usar Redis si hay varios workers |
| Baja | Sin `ProxyFix` para proxy inverso | **Pendiente**: configurar `X-Forwarded-Proto` para HSTS/enlaces |
| Baja | Sin auditoría centralizada de logins/cambios | **Recomendado** |

---

## 7. Recomendaciones operativas

1. **Aplicar la migración nueva:**
   ```bash
   flask --app wsgi db upgrade
   ```

2. **Producción:** `DEBUG=False`, HTTPS obligatorio y `TRUSTED_HOSTS` con el dominio real:
   ```env
   DEBUG=False
   TRUSTED_HOSTS=midominio.com,www.midominio.com
   ```

3. **Rate limiting distribuido:** Redis si se usan varios workers/hosts.

4. **Proxy inverso:** configurar `ProxyFix` o `X-Forwarded-Proto` para que HSTS y los enlaces absolutos usen HTTPS.

5. **Base de datos:** SQLite es suficiente para desarrollo; para escrituras concurrentes usar MySQL/PostgreSQL.

6. **CSP:** sustituir `unsafe-inline`/`unsafe-eval` por nonces/hashes cuando se pueda.

---

## 8. Reproducción

### Tests y dependencias

```bash
.venv/bin/pytest -q
.venv/bin/pip check
.venv/bin/pip-audit -r requirements.txt
.venv/bin/bandit -q -r blog main.py
```

### Estrés

```bash
DB=/tmp/microblog-stress.db
rm -f "$DB"
DEBUG=True DATABASE_URI="sqlite:///$DB" PYTHONPATH=. .venv/bin/python - <<'PY'
from main import app
from blog.core.extensions import db
from blog.arch.models import User, Category, Post, Page
with app.app_context():
    db.drop_all(); db.create_all()
    user = User(username='admin', email='admin@example.com')
    user.set_password('secret123')
    category = Category(name='Python')
    db.session.add_all([user, category]); db.session.commit()
    for i in range(20):
        db.session.add(Post(title=f'Post {i}', content='<p>Contenido</p>' * 5,
                            category_id=category.id, user_id=user.id, status='published'))
    db.session.add(Page(title='Acerca', content='<p>Pagina</p>', user_id=user.id, status='published'))
    db.session.commit()
PY

DEBUG=True DATABASE_URI="sqlite:///$DB" PORT=10333 \
  WEB_CONCURRENCY=2 GUNICORN_THREADS=4 \
  .venv/bin/gunicorn -c gunicorn.conf.py wsgi:app &

ab -q -k -n 1500 -c 50 http://127.0.0.1:10333/
ab -q -k -n 800 -c 40 http://127.0.0.1:10333/post/1
ab -q -k -n 800 -c 40 'http://127.0.0.1:10333/search?q=prueba'
ab -q -k -n 800 -c 40 http://127.0.0.1:10333/theme.css
```

### Nota

Las pruebas OWASP y de concurrencia se ejecutaron con scripts temporales de auditoría durante la sesión, usando bases SQLite en `/tmp` y clientes Flask independientes. No se incluyeron credenciales reales en este informe.
