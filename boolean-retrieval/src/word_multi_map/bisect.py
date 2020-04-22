import bisect
from typing import List, Any

from word_multi_map.model import WordMultiMap


class BisectMap(WordMultiMap):
    def __init__(self):
        self._keys: List[str] = list()
        self._value: List[List[Any]] = list()

    def insert(self, key: str, value: Any):
        i = bisect.bisect_left(self._keys, key)
        if i == len(self._keys) or self._keys[i] != key:
            self._keys.insert(i, key)
            self._value.insert(i, [value])
        elif i != len(self._keys):
            self._value[i].append(value)

    def get(self, key: str) -> List[Any]:
        i = bisect.bisect_left(self._keys, key)
        if i == len(self._keys) or self._keys != key:
            return []
        else:
            return self._value[i]
