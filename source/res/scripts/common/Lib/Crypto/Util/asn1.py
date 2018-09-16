# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/Crypto/Util/asn1.py
from __future__ import nested_scopes
import sys
if sys.version_info[0] == 2 and sys.version_info[1] == 1:
    from Crypto.Util.py21compat import *
from Crypto.Util.py3compat import *
if sys.version_info[0] == 2 and sys.version_info[1] == 1:
    from Crypto.Util.py21compat import *
from Crypto.Util.number import long_to_bytes, bytes_to_long
__all__ = ['DerObject',
 'DerInteger',
 'DerOctetString',
 'DerNull',
 'DerSequence',
 'DerObjectId',
 'DerBitString',
 'DerSetOf',
 'newDerInteger',
 'newDerOctetString',
 'newDerSequence',
 'newDerObjectId',
 'newDerBitString',
 'newDerSetOf']

def _isInt(x, onlyNonNegative=False):
    test = 0
    try:
        test += x
    except TypeError:
        return False

    return not onlyNonNegative or x >= 0


class BytesIO_EOF(BytesIO):

    def __init__(self, *params):
        BytesIO.__init__(self, *params)
        self.setRecord(False)

    def setRecord(self, record):
        self._record = record
        self._recording = b('')

    def read(self, length):
        s = BytesIO.read(self, length)
        if len(s) < length:
            raise EOFError
        if self._record:
            self._recording += s
        return s

    def read_byte(self):
        return self.read(1)[0]


class _NoDerElementError(EOFError):
    pass


class DerObject(object):

    def __init__(self, asn1Id=None, payload=b(''), implicit=None, constructed=False):
        if asn1Id == None:
            self._idOctet = None
            return
        else:
            asn1Id = self._convertTag(asn1Id)
            self._implicit = implicit
            if implicit:
                self._idOctet = 128 | self._convertTag(implicit)
            else:
                self._idOctet = asn1Id
            if constructed:
                self._idOctet |= 32
            self.payload = payload
            return

    def _convertTag(self, tag):
        if not _isInt(tag):
            if len(tag) == 1:
                tag = bord(tag[0])
        if not (_isInt(tag) and 0 <= tag < 31):
            raise ValueError('Wrong DER tag')
        return tag

    def _lengthOctets(self):
        payloadLen = len(self.payload)
        if payloadLen > 127:
            encoding = long_to_bytes(payloadLen)
            return bchr(len(encoding) + 128) + encoding
        return bchr(payloadLen)

    def encode(self):
        return bchr(self._idOctet) + self._lengthOctets() + self.payload

    def _decodeLen(self, s):
        length = bord(s.read_byte())
        if length <= 127:
            return length
        payloadLength = bytes_to_long(s.read(length & 127))
        if payloadLength <= 127:
            raise ValueError('Not a DER length tag (but still valid BER).')
        return payloadLength

    def decode(self, derEle):
        s = BytesIO_EOF(derEle)
        self._decodeFromStream(s)
        try:
            b = s.read_byte()
            raise ValueError('Unexpected extra data after the DER structure')
        except EOFError:
            pass

    def _decodeFromStream(self, s):
        try:
            idOctet = bord(s.read_byte())
        except EOFError:
            raise _NoDerElementError

        if self._idOctet != None:
            if idOctet != self._idOctet:
                raise ValueError('Unexpected DER tag')
        else:
            self._idOctet = idOctet
        length = self._decodeLen(s)
        self.payload = s.read(length)
        return


class DerInteger(DerObject):

    def __init__(self, value=0, implicit=None):
        DerObject.__init__(self, 2, b(''), implicit, False)
        self.value = value

    def encode(self):
        number = self.value
        self.payload = b('')
        while True:
            self.payload = bchr(number & 255) + self.payload
            if 128 <= number <= 255:
                self.payload = bchr(0) + self.payload
            if -128 <= number <= 255:
                break
            number >>= 8

        return DerObject.encode(self)

    def decode(self, derEle):
        DerObject.decode(self, derEle)

    def _decodeFromStream(self, s):
        DerObject._decodeFromStream(self, s)
        self.value = 0L
        bits = 1
        for i in self.payload:
            self.value *= 256
            self.value += bord(i)
            bits <<= 8

        if self.payload and bord(self.payload[0]) & 128:
            self.value -= bits


def newDerInteger(number):
    der = DerInteger(number)
    return der


class DerSequence(DerObject):

    def __init__(self, startSeq=None, implicit=None):
        DerObject.__init__(self, 16, b(''), implicit, True)
        if startSeq == None:
            self._seq = []
        else:
            self._seq = startSeq
        return

    def __delitem__(self, n):
        del self._seq[n]

    def __getitem__(self, n):
        return self._seq[n]

    def __setitem__(self, key, value):
        self._seq[key] = value

    def __setslice__(self, i, j, sequence):
        self._seq[i:j] = sequence

    def __delslice__(self, i, j):
        del self._seq[i:j]

    def __getslice__(self, i, j):
        return self._seq[max(0, i):max(0, j)]

    def __len__(self):
        return len(self._seq)

    def __iadd__(self, item):
        self._seq.append(item)
        return self

    def append(self, item):
        self._seq.append(item)
        return self

    def hasInts(self, onlyNonNegative=True):

        def _isInt2(x):
            return _isInt(x, onlyNonNegative)

        return len(filter(_isInt2, self._seq))

    def hasOnlyInts(self, onlyNonNegative=True):
        return self._seq and self.hasInts(onlyNonNegative) == len(self._seq)

    def encode(self):
        self.payload = b('')
        for item in self._seq:
            try:
                self.payload += item
            except TypeError:
                try:
                    self.payload += DerInteger(item).encode()
                except TypeError:
                    raise ValueError('Trying to DER encode an unknown object')

        return DerObject.encode(self)

    def decode(self, derEle):
        DerObject.decode(self, derEle)

    def _decodeFromStream(self, s):
        self._seq = []
        DerObject._decodeFromStream(self, s)
        p = BytesIO_EOF(self.payload)
        while True:
            try:
                p.setRecord(True)
                der = DerObject()
                der._decodeFromStream(p)
                if der._idOctet != 2:
                    self._seq.append(p._recording)
                else:
                    derInt = DerInteger()
                    derInt.decode(p._recording)
                    self._seq.append(derInt.value)
            except _NoDerElementError:
                break


