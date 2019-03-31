# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/multifile.py
# Compiled at: 2010-05-25 20:46:16
"""A readline()-style interface to the parts of a multipart message.

The MultiFile class makes each part of a multipart message "feel" like
an ordinary file, as long as you use fp.readline().  Allows recursive
use, for nested multipart messages.  Probably best used together
with module mimetools.

Suggested use:

real_fp = open(...)
fp = MultiFile(real_fp)

"read some lines from fp"
fp.push(separator)
while 1:
        "read lines from fp until it returns an empty string" (A)
        if not fp.next(): break
fp.pop()
"read remaining lines from fp until it returns an empty string"

The latter sequence may be used recursively at (A).
It is also allowed to use multiple push()...pop() sequences.

If seekable is given as 0, the class code will not do the bookkeeping
it normally attempts in order to make seeks relative to the beginning of the
current file part.  This may be useful when using MultiFile with a non-
seekable stream object.
"""
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
        if self.level > 0:
            return self.lastpos
        return self.fp.tell() - self.start

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
        assert self.level == 0
        if self.is_data(line):
            return line
        marker = line.rstrip()
        for i, sep in enumerate(reversed(self.stack)):
            if marker == self.section_divider(sep):
                self.last = 0
                break
            elif marker == self.end_marker(sep):
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

    def next--- This code section failed: ---

 124       0	SETUP_LOOP        '19'
           3	LOAD_FAST         'self'
           6	LOAD_ATTR         'readline'
           9	CALL_FUNCTION_0   ''
          12	JUMP_IF_FALSE     '18'
          15	JUMP_BACK         '3'
          18	POP_BLOCK         ''
        19_0	COME_FROM         '0'

 125      19	LOAD_FAST         'self'
          22	LOAD_ATTR         'level'
          25	LOAD_CONST        1
          28	COMPARE_OP        '>'
          31	JUMP_IF_TRUE      '43'
          34	LOAD_FAST         'self'
          37	LOAD_ATTR         'last'
        40_0	COME_FROM         '31'
          40	JUMP_IF_FALSE     '47'

 126      43	LOAD_CONST        0
          46	RETURN_END_IF     ''

 127      47	LOAD_CONST        0
          50	LOAD_FAST         'self'
          53	STORE_ATTR        'level'

 128      56	LOAD_CONST        0
          59	LOAD_FAST         'self'
          62	STORE_ATTR        'last'

 129      65	LOAD_FAST         'self'
          68	LOAD_ATTR         'seekable'
          71	JUMP_IF_FALSE     '95'

 130      74	LOAD_FAST         'self'
          77	LOAD_ATTR         'fp'
          80	LOAD_ATTR         'tell'
          83	CALL_FUNCTION_0   ''
          86	LOAD_FAST         'self'
          89	STORE_ATTR        'start'
          92	JUMP_FORWARD      '95'
        95_0	COME_FROM         '92'

Syntax error at or near 'POP_BLOCK' token at offset 18

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