import argparse

from tqdm import tqdm

from error_model import ErrorModel
from load_data import load_data, MistakeItem, WordItem
from trie import Trie


def main(args):
    pairs = tqdm(load_data(args.input, factory=MistakeItem), total=362257)

    em = ErrorModel((0.1, 0.1, 0.9))
    em.fit(tqdm(load_data(args.train, factory=MistakeItem), total=362257))

    t = Trie(em)
    words = load_data(args.words, factory=WordItem)
    t.fit(words)

    with open(args.output, 'w') as f:
        f.write('Id,Predicted\n')
        for p in pairs:  # type: MistakeItem
            left = p.actual
            right = p.expected
            ans_freq = t.find_freq(right + '$')
            query_freq = t.find_freq(left + '$')
            if ans_freq and query_freq and ans_freq > query_freq * args.threshold:
                f.write(f'{left},{right}\n')
            else:
                f.write(f'{left},{left}\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--train', type=str, help='train csv', required=True)
    parser.add_argument('--words', type=str, help='words csv', required=True)
    parser.add_argument('--threshold', '-t', type=float, required=True)
    parser.add_argument('--input', '-i', type=str, required=True)
    parser.add_argument('--output', '-o', type=str, required=True)
    main(parser.parse_args())
