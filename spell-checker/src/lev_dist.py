from enum import Enum
from typing import Tuple, List, Dict

import numpy as np


class Op(Enum):
    replace = 0
    delete = 1
    insert = 2

# hll
# hell

# hell
# hll

# hello
# hella


# s1 -> s2
def lev_dist(s1: str, s2: str):
    # NOTE: We don't care about several edit way

    d = np.zeros((len(s1) + 1, len(s2) + 1), dtype=int)

    for i in range(0, len(s1)):
        d[i+1, 0] = i+1
    for j in range(0, len(s2)):
        d[0, j+1] = j+1

    for i in range(0, len(s1)):
        for j in range(0, len(s2)):
            d[i+1, j+1] = min(d[i+1, j  ] + 1,  # insert to s1 (delete in s2)
                              d[i  , j+1] + 1,  # delete in s1
                              d[i  , j ] + int(s1[i] != s2[j]))

    level1 = {
        Op.insert: [],
        Op.delete: [],
        Op.replace: []
    }

    level2 = {
        Op.insert: [],
        Op.delete: [],
        Op.replace: []
    }

    i, j = (len(s1), len(s2))
    while i != 0 or j != 0:
        if d[i, j] == d[i - 1, j - 1] + int(s1[i - 1] != s2[j - 1]):
            if s1[i - 1] != s2[j - 1]:
                level1[Op.replace].append((s1[i - 1], s2[j - 1]))
                prev1 = s1[i - 2] if i - 2 >= 0 else ''
                prev2 = s2[j - 2] if j - 2 >= 0 else ''
                if prev1 == prev2:
                    level2[Op.replace].append((prev1, s1[i - 1], s2[j - 1]))
            i = i - 1
            j = j - 1
        elif d[i, j] == d[i, j-1] + 1:
            level1[Op.insert].append(s2[j - 1])
            prev = s2[j-2] if j - 2 >= 0 else ''
            level2[Op.insert].append((prev, s2[j - 1]))
            j = j - 1
        elif d[i, j] == d[i-1, j] + 1:
            level1[Op.delete].append(s1[i - 1])
            prev = s1[i-2] if i - 2 >= 0 else ''
            level2[Op.delete].append((prev, s1[i - 1]))
            i = i - 1
        else:
            raise RuntimeError("Logic error")

    return d[len(s1), len(s2)], level1, level2
