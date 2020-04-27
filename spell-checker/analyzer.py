import argparse
import sys

from tqdm import tqdm

from error_model import ErrorModel
from load_data import load_data, WordItem, MistakeItem
from trie import Trie


def main(args):
    em = ErrorModel((0.1, 0.1, 0.9))
    em.fit(tqdm(load_data(args.train, factory=MistakeItem), total=362257))

    t = Trie(em)
    words = load_data(args.words, factory=WordItem)
    t.fit(words)

    s = list((it.actual, it.expected) for it in load_data(args.output, factory=MistakeItem) if it.actual != it.expected)
    s.sort(key=lambda it: t.find_freq(it[1] + '$') / t.find_freq(it[0] + '$'))
    # s = list(f'{it.actual} -> {it.expected}' for it in load_data(args.output, factory=MistakeItem) if it.actual != it.expected and t.find_freq(it.expected + '$') / t.find_freq(it.actual + '$') > 7)
    for th in [5, 10, 20, 30, 40, 50, 60, 70]:
        print(f'Threshold = {th}')
        sf = [f'{it[0]} -> {it[1]}' for it in s if t.find_freq(it[1] + '$') / t.find_freq(it[0] + '$') > th]
        print(len(sf))
        print(sf[:30])


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--train', type=str, help='train csv', required=True)
    parser.add_argument('--words', type=str, help='words csv', required=True)
    parser.add_argument('--output', type=str, help='name of output file', required=False)
    parser.add_argument('--input', type=str, help='no_fix csv for queries', required=True)
    main(parser.parse_args())
