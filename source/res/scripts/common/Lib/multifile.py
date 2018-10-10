# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/multifile.py
from warnings import warn
warn('the multifile module has been deprecated since Python 2.5', DeprecationWarning, stacklevel=2)
del warn
__all__ = ['MultiFile', 'Error']

class Error(Exception):
    pass


class MultiFile:
    seekable = 0

    def __init__(self, fp, seekable=1):
        self.fp = fp
        self.stack = []
        self.level = 0
        self.last = 0
        if seekable:
            self.seekable = 1
            self.start = self.fp.tell()
            self.posstack = []

    def tell(self):
        return self.lastpos if self.level > 0 else self.fp.tell() - self.start

    def seek(self, pos, whence=0):
        here = self.tell()
        if whence:
            if whence == 1:
                pos = pos + here
            elif whence == 2:
                if self.level > 0:
                    pos = pos + self.lastpos
                else:
                    raise Error, "can't use whence=2 yet"
        if not 0 <= pos <= here or self.level > 0 and pos > self.lastpos:
            raise Error, 'bad MultiFile.seek() call'
        self.fp.seek(pos + self.start)
        self.level = 0
        self.last = 0

    def readline(self):
        if self.level > 0:
            return ''
        line = self.fp.readline()
        if not line:
            self.level = len(self.stack)
            self.last = self.level > 0
            if self.last:
                raise Error, 'sudden EOF in MultiFile.readline()'
            return ''
        if self.is_data(line):
            return line
        marker = line.rstrip()
        for i, sep in enumerate(reversed(self.stack)):
            if marker == self.section_divider(sep):
                self.last = 0
                break
            if marker == self.end_marker(sep):
                self.last = 1
                break
        else:
            return line

        if self.seekable:
            self.lastpos = self.tell() - len(line)
        self.level = i + 1
        if self.level > 1:
            raise Error, 'Missing endmarker in MultiFile.readline()'

    def readlines(self):
        list = []
        while 1:
            line = self.readline()
            if not line:
                break
            list.append(line)

        return list

    def read(self):
        return ''.join(self.readlines())

    def next(self):
        while self.readline():
            pass

        if self.level > 1 or self.last:
            return 0
        self.level = 0
        self.last = 0
        if self.seekable:
            self.start = self.fp.tell()

    def push(self, sep):
        if self.level > 0:
            raise Error, 'bad MultiFile.push() call'
        self.stack.append(sep)
        if self.seekable:
            self.posstack.append(self.start)
            self.start = self.fp.tell()

    def pop(self):
        if self.stack == []:
            raise Error, 'bad MultiFile.pop() call'
        if self.level <= 1:
            self.last = 0
        else:
            abslastpos = self.lastpos + self.start
        self.level = max(0, self.level - 1)
        self.stack.pop()
        if self.seekable:
            self.start = self.posstack.pop()
            if self.level > 0:
                self.lastpos = abslastpos - self.start

    def is_data(self, line):
        return line[:2] != '--'

    def section_divider(self, str):
        return '--' + str

    def end_marker(self, str):
        return '--' + str + '--'
