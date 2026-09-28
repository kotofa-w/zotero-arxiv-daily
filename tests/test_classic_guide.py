"""A guide must be uniquely matched, complete, and safe to embed."""

import csv

import pytest

from zotero_arxiv_daily.classic_guide import load_classic_guide
from zotero_arxiv_daily.daily_classics import ClassicPaper


def test_loads_four_sections_and_rejects_ambiguous_or_unsafe_guide(tmp_path):
    paper = ClassicPaper("AI", "01", "Example", "A", 1980, "Journal", "10.1/ABC", "https://example.org/paper")
    manifest = tmp_path / "manifest.csv"
    guide = tmp_path / "guide.md"
    guide.write_text(
        "# Guide\n\nSource metadata\n\n"
        "## 为什么读\n\nFirst <script>alert(1)</script>.\n\nSecond paragraph.\n\n"
        "## 核心思想\n\n**Core <safe>**.\n\n"
        "## 对后续学习的作用\n\nLater.\n\n"
        "## 阅读前置与思考题\n\nQuestion?\n", encoding="utf-8",
    )
    with manifest.open("w", encoding="utf-8", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=("identifier", "status", "guide_path"))
        writer.writeheader()
        writer.writerow({"identifier": "10.1/abc", "status": "draft", "guide_path": guide.name})
    output = load_classic_guide(paper, manifest)
    assert output.count("<h3>") == 4
    assert "<p>First &lt;script&gt;alert(1)&lt;/script&gt;.</p>" in output
    assert "<p>Second paragraph.</p>" in output
    assert "<p><strong>Core &lt;safe&gt;</strong>.</p>" in output
    assert "Source metadata" not in output

    with manifest.open("a", encoding="utf-8", newline="") as target:
        csv.writer(target).writerow(("https://example.org/paper", "draft", guide.name))
    with pytest.raises(ValueError, match="Expected one classic guide"):
        load_classic_guide(paper, manifest)

    with manifest.open("w", encoding="utf-8", newline="") as target:
        writer = csv.DictWriter(target, fieldnames=("identifier", "status", "guide_path"))
        writer.writeheader()
        writer.writerow({"identifier": paper.doi, "status": "draft", "guide_path": "../outside.md"})
    with pytest.raises(ValueError, match="Invalid classic guide path"):
        load_classic_guide(paper, manifest)
