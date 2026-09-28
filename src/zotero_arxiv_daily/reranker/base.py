from abc import ABC, abstractmethod
from omegaconf import DictConfig
from ..protocol import Paper, CorpusPaper
import numpy as np
from typing import Type
class BaseReranker(ABC):
    def __init__(self, config:DictConfig):
        self.config = config

    def rerank(self, candidates:list[Paper], corpus:list[CorpusPaper],
               classic_seeds:list[CorpusPaper] | None = None, classic_weight:float = 0.15) -> list[Paper]:
        if not 0 <= classic_weight <= 0.15:
            raise ValueError("classic_weight must be between 0 and 0.15")
        corpus = sorted(corpus,key=lambda x: x.added_date,reverse=True)
        classic_seeds = [c for c in (classic_seeds or []) if c.abstract and c.abstract.strip()]
        if not corpus and not classic_seeds:
            raise ValueError("Cannot rerank without a personal corpus or classic seeds")

        abstracts = [c.abstract for c in corpus + classic_seeds]
        sim = self.get_similarity_score([c.abstract for c in candidates], abstracts)
        assert sim.shape == (len(candidates), len(abstracts))
        if corpus:
            time_decay_weight = 1 / (1 + np.log10(np.arange(len(corpus)) + 1))
            time_decay_weight = time_decay_weight / time_decay_weight.sum()
            personal_scores = (sim[:, :len(corpus)] * time_decay_weight).sum(axis=1)
        if classic_seeds:
            classic_scores = sim[:, len(corpus):].mean(axis=1)
        if corpus and classic_seeds:
            scores = ((1 - classic_weight) * personal_scores + classic_weight * classic_scores) * 10
        else:
            scores = (personal_scores if corpus else classic_scores) * 10
        for s,c in zip(scores,candidates):
            c.score = s
        candidates = sorted(candidates,key=lambda x: x.score,reverse=True)
        return candidates
    
    @abstractmethod
    def get_similarity_score(self, s1:list[str], s2:list[str]) -> np.ndarray:
        raise NotImplementedError

registered_rerankers = {}

def register_reranker(name:str):
    def decorator(cls):
        registered_rerankers[name] = cls
        return cls
    return decorator

def get_reranker_cls(name:str) -> Type[BaseReranker]:
    if name not in registered_rerankers:
        raise ValueError(f"Reranker {name} not found")
    return registered_rerankers[name]
