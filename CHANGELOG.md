# Changelog

## Unreleased

- Prepare NuGet metadata and displayed README for manual NuGet.org release.
- Validate NuGet archive bytes, isolated consumer installation and release checksum in Windows CI.
- Record CC BY 3.0 US licensing basis while preserving historical notices.

- Move original artwork to `src/`, historical files to `docs/upstream/`, and NuGet templates to `packaging/nuget/`.
- Separate installation guidance from contributor build and release instructions.
- Keep generated asset paths and CSS classes stable.

## 1.0.0

- Package all four original PNG variants without modifying source files.
- Add padded CSS sprites, searchable offline preview and SHA-256 manifest.
- Add deterministic ZIP builds, npm packaging, NuGet template and CI verification.
