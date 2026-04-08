# fix-text

`fix-text` is a small Python CLI for detecting and cleaning suspicious Unicode
characters in text files, including fullwidth spaces, non-breaking spaces, zero-width
characters, BOM markers, and optional control characters.

## What it fixes

- Replaces fullwidth and non-standard spacing characters with a normal ASCII space
- Removes zero-width characters and byte order marks
- Optionally removes unsupported control characters with `--include-controls`
- Scans individual files or entire directory trees

## Install for development

This project is managed with `uv`.

```bash
uv sync
```

Run the CLI without installing globally:

```bash
uv run fix-text --help
```

## Usage

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

## Example output

```text
notes.txt
  3:14 U+3000 IDEOGRAPHIC SPACE '\u3000' -> replace with space
  8:2 U+200B ZERO WIDTH SPACE '\u200b' -> delete

Found 2 issue(s). Re-run with --apply to rewrite files.
```

## PyPI release plan

1. Choose the final package metadata in `pyproject.toml`, especially author, homepage, and repository URLs.
2. Create a PyPI account and API token.
3. Build distributions with `uv build`.
4. Publish with `uv publish`.
5. Tag the release in git so the source and package versions stay aligned.

Recommended pre-release checks:

- `uv run fix-text --help`
- `uv run fix-text README.md`
- `uv build`

## License

MIT
