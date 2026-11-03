# JobHunter Community Enterprise PRO v6.0 — LinkedIn Edition

**Integración Comunitaria:** registro local de búsquedas en SQLite, métricas por orden, almacenamiento de ofertas agregadas manualmente y envío opcional al webhook Discord, sin scraping ni credenciales de LinkedIn.

**Instalación y seguridad:** consulta [COMMUNITY_v6.md](COMMUNITY_v6.md) y [backend/INSTALAR_WINDOWS.bat](backend/INSTALAR_WINDOWS.bat).

**Aviso de compatibilidad:** este repositorio contenía los archivos de v3.0 cuando comenzó la integración; el módulo Comunidad se añadió sin eliminar las funciones que ya existían en `main`. La distribución ZIP de v5.0 contiene módulos adicionales que aún requieren portarse explícitamente al repositorio.

---

# Azzlaer JobHunter Enterprise PRO v3.0 — LinkedIn Edition

Extensión Chrome Manifest V3, en español, centrada exclusivamente en búsquedas laborales de LinkedIn. Interfaz Corporate Blue con panel lateral.

## Instalar
1. Extrae el ZIP completo. NO selecciones directamente el ZIP desde Chrome.
2. Visita `chrome://extensions/` y activa **Modo de desarrollador**.
3. Selecciona **Cargar descomprimida** y elige la carpeta `Azzlaer_JobHunter_LinkedIn_Enterprise_v3` que contiene `manifest.json`.
4. Fija el icono de la extensión y haz clic: se abrirá el panel lateral (Chrome 116 o posterior).
5. Si instalaste v2, puedes desactivarla para evitar confusiones. La versión v3 tiene almacenamiento separado: los datos v2 no se migran automáticamente.

## Funciones
- Generación de búsquedas en LinkedIn según cargo, modalidad remota, nivel y fecha.
- Captura **manual** de URLs, título, empresa, modalidad y descripción de empleos LinkedIn.
- Evaluación **heurística y orientativa**, sin servicios de terceros ni IA integrada obligatoria.
- Filtros por texto, compatibilidad, modalidad, estado, seniority e inglés oral avanzado.
- Gestión del historial: guardar, actualizar, editar, abrir, marcar postulaciones y eliminar.
- Dashboard, análisis local de skills, recomendaciones de perfil.
- Asistente opcional basado en prompts para ChatGPT; copia solo cuando el usuario lo pide.
- Prompts para adaptación de CV, análisis de oferta, traducción, mensajes y entrevistas.
- Exportación CSV (compatible con Excel), JSON y recuperación desde respaldo JSON.
- Datos guardados en `chrome.storage.local` del perfil de Chrome; NO hay sincronización en la nube.

## Seguridad y alcance
- No solicita contraseñas de LinkedIn ni de Google, ni claves de API.
- No instala scripts en LinkedIn, no recorre páginas automáticamente, no hace scraping ni postulaciones automáticas.
- Permiso `tabs`: se usa para abrir LinkedIn y para copiar el **enlace de la pestaña activa** cuando pulsas "Pestaña"; no lee el contenido de la página.
- Permisos `storage` y `sidePanel`: guardar datos en Chrome y mostrar el panel lateral.
- Sin `host_permissions`, sin servidores propios y sin peticiones API en segundo plano.
- Al usar "Abrir ChatGPT", se abre la web. El prompt no se envía ni pega automáticamente: revísalo y compártelo solo si quieres.
- Los porcentajes de compatibilidad no son probabilidades de contratación. Son reglas simples sobre las palabras del texto proporcionado.
- Solo se aceptan URL `https://linkedin.com/jobs/...` y subdominios previstos `www` o `cl`.
- Al exportar CSV se protege contra fórmulas iniciadas por `=`, `+`, `-` y `@`.
- No conserves información privada de terceras personas en las descripciones o las notas.

## Limitaciones
- LinkedIn puede cambiar sus URLs o sus filtros. Los parámetros de búsqueda pueden no estar disponibles para todos los usuarios/regiones.
- No existe lectura automática del contenido de una vacante: tienes que pegarlo.
- La traducción y la IA son **asistidas** mediante prompts, no integradas dentro de la extensión.
- El currículum adaptado se genera mediante el asistente que decidas usar; la extensión no crea nuevos PDF o DOCX por sí sola.
- Las puntuaciones y las alertas son estimaciones que requieren revisión humana.

## Pruebas
Ejecuta `node tests/test-core.js` desde esta carpeta para probar validación, scoring, búsquedas, prompts y CSV. La instalación y navegación visual deben verificarse adicionalmente en Chrome.

**Licencia:** proyecto de portafolio personal. Revisa la licencia antes de distribuir o publicar el código.
