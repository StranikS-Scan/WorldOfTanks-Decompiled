# Embedded file name: scripts/common/Lib/plat-irix5/panelparser.py
from warnings import warnpy3k
warnpy3k('the panelparser module has been removed in Python 3.0', stacklevel=2)
del warnpy3k
whitespace = ' \t\n'
operators = "()'"
separators = operators + whitespace + ';' + '"'

def tokenize_string(s):
    tokens = []
    while s:
        c = s[:1]
        if c in whitespace:
            s = s[1:]
        elif c == ';':
            s = ''
        elif c == '"':
            n = len(s)
            i = 1
            while i < n:
                c = s[i]
                i = i + 1
                if c == '"':
                    break
                if c == '\\':
                    i = i + 1

            tokens.append(s[:i])
            s = s[i:]
        elif c in operators:
            tokens.append(c)
            s = s[1:]
        else:
            n = len(s)
            i = 1
            while i < n:
                if s[i] in separators:
                    break
                i = i + 1

            tokens.append(s[:i])
            s = s[i:]

    return tokens


def tokenize_file(fp):
    tokens = []
    while 1:
        line = fp.readline()
        if not line:
            break
        tokens = tokens + tokenize_string(line)

    return tokens


syntax_error = 'syntax error'

def parse_expr(tokens):
    if not tokens or tokens[0] != '(':
        raise syntax_error, 'expected "("'
    tokens = tokens[1:]
    expr = []
    while 1:
        if not tokens:
            raise syntax_error, 'missing ")"'
        if tokens[0] == ')':
            return (expr, tokens[1:])
        if tokens[0] == '(':
            subexpr, tokens = parse_expr(tokens)
            expr.append(subexpr)
        else:
            expr.append(tokens[0])
            tokens = tokens[1:]


def parse_file(fp):
    tokens = tokenize_file(fp)
    exprlist = []
    while tokens:
        expr, tokens = parse_expr(tokens)
        exprlist.append(expr)

    return exprlist
