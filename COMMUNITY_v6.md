# Azzlaer JobHunter Community v6 — LinkedIn Edition

Integración de la v5 con un servicio **Python Native Messaging + SQLite** y un módulo de comunidad con Discord. Sin scraping ni accesos a credenciales.

## Windows

1. Abre `chrome://extensions`, activa **Modo de desarrollador** y copia el ID de la extensión.
2. Instala la extensión desde la **raíz del repositorio** usando **Cargar descomprimida**.
3. Ejecuta `backend/INSTALAR_WINDOWS.bat`, pega el ID y reinicia Chrome. Requiere Python 3.10+.
4. Abre el apartado **Comunidad** y pulsa **Probar conexión**. La base se genera en `%USERPROFILE%/AzzlaerJobHunter/jobhunter.sqlite3`.
5. En Comunidad puedes configurar un webhook de Discord. Configurar es opcional y ambas opciones de publicación están desactivadas por defecto. **No añadas tu webhook a GitHub.**

**Importante:** las búsquedas son URLs de resultados, **no vacantes verificadas**. Los enlaces de ofertas se guardan manualmente. Los contadores Comunidad se obtienen desde SQLite; el seguimiento y CV de v5 permanecen en Chrome. No hay postulación automática.

## Comprobaciones

`python -m unittest discover -s tests -p "test_native.py"`

`node tests/test-core.js`

`node tests/test-ultimate.js`

## Privacidad
No se guardan contraseñas de LinkedIn, ni se envían CV o datos de usuario a Discord. El webhook reside en el archivo `config.json` de tu perfil de Windows, nunca en el repositorio. Cada búsqueda se registra cuando la inicias tú. No existe extracción de datos del DOM de LinkedIn.

**Proyecto independiente sin afiliación oficial con LinkedIn o Discord.**
