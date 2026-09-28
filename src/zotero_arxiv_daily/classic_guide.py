"""Load the selected classic's reviewed guide for the email preview."""

import csv
import html
import re
from pathlib import Path

from .daily_classics import ClassicPaper


SECTIONS = ("为什么读", "核心思想", "对后续学习的作用", "阅读前置与思考题")


def load_classic_guide(paper: ClassicPaper, manifest_path: Path) -> str:
    """Return safe HTML for a draft guide matched by DOI or stable URL."""
    identifiers = {value.strip().casefold() for value in (paper.doi, paper.url) if value.strip()}
    with manifest_path.open(encoding="utf-8-sig", newline="") as source:
        reader = csv.DictReader(source)
        if not reader.fieldnames or not {"identifier", "status", "guide_path"} <= set(reader.fieldnames):
            raise ValueError(f"Invalid classic guide manifest: {manifest_path}")
        matches = [row for row in reader if (row.get("identifier") or "").strip().casefold() in identifiers]
    if len(matches) != 1:
        raise ValueError(f"Expected one classic guide for {paper.key}, found {len(matches)}")
    row = matches[0]
    if row["status"].strip().casefold() != "draft":
        raise ValueError(f"Classic guide is not draft: {paper.key}")

    root = manifest_path.parent.resolve()
    relative_path = Path((row["guide_path"] or "").strip())
    guide_path = (root / relative_path).resolve()
    if not relative_path.name or not guide_path.is_relative_to(root) or guide_path == root:
        raise ValueError(f"Invalid classic guide path: {row['guide_path']}")
    guide = guide_path.read_text(encoding="utf-8")

    headings = list(re.finditer(r"^##\s+(.+?)\s*$", guide, flags=re.MULTILINE))
    if [match.group(1) for match in headings] != list(SECTIONS):
        raise ValueError(f"Classic guide requires four ordered sections: {guide_path}")
    output = []
    for index, heading in enumerate(headings):
        end = headings[index + 1].start() if index + 1 < len(headings) else len(guide)
        body = guide[heading.end():end].strip()
        paragraphs = [part.strip() for part in re.split(r"\n\s*\n", body) if part.strip()]
        if not paragraphs:
            raise ValueError(f"Empty classic guide section: {heading.group(1)}")
        output.append(f"<h3>{html.escape(heading.group(1))}</h3>")
        for paragraph in paragraphs:
            escaped = html.escape(" ".join(paragraph.splitlines()))
            emphasized = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", escaped)
            output.append(f"<p>{emphasized}</p>")
    return "\n".join(output)
