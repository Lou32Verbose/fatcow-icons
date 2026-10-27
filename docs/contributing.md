# Contributing to FatCow

Run all commands from the repository root. Source artwork belongs in `src/`; generate the installable assets in `dist/` with the build script.

## Repository layout

```text
fatcow/
├── README.md                  Installation, usage and attribution
├── LICENSE.md
├── NOTICE.md
├── CHANGELOG.md
├── package.json               npm package metadata and commands
├── requirements.txt           Pinned build dependency
├── src/                       Original PNGs, preserved byte-for-byte
│   ├── 16x16/
│   ├── 16x16-grey/
│   ├── 32x32/
│   └── 32x32-grey/
├── dist/                      Generated, committed installation assets
│   ├── <variant>/png/
│   ├── <variant>/sprite/      fatcow.png, fatcow.css, fatcow.min.css
│   ├── icons.json             Hashes, source paths, dimensions, positions
│   └── index.html             Searchable offline catalogue
├── docs/
│   ├── contributing.md
│   └── upstream/              Original release notes and filename list
├── scripts/
│   ├── build.py
│   └── verify.py
├── packaging/
│   └── nuget/fatcow.nuspec
├── .github/workflows/verify.yml
└── artifacts/                 Ignored local packages and install tests
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

Build and verify first, then use the NuGet CLI from the repository root:

```sh
nuget pack packaging/nuget/fatcow.nuspec -OutputDirectory artifacts
```

The template resolves its inputs relative to `packaging/nuget/`. It includes legacy `content/fatcow` and modern `contentFiles/any/any/fatcow` assets, plus documentation and attribution. NuGet packaging has no automatic build step. For ASP.NET applications, copy the selected files into `wwwroot`; output copying alone does not make them web-accessible.

## Continuous integration

CI builds and verifies on Windows and Linux, checks the committed distribution for drift, checks reproducible ZIP output, creates an npm tarball, and installs that tarball in an isolated directory. Packages are retained as workflow artifacts.

## Release checklist

1. Confirm standalone redistribution rights against [the supplied license notices](../LICENSE.md). Preserve [upstream files](upstream/) and [attribution](../NOTICE.md).
2. Update `package.json`, `packaging/nuget/fatcow.nuspec`, versioned package examples and the CI archive/install paths together. Record changes in `CHANGELOG.md`.
3. Install the pinned dependency, rebuild and verify, and inspect the catalogue.
4. Commit source, documentation and regenerated `dist/`. Require CI to pass and review package contents.
5. For a public registry release, check package-name availability, set publisher/repository metadata, and remove `private: true` from `package.json` only after the redistribution terms are clarified.

The repository remains configured for local packages rather than automatic publication.
