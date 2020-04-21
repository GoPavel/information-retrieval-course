from typing import TypeVar, Callable, Tuple, Optional

T = TypeVar('T')
ParserType = Callable[[str], Optional[Tuple[T, str]]]


def parser_fmap(parser: ParserType, f: Callable) -> ParserType:
    def new_parser(s):
        t = parser(s)
        if t is None: return None
        v, s = t
        return f(v), s

    return new_parser


def alter(left_parser: ParserType, right_parser: ParserType) -> ParserType:
    def new_parser(s: str):
        return left_parser(s) or (right_parser(s) or None)
        
    return new_parser


def or_op_parser(s) -> Optional[Tuple[T, str]]:
    e, sep, s = s.partition('|')
    if e or sep != '|':
        return None
    else:
        return sep, s


def and_op_parser(s) -> Optional[Tuple[T, str]]:
    e, sep, s = s.partition(' ')
    if e or sep != ' ':
        return None
    else:
        return sep, s.strip()


def someOp(*, parser: ParserType, op: ParserType, f: Callable, z=None) -> ParserType:
    def new_parser(s: str):
        s = s.strip()
        t = parser(s)
        if t is None:
            return None
        v, s = t
        args = [v]
        while True:
            t = op(s)
            if t is None: break
            _, _s = t
            t = parser(_s)
            if t is None: break
            arg, s = t
            args.append(arg)

        if z is None:
            res = args[0]
        elif isinstance(z, Callable):
            res = f(z(), args[0])
        else:
            res = f(z, args[0])
        for arg in args[1:]:
            res = f(res, arg)
        return res, s

    return new_parser


def satisfy(pred: Callable[[str], bool]) -> ParserType:
    def new_parser(s: str):
        s = s.strip()
        i = 0
        while len(s) > i and pred(s[i]):
            i += 1
        if i == 0: return None
        res = s[:i]
        s = s[i:]
        return res, s

    return new_parser


word = satisfy(str.isalpha)


def brackets(parser: ParserType) -> ParserType:
    def new_parser(s: str):
        e1, sep1, s = s.partition('(')
        if e1 or sep1 != '(': return None
        t = parser(s)
        if t is None: return None
        v, s = t
        e2, sep2, s = s.partition(')')
        if e2 or sep2 != ')': return None
        return v, s

    return new_parser
