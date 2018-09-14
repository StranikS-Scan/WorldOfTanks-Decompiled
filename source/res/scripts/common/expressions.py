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


class ExpressionParser(object):
    _CMP_OPERATORS = {'==': lambda left, right: lambda context: left(context) == right(context),
     '!=': lambda left, right: lambda context: left(context) != right(context),
     '<': lambda left, right: lambda context: left(context) < right(context),
     '<=': lambda left, right: lambda context: left(context) <= right(context),
     '>': lambda left, right: lambda context: left(context) > right(context),
     '>=': lambda left, right: lambda context: left(context) >= right(context)}
    _SUM_OPERATORS = {'+': lambda left, right: lambda context: left(context) + right(context),
     '-': lambda left, right: lambda context: left(context) - right(context)}

    def __init__(self):
        self.tokens = set()

    def parseExpression(self, s):
        tokenizer = _Tokenizer(s.strip())
        expression = self._parseExpression(tokenizer)
        tokenizer.match(token.ENDMARKER)
        return (expression, self.tokens)

    def _parseOperator(self, tokenizer, operators):
        toknum, tokval = tokenizer.peek()
        if toknum == token.OP and tokval in operators:
            tokenizer.match(toknum)
            return operators[tokval]
        else:
            return None
            return None

    def _parseExpression(self, tokenizer):
        return self._parseOrExpression(tokenizer)

    def _parseOrExpression(self, tokenizer):
        left = self._parseAndExpression(tokenizer)
        toknum, tokval = tokenizer.peek()
        if toknum == token.NAME and tokval == 'or':
            tokenizer.match(token.NAME)
            right = self._parseOrExpression(tokenizer)
            return lambda context: left(context) or right(context)
        else:
            return left

    def _parseAndExpression(self, tokenizer):
        left = self._parseCondition(tokenizer)
        toknum, tokval = tokenizer.peek()
        if toknum == token.NAME and tokval == 'and':
            tokenizer.match(token.NAME)
            right = self._parseAndExpression(tokenizer)
            return lambda context: left(context) and right(context)
        else:
            return left

    def _parseCondition(self, tokenizer):
        toknum, tokval = tokenizer.peek()
        if toknum == token.NAME and tokval == 'not':
            tokenizer.match(token.NAME, 'not')
            expression = self._parseCondition(tokenizer)
            return lambda context: not expression(context)
        else:
            left = self._parseSum(tokenizer)
            op = self._parseOperator(tokenizer, self._CMP_OPERATORS)
            if op is not None:
                right = self._parseSum(tokenizer)
                return op(left, right)
            return left
            return

    def _parseSum(self, tokenizer):
        toknum, tokval = tokenizer.peek()
        if toknum == token.OP and tokval == '(':
            tokenizer.match(token.OP, '(')
            expression = self._parseExpression(tokenizer)
            tokenizer.match(token.OP, ')')
            left = expression
        else:
            left = self._parseTerm(tokenizer)
        op = self._parseOperator(tokenizer, self._SUM_OPERATORS)
        if op is not None:
            right = self._parseSum(tokenizer)
            return op(left, right)
        else:
            return left
            return

    def _parseTerm(self, tokenizer):
        toknum, tokval = tokenizer.peek()
        if toknum == token.NAME:
            self.tokens.add(tokval)
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


def parseExpression(condition):
    return ExpressionParser().parseExpression(condition)
