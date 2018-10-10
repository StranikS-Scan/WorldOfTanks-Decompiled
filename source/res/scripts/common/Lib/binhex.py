# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/binhex.py
import sys
import os
import struct
import binascii
__all__ = ['binhex', 'hexbin', 'Error']

class Error(Exception):
    pass


_DID_HEADER, _DID_DATA, _DID_RSRC = range(3)
REASONABLY_LARGE = 32768
LINELEN = 64
RUNCHAR = chr(144)
try:
    from Carbon.File import FSSpec, FInfo
    from MacOS import openrf

    def getfileinfo(name):
        finfo = FSSpec(name).FSpGetFInfo()
        dir, file = os.path.split(name)
        fp = open(name, 'rb')
        fp.seek(0, 2)
        dlen = fp.tell()
        fp = openrf(name, '*rb')
        fp.seek(0, 2)
        rlen = fp.tell()
        return (file,
         finfo,
         dlen,
         rlen)


    def openrsrc(name, *mode):
        if not mode:
            mode = '*rb'
        else:
            mode = '*' + mode[0]
        return openrf(name, mode)


except ImportError:

    class FInfo:

        def __init__(self):
            self.Type = '????'
            self.Creator = '????'
            self.Flags = 0


    def getfileinfo(name):
        finfo = FInfo()
        fp = open(name)
        data = open(name).read(256)
        for c in data:
            if not c.isspace() and (c < ' ' or ord(c) > 127):
                break
        else:
            finfo.Type = 'TEXT'

        fp.seek(0, 2)
        dsize = fp.tell()
        fp.close()
        dir, file = os.path.split(name)
        file = file.replace(':', '-', 1)
        return (file,
         finfo,
         dsize,
         0)


    class openrsrc:

        def __init__(self, *args):
            pass

        def read(self, *args):
            pass

        def write(self, *args):
            pass

        def close(self):
            pass


class _Hqxcoderengine:

    def __init__(self, ofp):
        self.ofp = ofp
        self.data = ''
        self.hqxdata = ''
        self.linelen = LINELEN - 1

    def write(self, data):
        self.data = self.data + data
        datalen = len(self.data)
        todo = datalen // 3 * 3
        data = self.data[:todo]
        self.data = self.data[todo:]
        if not data:
            return
        self.hqxdata = self.hqxdata + binascii.b2a_hqx(data)
        self._flush(0)

    def _flush(self, force):
        first = 0
        while first <= len(self.hqxdata) - self.linelen:
            last = first + self.linelen
            self.ofp.write(self.hqxdata[first:last] + '\n')
            self.linelen = LINELEN
            first = last

        self.hqxdata = self.hqxdata[first:]
        if force:
            self.ofp.write(self.hqxdata + ':\n')

    def close(self):
        if self.data:
            self.hqxdata = self.hqxdata + binascii.b2a_hqx(self.data)
        self._flush(1)
        self.ofp.close()
        del self.ofp


class _Rlecoderengine:

    def __init__(self, ofp):
        self.ofp = ofp
        self.data = ''

    def write(self, data):
        self.data = self.data + data
        if len(self.data) < REASONABLY_LARGE:
            return
        rledata = binascii.rlecode_hqx(self.data)
        self.ofp.write(rledata)
        self.data = ''

    def close(self):
        if self.data:
            rledata = binascii.rlecode_hqx(self.data)
            self.ofp.write(rledata)
        self.ofp.close()
        del self.ofp


