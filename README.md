# ISH / ICH2026 website

Static multipage website for the International Society for Hantaviruses and the
ICH2026 meeting.

## Files

- `content/`: source of truth for public pages and shared content.
- `index.html`: generated public home page.
- `about-ish/`, `communications/`, `contact/`, `former-meetings/`, `ich2026/`:
  generated static pages matching the site structure.
- `styles.css`: responsive design, layout, motion and theme.
- `script.js`: mobile menu, scroll reveal and active navigation state.
- `scripts/build_site.py`: regenerates static HTML from `content/`.

## Public website workflow

The public website does not depend on ISH Editor. It can be updated, built,
validated, previewed and published with Python's standard library only.

After changing `content/`, assets, styles or public JavaScript, run:

```bash
./update-site.sh
```

On Windows use `update-site.cmd`. To regenerate and serve the public website on
`0.0.0.0:8080`, independently from the editor, run:

```bash
./start-site.sh
```

On Windows use `start-site.cmd`. The complete maintenance workflow is described
in [`docs/sitio-publico.md`](docs/sitio-publico.md).

### Direct file preview

This can be opened directly in a browser:

`/mnt/data2/pagina_nicole/frontend/index.html`

For a closer production preview, serve the folder with any static server and open
the generated local URL.

## Optional local visual editor

El repositorio incluye **ISH Editor**, una aplicacion visual para modificar el
contenido sin editar HTML, CSS, JavaScript ni JSON. Permite trabajar sin
conexion, guardar borradores, previsualizar cada pagina, administrar imagenes y
PDF, recuperar versiones y publicar directamente en la rama `gh-pages`.

El editor es opcional: no se necesita para usar `update-site.sh`, revisar el
sitio publico ni publicarlo manualmente.

En Linux o macOS:

```bash
./start-editor.sh
```

La edicion comercial se configura y recuerda localmente:

```bash
./start-editor.sh --edition basic     # $800.000, alcance visible
./start-editor.sh --edition advanced  # $1.200.000, alcance visible
./start-editor.sh --edition unified   # todas las funciones, sin distincion
```

En Windows, ejecutar `start-editor.cmd`. La primera apertura instala las
dependencias locales y compila la interfaz; las aperturas posteriores son
directas. El editor escucha en `0.0.0.0` para acceso por LAN o Tailscale y usa credenciales
locales con una sesion protegida. No depende de un servicio de autenticacion en
linea. Solo **Sincronizar** y **Publicar** se conectan con GitHub.

La guia completa para editores esta en
[`docs/editor-usuario.md`](docs/editor-usuario.md). La separacion entre la
cotizacion de administracion y el sitio personalizado se documenta en
[`docs/alcance-cotizacion.md`](docs/alcance-cotizacion.md).

### Aplicaciones instalables

El workflow `Build ISH Editor` genera automaticamente:

- `ISH-Editor.exe` para Windows.
- `ISH-Editor-macOS.dmg` para macOS.
- `ISH-Editor-x86_64.AppImage` para Linux.

Se puede ejecutar manualmente desde GitHub Actions. Al crear una etiqueta como
`editor-v0.1.0`, los tres paquetes tambien se adjuntan a una nueva release. No
requieren Python o Node.js, pero si una instalacion local de Git. Actualmente no
estan firmados con certificados comerciales del sistema operativo.

## GitHub Pages

Repository:

`https://github.com/fundacion-ciencia-vida/ISH`

Expected GitHub Pages URL:

`https://fundacion-ciencia-vida.github.io/ISH/`

This repository is published from the `gh-pages` branch. If the Pages site is
not active yet, enable it in GitHub:

1. Open `https://github.com/fundacion-ciencia-vida/ISH/settings/pages`.
2. Under `Build and deployment`, choose `Deploy from a branch`.
3. Branch: `gh-pages`.
4. Folder: `/ (root)`.
5. Click `Save`.
6. Wait 1-3 minutes and open `https://fundacion-ciencia-vida.github.io/ISH/`.

## Deployment

The configured SSH remote for the Fundacion Ciencia Vida repository is:

`git@github-fcv:fundacion-ciencia-vida/ISH.git`

Build and validate the site, then publish the current branch to GitHub Pages:

```bash
./update-site.sh
git push fcv gh-pages:gh-pages
```

La publicacion desde ISH Editor realiza el mismo destino de forma controlada:
sincroniza GitHub, compila en un worktree temporal, valida enlaces y recursos,
crea un commit identificable y solo entonces lo envia a `gh-pages`.

## Google Sites embed

This site can also be embedded in Google Sites through
`Insert > Embed > Embed URL`.

Important iframe requirement: the hosting service must not block embedding with
`X-Frame-Options` or a restrictive `Content-Security-Policy frame-ancestors`
header.

## Asset note

Images are now stored locally under `assets/images/`, so the published page does
not depend on Google Sites image hotlinks. Keep replacing or optimizing those
files in the same paths as the site evolves.
