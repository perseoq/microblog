# RULES.md — Reglas imperantes de `microblog`

> **Documento de cumplimiento obligatorio.**
> Todo cambio sobre `microblog` (código, carpetas o configuración) debe respetar estas reglas.
> Si una tarea planificada entra en conflicto con este documento, **mandan estas reglas**.

---

## 1. Requisito imperante

1. **No cambiar el patrón de código existente.**
2. **No cambiar la estructura de carpetas existente.**
3. **Mantener el proyecto limpio, con código sencillo y fácil de entender.**
4. **Diseñar para escalar en el futuro** sin reescrituras ni reorganizaciones.

`microblog` es una aplicación web de blog construida con **Flask**, **SQLAlchemy** y
**Flask-Login**, organizada en paquetes por responsabilidad (`blog/core`, `blog/arch`,
`blog/views`) con separación entre lógica, modelos, formularios y vistas.

---

## 2. Estructura canónica (no alterar)

```
microblog/
├── main.py                  # crea la app e inicializa extensiones y blueprints
├── wsgi.py                  # entrada WSGI / arranque del servidor
├── gunicorn.conf.py         # configuración de Gunicorn
├── pytest.ini               # configuración de pytest
├── migrations/              # migraciones de base de datos (Flask-Migrate)
├── tests/                   # pruebas automatizadas (pytest)
├── RULES.md                 # este documento
├── directory_blog.txt       # snapshot del árbol de carpetas
├── .env                     # variables de entorno (NO se versiona)
├── .gitignore
├── .venv/                   # entorno virtual (NO se versiona)
├── blog/
│   ├── arch/                # capa de dominio: modelos y formularios
│   │   ├── models.py        # modelos SQLAlchemy
│   │   ├── forms.py         # formularios WTForms
│   │   └── middleware.py    # middleware / hooks de petición
│   ├── core/                # infraestructura y configuración
│   │   ├── commands.py      # comandos CLI (seed-admin)
│   │   ├── database.py      # crea la base de datos si no existe
│   │   ├── enviroment.py    # carga de variables de entorno (dotenv)
│   │   ├── extensions.py    # instancias de extensiones Flask
│   │   ├── ratelimit.py     # límite de intentos en login y recuperación
│   │   ├── settings.py      # clases de configuración
│   │   ├── site.py          # configuración editable del sitio
│   │   ├── themes.py        # catálogo de temas y CSS dinámico
│   │   └── totp.py          # utilidades TOTP (2FA)
│   └── views/               # blueprints (una vista por archivo)
│       ├── auth.py          # blueprint 'auth' (login/logout/recover/install)
│       ├── admin.py         # blueprint 'admin' (panel de administración)
│       ├── blog.py          # blueprint 'blog'
│       ├── posts.py         # blueprint 'posts'
│       ├── pages.py         # blueprint 'pages'
│       └── gallery.py       # blueprint 'gallery'
├── static/
│   ├── css/
│   │   └── style.css
│   ├── img/
│   ├── js/
│   │   ├── script.js
│   │   ├── theme.js
│   │   ├── gallery-upload.js
│   │   ├── gallery-browser.js
│   │   ├── themes.js
│   │   ├── effects.js
│   │   ├── events.js
│   │   └── highlight.js
│   └── uploads/
│       ├── docs/
│       ├── imgs/
│       └── media/
└── templates/
    ├── base/                # layouts base
    │   ├── base_blog.html
    │   ├── base_admin.html
    │   ├── theme_toggle.html
    │   └── base_login.html
    ├── auth/                # autenticación e instalación
    │   ├── login.html
    │   ├── verify_2fa.html
    │   ├── recovery.html
    │   ├── reset.html
    │   └── install.html
    ├── blog/                # vistas públicas del blog
    │   ├── header.html
    │   ├── footer.html
    │   ├── sidebar.html
    │   ├── _post_list.html
    │   ├── home.html
    │   ├── index.html
    │   ├── categories.html
    │   ├── pages_index.html
    │   ├── posts.html
    │   ├── pages.html
    │   ├── gallery.html
    │   ├── gallery_detail.html
    │   └── search_by.html
    └── admin/               # panel de administración
        ├── dashboard.html
        ├── new_post.html
        ├── post_list.html
        ├── posts_list.html
        ├── pages_list.html
        ├── new_page.html
        ├── categories_list.html
        ├── tags_list.html
        ├── gallery.html
        ├── new_gallery.html
        ├── gallery_manage.html
        ├── gallery_browser.html
        ├── _ckeditor_gallery.html
        ├── profile.html
        ├── two_factor.html
        ├── site_config.html
        ├── themes.html
        ├── settings.html
        └── search_by.html
```

