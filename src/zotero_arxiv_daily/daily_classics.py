"""Pure catalog selection for the optional daily classics section."""

import csv
import json
import os
import tempfile
from dataclasses import dataclass
from datetime import date
from pathlib import Path


@dataclass(frozen=True)
class ClassicPaper:
    area: str
    path: str
    title: str
    authors: str
    year: int
    venue: str
    doi: str
    url: str

    @property
    def key(self) -> str:
        return (self.doi or self.url).casefold()


def load_catalog(path: Path) -> list[ClassicPaper]:
    """Read reviewed bibliographic records without contacting Zotero or publishers."""
    papers = []
    keys = set()
    with path.open(encoding="utf-8-sig", newline="") as source:
        for row in csv.DictReader(source):
            if not all(row.get(field) for field in ("area", "path", "title", "authors", "year", "venue", "stable_url")):
                raise ValueError("Incomplete daily classics catalog record")
            if not row["stable_url"].startswith("https://"):
                raise ValueError("Daily classics links must use HTTPS")
            paper = ClassicPaper(
                area=row["area"], path=row["path"], title=row["title"],
                authors=row["authors"], year=int(row["year"]), venue=row["venue"],
                doi=row.get("doi", ""), url=row["stable_url"],
            )
            if paper.key in keys:
                raise ValueError(f"Duplicate daily classics identifier: {paper.key}")
            keys.add(paper.key)
            papers.append(paper)
    return sorted(papers, key=lambda paper: (paper.path, paper.year, paper.title))


def select_classic(catalog: list[ClassicPaper], sent_keys: list[str]) -> ClassicPaper | None:
    """Choose one unsent paper in learning-path order, then start a new cycle."""
    if not catalog:
        return None
    sent = set(sent_keys)
    return next((paper for paper in catalog if paper.key not in sent), catalog[0])


def advance_history(catalog: list[ClassicPaper], sent_keys: list[str], selected: ClassicPaper) -> list[str]:
    """Calculate history after an accepted email; callers persist it separately."""
    expected = select_classic(catalog, sent_keys)
    if expected is None or selected.key != expected.key:
        raise ValueError("Selected classic does not match current catalog and history")
    if selected.key in sent_keys:
        return [selected.key]
    return [*sent_keys, selected.key]


def load_state(path: Path) -> list[dict[str, str]]:
    """Read committed send history; a missing state file is a configuration error."""
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("version") != 1 or not isinstance(data.get("sent"), list):
        raise ValueError("Unsupported daily classics state")
    sent = data["sent"]
    if any(not isinstance(entry, dict) or not isinstance(entry.get("key"), str)
           or not isinstance(entry.get("date"), str) for entry in sent):
        raise ValueError("Invalid daily classics history entry")
    keys = [entry["key"] for entry in sent]
    if len(keys) != len(set(keys)):
        raise ValueError("Duplicate daily classics history identifier")
    return sent


def advance_state(catalog: list[ClassicPaper], sent: list[dict[str, str]],
                  selected: ClassicPaper, send_date: date) -> list[dict[str, str]]:
    """Build the state to commit only after SMTP accepted the email."""
    keys = [entry["key"] for entry in sent]
    next_keys = advance_history(catalog, keys, selected)
    new_entry = {"key": selected.key, "date": send_date.isoformat()}
    return [new_entry] if len(next_keys) == 1 else [*sent, new_entry]


def save_state(path: Path, sent: list[dict[str, str]]) -> None:
    """Atomically replace local state; the workflow must persist its state branch."""
    payload = json.dumps({"version": 1, "sent": sent}, ensure_ascii=False, indent=2) + "\n"
    temporary = None
    try:
        with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent,
                                         prefix=path.name + ".", delete=False) as target:
            temporary = Path(target.name)
            target.write(payload)
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
