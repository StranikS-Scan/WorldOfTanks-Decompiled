# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/idlelib/SearchEngine.py
import re
from Tkinter import StringVar, BooleanVar, TclError
import tkMessageBox

def get(root):
    if not hasattr(root, '_searchengine'):
        root._searchengine = SearchEngine(root)
    return root._searchengine


class SearchEngine:

    def __init__(self, root):
        self.root = root
        self.patvar = StringVar(root, '')
        self.revar = BooleanVar(root, False)
        self.casevar = BooleanVar(root, False)
        self.wordvar = BooleanVar(root, False)
        self.wrapvar = BooleanVar(root, True)
        self.backvar = BooleanVar(root, False)

    def getpat(self):
        return self.patvar.get()

    def setpat(self, pat):
        self.patvar.set(pat)

    def isre(self):
        return self.revar.get()

    def iscase(self):
        return self.casevar.get()

    def isword(self):
        return self.wordvar.get()

    def iswrap(self):
        return self.wrapvar.get()

    def isback(self):
        return self.backvar.get()

    def setcookedpat(self, pat):
        if self.isre():
            pat = re.escape(pat)
        self.setpat(pat)

    def getcookedpat(self):
        pat = self.getpat()
        if not self.isre():
            pat = re.escape(pat)
        if self.isword():
            pat = '\\b%s\\b' % pat
        return pat

    def getprog(self):
        pat = self.getpat()
        if not pat:
            self.report_error(pat, 'Empty regular expression')
            return None
        else:
            pat = self.getcookedpat()
            flags = 0
            if not self.iscase():
                flags = flags | re.IGNORECASE
            try:
                prog = re.compile(pat, flags)
            except re.error as what:
                args = what.args
                msg = args[0]
                col = args[1] if len(args) >= 2 else -1
                self.report_error(pat, msg, col)
                return None

            return prog

    def report_error(self, pat, msg, col=-1):
        msg = 'Error: ' + str(msg)
        if pat:
            msg = msg + '\nPattern: ' + str(pat)
        if col >= 0:
            msg = msg + '\nOffset: ' + str(col)
        tkMessageBox.showerror('Regular expression error', msg, master=self.root)

    def search_text(self, text, prog=None, ok=0):
        if not prog:
            prog = self.getprog()
            if not prog:
                return None
        wrap = self.wrapvar.get()
        first, last = get_selection(text)
        if self.isback():
            if ok:
                start = last
            else:
                start = first
            line, col = get_line_col(start)
            res = self.search_backward(text, prog, line, col, wrap, ok)
        else:
            if ok:
                start = first
            else:
                start = last
            line, col = get_line_col(start)
            res = self.search_forward(text, prog, line, col, wrap, ok)
        return res

    def search_forward(self, text, prog, line, col, wrap, ok=0):
        wrapped = 0
        startline = line
        chars = text.get('%d.0' % line, '%d.0' % (line + 1))
        while chars:
            m = prog.search(chars[:-1], col)
            if m and (ok or m.end() > col):
                return (line, m)
            line = line + 1
            if wrapped and line > startline:
                break
            col = 0
            ok = 1
            chars = text.get('%d.0' % line, '%d.0' % (line + 1))
            if not chars and wrap:
                wrapped = 1
                wrap = 0
                line = 1
                chars = text.get('1.0', '2.0')

        return None

    def search_backward(self, text, prog, line, col, wrap, ok=0):
        wrapped = 0
        startline = line
        chars = text.get('%d.0' % line, '%d.0' % (line + 1))
        while 1:
            m = search_reverse(prog, chars[:-1], col)
            if m and (ok or m.start() < col):
                return (line, m)
            line = line - 1
            if wrapped and line < startline:
                break
            ok = 1
            if line <= 0:
                if not wrap:
                    break
                wrapped = 1
                wrap = 0
                pos = text.index('end-1c')
                line, col = map(int, pos.split('.'))
            chars = text.get('%d.0' % line, '%d.0' % (line + 1))
            col = len(chars) - 1

        return None


def search_reverse(prog, chars, col):
    m = prog.search(chars)
    if not m:
        return
    else:
        found = None
        i, j = m.span()
        while i < col and j <= col:
            found = m
            if i == j:
                j = j + 1
            m = prog.search(chars, j)
            if not m:
                break
            i, j = m.span()

        return found


def get_selection(text):
    try:
        first = text.index('sel.first')
        last = text.index('sel.last')
    except TclError:
        first = last = None

    if not first:
        first = text.index('insert')
    if not last:
        last = first
    return (first, last)


def get_line_col(index):
    line, col = map(int, index.split('.'))
    return (line, col)


if __name__ == '__main__':
    import unittest
    unittest.main('idlelib.idle_test.test_searchengine', verbosity=2, exit=False)