**Reglas de ubicación:**

- No renombrar, mover ni eliminar carpetas existentes.
- No reorganizar archivos ya existentes.
- Los archivos nuevos se crean **dentro de las carpetas existentes** y en la capa que
  les corresponde (`core` para infraestructura, `arch` para modelos/formularios,
  `views` para blueprints).
- Las plantillas se ubican en `templates/base/`, `templates/auth/`, `templates/blog/`
  o `templates/admin/` según su ámbito.
- Los recursos estáticos se sirven desde `static/` y respetan su subcarpeta:
  `css/`, `js/`, `img/` y `uploads/{docs,imgs,media}/`.
- Carpetas de primer nivel con propósito fijo y aprobado: `migrations/` (migraciones de
  Flask-Migrate) y `tests/` (pruebas con pytest).
- No crear otras carpetas de primer nivel nuevas sin justificación y aprobación explícita.

---

## 3. Patrón de código (no alterar)

- **Un blueprint por archivo** dentro de `blog/views/` (`auth.py`, `blog.py`,
  `posts.py`, `pages.py`, `gallery.py`). El objeto blueprint se define con
  `Blueprint('<nombre>', __name__)` y se importa desde la vista correspondiente.
- **Los blueprints se registran en `main.py`**, en un solo lugar
  (`app.register_blueprint(...)`), junto con la inicialización de extensiones.
- **Extensiones** (`bc`, `db`, `login`, `mail`, `csrf`, `ckeditor`) viven únicamente en
  `blog/core/extensions.py`. No se instancian en otros módulos.
- **Configuración** en `blog/core/settings.py` mediante clases (`Config`,
  `ProductionConfig`). Los valores se leen de `blog/core/enviroment.py`.
- **Variables de entorno** en `blog/core/enviroment.py` con `dotenv`; los módulos consumen
  esas constantes, nunca `os.getenv` disperso por el código.
- **Formularios** en `blog/arch/forms.py` con **Flask-WTF** y validadores de WTForms.
- **Modelos** en `blog/arch/models.py` con **SQLAlchemy**. Si un dominio crece, puede
  añadir su propio `models.py` dentro de su carpeta, sin mover los existentes.
- Se mantiene el estilo actual: rutas claras, `url_for(...)` para enlaces,
  mensajes/comentarios en español e identificadores en inglés sencillo.
- Nada de lógica de negocio en las plantillas: solo presentación. La herencia de
  plantillas parte de `templates/base/`.

---

## 4. Modelo de datos

Los modelos actuales son la base del dominio y no deben reestructurarse sin necesidad:

- **User** — usuario autenticable (Flask-Login), con TOTP opcional para el segundo factor.
- **SiteConfig** — título, descripción, texto del footer y tema editables desde el panel.
- **Category**, **Post**, **PostTags** — contenido del blog y su categorización.
- **Comment** — comentarios sobre publicaciones.
- **Page** — páginas estáticas.
- **ExternalLink** — enlaces externos.
- **Gallery**, **Image**, **ImagesPost**, **ImagesPage** — galería y su relación con
  posts y páginas.

- Las relaciones entre tablas se expresan con `db.relationship` y claves foráneas.
- Las tablas asociativas (`PostTags`, `ImagesPost`, `ImagesPage`) se definen con
  `__tablename__` explícito.
- Las fechas se gestionan con `db.DateTime` y `default=db.func.current_timestamp()`.

