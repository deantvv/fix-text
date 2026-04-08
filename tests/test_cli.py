from __future__ import annotations

from pathlib import Path

from fix_text.cli import (
    main,
    process_file,
    sanitize_text,
    validate_json_text,
    validate_yaml_text,
)


def test_sanitize_text_replaces_and_deletes_mapped_characters() -> None:
    assert sanitize_text("A\u3000B\u200bC", include_controls=False) == "A BC"


def test_validate_json_text_accepts_valid_json() -> None:
    assert validate_json_text('{"name":"value"}')


def test_validate_json_text_rejects_invalid_json() -> None:
    assert not validate_json_text('{"name":"value",}')


def test_validate_yaml_text_accepts_valid_yaml() -> None:
    assert validate_yaml_text("name: value\nitems:\n  - one\n")


def test_validate_yaml_text_rejects_invalid_yaml() -> None:
    assert not validate_yaml_text("items: [one\n")


def test_process_file_rewrites_valid_json(tmp_path: Path, capsys) -> None:
    path = tmp_path / "sample.json"
    path.write_text('{"name":"A\u3000B","note":"x\u200by"}\n', encoding="utf-8")

    issues, changed = process_file(path, encoding="utf-8", apply=True, include_controls=False)

    assert issues == 2
    assert changed is True
    assert path.read_text(encoding="utf-8") == '{"name":"A B","note":"xy"}\n'
    captured = capsys.readouterr()
    assert "rewritten" in captured.out


def test_process_file_skips_invalid_json_rewrite(tmp_path: Path, capsys) -> None:
    path = tmp_path / "invalid.json"
    original = '{"name":"A\u3000B",}\n'
    path.write_text(original, encoding="utf-8")

    issues, changed = process_file(path, encoding="utf-8", apply=True, include_controls=False)

    assert issues == 1
    assert changed is False
    assert path.read_text(encoding="utf-8") == original
    captured = capsys.readouterr()
    assert "skipped rewrite: cleaned content is not valid JSON" in captured.err


def test_process_file_rewrites_valid_yaml(tmp_path: Path, capsys) -> None:
    path = tmp_path / "sample.yaml"
    path.write_text("title: A\u3000B\nnote: x\u200by\n", encoding="utf-8")

    issues, changed = process_file(path, encoding="utf-8", apply=True, include_controls=False)

    assert issues == 2
    assert changed is True
    assert path.read_text(encoding="utf-8") == "title: A B\nnote: xy\n"
    captured = capsys.readouterr()
    assert "rewritten" in captured.out


def test_process_file_skips_invalid_yml_rewrite(tmp_path: Path, capsys) -> None:
    path = tmp_path / "invalid.yml"
    original = "items: [one\u200b\n"
    path.write_text(original, encoding="utf-8")

    issues, changed = process_file(path, encoding="utf-8", apply=True, include_controls=False)

    assert issues == 1
    assert changed is False
    assert path.read_text(encoding="utf-8") == original
    captured = capsys.readouterr()
    assert "skipped rewrite: cleaned content is not valid YAML" in captured.err


def test_main_reports_findings_without_apply(tmp_path: Path, capsys) -> None:
    path = tmp_path / "notes.txt"
    path.write_text("hello\u3000world\n", encoding="utf-8")

    exit_code = main([str(path)])

    assert exit_code == 1
    captured = capsys.readouterr()
    assert "U+3000 IDEOGRAPHIC SPACE" in captured.out
    assert "Re-run with --apply" in captured.out
