# Contributing to FatCow

Run all commands from the repository root. Source artwork belongs in `src/`; generate the installable assets in `dist/` with the build script.

## Repository layout

```text
fatcow/
â”œâ”€â”€ README.md                  Installation, usage and attribution
â”œâ”€â”€ LICENSE.md
â”œâ”€â”€ NOTICE.md
â”œâ”€â”€ CHANGELOG.md
â”œâ”€â”€ package.json               npm package metadata and commands
â”œâ”€â”€ requirements.txt           Pinned build dependency
â”œâ”€â”€ src/                       Original PNGs, preserved byte-for-byte
â”‚   â”œâ”€â”€ 16x16/
â”‚   â”œâ”€â”€ 16x16-grey/
â”‚   â”œâ”€â”€ 32x32/
â”‚   â””â”€â”€ 32x32-grey/
â”œâ”€â”€ dist/                      Generated, committed installation assets
â”‚   â”œâ”€â”€ <variant>/png/
â”‚   â”œâ”€â”€ <variant>/sprite/      fatcow.png, fatcow.css, fatcow.min.css
â”‚   â”œâ”€â”€ icons.json             Hashes, source paths, dimensions, positions
â”‚   â””â”€â”€ index.html             Searchable offline catalogue
â”œâ”€â”€ docs/
â”‚   â”œâ”€â”€ contributing.md
â”‚   â””â”€â”€ upstream/              Original release notes and filename list
â”œâ”€â”€ scripts/
â”‚   â”œâ”€â”€ build.py
â”‚   â””â”€â”€ verify.py
â”œâ”€â”€ packaging/
â”‚   â””â”€â”€ nuget/fatcow.nuspec
â”œâ”€â”€ .github/workflows/verify.yml
â””â”€â”€ artifacts/                 Ignored local packages and install tests
```

The old root-level source directories now live under `src/`. Source paths in `dist/icons.json` are repository-relative and include `src/`. Generated PNG paths, sprite URLs and CSS classes retain their existing names.

## Build and verify

Requires Python 3.11+ and Pillow. Node/npm is only required for npm packaging; the NuGet CLI is only required for NuGet packaging.

```sh
python -m pip install -r requirements.txt
python scripts/build.py
python scripts/verify.py
```

The build validates source names, format and dimensions before producing output. Each variant is catalogued independently. Sprite entries have transparent padding to prevent neighboring pixels bleeding into an icon.

The upstream `file_extension_png.png` is 32x32 in both 16px source folders. The build explicitly handles this exception without resizing the original. Other unexpected dimensions fail the build.

Verification checks all 15,704 PNG copies against original bytes and SHA-256 hashes, checks sprite pixels and CSS coordinates, and checks the manifest and minified CSS. Commit regenerated `dist/` with source or build changes; do not edit generated files directly.

Open `dist/index.html` in a browser to browse or search all variants locally.

## Create local packages

### ZIP

```sh
python scripts/build.py --archive
```

Creates `artifacts/fatcow-1.0.0.zip` containing built assets, documentation and upstream notices. Archive order, timestamps and permissions are fixed so the same inputs produce the same ZIP. Verify the build before distributing it.

### npm

With Node/npm installed, build and verify first, then run:

```sh
npm pack
```

Creates `fatcow-1.0.0.tgz` in the repository root. `prepack` verifies existing assets; it does not build them. The package contains `dist/`, documentation and attribution files. Installing it requires no Python build step.

To test installation in a separate local application:

```sh
npm install /absolute/path/to/fatcow-1.0.0.tgz
```

Equivalent maintainer commands are `npm run build`, `npm test` and `npm run archive`.

### NuGet

On Windows with Python dependencies and the .NET 10 SDK installed, run:

```sh
python scripts/pack_nuget.py
```

This verifies existing assets, downloads NuGet CLI 7.9.0 from dist.nuget.org into ignored `artifacts/tools/`, packs the template with the current Git commit, checks every packaged payload byte and metadata, and restores/builds an isolated .NET 10 consumer from a local feed with a fresh cache. Errors and warnings fail validation. A `.nupkg.sha256` file is written only after all checks pass. Rebuild first if source artwork changed.

Outputs are `artifacts/fatcow.1.0.0.nupkg` and its SHA-256 file. The package contains legacy `content/fatcow` and modern `contentFiles/any/any/fatcow` assets, documentation and attribution. PackageReference builds copy assets to `fatcow/` under the build output. For ASP.NET applications, copy selected files into `wwwroot`; output copying alone does not make them web-accessible.

## Continuous integration

CI builds and verifies on Windows and Linux, checks the committed distribution for drift, checks reproducible ZIP output, creates an npm tarball, and installs that tarball in an isolated directory. Packages are retained as workflow artifacts.

## Manual NuGet.org release

1. Preserve the CC BY 3.0 US license, FatCow attribution and original upstream notices. The licensing basis is recorded in LICENSE.md.
2. Keep package.json, the NuGet template, versioned examples and CI paths in sync. Record changes in CHANGELOG.md. npm remains private; a NuGet release does not require changing it.
3. Rebuild, verify and inspect the catalogue. Commit all release changes and require the Windows and Linux CI jobs to pass. The packed repository commit must match that release commit; packages made from a dirty checkout are for local review only.
4. Download the `.nupkg` and `.nupkg.sha256` from the passing Windows CI artifact. Check the package with `Get-FileHash artifacts/fatcow.1.0.0.nupkg -Algorithm SHA256` and compare against the supplied checksum. Inspect archive contents and the repository commit before uploading. A checksum checks artifact integrity, not publisher identity.
5. Sign in to the intended NuGet.org publisher account. Check the `fatcow` ID and `1.0.0` version in the gallery and upload flow, including ownership or reserved-prefix restrictions. An absent search result does not guarantee availability. If the ID/version conflicts, stop and explicitly decide the new ID/version; do not overwrite or silently rename.
6. Open https://www.nuget.org/packages/manage/upload and select the validated `.nupkg`. Review ID, version, license, README, repository links, ownership and all validation messages in the preview, then submit manually. No credentials belong in this repository or CI.
7. After indexing, inspect https://www.nuget.org/packages/fatcow/1.0.0 and test installation from NuGet.org in a fresh application. If a defect is discovered, unlist the affected release if appropriate and prepare a new version; published versions cannot be replaced.

CI never publishes packages. The Windows job also packs and validates NuGet, restores/builds the isolated consumer and retains the package plus checksum alongside the existing ZIP/npm artifacts.
