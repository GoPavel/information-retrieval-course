import argparse
import sys

from tqdm import tqdm

from error_model import ErrorModel
from load_data import load_data, WordItem, MistakeItem
from trie import Trie

from multiprocessing.pool import Pool

sys.setrecursionlimit(25000)

t = None


def main(args):
    em = ErrorModel((0, 0, 1))
    em.fit(load_data(args.train, factory=MistakeItem))

    global t
    t = Trie(em)
    words = load_data(args.words, factory=WordItem)
    t.fit(words)

    # with Pool(6) as pool:
    #     it = load_data(args.input, factory=lambda x, y: x)
    #     res_it = pool.imap(t.search2, it, chunksize=10000)
    #
    #     with open(args.output, 'w') as f:
    #         it2 = load_data(args.input, factory=lambda x, y: x)
    #         for a, e in tqdm(zip(it2, res_it), total=362257):
    #             f.write(f'{a},{e}\n')
    #

    with open(args.output, 'w') as f:
        f.write('Id,Predicted\n')
        for item in tqdm(load_data(args.input, factory=MistakeItem), total=362257):
            s = item.actual
            f.write(f'{s},{t.search2(s)}\n')

    # s = list((it.actual, it.expected) for it in load_data(args.output, factory=MistakeItem) if it.actual != it.expected)
    # s.sort(key=lambda it: t.find_freq(it[1] + '$') / t.find_freq(it[0] + '$'))
    # # s = list(f'{it.actual} -> {it.expected}' for it in load_data(args.output, factory=MistakeItem) if it.actual != it.expected and t.find_freq(it.expected + '$') / t.find_freq(it.actual + '$') > 7)
    # s = [f'{it[0]} -> {it[1]}' for it in s if t.find_freq(it[1] + '$') / t.find_freq(it[0] + '$') > 40]
    # # s = [t.find_freq(it[1] + '$') / t.find_freq(it[0] + '$') for it in s if t.find_freq(it[1] + '$') / t.find_freq(it[0] + '$') > 1]
    # print(len(s))
    # print(s[:50])


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--train', type=str, help='train csv', required=True)
    parser.add_argument('--words', type=str, help='words csv', required=True)
    parser.add_argument('--output', type=str, help='name of output file', required=False)
    parser.add_argument('--input', type=str, help='no_fix csv for queries', required=True)
    main(parser.parse_args())

# 0.14021537195968609
# 0.1695757431878473
