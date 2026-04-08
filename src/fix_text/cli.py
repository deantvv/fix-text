from __future__ import annotations

import argparse
import sys
import unicodedata
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

from fix_text import __version__


REPLACEMENTS: dict[str, str] = {
    "\u00a0": " ",   # no-break space
    "\u1680": " ",   # ogham space mark
    "\u2000": " ",
    "\u2001": " ",
    "\u2002": " ",
    "\u2003": " ",
    "\u2004": " ",
    "\u2005": " ",
    "\u2006": " ",
    "\u2007": " ",
    "\u2008": " ",
    "\u2009": " ",
    "\u200a": " ",
    "\u202f": " ",
    "\u205f": " ",
    "\u3000": " ",   # fullwidth space
    "\ufeff": "",    # BOM / zero-width no-break space
    "\u200b": "",    # zero-width space
    "\u200c": "",    # zero-width non-joiner
    "\u200d": "",    # zero-width joiner
    "\u2060": "",    # word joiner
    "\u00ad": "",    # soft hyphen
}

CONTROL_EXCEPTIONS = {"\n", "\r", "\t"}
TEXT_SUFFIXES = {
    ".csv",
    ".html",
    ".ini",
    ".js",
    ".json",
    ".md",
    ".py",
    ".rst",
    ".sql",
    ".svg",
    ".toml",
    ".ts",
    ".tsx",
    ".txt",
    ".xml",
    ".yaml",
    ".yml",
}


@dataclass(slots=True)
class Issue:
    line: int
    column: int
    char: str
    action: str


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="fix-text",
        description=(
            "Detect and normalize suspicious Unicode characters in text files. "
            "Use --apply to rewrite files in place."
        ),
    )
    parser.add_argument("paths", nargs="+", help="File or directory paths to scan.")
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Rewrite files in place. Without this flag the tool only reports issues.",
    )
    parser.add_argument(
        "--include-controls",
        action="store_true",
        help="Remove unsupported control characters as well as mapped Unicode spaces.",
    )
    parser.add_argument(
        "--ext",
        action="append",
        default=[],
        metavar="SUFFIX",
        help="Extra file suffix to treat as text, for example --ext .log",
    )
    parser.add_argument(
        "--encoding",
        default="utf-8",
        help="Text encoding to use when reading and writing files. Default: utf-8",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    return parser


def iter_target_files(paths: Iterable[str], extra_suffixes: Iterable[str]) -> Iterable[Path]:
    suffixes = TEXT_SUFFIXES | {normalize_suffix(value) for value in extra_suffixes}
    seen: set[Path] = set()

    for raw_path in paths:
        path = Path(raw_path)
        if not path.exists():
            print(f"warning: path does not exist: {path}", file=sys.stderr)
            continue

        candidates = [path] if path.is_file() else sorted(p for p in path.rglob("*") if p.is_file())
        for candidate in candidates:
            resolved = candidate.resolve()
            if resolved in seen:
                continue
            seen.add(resolved)
            if candidate.suffix.lower() in suffixes:
                yield candidate


def normalize_suffix(value: str) -> str:
    return value if value.startswith(".") else f".{value}"


def find_issues(text: str, include_controls: bool) -> list[Issue]:
    issues: list[Issue] = []
    line = 1
    column = 1

    for char in text:
        action = replacement_for(char, include_controls)
        if action is not None:
            issues.append(Issue(line=line, column=column, char=char, action=describe_action(char, action)))

        if char == "\n":
            line += 1
            column = 1
        else:
            column += 1

    return issues


def replacement_for(char: str, include_controls: bool) -> str | None:
    replacement = REPLACEMENTS.get(char)
    if replacement is not None:
        return replacement

    if include_controls and unicodedata.category(char) == "Cc" and char not in CONTROL_EXCEPTIONS:
        return ""

    return None


def describe_action(char: str, replacement: str) -> str:
    if replacement == "":
        return "delete"
    if replacement == " ":
        return "replace with space"
    return f"replace with {replacement!r}"


def sanitize_text(text: str, include_controls: bool) -> str:
    cleaned: list[str] = []
    for char in text:
        replacement = replacement_for(char, include_controls)
        cleaned.append(char if replacement is None else replacement)
    return "".join(cleaned)


def format_char(char: str) -> str:
    codepoint = f"U+{ord(char):04X}"
    name = unicodedata.name(char, "UNKNOWN")
    printable = repr(char)
    return f"{codepoint} {name} {printable}"


def process_file(path: Path, encoding: str, apply: bool, include_controls: bool) -> tuple[int, bool]:
    try:
        original = path.read_text(encoding=encoding)
    except UnicodeDecodeError:
        print(f"skipped binary or non-{encoding} file: {path}", file=sys.stderr)
        return 0, False

    issues = find_issues(original, include_controls=include_controls)
    if not issues:
        return 0, False

    print(path)
    for issue in issues:
        print(f"  {issue.line}:{issue.column} {format_char(issue.char)} -> {issue.action}")

    changed = False
    if apply:
        sanitized = sanitize_text(original, include_controls=include_controls)
        if sanitized != original:
            path.write_text(sanitized, encoding=encoding)
            changed = True
            print("  rewritten")

    return len(issues), changed


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    total_issues = 0
    changed_files = 0

    for path in iter_target_files(args.paths, args.ext):
        issue_count, changed = process_file(
            path,
            encoding=args.encoding,
            apply=args.apply,
            include_controls=args.include_controls,
        )
        total_issues += issue_count
        changed_files += int(changed)

    if total_issues == 0:
        print("No suspicious characters found.")
        return 0

    if args.apply:
        print(f"\nFixed {total_issues} issue(s) across {changed_files} file(s).")
    else:
        print(f"\nFound {total_issues} issue(s). Re-run with --apply to rewrite files.")

    return 1 if not args.apply else 0


if __name__ == "__main__":
    raise SystemExit(main())
