from loguru import logger
from pyzotero import zotero
from omegaconf import DictConfig, ListConfig
from .utils import glob_match
from .retriever import get_retriever_cls
from .protocol import CorpusPaper
import random
import os
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
from .reranker import get_reranker_cls
from .construct_email import render_email
from .daily_classics import advance_state, load_catalog, load_state, save_state, select_classic
from .utils import send_email
from openai import OpenAI
from tqdm import tqdm


def normalize_path_patterns(patterns: list[str] | ListConfig | None, config_key: str) -> list[str] | None:
    if patterns is None:
        return None

    if not isinstance(patterns, (list, ListConfig)):
        raise TypeError(
            f"config.zotero.{config_key} must be a list of glob patterns or null, "
            'for example ["2026/survey/**"]. Single strings are not supported.'
        )

    if any(not isinstance(pattern, str) for pattern in patterns):
        raise TypeError(f"config.zotero.{config_key} must contain only glob pattern strings.")

    return list(patterns)


class Executor:
    def __init__(self, config:DictConfig):
        self.config = config
        self.include_path_patterns = normalize_path_patterns(config.zotero.include_path, "include_path")
        self.ignore_path_patterns = normalize_path_patterns(config.zotero.ignore_path, "ignore_path")
        self.retrievers = {
            source: get_retriever_cls(source)(config) for source in config.executor.source
        }
        self.reranker = get_reranker_cls(config.executor.reranker)(config)
        self.openai_client = OpenAI(api_key=config.llm.api.key, base_url=config.llm.api.base_url)
    def fetch_zotero_corpus(self) -> list[CorpusPaper]:
        logger.info("Fetching zotero corpus")
        zot = zotero.Zotero(self.config.zotero.user_id, 'user', self.config.zotero.api_key)
        collections = zot.everything(zot.collections())
        collections = {c['key']:c for c in collections}
        corpus = zot.everything(zot.items(itemType='conferencePaper || journalArticle || preprint'))
        corpus = [c for c in corpus if c['data']['abstractNote'] != '']
        def get_collection_path(col_key:str) -> str:
            if p := collections[col_key]['data']['parentCollection']:
                return get_collection_path(p) + '/' + collections[col_key]['data']['name']
            else:
                return collections[col_key]['data']['name']
        for c in corpus:
            paths = [get_collection_path(col) for col in c['data']['collections']]
            c['paths'] = paths
        logger.info(f"Fetched {len(corpus)} zotero papers")
        return [CorpusPaper(
            title=c['data']['title'],
            abstract=c['data']['abstractNote'],
            added_date=datetime.strptime(c['data']['dateAdded'], '%Y-%m-%dT%H:%M:%SZ'),
            paths=c['paths']
        ) for c in corpus]
    
    def filter_corpus(self, corpus:list[CorpusPaper]) -> list[CorpusPaper]:
        if self.include_path_patterns:
            logger.info(f"Selecting zotero papers matching include_path: {self.include_path_patterns}")
            corpus = [
                c for c in corpus
                if any(
                    glob_match(path, pattern)
                    for path in c.paths
                    for pattern in self.include_path_patterns
                )
            ]
        if self.ignore_path_patterns:
            logger.info(f"Excluding zotero papers matching ignore_path: {self.ignore_path_patterns}")
            corpus = [
                c for c in corpus
                if not any(
                    glob_match(path, pattern)
                    for path in c.paths
                    for pattern in self.ignore_path_patterns
                )
            ]
        if self.include_path_patterns or self.ignore_path_patterns:
            samples = random.sample(corpus, min(5, len(corpus)))
            samples = '\n'.join([c.title + ' - ' + '\n'.join(c.paths) for c in samples])
            logger.info(f"Selected {len(corpus)} zotero papers:\n{samples}\n...")
        return corpus

    def split_classic_corpus(self, corpus:list[CorpusPaper]) -> tuple[list[CorpusPaper], list[CorpusPaper]]:
        classics = self.config.get("classics")
        if not classics or not classics.get("collection_path"):
            return corpus, []
        collection_path = str(classics.collection_path).strip("/")
        seed_path = str(classics.get("interest_seed_path") or "").strip("/")
        if seed_path and not seed_path.startswith(collection_path + "/"):
            raise ValueError("classics.interest_seed_path must be inside classics.collection_path")
        personal = []
        seeds = []
        for paper in corpus:
            if seed_path and seed_path in paper.paths and paper.abstract and paper.abstract.strip():
                seeds.append(paper)
            if not any(path == collection_path or path.startswith(collection_path + "/") for path in paper.paths):
                personal.append(paper)
        return personal, seeds

    
    def run(self):
        classic = None
        classic_context = None
        classic_config = self.config.get("classics")
        enabled = classic_config and str(classic_config.get("enabled", False)).lower() == "true"
        if enabled:
            if not classic_config.get("state_path"):
                raise ValueError("classics.state_path is required when classics are enabled")
            root = Path(__file__).resolve().parents[2]
            catalog_path = root / classic_config.catalog_path
            state_path = root / classic_config.state_path
            catalog = load_catalog(catalog_path)
            history = load_state(state_path)
            classic = select_classic(catalog, [entry["key"] for entry in history])
            classic_context = (catalog, history, state_path)

        corpus, classic_seeds = self.split_classic_corpus(self.fetch_zotero_corpus())
        corpus = self.filter_corpus(corpus)
        if not corpus and not classic_seeds:
            logger.error("No Zotero papers found. Check the Zotero ID and collection filters.")
            if classic is None:
                return
        all_papers = []
        for source, retriever in (self.retrievers.items() if corpus or classic_seeds else []):
            logger.info(f"Retrieving {source} papers...")
            papers = retriever.retrieve_papers()
            if len(papers) == 0:
                logger.info(f"No {source} papers found")
                continue
            logger.info(f"Retrieved {len(papers)} {source} papers")
            all_papers.extend(papers)
        logger.info(f"Total {len(all_papers)} papers retrieved from all sources")
        reranked_papers = []
        if len(all_papers) > 0:
            logger.info("Reranking papers...")
            classic_weight = float(classic_config.get("interest_seed_weight", 0.15)) if classic_config else 0.15
            reranked_papers = self.reranker.rerank(all_papers, corpus, classic_seeds, classic_weight)
            reranked_papers = reranked_papers[:self.config.executor.max_paper_num]
            logger.info("Generating TLDR and affiliations...")
            for p in tqdm(reranked_papers):
                p.generate_tldr(self.openai_client, self.config.llm)
                p.generate_affiliations(self.openai_client, self.config.llm)
        elif not self.config.executor.send_empty and classic is None:
            logger.info("No new papers found. No email will be sent.")
            return
        logger.info("Sending email...")
        email_content = render_email(reranked_papers, classic)
        if classic is not None:
            logger.info(f"Selected classic: {classic.doi or classic.url}")
        send_email(self.config, email_content, has_classic=classic is not None)
        logger.info("Email accepted by SMTP")
        if classic is not None and os.environ.get("GITHUB_EVENT_NAME") == "schedule":
            catalog, history, state_path = classic_context
            try:
                send_date = datetime.now(ZoneInfo("Asia/Hong_Kong")).date()
                updated = advance_state(catalog, history, classic, send_date)
                save_state(state_path, updated)
            except Exception:
                logger.error(f"SMTP accepted but classics state was not saved. DOI: {classic.doi or classic.url}")
                raise
