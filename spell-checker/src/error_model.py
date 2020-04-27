from collections import defaultdict
from typing import Dict, Iterable, Tuple, Optional

from load_data import MistakeItem


class ErrorModel:
    def __init__(self, coef: Tuple[float, float, float]):
        # We care only about replace
        # self.level0: Dict[(str, str), float]
        self.level1: Dict[(str, str), float] = defaultdict(float)  # P(s | s)
        self.level2: Dict[(str, str), float] = defaultdict(float)  # P(s's | s's) where prev syms is same.
        self.coef = coef

    def fit(self, mistakes: Iterable[MistakeItem]):
        for m in mistakes:
            if len(m.actual) == len(m.expected):
                start = 0
                end = min(len(m.actual), len(m.expected))
                for i in range(start, end):
                    self.level1[(m.actual[i], m.expected[i])] += 1
                    if i != 0 and m.actual[i - 1] == m.expected[i - 1]:
                        self.level2[(m.actual[i - 1:i + 1], m.expected[i - 1:i + 1])] += 1
                    if i == 0:
                        self.level2[(m.actual[i], m.expected[i])] += 1

    def p_step(self, cur: Optional[str], next: str, sug: str) -> float:
        return self.coef[1] * self.level1[next, sug] + \
               self.coef[2] * self.level2[cur + next, cur + sug]
