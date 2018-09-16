# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/Crypto/Util/py3compat.py
__revision__ = '$Id$'
import sys
if sys.version_info[0] == 2:
    from types import UnicodeType as _UnicodeType

    def b(s):
        return s


    def bchr(s):
        return chr(s)


    def bstr(s):
        return str(s)


    def bord(s):
        return ord(s)


    def tobytes(s):
        if isinstance(s, _UnicodeType):
            return s.encode('latin-1')
        else:
            return ''.join(s)


    def tostr(bs):
        return unicode(bs, 'latin-1')


    from StringIO import StringIO as BytesIO
else:

    def b(s):
        return s.encode('latin-1')


    def bchr(s):
        return bytes([s])


    def bstr(s):
        if isinstance(s, str):
            return bytes(s, 'latin-1')
        else:
            return bytes(s)


    def bord(s):
        return s


    def tobytes(s):
        if isinstance(s, bytes):
            return s
        elif isinstance(s, str):
            return s.encode('latin-1')
        else:
            return bytes(s)


    def tostr(bs):
        return bs.decode('latin-1')


    from io import BytesIO