def newDerSequence(*der_objs):
    der = DerSequence()
    for obj in der_objs:
        if isinstance(obj, DerObject):
            der += obj.encode()
        der += obj

    return der


class DerOctetString(DerObject):

    def __init__(self, value=b(''), implicit=None):
        DerObject.__init__(self, 4, value, implicit, False)


def newDerOctetString(binstring):
    if isinstance(binstring, DerObject):
        der = DerOctetString(binstring.encode())
    else:
        der = DerOctetString(binstring)
    return der


class DerNull(DerObject):

    def __init__(self):
        DerObject.__init__(self, 5, b(''), False)


class DerObjectId(DerObject):

    def __init__(self, value='', implicit=None):
        DerObject.__init__(self, 6, b(''), implicit, False)
        self.value = value

    def encode(self):
        comps = map(int, self.value.split('.'))
        if len(comps) < 2:
            raise ValueError('Not a valid Object Identifier string')
        self.payload = bchr(40 * comps[0] + comps[1])
        for v in comps[2:]:
            enc = []
            while v:
                enc.insert(0, v & 127 | 128)
                v >>= 7

            enc[-1] &= 127
            self.payload += b('').join(map(bchr, enc))

        return DerObject.encode(self)

    def decode(self, derEle):
        DerObject.decode(self, derEle)

    def _decodeFromStream(self, s):
        DerObject._decodeFromStream(self, s)
        p = BytesIO_EOF(self.payload)
        comps = list(map(str, divmod(bord(p.read_byte()), 40)))
        v = 0
        try:
            while True:
                c = p.read_byte()
                v = v * 128 + (bord(c) & 127)
                if not bord(c) & 128:
                    comps.append(str(v))
                    v = 0

        except EOFError:
            pass

        self.value = '.'.join(comps)


def newDerObjectId(dottedstring):
    der = DerObjectId(dottedstring)
    return der


class DerBitString(DerObject):

    def __init__(self, value=b(''), implicit=None):
        DerObject.__init__(self, 3, b(''), implicit, False)
        self.value = value

    def encode(self):
        self.payload = b('\x00') + self.value
        return DerObject.encode(self)

    def decode(self, derEle):
        DerObject.decode(self, derEle)

    def _decodeFromStream(self, s):
        DerObject._decodeFromStream(self, s)
        if self.payload and bord(self.payload[0]) != 0:
            raise ValueError('Not a valid BIT STRING')
        self.value = b('')
        if self.payload:
            self.value = self.payload[1:]


def newDerBitString(binstring):
    if isinstance(binstring, DerObject):
        der = DerBitString(binstring.encode())
    else:
        der = DerBitString(binstring)
    return der


class DerSetOf(DerObject):

    def __init__(self, startSet=None, implicit=None):
        DerObject.__init__(self, 17, b(''), implicit, True)
        self._seq = []
        self._elemOctet = None
        if startSet:
            for e in startSet:
                self.add(e)

        return

    def __getitem__(self, n):
        return self._seq[n]

    def __iter__(self):
        return iter(self._seq)

    def __len__(self):
        return len(self._seq)

    def add(self, elem):
        if _isInt(elem):
            eo = 2
        else:
            eo = bord(elem[0])
        if self._elemOctet != eo:
            if self._elemOctet:
                raise ValueError('New element does not belong to the set')
            self._elemOctet = eo
        if elem not in self._seq:
            self._seq.append(elem)

    def decode(self, derEle):
        DerObject.decode(self, derEle)

    def _decodeFromStream(self, s):
        self._seq = []
        DerObject._decodeFromStream(self, s)
        p = BytesIO_EOF(self.payload)
        setIdOctet = -1
        while True:
            try:
                p.setRecord(True)
                der = DerObject()
                der._decodeFromStream(p)
                if setIdOctet < 0:
                    setIdOctet = der._idOctet
                elif setIdOctet != der._idOctet:
                    raise ValueError('Not all elements are of the same DER type')
                if setIdOctet != 2:
                    self._seq.append(p._recording)
                else:
                    derInt = DerInteger()
                    derInt.decode(p._recording)
                    self._seq.append(derInt.value)
            except _NoDerElementError:
                break

    def encode(self):
        ordered = []
        for item in self._seq:
            if _isInt(item):
                bys = DerInteger(item).encode()
            else:
                bys = item
            ordered.append(bys)

        ordered.sort()
        self.payload = b('').join(ordered)
        return DerObject.encode(self)


def newDerSetOf(*der_objs):
    der = DerSetOf()
    for obj in der_objs:
        if isinstance(obj, DerObject):
            der.add(obj.encode())
        der.add(obj)

    return der
