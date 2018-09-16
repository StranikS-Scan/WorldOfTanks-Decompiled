# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/lib2to3/pgen2/parse.py
from . import token

class ParseError(Exception):

    def __init__(self, msg, type, value, context):
        Exception.__init__(self, '%s: type=%r, value=%r, context=%r' % (msg,
         type,
         value,
         context))
        self.msg = msg
        self.type = type
        self.value = value
        self.context = context


class Parser(object):

    def __init__(self, grammar, convert=None):
        self.grammar = grammar
        self.convert = convert or (lambda grammar, node: node)

    def setup(self, start=None):
        if start is None:
            start = self.grammar.start
        newnode = (start,
         None,
         None,
         [])
        stackentry = (self.grammar.dfas[start], 0, newnode)
        self.stack = [stackentry]
        self.rootnode = None
        self.used_names = set()
        return

    def addtoken(self, type, value, context):
        ilabel = self.classify(type, value, context)
        while True:
            dfa, state, node = self.stack[-1]
            states, first = dfa
            arcs = states[state]
            for i, newstate in arcs:
                t, v = self.grammar.labels[i]
                if ilabel == i:
                    self.shift(type, value, newstate, context)
                    state = newstate
                    while states[state] == [(0, state)]:
                        self.pop()
                        if not self.stack:
                            return True
                        dfa, state, node = self.stack[-1]
                        states, first = dfa

                    return False
                if t >= 256:
                    itsdfa = self.grammar.dfas[t]
                    itsstates, itsfirst = itsdfa
                    if ilabel in itsfirst:
                        self.push(t, self.grammar.dfas[t], newstate, context)
                        break
            else:
                if (0, state) in arcs:
                    self.pop()
                    if not self.stack:
                        raise ParseError('too much input', type, value, context)
                raise ParseError('bad input', type, value, context)

    def classify(self, type, value, context):
        if type == token.NAME:
            self.used_names.add(value)
            ilabel = self.grammar.keywords.get(value)
            if ilabel is not None:
                return ilabel
        ilabel = self.grammar.tokens.get(type)
        if ilabel is None:
            raise ParseError('bad token', type, value, context)
        return ilabel

    def shift(self, type, value, newstate, context):
        dfa, state, node = self.stack[-1]
        newnode = (type,
         value,
         context,
         None)
        newnode = self.convert(self.grammar, newnode)
        if newnode is not None:
            node[-1].append(newnode)
        self.stack[-1] = (dfa, newstate, node)
        return

    def push(self, type, newdfa, newstate, context):
        dfa, state, node = self.stack[-1]
        newnode = (type,
         None,
         context,
         [])
        self.stack[-1] = (dfa, newstate, node)
        self.stack.append((newdfa, 0, newnode))
        return

    def pop(self):
        popdfa, popstate, popnode = self.stack.pop()
        newnode = self.convert(self.grammar, popnode)
        if newnode is not None:
            if self.stack:
                dfa, state, node = self.stack[-1]
                node[-1].append(newnode)
            else:
                self.rootnode = newnode
                self.rootnode.used_names = self.used_names
        return
