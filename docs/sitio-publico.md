# Mantenimiento independiente del sitio publico

El sitio publico y el editor local son dos herramientas separadas. El sitio es
estatico, no necesita FastAPI, React, una base de datos ni el proceso de ISH
Editor para compilarse, revisarse o publicarse.

## Fuente del sitio

- `content/site.json`: datos generales, navegacion, enlaces y fechas comunes.
- `content/pages/`: contenido y estructura de cada pagina.
- `content/collections/`: noticias y registros compartidos.
- `assets/`: imagenes, documentos, iconos y fuentes.
- `styles.css` y `script.js`: presentacion y comportamiento publico.
- `scripts/build_site.py`: genera los HTML estaticos.
- `scripts/validate_site.py`: comprueba contenido, enlaces internos y recursos.

Los archivos `index.html` de la raiz y de cada ruta son resultados generados. Un
cambio manual hecho solamente sobre ellos se perdera en la siguiente
compilacion; los cambios permanentes deben hacerse en las fuentes anteriores.

## Actualizar sin el editor

En Linux o macOS:

```bash
./update-site.sh
```

En Windows:

```bat
update-site.cmd
```

Estos comandos regeneran y validan todo el sitio usando solo la biblioteca
estandar de Python. No instalan, importan ni inician el editor.

## Ver el sitio localmente

En Linux o macOS:

```bash
./start-site.sh
```

En Windows:

```bat
start-site.cmd
```

El sitio queda disponible por defecto en `http://127.0.0.1:8080/` y escucha en
`0.0.0.0:8080` para poder revisarlo desde la red local o Tailscale. El puerto se
puede cambiar con `ISH_SITE_PORT` y la interfaz con `ISH_SITE_HOST`.

## Publicar sin el editor

1. Ejecutar `update-site.sh` o `update-site.cmd`.
2. Revisar `git status --short` y las diferencias generadas.
3. Crear un commit con las fuentes y los HTML resultantes.
4. Enviar la rama `gh-pages` al remoto `fcv`.

```bash
git push fcv gh-pages:gh-pages
```

GitHub Actions vuelve a compilar y validar el sitio sin dependencias del editor.
Si falta regenerar algun archivo, la comprobacion falla antes de considerar la
version lista.

## Relacion con ISH Editor

ISH Editor es una interfaz opcional sobre la misma fuente estructurada. Guardar
borradores o abrir una vista previa escribe solamente dentro de `.ish-editor/`,
una carpeta local ignorada por Git. No modifica el sitio publico.

Solo la accion explicita **Publicar** del editor genera un commit mediante un
worktree temporal. Si existen cambios manuales sin incorporar, la publicacion
se bloquea para no sobrescribirlos. El flujo directo descrito en este documento
sigue disponible aunque el editor este cerrado o no se haya instalado.
