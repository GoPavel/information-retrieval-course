from typing import Optional, Iterable, Dict, List, Tuple

import attr

from error_model import ErrorModel
from load_data import WordItem


@attr.s(auto_attribs=True, slots=True, repr=False)
class Node:
    go: Optional[Dict[str, 'Node']] = attr.ib(default=attr.Factory(dict))
    freq: Optional[float] = None
    is_end: bool = False


class Trie:
    def __init__(self, em: ErrorModel):
        self.root = Node(go={'$': Node(is_end=True)})
        self.em = em

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

    def fit(self, words: Iterable[WordItem]):
        for it in words:
            self._fit_word(it.word + '$', it.freq)

    # def _go_search(self, v: Node, s: str, i: int) -> Tuple[str, float]:
    #     TODO care about only one correction
    # if v.is_end:
    #     return '', v.freq
    # p = [(self.em.p_step(s[i], s[i + 1], ch), ch) for ch, u in v.go if ch != s[i+1]]
    # p.sort()
    # results = [(self._go_search(v.go[ch], s, i + 1), ch) for ch in p[:5]]
    # (sug, freq), ch = max(results, key=lambda t: t[0][1])
    # return ch + sug, freq

    def search2(self, s: str) -> str:
        max_freq = 0
        res: Optional[str] = None

        def update(freq, suggest):
            nonlocal max_freq, res
            if max_freq < freq:
                res = suggest
                max_freq = freq

        cur_node = self.root
        for i in range(len(s)):
            if i + 3 >= len(s):
                break
            prev_sym = '' if i == 0 else s[i-1]
            sugs = sorted(((self.em.p_step(prev_sym, s[i], ch), ch) for ch, u in cur_node.go.items()), reverse=True)
            for p, ch in sugs[1:6]:
                if len(sugs) < 2 or p > sugs[1][0] * 0.1:
                # if p > sugs[0][0] * 0.1:
                    freq = self.find_freq(s[i + 1:] + '$', cur_node.go[ch])
                    if freq is not None:
                        update(freq, s[:i] + ch + s[i + 1:])
            if s[i] in cur_node.go:
                cur_node = cur_node.go[s[i]]
            else:
                return s

        actual_freq = self.find_freq(s + '$')
        if actual_freq and res and max_freq / 70 > actual_freq:  # TODO add logging
            return res
        else:
            return s

