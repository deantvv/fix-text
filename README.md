# fix-text

`fix-text` is a small Python CLI for detecting and cleaning suspicious Unicode
characters in text files, including fullwidth spaces, non-breaking spaces, zero-width
characters, BOM markers, and optional control characters.

## What it fixes

- Replaces fullwidth and non-standard spacing characters with a normal ASCII space
- Removes zero-width characters and byte order marks
- Optionally removes unsupported control characters with `--include-controls`
- Validates cleaned `.json` files before rewriting them
- Validates cleaned `.yaml` and `.yml` files before rewriting them
- Scans individual files or entire directory trees

## Install for development

This project is managed with `uv`.

```bash
uv sync
```

Install the test dependency group:

```bash
uv sync --group dev
```

Run the CLI without installing globally:

```bash
uv run fix-text --help
```

Run the test suite:

```bash
uv run --group dev pytest
```

## Usage

Run directly from PyPI with `uvx`:

```bash
uvx fix-text --help
```

Scan a file without installing the package into your current environment:

```bash
uvx fix-text path/to/file.txt
```

Scan a file or directory:

```bash
uv run fix-text path/to/file.txt path/to/dir
```

Rewrite files in place:

```bash
uv run fix-text --apply path/to/file.txt
```

Include control-character cleanup:

```bash
uv run fix-text --apply --include-controls logs/
```

Treat additional suffixes as text:

```bash
uv run fix-text --ext .log --ext .cfg sample/
```

For `.json` files, `fix-text` validates the cleaned output with `orjson` before writing.
For `.yaml` and `.yml`, it validates the cleaned output with `PyYAML`.
If the cleaned content would still be invalid JSON or YAML, the file is left unchanged.

## Example output

```text
notes.txt
  3:14 U+3000 IDEOGRAPHIC SPACE '\u3000' -> replace with space
  8:2 U+200B ZERO WIDTH SPACE '\u200b' -> delete

Found 2 issue(s). Re-run with --apply to rewrite files.
```

## PyPI release plan

1. Replace the placeholder GitHub URLs in `pyproject.toml`.
2. Create a PyPI account and API token.
3. Build distributions with `uv build`.
4. Publish with `uv publish`.
5. Tag the release in git so the source and package versions stay aligned.

Recommended pre-release checks:

- `uv run fix-text --help`
- `uv run fix-text README.md`
- `uv run --group dev pytest`
- `uv build --out-dir dist`

Build into the repo-local `dist/` directory:

```bash
./scripts/release.sh build
```

Publish the repo-local artifacts:

```bash
./scripts/release.sh publish
```

## License

MIT
