from word_multi_map.model import WordMultiMap


class Bor(WordMultiMap):
    def __init__(self):
        self.root = {'#': []}
        self._size = 0

    def insert(self, s: str, value):
        cur = self.root
        i = 0
        while True:
            if i == len(s):
                cur['#'].append(value)
                break
            if s[i] in cur:
                j = 0
                path, nxt = cur[s[i]]
                while j < len(path) and (i + j) < len(s) \
                        and s[i + j] == path[j]:
                    j += 1
                if j == len(path):
                    i += j
                    cur = nxt
                    continue
                elif (i + j) == len(s):
                    new_d = {}
                    cur[s[i]] = path[:j], new_d
                    new_d[path[j]] = path[j:], nxt
                    new_d['#'] = [value]
                    self._size += 1
                    break
                elif s[i + j] != path[j]:
                    new_d = {}
                    cur[s[i]] = path[:j], new_d
                    new_d[s[i + j]] = path[j:], nxt
                    new_d['#'] = []
                    new_d2 = {}
                    new_d[s[i + j]] = s[i + j:], new_d2
                    new_d2['#'] = [value]
                    self._size += 2
                    break
            if s[i] not in cur:
                new_d = {}
                cur[s[i]] = s[i:], new_d
                new_d['#'] = [value]
                self._size += 1
                break

        # for ch in s:
        #     if ch not in cur:
        #         cur[ch] = {'#': []}
        #         self._size += 1
        #     cur = cur[ch]
        # cur['#'].append(value)

    def get(self, s: str) -> list:
        cur = self.root
        for ch in s:
            if ch not in cur:
                return []
            cur = cur[ch]
        return cur['#']

    def __len__(self):
        return self._size
