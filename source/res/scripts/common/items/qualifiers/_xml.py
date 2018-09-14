# Python 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/qualifiers/_xml.py
import expressions

def parseCondition(section):
    if not section.has_key('condition'):
        return (None, None)
    else:
        return expressions.parseExpression(section['condition'].asString)


def parseValue(section):
    if not section.has_key('value'):
        return (None, None)
    else:
        x = section['value'].asString.strip(' ')
        if x.endswith('%'):
            res = (True, int(x[:-1]))
        else:
            res = (False, int(x))
        return res
