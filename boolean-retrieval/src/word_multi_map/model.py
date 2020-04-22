from typing import Any, List


class WordMultiMap:

    def insert(self, key: str, value: Any):
        raise NotImplementedError

    def get(self, key: str) -> List[Any]:
        raise NotImplementedError
