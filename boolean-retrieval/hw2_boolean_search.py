#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import codecs
from binascii import crc32
from dataclasses import dataclass
from typing import List, Set, Any

from src.parser import someOp, satisfy, brackets, or_op_parser, and_op_parser, alter, ParserType, parser_fmap
from word_multi_map.model import WordMultiMap


class WeakHashTable(WordMultiMap):
    def __init__(self, size: int = 10000):
        self._data = [bytearray() for i in range(size)]
        self._size = size

    def insert(self, key: str, value: bytes):
        i = crc32(bytes(key, 'utf-8')) % self._size
        self._data[i].append(value[0])
        self._data[i].append(value[1])

    def get(self, key: str) -> List[Any]:
        i = crc32(bytes(key, 'utf-8')) % self._size
        res = []
        for j in range(len(self._data[i]) // 2):
            res.append(int.from_bytes(self._data[i][2*j:2*j + 2], byteorder='big'))
        return res


class Index:
    def __init__(self, docs_path: str):
        self._term_to_doc: WordMultiMap = WeakHashTable(size=100057)
        self._create_index(docs_path)

    def _create_index(self, docs_path: str):
        with codecs.open(docs_path) as file:
            for line in file:
                words = line.split()
                doc_id = int(words[0]).to_bytes(2, byteorder='big')
                for w in set(words[1:]):
                    self._term_to_doc.insert(w, doc_id)

        # Количество уникальных термов 244863
        # Суммарное количество doc_id по всем уникальным термам  # 2563602
        # Суммарный размер doc_id по всем уникальным термам, если считать, что каждый 4 байта  # 10254408
        # Суммарная длина слов по всем уникальным термам  # 1965197
        # Суммарная длина документов, если унифицировать слова в документах  # 19271201

    def __getitem__(self, term: str) -> Set[int]:
        return set(self._term_to_doc.get(term))


@dataclass
class QueryTreeBase:

    def search(self, index: Index):
        raise NotImplementedError


@dataclass
class QueryAnd(QueryTreeBase):
    left: QueryTreeBase
    right: QueryTreeBase

    def search(self, index: Index):
        l = self.left.search(index)
        r = self.right.search(index)
        return l & r

    def __repr__(self):
        return f'({repr(self.left)}&&{repr(self.right)})'


@dataclass
class QueryOr(QueryTreeBase):
    left: QueryTreeBase
    right: QueryTreeBase

    def search(self, index: Index):
        l = self.left.search(index)
        r = self.right.search(index)
        return l | r

    def __repr__(self):
        return f'({repr(self.left)}||{repr(self.right)})'


@dataclass
class QueryWord(QueryTreeBase):
    word: str

    def search(self, index: Index):
        return index[self.word]

    def __repr__(self):
        return f'{self.word}'


"""
S -> T ('|' T)
T -> E (' ' E)
E -> (S)
E -> W
"""

word: ParserType = satisfy(lambda s: s.isalpha() or s.isnumeric())
term_query: ParserType = alter(brackets(lambda s: or_query(s)), parser_fmap(word, lambda w: QueryWord(w)))
and_query: ParserType = someOp(parser=term_query, op=and_op_parser, f=lambda a, b: QueryAnd(a, b))
or_query: ParserType = someOp(parser=and_query, op=or_op_parser, f=lambda a, b: QueryOr(a, b))


class Query:
    def __init__(self, qid: int, query: str):
        self.qid = qid
        t = or_query(query)
        assert t is not None
        self.query_tree: QueryTreeBase = t[0]
        assert not t[1]

    def search(self, index):
        return self.qid, self.query_tree.search(index)


class SearchResults:
    def __init__(self):
        self.data = set()

    def add(self, found):
        qid, docs = found
        for d in docs:
            self.data.add((qid, d))

    def print_submission(self, objects_file_path, submission_file_path):
        with codecs.open(objects_file_path, mode='r', encoding='utf-8') as file:
            with codecs.open(submission_file_path, mode='w', encoding='utf-8') as res:
                start = True
                for line in file:
                    if start:
                        start = False
                        res.write("ObjectId,Relevance\n")
                        continue
                    oid, qid, did = tuple(map(int, line.split(',')))
                    # if (qid, did) in self.data:  # TODO
                    res.write(f'{oid},{(qid, did) in self.data:b}\n')


def main():
    # Command line arguments.
    parser = argparse.ArgumentParser(description='Homework 2: Boolean Search')
    parser.add_argument('--queries_file', required=True, help='queries.numerate.txt')
    parser.add_argument('--objects_file', required=True, help='objects.numerate.txt')
    parser.add_argument('--docs_file', required=True, help='docs.tsv')
    parser.add_argument('--submission_file', required=True, help='output file with relevances')
    args = parser.parse_args()

    # Build index.
    index = Index(args.docs_file)

    # Process queries.
    search_results = SearchResults()
    with codecs.open(args.queries_file, mode='r', encoding='utf-8') as queries_fh:
        for line in queries_fh:
            fields = line.rstrip('\n').split('\t')
            qid = int(fields[0])

            # Parse query.
            query = Query(qid, fields[1])

            # Search and save results.
            search_results.add(query.search(index))

    # Generate submission file.
    search_results.print_submission(args.objects_file, args.submission_file)


if __name__ == "__main__":
    main()
