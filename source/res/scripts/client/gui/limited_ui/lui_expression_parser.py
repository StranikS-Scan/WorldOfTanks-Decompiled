# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/limited_ui/lui_expression_parser.py
import typing
from expressions import ExpressionParser
if typing.TYPE_CHECKING:
    from typing import List

class LimitedUIExpressionParser(ExpressionParser):

    def __init__(self):
        super(LimitedUIExpressionParser, self).__init__()
        self.__elements = []

    @property
    def elements(self):
        return self.__elements

    def _processToken(self, tokval):
        self.__elements.append(tokval)


def parseExpression(condition):
    parser = LimitedUIExpressionParser()
    expression, tokens = parser.parseExpression(condition)
    return (expression, tokens, parser.elements)
