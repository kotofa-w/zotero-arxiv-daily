"""Generate one daily reading preview without Zotero or SMTP side effects."""

from pathlib import Path
from xml.etree import ElementTree

from omegaconf import OmegaConf
from openai import OpenAI

from .construct_email import render_email
from .protocol import Paper


def main() -> None:
    root = Path(__file__).resolve().parents[2]
    config = OmegaConf.merge(
        OmegaConf.load(root / "config/base.yaml"),
        OmegaConf.load(root / "config/custom.yaml"),
    )
    feed = ElementTree.parse(root / "tests/retriever/arxiv_rss_example.xml")
    atom = "{http://www.w3.org/2005/Atom}"
    entry = feed.getroot().find(f"{atom}entry")
    if entry is None:
        raise ValueError("RSS preview fixture has no entry")
    title = entry.findtext(f"{atom}title") or ""
    summary = entry.findtext(f"{atom}summary") or ""
    if "Abstract:" not in summary:
        raise ValueError("RSS preview fixture has no abstract")
    abstract = summary.split("Abstract:", 1)[1].strip()
    url = next(
        (link.get("href", "") for link in entry.findall(f"{atom}link")
         if link.get("rel") == "alternate"),
        "",
    )
    if not title or not abstract or not url:
        raise ValueError("Incomplete RSS preview fixture")
    paper = Paper(
        source="arxiv", title=title, authors=[], abstract=abstract,
        url=url, pdf_url=url.replace("/abs/", "/pdf/"), score=7.0,
    )
    client = OpenAI(api_key=config.llm.api.key, base_url=config.llm.api.base_url)
    paper.generate_reading(client, config.llm)
    if not paper.abstract_zh or not paper.guide:
        raise RuntimeError("Daily reading generation did not return translation and guide")
    html = render_email([paper])
    if "摘要译文" not in html or "导读（依据摘要）" not in html or "学科经典" in html:
        raise RuntimeError("Daily reading preview HTML is incomplete")
    (root / "daily-reading-preview.html").write_text(html, encoding="utf-8")
    print(f"Daily reading preview ready: {title}; translation={len(paper.abstract_zh)} chars; guide={len(paper.guide)} chars")


if __name__ == "__main__":
    main()
