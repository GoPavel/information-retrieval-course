from tqdm import tqdm

from error_model import ErrorModel
from load_data import load_data, WordItem, MistakeItem
from trie import Trie


def main():
    em = ErrorModel((1, 0, 1))
    em.fit(tqdm(load_data('data/train.csv', factory=MistakeItem), total=362257))

    t = Trie(em)
    t.fit(load_data('data/words.csv', factory=WordItem))

    words = [ 'ЛEСБІЯНКИ',
             'ОЧЮЖДЕНИЯ',
             'ХӘНИЯ',
             'MÖWENPICK',
             'РУЛЄТКА',
             'ОДҢОКЛАССНИКИ',
             'ОБРАЩЯТЬСЯ',
             'РЕЬЕНКУ',
             'VERTĖJAS',
             'ПАЬРУЛЬ',
             'МАЛОЛЄТКИ',
             'АВТОЬУСОВ',
             'ЛEЙЛА',
             'ЛЄТУАЛЬ',
             'ПPЯМО',
             'КАЬАЛОГ',
             'ЖEНЩИНЫ',
             'ТУPЦИИ',
             'ЦEРКВА',
             'КОМПЪЮТЕРА',
             'ПЪЯНЫМИ',
             'ХАРАКТEРИСТИКА',
             'ОЬРАЗНОЙ',
             'МEЙЗУ',
             ]
    for w in words:
        print(f'{w} -> {t.search2(w)}')


if __name__ == '__main__':
    main()
