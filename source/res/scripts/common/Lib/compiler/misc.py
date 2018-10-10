# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/compiler/misc.py


def flatten(tup):
    elts = []
    for elt in tup:
        if isinstance(elt, tuple):
            elts = elts + flatten(elt)
        elts.append(elt)

    return elts


class Set:

    def __init__(self):
        self.elts = {}

    def __len__(self):
        return len(self.elts)

    def __contains__(self, elt):
        return elt in self.elts

    def add(self, elt):
        self.elts[elt] = elt

    def elements(self):
        return self.elts.keys()

    def has_elt(self, elt):
        return elt in self.elts

    def remove(self, elt):
        del self.elts[elt]

    def copy(self):
        c = Set()
        c.elts.update(self.elts)
        return c


class Stack:

    def __init__(self):
        self.stack = []
        self.pop = self.stack.pop

    def __len__(self):
        return len(self.stack)

    def push(self, elt):
        self.stack.append(elt)

    def top(self):
        return self.stack[-1]

    def __getitem__(self, index):
        return self.stack[index]


MANGLE_LEN = 256

def mangle(name, klass):
    if not name.startswith('__'):
        return name
    if len(name) + 2 >= MANGLE_LEN:
        return name
    if name.endswith('__'):
        return name
    try:
        i = 0
        while klass[i] == '_':
            i = i + 1

    except IndexError:
        return name

    klass = klass[i:]
    tlen = len(klass) + len(name)
    if tlen > MANGLE_LEN:
        klass = klass[:MANGLE_LEN - tlen]
    return '_%s%s' % (klass, name)


def set_filename(filename, tree):
    worklist = [tree]
    while worklist:
        node = worklist.pop(0)
        node.filename = filename
        worklist.extend(node.getChildNodes())
