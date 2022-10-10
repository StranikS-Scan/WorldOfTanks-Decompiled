# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/io.py
__author__ = "Guido van Rossum <guido@python.org>, Mike Verdone <mike.verdone@gmail.com>, Mark Russell <mark.russell@zen.co.uk>, Antoine Pitrou <solipsis@pitrou.net>, Amaury Forgeot d'Arc <amauryfa@gmail.com>, Benjamin Peterson <benjamin@python.org>"
__all__ = ['BlockingIOError',
 'open',
 'IOBase',
 'RawIOBase',
 'FileIO',
 'BytesIO',
 'StringIO',
 'BufferedIOBase',
 'BufferedReader',
 'BufferedWriter',
 'BufferedRWPair',
 'BufferedRandom',
 'TextIOBase',
 'TextIOWrapper',
 'UnsupportedOperation',
 'SEEK_SET',
 'SEEK_CUR',
 'SEEK_END']
import _io
import abc
from _io import DEFAULT_BUFFER_SIZE, BlockingIOError, UnsupportedOperation, open, FileIO, BytesIO, StringIO, BufferedReader, BufferedWriter, BufferedRWPair, BufferedRandom, IncrementalNewlineDecoder, TextIOWrapper
OpenWrapper = _io.open
SEEK_SET = 0
SEEK_CUR = 1
SEEK_END = 2

class IOBase(_io._IOBase):
    __metaclass__ = abc.ABCMeta
    __doc__ = _io._IOBase.__doc__


class RawIOBase(_io._RawIOBase, IOBase):
    __doc__ = _io._RawIOBase.__doc__


class BufferedIOBase(_io._BufferedIOBase, IOBase):
    __doc__ = _io._BufferedIOBase.__doc__


class TextIOBase(_io._TextIOBase, IOBase):
    __doc__ = _io._TextIOBase.__doc__


RawIOBase.register(FileIO)
for klass in (BytesIO,
 BufferedReader,
 BufferedWriter,
 BufferedRandom,
 BufferedRWPair):
    BufferedIOBase.register(klass)

for klass in (StringIO, TextIOWrapper):
    TextIOBase.register(klass)

del klass
