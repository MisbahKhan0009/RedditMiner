# CI / CD → PyPI (GitHub Actions)

This document explains how the repository's GitHub Actions workflow publishes packages to PyPI and how to configure it safely.

## Purpose
- Automatically build and publish the package to PyPI when changes are pushed to `main` (workflow: `.github/workflows/publish.yml`).
- By default the workflow uses `twine upload --skip-existing` to avoid failures if identical files already exist.

## Recommended workflow (safe default)
We recommend publishing only from tagged releases to avoid accidental publishes:
1. Create a release tag locally and push it:
   ```bash
   git tag v1.0.2
   git push origin v1.0.2
   ```
2. Configure the workflow to trigger on `push: tags:` (see note below).

## Configure PyPI token
1. Create an API token on PyPI: https://pypi.org/manage/account/token/
   - Name: e.g. `github-actions`.
   - Scope: choose project-specific token or an all-project token per your workflow.
2. In GitHub, go to your repository → Settings → Secrets → Actions → New repository secret.
   - Name: `pypi_PYPI_API_TOKEN` (recommended; GitHub secret names cannot contain dashes)
   - Value: the token you created on PyPI (token values themselves commonly start with `pypi-`)

## Workflow triggers
- Current workflow triggers on pushes to `main`. To publish only for tags, edit `.github/workflows/publish.yml` and replace the `on:` block with:

```yaml
on:
  push:
    tags:
      - 'v*'
```

This will publish only when tags like `v1.0.2` are pushed.

## Local verification steps
Before pushing a release, test locally:

```bash
# clean previous builds
rm -rf dist build *.egg-info
# build
python -m build
# upload to Test PyPI (optional, useful for testing)
python -m pip install --upgrade twine
python -m twine upload --repository testpypi dist/*
# or to upload to real PyPI (use local token or environment variable)
python -m twine upload dist/*
```

## Notes & troubleshooting
- If PyPI returns a "File already exists" error, increment the package version in `setup.py` and `pyproject.toml`, then rebuild.
- The workflow uses `--skip-existing` to avoid failing when an identical file exists on PyPI. If you prefer strict behavior, remove `--skip-existing`.
- Protect the `main` branch and require reviews for merges to avoid accidental publishes.

## Security
- Keep your `PYPI_API_TOKEN` secret; treat it like a password.
- Prefer project-scoped tokens over global tokens.
- Rotate tokens periodically and remove unused tokens from PyPI.

## Quick checklist before releasing
- Bump version in `setup.py` and `pyproject.toml`.
- Commit and push the change.
- Tag the commit (if using tag-based publishing) and push the tag.
- Verify CI run in GitHub Actions and check PyPI for the new release.

---

If you want, I can update `.github/workflows/publish.yml` to trigger only on tags and add a small GitHub Actions check to verify the version matches `pyproject.toml` before publishing.