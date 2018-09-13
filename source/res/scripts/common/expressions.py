# Embedded file name: scripts/common/expressions.py
import cStringIO
import tokenize, token

class ParserException(Exception):

    def __init__(self, message):
        super(ParserException, self).__init__(message)


class _Tokenizer:

    def __init__(self, s):
        self.tokenizer = tokenize.generate_tokens(cStringIO.StringIO(s).readline)
        self.__currentToken = None
        return

    def __next(self):
        try:
            while True:
                toknum, tokval, _, _, _ = self.tokenizer.next()
                self.__currentToken = (toknum, tokval)
                if toknum not in (tokenize.NL,
                 token.NEWLINE,
                 token.INDENT,
                 token.DEDENT):
                    break

        except StopIteration:
            self.__currentToken = None

        return

    def peek(self):
        if self.__currentToken is None:
            self.__next()
        return self.__currentToken

    def match(self, toknum, tokval = None):
        if self.__currentToken is None:
            self.__next()
        currentToken = self.__currentToken
        if currentToken is None or toknum != currentToken[0]:
            raise ParserException('unexpected token %s "%s", expected %s' % (token.tok_name[currentToken[0]], currentToken[1], token.tok_name[toknum]))
        if tokval is not None and tokval != currentToken[1]:
            raise ParserException('unexpected token %s "%s", expected %s "%s"' % (token.tok_name[currentToken[0]],
             currentToken[1],
             token.tok_name[toknum],
             tokval))
        self.__currentToken = None
        return currentToken[1]


def parseExpression(s):
    tokenizer = _Tokenizer(s.strip())
    expression = _parseExpression(tokenizer)
    tokenizer.match(token.ENDMARKER)
    return expression


def _parseOperator(tokenizer, operators):
    toknum, tokval = tokenizer.peek()
    if toknum == token.OP and tokval in operators:
        tokenizer.match(toknum)
        return operators[tokval]
    else:
        return None
        return None


_CMP_OPERATORS = {'==': lambda left, right: lambda context: left(context) == right(context),
 '!=': lambda left, right: lambda context: left(context) != right(context),
 '<': lambda left, right: lambda context: left(context) < right(context),
 '<=': lambda left, right: lambda context: left(context) <= right(context),
 '>': lambda left, right: lambda context: left(context) > right(context),
 '>=': lambda left, right: lambda context: left(context) >= right(context)}
_SUM_OPERATORS = {'+': lambda left, right: lambda context: left(context) + right(context),
 '-': lambda left, right: lambda context: left(context) - right(context)}

def _parseExpression(tokenizer):
    return _parseOrExpression(tokenizer)


def _parseOrExpression(tokenizer):
    left = _parseAndExpression(tokenizer)
    toknum, tokval = tokenizer.peek()
    if toknum == token.NAME and tokval == 'or':
        tokenizer.match(token.NAME)
        right = _parseOrExpression(tokenizer)
        return lambda context: left(context) or right(context)
    else:
        return left


def _parseAndExpression(tokenizer):
    left = _parseCondition(tokenizer)
    toknum, tokval = tokenizer.peek()
    if toknum == token.NAME and tokval == 'and':
        tokenizer.match(token.NAME)
        right = _parseAndExpression(tokenizer)
        return lambda context: left(context) and right(context)
    else:
        return left


def _parseCondition(tokenizer):
    toknum, tokval = tokenizer.peek()
    if toknum == token.NAME and tokval == 'not':
        tokenizer.match(token.NAME, 'not')
        expression = _parseCondition(tokenizer)
        return lambda context: not expression(context)
    else:
        left = _parseSum(tokenizer)
        op = _parseOperator(tokenizer, _CMP_OPERATORS)
        if op is not None:
            right = _parseSum(tokenizer)
            return op(left, right)
        return left
        return


def _parseSum(tokenizer):
    toknum, tokval = tokenizer.peek()
    if toknum == token.OP and tokval == '(':
        tokenizer.match(token.OP, '(')
        expression = _parseExpression(tokenizer)
        tokenizer.match(token.OP, ')')
        left = expression
    else:
        left = _parseTerm(tokenizer)
    op = _parseOperator(tokenizer, _SUM_OPERATORS)
    if op is not None:
        right = _parseSum(tokenizer)
        return op(left, right)
    else:
        return left
        return


def _parseTerm(tokenizer):
    toknum, tokval = tokenizer.peek()
    if toknum == token.NAME:
        tokenizer.match(token.NAME)
        return lambda context: context[tokval]
    if toknum == token.NUMBER:
        tokenizer.match(token.NUMBER)
        try:
            tokval = int(tokval)
        except ValueError:
            tokval = float(tokval)

        return lambda context: tokval
    if toknum == token.STRING:
        tokenizer.match(token.STRING)
        if tokval.startswith('"') and tokval.endswith('"') or tokval.startswith("'") and tokval.endswith("'"):
            tokval = tokval[1:-1].decode('string_escape')
        else:
            raise ParserException('unsupported string literal')
        return lambda context: tokval
    raise ParserException('expected term, but found %s (%s)' % (token.tok_name[toknum], tokval))


if __name__ == '__main__':

    def runTests():
        context = {'a': 1,
         'b': 10,
         'c': 100,
         's': "string'"}
        tests = ['a < b',
         'a > b',
         'a == b',
         'a < b and b < c',
         'a < b and not b < c',
         '(a < b or b < c) and (a != a)',
         'a < b or (b < c and a != a)',
         'a < b or b < c and a != a',
         'a < 5',
         'b < 5.0',
         'a > 0 or a < 0 and a < 0',
         'a + b < 12 and a + b > 10',
         'a + b == 11',
         '(a - b) + b == a',
         'a + 9 == (c - 90)',
         "s == 'string\\''"]
        for test in tests:
            expected = eval(test, None, context)
            print '%s -> %s' % (test, expected)
            raise expected == parseExpression(test)(context) or AssertionError

        import timeit
        setup = ''
        for key, value in context.iteritems():
            setup += key + '=' + value.__repr__() + ';'

        for test in tests:
            expression = parseExpression(test)
            print '%s: %s vs %s' % (test, timeit.timeit(test, setup), timeit.timeit(lambda : expression(context)))

        return


    runTests()
