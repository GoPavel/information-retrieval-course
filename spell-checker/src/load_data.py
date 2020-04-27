import attr
from tqdm import tqdm


def load_data(path, factory, tqdm_total=-1):
    print(f'Load data from {path}')
    with open(path) as f:
        headers = f.readline()
        for line in (f if tqdm_total == -1 else tqdm(f, total=tqdm_total)):
            parts = line.rstrip("\n").split(',')
            item = factory(*parts)
            yield item


@attr.s(auto_attribs=True, slots=True)
class WordItem:
    word: str
    freq: float = attr.ib(converter=int)


@attr.s(auto_attribs=True, slots=True)
class MistakeItem:
    actual: str
    expected: str