---

## 5. Reglas de calidad

- **Cada fase deja la aplicación arrancable** (`python wsgi.py`) y sin errores 500 conocidos.
- **Sin secretos ni credenciales en el código**: todo por variables de entorno (`.env`),
  que **nunca** se versiona.
- **Toda entrada de usuario se valida** con formularios WTForms y protección CSRF.
- **Funciones pequeñas y con una sola responsabilidad**; sin duplicación.
- **Sin código muerto** (nada de `pass` en vistas ni funciones vacías sin uso).
- **Comentarios solo donde aportan**; el nombre del código debe explicar el qué.
- Formato consistente y legible (PEP 8).

---

## 6. Reglas de escalabilidad

- Añadir funcionalidad nueva = añadir un blueprint en `blog/views/` (y su modelo/formulario
  si aplica), no reestructurar lo existente.
- Los módulos no se acoplan entre sí directamente: se comunican por funciones claras.
- La lógica compartida vive en `blog/core/`; los modelos y formularios de dominio, en
  `blog/arch/`.
- Antes de agregar complejidad, comprobar si una solución más simple respeta estas reglas.

---

## 7. Reglas de interfaz (UI)

- **Recursos locales únicamente.** El CSS vive en `static/css/` y el JavaScript en
  `static/js/`. **Sin CDN**: nada de recursos remotos.
- **Sin emojis.** La iconografía se hace con archivos servidos desde `static/`.
- Las plantillas heredan de una base en `templates/base/` (`base_blog.html`,
  `base_admin.html`, `base_login.html`) y no incluyen lógica de negocio.
- Los formularios se renderizan con WTForms e incluyen su token CSRF.
- Las subidas de archivos se guardan bajo `static/uploads/{docs,imgs,media}/` según su tipo.

---

## 8. Repositorio y control de versiones

- **Repositorio remoto oficial:** `https://github.com/perseoq/microblog.git`.
- **Regla imperante:** **cada vez que se termina una tarea se hace commit y push inmediato**
  a ese repositorio. El push no se acumula ni se deja para el final de una fase.
- No se considera terminada una tarea que no esté publicada en el remoto.
- Flujo por tarea: terminar la tarea → comprobar que la aplicación arranca → `git add` →
  `git commit` → `git push`.
- La rama principal es **`main`**.
- **Nunca** se suben secretos ni datos locales: `.env`, `.venv/`, `*.pyc`,
  `__pycache__/` y los archivos de `static/uploads/` deben estar en `.gitignore`.
- Antes de cada push, comprobar que la aplicación arranca y que se cumplen estas reglas.
- Mensajes de commit claros y descriptivos.

---

## 9. Registro de cambios (`LOG.md`)

- Cuando exista, `LOG.md` es el registro **cronológico de los commits**, en una tabla con
  `Fecha`, `Proyecto`, `Commit`, `Descripción` y `Cambios`.
- **Regla imperante:** **cada vez que se hace push se guardan en `LOG.md` los cambios nuevos**,
  añadiendo la entrada correspondiente al final.
- Los commits que solo actualizan el propio `LOG.md` no se registran (son mantenimiento).

---

## 10. Comandos habituales

- **Desarrollo:** `python wsgi.py` (usa `DEBUG` de la configuración).
- **Migraciones:** `flask --app wsgi db migrate -m "mensaje"` y `flask --app wsgi db upgrade`.
- **Crear administrador:** `flask --app wsgi seed-admin`.
- **Pruebas:** `pytest`.
- **Producción:** `gunicorn -c gunicorn.conf.py wsgi:app`.

---

## 11. Definición de "hecho"

Una tarea se considera terminada cuando:

1. La aplicación arranca (`python wsgi.py`) y la funcionalidad responde.
2. Las pruebas pasan (`pytest`).
3. Se respetan el patrón de código y la estructura de carpetas.
4. No se introducen secretos ni código muerto.
5. El código es legible por otra persona sin explicaciones adicionales.
6. Los cambios están publicados (**push**) en `https://github.com/perseoq/microblog.git`.
