from collections import defaultdict
from typing import Dict, Iterable, Tuple, Optional

from load_data import MistakeItem
from lev_dist import lev_dist, Op

from enum import Enum


class ErrorModel:
    def __init__(self, coef: Tuple[float, float, float]):
        # We care only about replace
        # self.level0: Dict[(str, str), float]
        self.op_weight = {Op.insert: 0.01,
                          Op.replace: 1,
                          Op.delete: 0.01}
        self.level0 = {Op.insert: 0.01,
                       Op.replace: 0.98,
                       Op.delete: 0.01}
        self.level1 = {Op.insert: defaultdict(float),
                       Op.replace: defaultdict(float),
                       Op.delete: defaultdict(float)}  # P(s | s)
        self.level2 = {Op.insert: defaultdict(float),
                       Op.replace: defaultdict(float),
                       Op.delete: defaultdict(float)}  # P(s's | s's) where prev syms is same.
        self.coef = coef

    def normalize(self):
        for op in [Op.replace, Op.delete, Op.insert]:
            level1 = self.level1[op]
            total = sum(level1.values())
            for k, v in level1.items():
                level1[k] = v / total
            level2 = self.level2[op]
            totals = defaultdict(float)
            for k, v in level2.items():
                totals[k[0]] += v
            for k, v in level2.items():
                level2[k] = v / totals[k[0]]

    def fit(self, mistakes: Iterable[MistakeItem]):
        for m in mistakes:
            d, lev1, lev2 = lev_dist(m.expected, m.actual)
            if d < 3:
                for a, b in lev1[Op.replace]:
                    self.level1[Op.replace][(a, b)] += 1
                for a in lev1[Op.insert]:
                    self.level1[Op.insert][a] += 1
                for a in lev1[Op.delete]:
                    self.level1[Op.delete][a] += 1

                for prev, a, b in lev2[Op.replace]:
                    self.level2[Op.replace][(prev, a, b)] += 1
                for prev, a in lev2[Op.insert]:
                    self.level2[Op.insert][(prev, a)] += 1
                for prev, a in lev2[Op.delete]:
                    self.level2[Op.delete][(prev, a)] += 1
        self.normalize()

    def p_replace(self, cur: str, next: str, sug: str) -> float:
        return self.op_weight[Op.replace] * (self.coef[0] * self.level0[Op.replace] +
                                             self.coef[1] * self.level1[Op.replace][sug, next] +
                                             self.coef[2] * self.level2[Op.replace][cur, sug, next])

    def p_insert(self, cur: str, next: str) -> float:
        return self.op_weight[Op.insert] * (self.coef[0] * self.level0[Op.insert] +
                                            self.coef[1] * self.level1[Op.insert][next] +
                                            self.coef[2] * self.level2[Op.insert][cur, next])

    def p_delete(self, cur: str, next: str) -> float:
        return self.op_weight[Op.delete] * (self.coef[0] * self.level0[Op.delete] +
                                            self.coef[1] * self.level1[Op.delete][next] +
                                            self.coef[2] * self.level2[Op.delete][cur, next])
