# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/varint.py
"""Varint encoder/decoder

varints are a common encoding for variable length integer data, used in
libraries such as sqlite, protobuf, v8, and more.

Here's a quick and dirty module to help avoid reimplementing the same thing
over and over again.
"""
from cStringIO import StringIO as BytesIO

def encode_zigzag64(n):
    return n << 1 ^ n >> 63


def decode_zigzag(n):
    return n >> 1 ^ -(n & 1)


def encode(number):
    """Pack `number` into varint bytes"""
    buf = BytesIO()
    while True:
        towrite = number & 127
        number >>= 7
        if number:
            buf.write(chr(towrite | 128))
        buf.write(chr(towrite))
        break

    return buf.getvalue()


def decode_stream(stream):
    """Read a varint from `stream`"""
    shift = 0
    result = 0
    while True:
        i = _read_one(stream)
        result |= (i & 127) << shift
        shift += 7
        if not i & 128:
            return result


def decode_bytes(buf):
    """Read a varint from from `buf` bytes"""
    return decode_stream(BytesIO(buf))


def _read_one(stream):
    """Read a byte from the file (as an integer)
    
    raises EOFError if the stream ends while reading bytes.
    """
    c = stream.read(1)
    if c == '':
        raise EOFError('Unexpected EOF while reading bytes')
    return ord(c)
