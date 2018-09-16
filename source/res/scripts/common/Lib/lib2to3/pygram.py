# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/lib2to3/pygram.py
import os
from .pgen2 import token
from .pgen2 import driver
from . import pytree
_GRAMMAR_FILE = os.path.join(os.path.dirname(__file__), 'Grammar.txt')
_PATTERN_GRAMMAR_FILE = os.path.join(os.path.dirname(__file__), 'PatternGrammar.txt')

class Symbols(object):

    def __init__(self, grammar):
        for name, symbol in grammar.symbol2number.iteritems():
            setattr(self, name, symbol)


python_grammar = driver.load_grammar(_GRAMMAR_FILE)
python_symbols = Symbols(python_grammar)
python_grammar_no_print_statement = python_grammar.copy()
del python_grammar_no_print_statement.keywords['print']
pattern_grammar = driver.load_grammar(_PATTERN_GRAMMAR_FILE)
pattern_symbols = Symbols(pattern_grammar)
