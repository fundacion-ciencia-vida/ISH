# Arquitectura de ISH Editor

El sitio publico sigue siendo estatico y compatible con GitHub Pages. El editor
no agrega una base de datos ni un servidor publico.

## Independencia del sitio publico

El editor no forma parte del runtime ni del proceso obligatorio de construccion
del sitio. `update-site.sh` y `update-site.cmd` regeneran y validan la web usando
solo `content/`, `assets/`, `styles.css`, `script.js` y `scripts/`, incluso si el
editor esta cerrado o no se han instalado sus dependencias.

Los borradores y vistas previas del editor se guardan en `.ish-editor/`, fuera
de las fuentes publicas e ignorados por Git. La accion explicita **Publicar** es
el unico flujo del editor que puede crear y enviar un commit. El mantenimiento
directo se documenta en `docs/sitio-publico.md`.

## Componentes

- `content/`: fuente de verdad estructurada en JSON, esquema version 1.
- `scripts/content_store.py`: carga, validacion, escritura atomica y sanitizacion.
- `scripts/build_site.py`: renderizador determinista de JSON a HTML estatico.
- `scripts/validate_site.py`: verificacion de paginas, recursos y formatos.
- `editor/`: API FastAPI local, borradores, medios, historial y operaciones Git.
- `editor/ui/`: interfaz React/TypeScript con inspector y vista previa aislada.
- `packaging/`: entrada y especificacion para aplicaciones PyInstaller.

## Seguridad local

El servidor escucha en `0.0.0.0` para una red local o Tailscale, manteniendo protegido el editor con
usuario y contrasena locales. La contrasena se deriva con PBKDF2-SHA256, sal
aleatoria e iteraciones elevadas; el archivo local nunca contiene la contrasena
original. Las sesiones viven en memoria y se entregan mediante una cookie
`HttpOnly` con `SameSite=Strict`. La vista previa de borradores tambien requiere
una sesion valida. Los intentos de acceso repetidos se limitan temporalmente y
la contrasena se puede cambiar o restablecer sin recurrir a un servicio remoto.

No existe un proveedor de identidad en linea. El token de GitHub se obtiene del
llavero del sistema y se entrega a Git mediante un helper `GIT_ASKPASS` temporal;
no forma parte de argumentos, URL, contenido ni commits. Una llave SSH local
tambien puede autorizar solamente las operaciones de sincronizacion y
publicacion.

El HTML enriquecido usa una lista permitida de etiquetas y atributos. Las rutas
de paginas y archivos se normalizan y se comprueban antes de tocar el sistema de
archivos.

## Publicacion transaccional

1. Se valida el borrador y se consulta el commit remoto.
2. Se bloquea si existen cambios manuales o conflictos de contenido.
3. Se crea un `git worktree` temporal desde el ultimo commit remoto.
4. Se escriben los JSON, se incorporan medios y se generan variantes.
5. Se compila y valida el sitio completo.
6. Se comprueba que solo hayan cambiado rutas administradas.
7. Se crea y envia el commit a `gh-pages`.
8. Se actualiza la copia principal y se limpia el estado pendiente.

Un error en cualquier etapa elimina el worktree temporal y conserva el borrador
local para corregirlo o intentarlo nuevamente.

## Ediciones y alcance

`editor/config.py` es la unica fuente de configuracion comercial. La API expone
la edicion activa y entrega los catalogos estructurales solo cuando corresponde.
La interfaz no replica reglas de precio ni decide permisos por su cuenta.

- `basic`: contenido existente y noticias; muestra la separacion de $800.000.
- `advanced`: habilita estructura y muestra la separacion de $1.200.000.
- `unified`: habilita estructura y elimina toda presentacion comercial.

`--edition` guarda la seleccion en el perfil local. La variable
`ISH_EDITOR_EDITION` la reemplaza temporalmente para empaquetado o pruebas. La
matriz completa se encuentra en `docs/alcance-cotizacion.md`.
