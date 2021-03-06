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
    em = ErrorModel((0.1, 0.1, 0.9))
    em.fit(tqdm(load_data(args.train, factory=MistakeItem), total=362257))

    global t
    t = Trie(em)
    words = load_data(args.words, factory=WordItem)
    t.fit(words)

    with Pool(5) as pool:
        it = load_data(args.input, factory=lambda x, y: x)
        res_it = pool.imap(t.search2, it, chunksize=10000)

        with open(args.output, 'w') as f:
            f.write('Id,Predicted\n')
            it2 = load_data(args.input, factory=lambda x, y: x)
            for a, e in tqdm(zip(it2, res_it), total=362257):
                f.write(f'{a},{e}\n')

    # with open(args.output, 'w') as f:
    #     f.write('Id,Predicted\n')
    #     for item in tqdm(load_data(args.input, factory=MistakeItem), total=362257):
    #         s = item.actual
    #         f.write(f'{s},{t.search2(s)}\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--train', type=str, help='train csv', required=True)
    parser.add_argument('--words', type=str, help='words csv', required=True)
    parser.add_argument('--output', type=str, help='name of output file', required=False)
    parser.add_argument('--input', type=str, help='no_fix csv for queries', required=True)
    main(parser.parse_args())
