# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/lib2to3/fixes/fix_reduce.py
from lib2to3 import fixer_base
from lib2to3.fixer_util import touch_import

class FixReduce(fixer_base.BaseFix):
    BM_compatible = True
    order = 'pre'
    PATTERN = "\n    power< 'reduce'\n        trailer< '('\n            arglist< (\n                (not(argument<any '=' any>) any ','\n                 not(argument<any '=' any>) any) |\n                (not(argument<any '=' any>) any ','\n                 not(argument<any '=' any>) any ','\n                 not(argument<any '=' any>) any)\n            ) >\n        ')' >\n    >\n    "

    def transform(self, node, results):
        touch_import(u'functools', u'reduce', node)
