"""Focused checks for daily classics order and sent-history boundaries."""

import csv
import json
from datetime import date

import pytest

from zotero_arxiv_daily.daily_classics import (
    advance_history, advance_state, load_catalog, load_state, save_state, select_classic,
)


def make_catalog(tmp_path):
    path = tmp_path / "catalog.csv"
    with path.open("w", encoding="utf-8", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=("area", "path", "title", "authors", "year", "venue", "doi", "stable_url"))
        writer.writeheader()
        writer.writerows([
            {"area": "circuits", "path": "02 circuits", "title": "Later", "authors": "B", "year": "1982", "venue": "IEEE", "doi": "10.1/later", "stable_url": "https://doi.org/10.1/later"},
            {"area": "AI", "path": "01 foundations", "title": "First", "authors": "A", "year": "1976", "venue": "ACM", "doi": "10.1/first", "stable_url": "https://doi.org/10.1/first"},
        ])
    return path


def test_selects_once_then_wraps_after_full_cycle(tmp_path):
    catalog = load_catalog(make_catalog(tmp_path))
    first = select_classic(catalog, [])
    assert first.title == "First"
    sent = advance_history(catalog, [], first)
    second = select_classic(catalog, sent)
    assert second.title == "Later"
    sent = advance_history(catalog, sent, second)
    assert select_classic(catalog, sent) == first
    assert advance_history(catalog, sent, first) == [first.key]


def test_rejects_stale_selection_and_duplicate_identifier(tmp_path):
    path = make_catalog(tmp_path)
    catalog = load_catalog(path)
    with pytest.raises(ValueError, match="does not match"):
        advance_history(catalog, [], catalog[1])
    with path.open("a", encoding="utf-8", newline="") as target:
        writer = csv.writer(target)
        writer.writerow(("AI", "01 foundations", "Duplicate", "A", 1977, "ACM", "10.1/first", "https://doi.org/10.1/first"))
    with pytest.raises(ValueError, match="Duplicate"):
        load_catalog(path)


def test_state_changes_only_when_saved(tmp_path):
    catalog = load_catalog(make_catalog(tmp_path))
    state_path = tmp_path / "state.json"
    original = {"version": 1, "sent": []}
    state_path.write_text(json.dumps(original), encoding="utf-8")
    selected = select_classic(catalog, [])
    updated = advance_state(catalog, load_state(state_path), selected, date(2026, 9, 28))
    assert json.loads(state_path.read_text(encoding="utf-8")) == original
    save_state(state_path, updated)
    assert load_state(state_path) == [{"key": selected.key, "date": "2026-09-28"}]
    with pytest.raises(FileNotFoundError):
        load_state(tmp_path / "missing.json")
