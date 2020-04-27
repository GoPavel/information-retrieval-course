import itertools
from functools import lru_cache
from typing import Optional, Iterable, Dict, List, Tuple

import attr

from error_model import ErrorModel
from lev_dist import Op
from load_data import WordItem

import heapq


@attr.s(auto_attribs=True, slots=True, repr=False)
class Node:
    go: Optional[Dict[str, 'Node']] = attr.ib(default=attr.Factory(dict))
    freq: Optional[float] = None
    is_end: bool = False


class Trie:
    def __init__(self, em: ErrorModel):
        self.root = Node(go={'$': Node(is_end=True)})
        self.em = em
        self.mfw = dict()

    def _fit_word(self, word: str, freq: float):
        cur_node = self.root
        for ch in word:
            if ch in cur_node.go:
                cur_node = cur_node.go[ch]
            else:
                if ch == '$':
                    cur_node.go[ch] = Node(freq=freq, is_end=True)
                else:
                    cur_node.go[ch] = Node()
                cur_node = cur_node.go[ch]

    def find_freq(self, word, node=None) -> Optional[float]:
        cur_node = self.root if node is None else node
        for ch in word:
            if ch not in cur_node.go:
                return None
            cur_node = cur_node.go[ch]
        if cur_node.is_end:
            return cur_node.freq
        else:
            return None

    def fit(self, words: Iterable[WordItem], precalc: Optional[int] = None):
        if precalc is None:
            for it in words:
                self._fit_word(it.word + '$', it.freq)
        else:
            h = [(-1.0, '') for _ in range(precalc)]
            for it in words:
                self._fit_word(it.word + '$', it.freq)
                heapq.heappushpop(h, (it.freq, it.word))

            for _, w in h:
                self.mfw[w] = self.search2(w)

    def search2(self, s: str) -> str:
        if s in self.mfw:
            return self.mfw[s]

        max_freq = 0
        res: Optional[str] = None

        def update(freq, suggest):
            if freq is None:
                return
            nonlocal max_freq, res
            if max_freq < freq:
                res = suggest
                max_freq = freq

        cur_node = self.root
        for i in range(len(s)):
            if i + 3 >= len(s):
                break
            prev_sym = '' if i == 0 else s[i - 1]
            # try replace
            replace_sugs = ((self.em.p_replace(prev_sym, s[i], ch), Op.replace, ch) for ch in cur_node.go.keys())
            # try insert
            insert_sugs = [(self.em.p_insert(prev_sym, s[i]), Op.insert, None)]
            # try delete
            delete_sugs = ((self.em.p_delete(prev_sym, ch), Op.delete, ch) for ch in cur_node.go.keys())
            sugs = heapq.nlargest(5, itertools.chain(replace_sugs, insert_sugs, delete_sugs), key=lambda t: t[0])
            for p, op, ch in sugs:
                if p > sugs[0][0] * 0.1:
                    if op == Op.replace:
                        freq = self.find_freq(s[i + 1:] + '$', cur_node.go[ch])
                        update(freq, s[:i] + ch + s[i + 1:])
                    elif op == Op.insert:
                        new_s = s[:i] + s[i + 1:] + '$'
                        update(self.find_freq(new_s), s)
                    elif op == Op.delete:
                        freq = self.find_freq(s[i:] + '$', cur_node.go[ch])
                        update(freq, s[:i] + ch + s[i:])

            if s[i] in cur_node.go:
                cur_node = cur_node.go[s[i]]
            else:
                return s

        actual_freq = self.find_freq(s + '$')
        if actual_freq and res and max_freq / 50 > actual_freq:  # TODO add logging
            return res
        else:
            return s
