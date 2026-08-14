# ja3k.com

The source for [ja3k.com](https://ja3k.com).

## Repository layout

- `content/` writing and page-specific Python generators.
- `data/` page metadata and generated short-form post data.
- `template/` page templates and reusable components.
- `nongenerated/` CSS, JavaScript, and other files copied directly into the built site.
- `scripts/build/` static-site generator and local development server.
- `scripts/deploy/` S3 sync and CloudFront invalidation helpers.
- `scripts/mtg/` Magic: The Gathering utilities used by some posts.

The generator combines metadata, content, and templates, then copies the result plus `nongenerated/` into `../live`.

## Build locally

The build requires Python 3 and Node.js/npm. From the repository root, run:

```sh
./scripts/build/build_live.sh
```

This installs the locked npm dependencies when they are missing or out of date, then rebuilds `../live`. To serve that directory and rebuild when source files change, install `fswatch` on macOS or `inotifywait` on Linux, then run:

```sh
./scripts/build/auto_build.sh
```

## Deploy

Deployment is handled by `.github/workflows/deploy.yml`. With AWS credentials configured locally, the same build and sync can be run with:

```sh
./scripts/build/build_live.sh
./scripts/deploy/update.sh
```