class BinHex:

    def __init__(self, name_finfo_dlen_rlen, ofp):
        name, finfo, dlen, rlen = name_finfo_dlen_rlen
        if type(ofp) == type(''):
            ofname = ofp
            ofp = open(ofname, 'w')
        ofp.write('(This file must be converted with BinHex 4.0)\n\n:')
        hqxer = _Hqxcoderengine(ofp)
        self.ofp = _Rlecoderengine(hqxer)
        self.crc = 0
        if finfo is None:
            finfo = FInfo()
        self.dlen = dlen
        self.rlen = rlen
        self._writeinfo(name, finfo)
        self.state = _DID_HEADER
        return

    def _writeinfo(self, name, finfo):
        nl = len(name)
        if nl > 63:
            raise Error, 'Filename too long'
        d = chr(nl) + name + '\x00'
        d2 = finfo.Type + finfo.Creator
        d3 = struct.pack('>h', finfo.Flags)
        d4 = struct.pack('>ii', self.dlen, self.rlen)
        info = d + d2 + d3 + d4
        self._write(info)
        self._writecrc()

    def _write(self, data):
        self.crc = binascii.crc_hqx(data, self.crc)
        self.ofp.write(data)

    def _writecrc(self):
        if self.crc < 0:
            fmt = '>h'
        else:
            fmt = '>H'
        self.ofp.write(struct.pack(fmt, self.crc))
        self.crc = 0

    def write(self, data):
        if self.state != _DID_HEADER:
            raise Error, 'Writing data at the wrong time'
        self.dlen = self.dlen - len(data)
        self._write(data)

    def close_data(self):
        if self.dlen != 0:
            raise Error, 'Incorrect data size, diff=%r' % (self.rlen,)
        self._writecrc()
        self.state = _DID_DATA

    def write_rsrc(self, data):
        if self.state < _DID_DATA:
            self.close_data()
        if self.state != _DID_DATA:
            raise Error, 'Writing resource data at the wrong time'
        self.rlen = self.rlen - len(data)
        self._write(data)

    def close(self):
        if self.state < _DID_DATA:
            self.close_data()
        if self.state != _DID_DATA:
            raise Error, 'Close at the wrong time'
        if self.rlen != 0:
            raise Error, 'Incorrect resource-datasize, diff=%r' % (self.rlen,)
        self._writecrc()
        self.ofp.close()
        self.state = None
        del self.ofp
        return


def binhex(inp, out):
    finfo = getfileinfo(inp)
    ofp = BinHex(finfo, out)
    ifp = open(inp, 'rb')
    while 1:
        d = ifp.read(128000)
        if not d:
            break
        ofp.write(d)

    ofp.close_data()
    ifp.close()
    ifp = openrsrc(inp, 'rb')
    while 1:
        d = ifp.read(128000)
        if not d:
            break
        ofp.write_rsrc(d)

    ofp.close()
    ifp.close()


class _Hqxdecoderengine:

    def __init__(self, ifp):
        self.ifp = ifp
        self.eof = 0

    def read(self, totalwtd):
        decdata = ''
        wtd = totalwtd
        while wtd > 0:
            if self.eof:
                return decdata
            wtd = (wtd + 2) // 3 * 4
            data = self.ifp.read(wtd)
            while 1:
                try:
                    decdatacur, self.eof = binascii.a2b_hqx(data)
                    break
                except binascii.Incomplete:
                    pass

                newdata = self.ifp.read(1)
                if not newdata:
                    raise Error, 'Premature EOF on binhex file'
                data = data + newdata

            decdata = decdata + decdatacur
            wtd = totalwtd - len(decdata)
            if not decdata and not self.eof:
                raise Error, 'Premature EOF on binhex file'

        return decdata

    def close(self):
        self.ifp.close()


class _Rledecoderengine:

    def __init__(self, ifp):
        self.ifp = ifp
        self.pre_buffer = ''
        self.post_buffer = ''
        self.eof = 0

    def read(self, wtd):
        if wtd > len(self.post_buffer):
            self._fill(wtd - len(self.post_buffer))
        rv = self.post_buffer[:wtd]
        self.post_buffer = self.post_buffer[wtd:]
        return rv

    def _fill(self, wtd):
        self.pre_buffer = self.pre_buffer + self.ifp.read(wtd + 4)
        if self.ifp.eof:
            self.post_buffer = self.post_buffer + binascii.rledecode_hqx(self.pre_buffer)
            self.pre_buffer = ''
            return
        mark = len(self.pre_buffer)
        if self.pre_buffer[-3:] == RUNCHAR + '\x00' + RUNCHAR:
            mark = mark - 3
        elif self.pre_buffer[-1] == RUNCHAR:
            mark = mark - 2
        elif self.pre_buffer[-2:] == RUNCHAR + '\x00':
            mark = mark - 2
        elif self.pre_buffer[-2] == RUNCHAR:
            pass
        else:
            mark = mark - 1
        self.post_buffer = self.post_buffer + binascii.rledecode_hqx(self.pre_buffer[:mark])
        self.pre_buffer = self.pre_buffer[mark:]

    def close(self):
        self.ifp.close()


