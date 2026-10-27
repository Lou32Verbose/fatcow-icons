# FatCow Farm-Fresh icons

3,926 original icons in each of four variants: **16x16**, **16x16-grey**, **32x32** and **32x32-grey**. Use individual PNGs or CSS sprites with no runtime dependencies.

[Browse the icons](dist/index.html) by opening the catalogue locally in a browser. Packaging follows the [aspneticons](https://github.com/lou32Verbose/aspneticons) format.

## Choose a variant

| Variant | Appearance | PNG directory | Sprite directory / base CSS class |
| --- | --- | --- | --- |
| `16x16` | 16px, color | `dist/16x16/png/` | `dist/16x16/sprite/` / `fatcow-16x16` |
| `16x16-grey` | 16px, grey | `dist/16x16-grey/png/` | `dist/16x16-grey/sprite/` / `fatcow-16x16-grey` |
| `32x32` | 32px, color | `dist/32x32/png/` | `dist/32x32/sprite/` / `fatcow-32x32` |
| `32x32-grey` | 32px, grey | `dist/32x32-grey/png/` | `dist/32x32-grey/sprite/` / `fatcow-32x32-grey` |

Upstream exception: `file_extension_png.png` is 32x32 in both 16px variants. Its PNG, CSS and manifest preserve its actual size.

## Install

**Copy ready-to-use assets:** from this checkout or an extracted ZIP, copy the selected PNG directory or sprite directory into your application's static assets. Keep each sprite's CSS and PNG together.

**Install a local npm package:** with Node/npm installed, run this in the application consuming the pack:

```sh
npm install /path/to/fatcow-1.0.0.tgz
```

Assets are under `node_modules/fatcow/dist/`. Configure your bundler or static asset copying to expose the selected files. To create the tarball or ZIP from a checkout, see [contributor instructions](docs/contributing.md#build-and-verify).

**Use NuGet:** see [local NuGet packaging](docs/contributing.md#nuget). ASP.NET applications should copy the chosen assets into `wwwroot` to serve them.

## Display an individual icon

Copy `dist/16x16/png/` to `/assets/fatcow/16x16/`, then use:

```html
<img src="/assets/fatcow/16x16/accept.png" width="16" height="16" alt="Accepted">
```

## Display a sprite icon

Copy `dist/16x16/sprite/` to `/assets/fatcow/sprite/`, then use:

```html
<link rel="stylesheet" href="/assets/fatcow/sprite/fatcow.css">
<span class="fatcow-16x16 fatcow-accept" role="img" aria-label="Accepted"></span>
<button type="button"><span class="fatcow-16x16 fatcow-accept" aria-hidden="true"></span> Accept</button>
```

The first class selects the variant; the second is `fatcow-<filename without .png>`. Load the matching variant's stylesheet and use one variant per element. All four variants can coexist on a page. `fatcow.min.css` is the compact stylesheet.

## Attribution

Include this in your credits:

```html
Icons by <a href="http://www.fatcow.com/free-icons">FatCow</a>
```

See [LICENSE.md](LICENSE.md), [NOTICE.md](NOTICE.md) and the [original release notes](docs/upstream/readme-fatcow.txt). Registry publishing remains disabled pending clarification of the supplied redistribution notices.

## For contributors

Original artwork lives in `src/`; ready-to-use assets live in `dist/`. Build scripts are in `scripts/`, package templates in `packaging/`, and original reference files in `docs/upstream/`. Local packages are written to the ignored `artifacts/` directory.

See [contributor instructions](docs/contributing.md) for the full layout, build, verification and release workflow. [CHANGELOG.md](CHANGELOG.md) records changes.
