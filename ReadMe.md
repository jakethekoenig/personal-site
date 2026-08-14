# ja3k.com

This repository contains the source for [ja3k.com](https://ja3k.com), along with the custom static-site generator that builds it. The generator used to live in a separate repository named `exhibit`; its history is now merged here because it is bespoke infrastructure for this site, not a maintained general-purpose package.

The site is hosted on AWS. A push to `master` runs the deployment workflow, which builds the site and syncs the generated files to S3.

## Repository layout

- `content/` contains the writing and page-specific Python generators.
- `data/` contains page metadata and generated short-form post data.
- `template/` contains page templates and reusable components.
- `nongenerated/` contains CSS, JavaScript, and other files copied directly into the built site.
- `scripts/build/` contains the static-site generator and local development server.
- `scripts/deploy/` contains the S3 sync and CloudFront invalidation helpers.
- `scripts/mtg/` contains Magic: The Gathering utilities used by some posts.
- `scripts/one_off/` contains historical data migrations and legacy comment utilities.
- `comments/` and `backend/` contain the legacy commenting data and Lambda code.

The generator combines metadata, content, and templates, then copies the result plus `nongenerated/` into the directory named by `live` in `config.json` (currently the sibling `../live` directory).

## Build locally

The build requires Python 3 and Node.js/npm. From the repository root, run:

```sh
./scripts/build/build_live.sh
```

This installs the locked npm dependencies when they are missing or out of date, then rebuilds `../live`. To serve that directory and rebuild when source files change, install `fswatch` on macOS or `inotifywait` on Linux, then run:

```sh
./scripts/build/auto_build.sh
```

The watcher ignores changes under `node_modules/` and `.git/`. The local server listens on port 8070.

## Deploy

Deployment is normally handled by `.github/workflows/deploy.yml`. With AWS credentials configured locally, the same build and sync can be run with:

```sh
./scripts/build/build_live.sh
./scripts/deploy/update.sh
```