class HexBin:

    def __init__(self, ifp):
        if type(ifp) == type(''):
            ifp = open(ifp)
        while 1:
            ch = ifp.read(1)
            if not ch:
                raise Error, 'No binhex data found'
            if ch == '\r':
                continue
            if ch == ':':
                break
            if ch != '\n':
                dummy = ifp.readline()

        hqxifp = _Hqxdecoderengine(ifp)
        self.ifp = _Rledecoderengine(hqxifp)
        self.crc = 0
        self._readheader()

    def _read(self, len):
        data = self.ifp.read(len)
        self.crc = binascii.crc_hqx(data, self.crc)
        return data

    def _checkcrc(self):
        filecrc = struct.unpack('>h', self.ifp.read(2))[0] & 65535
        self.crc = self.crc & 65535
        if filecrc != self.crc:
            raise Error, 'CRC error, computed %x, read %x' % (self.crc, filecrc)
        self.crc = 0

    def _readheader(self):
        len = self._read(1)
        fname = self._read(ord(len))
        rest = self._read(19)
        self._checkcrc()
        type = rest[1:5]
        creator = rest[5:9]
        flags = struct.unpack('>h', rest[9:11])[0]
        self.dlen = struct.unpack('>l', rest[11:15])[0]
        self.rlen = struct.unpack('>l', rest[15:19])[0]
        self.FName = fname
        self.FInfo = FInfo()
        self.FInfo.Creator = creator
        self.FInfo.Type = type
        self.FInfo.Flags = flags
        self.state = _DID_HEADER

    def read(self, *n):
        if self.state != _DID_HEADER:
            raise Error, 'Read data at wrong time'
        if n:
            n = n[0]
            n = min(n, self.dlen)
        else:
            n = self.dlen
        rv = ''
        while len(rv) < n:
            rv = rv + self._read(n - len(rv))

        self.dlen = self.dlen - n
        return rv

    def close_data(self):
        if self.state != _DID_HEADER:
            raise Error, 'close_data at wrong time'
        if self.dlen:
            dummy = self._read(self.dlen)
        self._checkcrc()
        self.state = _DID_DATA

    def read_rsrc(self, *n):
        if self.state == _DID_HEADER:
            self.close_data()
        if self.state != _DID_DATA:
            raise Error, 'Read resource data at wrong time'
        if n:
            n = n[0]
            n = min(n, self.rlen)
        else:
            n = self.rlen
        self.rlen = self.rlen - n
        return self._read(n)

    def close(self):
        if self.rlen:
            dummy = self.read_rsrc(self.rlen)
        self._checkcrc()
        self.state = _DID_RSRC
        self.ifp.close()


def hexbin(inp, out):
    ifp = HexBin(inp)
    finfo = ifp.FInfo
    if not out:
        out = ifp.FName
    ofp = open(out, 'wb')
    while 1:
        d = ifp.read(128000)
        if not d:
            break
        ofp.write(d)

    ofp.close()
    ifp.close_data()
    d = ifp.read_rsrc(128000)
    if d:
        ofp = openrsrc(out, 'wb')
        ofp.write(d)
        while 1:
            d = ifp.read_rsrc(128000)
            if not d:
                break
            ofp.write(d)

        ofp.close()
    ifp.close()


def _test():
    fname = sys.argv[1]
    binhex(fname, fname + '.hqx')
    hexbin(fname + '.hqx', fname + '.viahqx')
    sys.exit(1)


if __name__ == '__main__':
    _test()
