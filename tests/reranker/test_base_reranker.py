"""Tests for BaseReranker: scoring, sorting, time decay, unknown reranker."""

import numpy as np
import pytest

from zotero_arxiv_daily.reranker.base import BaseReranker, get_reranker_cls
from tests.canned_responses import make_sample_paper, make_sample_corpus


class StubReranker(BaseReranker):
    """Reranker with a controlled similarity matrix for deterministic tests."""

    def __init__(self, sim_matrix: np.ndarray):
        self.config = None
        self._sim = sim_matrix

    def get_similarity_score(self, s1, s2):
        return self._sim


def test_rerank_scores_and_sorts():
    corpus = make_sample_corpus(3)
    papers = [make_sample_paper(title=f"Paper {i}") for i in range(2)]

    # Paper 1 has higher similarity to all corpus papers
    sim = np.array([
        [0.1, 0.1, 0.1],  # paper 0 — low
        [0.9, 0.9, 0.9],  # paper 1 — high
    ])
    reranker = StubReranker(sim)
    ranked = reranker.rerank(papers, corpus)
    assert ranked[0].title == "Paper 1"
    assert ranked[1].title == "Paper 0"
    assert ranked[0].score > ranked[1].score


def test_rerank_time_decay_weighting():
    corpus = make_sample_corpus(3)
    papers = [make_sample_paper(title="P")]

    # Only similar to the oldest paper (index 2 after reverse-sort by date)
    sim = np.array([[0.0, 0.0, 1.0]])
    reranker = StubReranker(sim)
    ranked_old = reranker.rerank(papers, corpus)
    score_old = ranked_old[0].score

    # Only similar to the newest paper (index 0 after reverse-sort by date)
    papers2 = [make_sample_paper(title="P")]
    sim2 = np.array([[1.0, 0.0, 0.0]])
    reranker2 = StubReranker(sim2)
    ranked_new = reranker2.rerank(papers2, corpus)
    score_new = ranked_new[0].score

    # Newest corpus paper gets higher time-decay weight, so score should be higher
    assert score_new > score_old


def test_rerank_single_candidate_single_corpus():
    corpus = make_sample_corpus(1)
    papers = [make_sample_paper()]
    sim = np.array([[0.5]])
    reranker = StubReranker(sim)
    ranked = reranker.rerank(papers, corpus)
    assert len(ranked) == 1
    assert ranked[0].score is not None


def test_classic_seeds_have_bounded_weight_and_do_not_change_personal_decay():
    corpus = make_sample_corpus(2)
    seeds = make_sample_corpus(6)
    papers = [make_sample_paper(title="Personal"), make_sample_paper(title="Classic")]
    sim = np.array([
        [1.0, 1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 1.0, 1.0, 1.0, 1.0, 1.0, 1.0],
    ])
    ranked = StubReranker(sim).rerank(papers, corpus, seeds)
    assert ranked[0].title == "Personal"
    assert papers[0].score == pytest.approx(8.5)
    assert papers[1].score == pytest.approx(1.5)


def test_classic_seed_cold_start_and_no_seed_baseline():
    corpus = make_sample_corpus(1)
    seeds = make_sample_corpus(2)
    papers = [make_sample_paper()]
    assert StubReranker(np.array([[0.2]])).rerank(papers, corpus)[0].score == pytest.approx(2.0)
    assert StubReranker(np.array([[0.4, 0.8]])).rerank(papers, [], seeds)[0].score == pytest.approx(6.0)


def test_get_reranker_cls_unknown():
    with pytest.raises(ValueError, match="not found"):
        get_reranker_cls("nonexistent_reranker_xyz")
