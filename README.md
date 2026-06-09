# ISH / ICH2026 website

Static multipage website for the International Society for Hantaviruses and the
ICH2026 meeting.

## Files

- `index.html`: public home/About ISH page.
- `about-ish/`, `communications/`, `contact/`, `former-meetings/`, `ich2026/`:
  static pages matching the site structure.
- `styles.css`: responsive design, layout, motion and theme.
- `script.js`: mobile menu, scroll reveal and active navigation state.
- `scripts/build_site.py`: regenerates the static HTML pages from shared page data.

## Local preview

This can be opened directly in a browser:

`/mnt/data2/pagina_nicole/frontend/index.html`

For a closer production preview, serve the folder with any static server and open
the generated local URL.

Regenerate pages after editing shared content:

`python3 scripts/build_site.py`

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

Publish the current branch to GitHub Pages:

`git push fcv gh-pages:gh-pages`

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
