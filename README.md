
# Flask: Autenticación vs Autorización + Hash de contraseñas + .env

App que muestra:
- **Autenticación** (login) y **Autorización** (acceso por rol).
- **Hash de contraseñas** con `werkzeug.security` (PBKDF2-SHA256).
- **Protección de datos sensibles** usando variables de entorno (`SECRET_KEY`, `DATABASE_URL`) cargadas con `python-dotenv`.

## Requisitos
- Python 3.10+ recomendado

## Instalación
```bash
cd flask_auth_auten
python -m venv .venv
# Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

Crea un archivo `.env` (o copia `.env.example`):
```
SECRET_KEY=ef5c00b968c4c14d2f3c698632d9c5a6d0729217d205bc6d4085fad1cebf5e07
DATABASE_URL=sqlite:///app.db
```

## Inicializa la base y un admin por defecto
```bash
flask --app app.py init-db
```
Esto crea las tablas y un admin: `usuario=admin`, `password=admin123` (recuerden cambiarlo luego).

## Ejecuta
```bash
flask --app app.py run
```
Se abre por defecto la siguiente URL http://127.0.0.1:5000

## Prueba rápida
1. Entra a **/register** y crea un usuario con rol `user`.
2. Haz login en **/login**.
3. Visita **/dashboard** (debe permitirte entrar por estar autenticado).
4. Intenta entrar a **/admin** con rol `user` (debe **bloquearte** por autorización).
5. Cierra sesión, inicia como `admin` y entra a **/admin** (debe **permitirte**).

## Buenas prácticas incluidas
- No se guardan contraseñas en texto plano (solo hashes).
- `SECRET_KEY` y `DATABASE_URL` NUNCA se hardcodean. Se leen de variables de entorno.
- Decoradores `@login_required` y `@role_required` para separar autenticación y autorización.
```

