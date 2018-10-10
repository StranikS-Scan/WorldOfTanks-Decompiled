# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/lib2to3/pgen2/conv.py
import re
from pgen2 import grammar, token

class Converter(grammar.Grammar):

    def run(self, graminit_h, graminit_c):
        self.parse_graminit_h(graminit_h)
        self.parse_graminit_c(graminit_c)
        self.finish_off()

    def parse_graminit_h(self, filename):
        try:
            f = open(filename)
        except IOError as err:
            print "Can't open %s: %s" % (filename, err)
            return False

        self.symbol2number = {}
        self.number2symbol = {}
        lineno = 0
        for line in f:
            lineno += 1
            mo = re.match('^#define\\s+(\\w+)\\s+(\\d+)$', line)
            if not mo and line.strip():
                print "%s(%s): can't parse %s" % (filename, lineno, line.strip())
            symbol, number = mo.groups()
            number = int(number)
            self.symbol2number[symbol] = number
            self.number2symbol[number] = symbol

        return True

    def parse_graminit_c(self, filename):
        try:
            f = open(filename)
        except IOError as err:
            print "Can't open %s: %s" % (filename, err)
            return False

        lineno = 0
        lineno, line = lineno + 1, f.next()
        lineno, line = lineno + 1, f.next()
        lineno, line = lineno + 1, f.next()
        allarcs = {}
        states = []
        while line.startswith('static arc '):
            while line.startswith('static arc '):
                mo = re.match('static arc arcs_(\\d+)_(\\d+)\\[(\\d+)\\] = {$', line)
                n, m, k = map(int, mo.groups())
                arcs = []
                for _ in range(k):
                    lineno, line = lineno + 1, f.next()
                    mo = re.match('\\s+{(\\d+), (\\d+)},$', line)
                    i, j = map(int, mo.groups())
                    arcs.append((i, j))

                lineno, line = lineno + 1, f.next()
                allarcs[n, m] = arcs
                lineno, line = lineno + 1, f.next()

            mo = re.match('static state states_(\\d+)\\[(\\d+)\\] = {$', line)
            s, t = map(int, mo.groups())
            state = []
            for _ in range(t):
                lineno, line = lineno + 1, f.next()
                mo = re.match('\\s+{(\\d+), arcs_(\\d+)_(\\d+)},$', line)
                k, n, m = map(int, mo.groups())
                arcs = allarcs[n, m]
                state.append(arcs)

            states.append(state)
            lineno, line = lineno + 1, f.next()
            lineno, line = lineno + 1, f.next()

        self.states = states
        dfas = {}
        mo = re.match('static dfa dfas\\[(\\d+)\\] = {$', line)
        ndfas = int(mo.group(1))
        for i in range(ndfas):
            lineno, line = lineno + 1, f.next()
            mo = re.match('\\s+{(\\d+), "(\\w+)", (\\d+), (\\d+), states_(\\d+),$', line)
            symbol = mo.group(2)
            number, x, y, z = map(int, mo.group(1, 3, 4, 5))
            state = states[z]
            lineno, line = lineno + 1, f.next()
            mo = re.match('\\s+("(?:\\\\\\d\\d\\d)*")},$', line)
            first = {}
            rawbitset = eval(mo.group(1))
            for i, c in enumerate(rawbitset):
                byte = ord(c)
                for j in range(8):
                    if byte & 1 << j:
                        first[i * 8 + j] = 1

            dfas[number] = (state, first)

        lineno, line = lineno + 1, f.next()
        self.dfas = dfas
        labels = []
        lineno, line = lineno + 1, f.next()
        mo = re.match('static label labels\\[(\\d+)\\] = {$', line)
        nlabels = int(mo.group(1))
        for i in range(nlabels):
            lineno, line = lineno + 1, f.next()
            mo = re.match('\\s+{(\\d+), (0|"\\w+")},$', line)
            x, y = mo.groups()
            x = int(x)
            if y == '0':
                y = None
            else:
                y = eval(y)
            labels.append((x, y))

        lineno, line = lineno + 1, f.next()
        self.labels = labels
        lineno, line = lineno + 1, f.next()
        lineno, line = lineno + 1, f.next()
        mo = re.match('\\s+(\\d+),$', line)
        ndfas = int(mo.group(1))
        lineno, line = lineno + 1, f.next()
        lineno, line = lineno + 1, f.next()
        mo = re.match('\\s+{(\\d+), labels},$', line)
        nlabels = int(mo.group(1))
        lineno, line = lineno + 1, f.next()
        mo = re.match('\\s+(\\d+)$', line)
        start = int(mo.group(1))
        self.start = start
        lineno, line = lineno + 1, f.next()
        try:
            lineno, line = lineno + 1, f.next()
        except StopIteration:
            pass

        return

    def finish_off(self):
        self.keywords = {}
        self.tokens = {}
        for ilabel, (type, value) in enumerate(self.labels):
            if type == token.NAME and value is not None:
                self.keywords[value] = ilabel
            if value is None:
                self.tokens[type] = ilabel

        return
