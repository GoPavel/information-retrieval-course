import pytest

from hw2_boolean_search import or_query, QueryOr, QueryAnd, QueryWord
from parser import *


class TestParser:

    def test_word(self):
        assert (word('a b') == 'a', ' b')
        assert (word(' a b') == 'a', ' b')
        assert (word('abab') == 'abab', '')
        assert (word('a)') == 'a', ')')
        assert word(' ') is None
        assert word(' %%%') is None

    def test_bracket(self):
        parser = brackets(word)

        assert (parser('(a)') == 'a', '')
        assert (parser(' ( ab )') == 'ab', '')
        assert (parser(' ( a b )') is None)
        assert (parser('()') is None)
        assert (brackets(parser)('( (a) )') == 'a', '')

    def test_some_or(self):
        parser = someOp(parser=word, op=or_op_parser, f=(lambda xs, x: xs.append(x) or xs), z=list)

        assert (parser('|a') is None)
        assert (parser('a') == ['a'], '')
        assert (parser('a|b') == ['a', 'b'], '')
        assert (parser('a|b|c') == ['a', 'b', 'c'], '')
        assert (parser('a|b|c|') == ['a', 'b', 'c'], '|')
        assert (parser('a|b|c&') == ['a', 'b', 'c'], '&')
        assert (parser('a|b|c & (a|b)') == ['a', 'b', 'c'], ' & (a|b)')

    def test_some_and(self):
        parser = someOp(parser=word, op=and_op_parser, f=(lambda xs, x: xs.append(x) or xs), z=list)

        assert (parser('|a') is None)
        assert (parser('a') == ['a'], '')
        assert (parser('a b') == ['a', 'b'], '')
        assert (parser('a b c') == ['a', 'b', 'c'], '')
        assert (parser('a b c ') == ['a', 'b', 'c'], ' ')
        assert (parser('a b c&') == ['a', 'b', 'c'], '&')
        assert (parser('a b c & (a b)') == ['a', 'b', 'c'], ' & (a b)')


class TestQueryParser:

    def test1(self):
        assert or_query("(ДЛИНА|ПРОТЯЖЕННОСТЬ) AUDI Q3")[0] == \
               QueryAnd(
                   QueryAnd(
                       QueryOr(
                           QueryWord("ДЛИНА"),
                           QueryWord("ПРОТЯЖЕННОСТЬ")),
                       QueryWord("AUDI"),
                   ),
                   QueryWord("Q3")
               )

    def test2(self):
        assert or_query("(ВАКАНСИЯ|РАБОТА) (ЛЕРУА МЕРЛЕН|LEROY MERLIN) (ВЛАДИКАВКАЗ|ВЛАДИКАВКАЗСКИЙ)")[0] == \
            QueryAnd(
                QueryAnd(
                    QueryOr(
                        QueryWord('ВАКАНСИЯ'),
                        QueryWord('РАБОТА'),
                    ),
                    QueryOr(
                        QueryAnd(
                            QueryWord('ЛЕРУА'),
                            QueryWord('МЕРЛЕН')
                        ),
                        QueryAnd(
                            QueryWord('LEROY'),
                            QueryWord('MERLIN')
                        )
                    )
                ),
                QueryOr(
                    QueryWord('ВЛАДИКАВКАЗ'),
                    QueryWord('ВЛАДИКАВКАЗСКИЙ')
                )
            )