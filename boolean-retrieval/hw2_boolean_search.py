#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import bisect
import codecs
import sys
from dataclasses import dataclass
from typing import Dict, List, Set, Optional, Tuple, Callable, TypeVar, Union
from collections import defaultdict, namedtuple

from sortedcontainers import SortedDict

from util.parser import someOp, satisfy, brackets, or_op_parser, and_op_parser, alter, ParserType, parser_fmap


class Bor:
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
                    new_d[s[i+j]] = path[j:], nxt
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


class Index:
    def __init__(self, docs_path: str):
        self._term_to_doc = list()
        self._create_index(docs_path)

    def normalize(self):
        # print(f"Start: {len(self._term_to_doc)}")
        self._term_to_doc.sort(key=lambda t: t[0])
        t = []
        cur_term = self._term_to_doc[0][0]
        cur_list = []
        for term, doc_id in self._term_to_doc:
            if cur_term == term:
                if isinstance(doc_id, int):
                    cur_list.append(doc_id)
                else:
                    cur_list = list(set(cur_list) | set(doc_id))
            else:
                t.append((cur_term, cur_list))
                cur_list = [doc_id]
                cur_term = term
        t.append((cur_term, cur_list))
        self._term_to_doc = t
        # print(f"End: {len(self._term_to_doc)}")

    def _create_index(self, docs_path: str):
        with codecs.open(docs_path) as file:
            for line in file:
                words = line.split()
                doc_id = int(words[0])
                for w in set(words[1:]):
                    i = bisect.bisect_left(self._term_to_doc, w)
                    if i == len(self._term_to_doc) or self._term_to_doc[i] != w:
                        bisect.insort(self._term_to_doc, w)
                    # self._term_to_doc.insert(w, doc_id)
                    # self._term_to_doc.append((w, doc_id))
            print(len(self._term_to_doc))
            # print(list((k, v[0] if v else []) for k, v in self._term_to_doc.root.items()))
            # self.normalize()
        # print(len(self._term_to_doc))  # 244863
        # print(sum(len(v) for v in self._term_to_doc.values()))  # 2563602
        # print(sum(sum(4 for s in v) for v in self._term_to_doc.values()))  # 10254408
        # print(sum(len(k) for k in self._term_to_doc.keys()))  # 1965197
        # print(sum(len(v) * len(k) for k, v in self._term_to_doc.items()))  # 19271201

    def __getitem__(self, term: str) -> Set[int]:
        return set()


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


@dataclass
class QueryOr(QueryTreeBase):
    left: QueryTreeBase
    right: QueryTreeBase

    def search(self, index: Index):
        l = self.left.search(index)
        r = self.right.search(index)
        return l | r


@dataclass
class QueryWord(QueryTreeBase):
    word: str

    def search(self, index: Index):
        return index[self.word]


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
            pass
            # self.data.add((qid, d))

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
