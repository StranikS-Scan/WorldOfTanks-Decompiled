# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/tarfile.py
__version__ = '$Revision: 85213 $'
version = '0.9.0'
__author__ = 'Lars Gust\xe4bel (lars@gustaebel.de)'
__date__ = '$Date$'
__cvsid__ = '$Id$'
__credits__ = 'Gustavo Niemeyer, Niels Gust\xe4bel, Richard Townsend.'
import sys
import os
import shutil
import stat
import errno
import time
import struct
import copy
import re
import operator
try:
    import grp, pwd
except ImportError:
    grp = pwd = None

__all__ = ['TarFile',
 'TarInfo',
 'is_tarfile',
 'TarError']
NUL = '\x00'
BLOCKSIZE = 512
RECORDSIZE = BLOCKSIZE * 20
GNU_MAGIC = 'ustar  \x00'
POSIX_MAGIC = 'ustar\x0000'
LENGTH_NAME = 100
LENGTH_LINK = 100
LENGTH_PREFIX = 155
REGTYPE = '0'
AREGTYPE = '\x00'
LNKTYPE = '1'
SYMTYPE = '2'
CHRTYPE = '3'
BLKTYPE = '4'
DIRTYPE = '5'
FIFOTYPE = '6'
CONTTYPE = '7'
GNUTYPE_LONGNAME = 'L'
GNUTYPE_LONGLINK = 'K'
GNUTYPE_SPARSE = 'S'
XHDTYPE = 'x'
XGLTYPE = 'g'
SOLARIS_XHDTYPE = 'X'
USTAR_FORMAT = 0
GNU_FORMAT = 1
PAX_FORMAT = 2
DEFAULT_FORMAT = GNU_FORMAT
SUPPORTED_TYPES = (REGTYPE,
 AREGTYPE,
 LNKTYPE,
 SYMTYPE,
 DIRTYPE,
 FIFOTYPE,
 CONTTYPE,
 CHRTYPE,
 BLKTYPE,
 GNUTYPE_LONGNAME,
 GNUTYPE_LONGLINK,
 GNUTYPE_SPARSE)
REGULAR_TYPES = (REGTYPE,
 AREGTYPE,
 CONTTYPE,
 GNUTYPE_SPARSE)
GNU_TYPES = (GNUTYPE_LONGNAME, GNUTYPE_LONGLINK, GNUTYPE_SPARSE)
PAX_FIELDS = ('path',
 'linkpath',
 'size',
 'mtime',
 'uid',
 'gid',
 'uname',
 'gname')
PAX_NUMBER_FIELDS = {'atime': float,
 'ctime': float,
 'mtime': float,
 'uid': int,
 'gid': int,
 'size': int}
S_IFLNK = 40960
S_IFREG = 32768
S_IFBLK = 24576
S_IFDIR = 16384
S_IFCHR = 8192
S_IFIFO = 4096
TSUID = 2048
TSGID = 1024
TSVTX = 512
TUREAD = 256
TUWRITE = 128
TUEXEC = 64
TGREAD = 32
TGWRITE = 16
TGEXEC = 8
TOREAD = 4
TOWRITE = 2
TOEXEC = 1
ENCODING = sys.getfilesystemencoding()
if ENCODING is None:
    ENCODING = sys.getdefaultencoding()

def stn(s, length):
    return s[:length] + (length - len(s)) * NUL


def nts(s):
    p = s.find('\x00')
    return s if p == -1 else s[:p]


def nti(s):
    if s[0] != chr(128):
        try:
            n = int(nts(s) or '0', 8)
        except ValueError:
            raise InvalidHeaderError('invalid header')

    else:
        n = 0L
        for i in xrange(len(s) - 1):
            n <<= 8
            n += ord(s[i + 1])

    return n


def itn(n, digits=8, format=DEFAULT_FORMAT):
    if 0 <= n < 8 ** (digits - 1):
        s = '%0*o' % (digits - 1, n) + NUL
    else:
        if format != GNU_FORMAT or n >= 256 ** (digits - 1):
            raise ValueError('overflow in number field')
        if n < 0:
            n = struct.unpack('L', struct.pack('l', n))[0]
        s = ''
        for i in xrange(digits - 1):
            s = chr(n & 255) + s
            n >>= 8

        s = chr(128) + s
    return s


def uts(s, encoding, errors):
    if errors == 'utf-8':
        try:
            return s.encode(encoding, 'strict')
        except UnicodeEncodeError:
            x = []
            for c in s:
                try:
                    x.append(c.encode(encoding, 'strict'))
                except UnicodeEncodeError:
                    x.append(c.encode('utf8'))

            return ''.join(x)

    else:
        return s.encode(encoding, errors)


def calc_chksums(buf):
    unsigned_chksum = 256 + sum(struct.unpack('148B', buf[:148]) + struct.unpack('356B', buf[156:512]))
    signed_chksum = 256 + sum(struct.unpack('148b', buf[:148]) + struct.unpack('356b', buf[156:512]))
    return (unsigned_chksum, signed_chksum)


def copyfileobj(src, dst, length=None):
    if length == 0:
        return
    elif length is None:
        shutil.copyfileobj(src, dst)
        return
    else:
        BUFSIZE = 16384
        blocks, remainder = divmod(length, BUFSIZE)
        for b in xrange(blocks):
            buf = src.read(BUFSIZE)
            if len(buf) < BUFSIZE:
                raise IOError('end of file reached')
            dst.write(buf)

        if remainder != 0:
            buf = src.read(remainder)
            if len(buf) < remainder:
                raise IOError('end of file reached')
            dst.write(buf)
        return


filemode_table = (((S_IFLNK, 'l'),
  (S_IFREG, '-'),
  (S_IFBLK, 'b'),
  (S_IFDIR, 'd'),
  (S_IFCHR, 'c'),
  (S_IFIFO, 'p')),
 ((TUREAD, 'r'),),
 ((TUWRITE, 'w'),),
 ((TUEXEC | TSUID, 's'), (TSUID, 'S'), (TUEXEC, 'x')),
 ((TGREAD, 'r'),),
 ((TGWRITE, 'w'),),
 ((TGEXEC | TSGID, 's'), (TSGID, 'S'), (TGEXEC, 'x')),
 ((TOREAD, 'r'),),
 ((TOWRITE, 'w'),),
 ((TOEXEC | TSVTX, 't'), (TSVTX, 'T'), (TOEXEC, 'x')))

def filemode(mode):
    perm = []
    for table in filemode_table:
        for bit, char in table:
            if mode & bit == bit:
                perm.append(char)
                break
        else:
            perm.append('-')

    return ''.join(perm)


class TarError(Exception):
    pass


class ExtractError(TarError):
    pass


class ReadError(TarError):
    pass


class CompressionError(TarError):
    pass


class StreamError(TarError):
    pass


class HeaderError(TarError):
    pass


class EmptyHeaderError(HeaderError):
    pass


class TruncatedHeaderError(HeaderError):
    pass


class EOFHeaderError(HeaderError):
    pass


class InvalidHeaderError(HeaderError):
    pass


class SubsequentHeaderError(HeaderError):
    pass


class _LowLevelFile():

    def __init__(self, name, mode):
        mode = {'r': os.O_RDONLY,
         'w': os.O_WRONLY | os.O_CREAT | os.O_TRUNC}[mode]
        if hasattr(os, 'O_BINARY'):
            mode |= os.O_BINARY
        self.fd = os.open(name, mode, 438)

    def close(self):
        os.close(self.fd)

    def read(self, size):
        return os.read(self.fd, size)

    def write(self, s):
        os.write(self.fd, s)


class _Stream():

    def __init__(self, name, mode, comptype, fileobj, bufsize):
        self._extfileobj = True
        if fileobj is None:
            fileobj = _LowLevelFile(name, mode)
            self._extfileobj = False
        if comptype == '*':
            fileobj = _StreamProxy(fileobj)
            comptype = fileobj.getcomptype()
        self.name = name or ''
        self.mode = mode
        self.comptype = comptype
        self.fileobj = fileobj
        self.bufsize = bufsize
        self.buf = ''
        self.pos = 0L
        self.closed = False
        if comptype == 'gz':
            try:
                import zlib
            except ImportError:
                raise CompressionError('zlib module is not available')

            self.zlib = zlib
            self.crc = zlib.crc32('') & 4294967295L
            if mode == 'r':
                self._init_read_gz()
            else:
                self._init_write_gz()
        if comptype == 'bz2':
            try:
                import bz2
            except ImportError:
                raise CompressionError('bz2 module is not available')

            if mode == 'r':
                self.dbuf = ''
                self.cmp = bz2.BZ2Decompressor()
            else:
                self.cmp = bz2.BZ2Compressor()
        return

    def __del__(self):
        if hasattr(self, 'closed') and not self.closed:
            self.close()

    def _init_write_gz(self):
        self.cmp = self.zlib.compressobj(9, self.zlib.DEFLATED, -self.zlib.MAX_WBITS, self.zlib.DEF_MEM_LEVEL, 0)
        timestamp = struct.pack('<L', long(time.time()))
        self.__write('\x1f\x8b\x08\x08%s\x02\xff' % timestamp)
        if type(self.name) is unicode:
            self.name = self.name.encode('iso-8859-1', 'replace')
        if self.name.endswith('.gz'):
            self.name = self.name[:-3]
        self.__write(self.name + NUL)

    def write(self, s):
        if self.comptype == 'gz':
            self.crc = self.zlib.crc32(s, self.crc) & 4294967295L
        self.pos += len(s)
        if self.comptype != 'tar':
            s = self.cmp.compress(s)
        self.__write(s)

    def __write(self, s):
        self.buf += s
        while len(self.buf) > self.bufsize:
            self.fileobj.write(self.buf[:self.bufsize])
            self.buf = self.buf[self.bufsize:]

    def close(self):
        if self.closed:
            return
        if self.mode == 'w' and self.comptype != 'tar':
            self.buf += self.cmp.flush()
        if self.mode == 'w' and self.buf:
            self.fileobj.write(self.buf)
            self.buf = ''
            if self.comptype == 'gz':
                self.fileobj.write(struct.pack('<L', self.crc & 4294967295L))
                self.fileobj.write(struct.pack('<L', self.pos & 4294967295L))
        if not self._extfileobj:
            self.fileobj.close()
        self.closed = True

    def _init_read_gz(self):
        self.cmp = self.zlib.decompressobj(-self.zlib.MAX_WBITS)
        self.dbuf = ''
        if self.__read(2) != '\x1f\x8b':
            raise ReadError('not a gzip file')
        if self.__read(1) != '\x08':
            raise CompressionError('unsupported compression method')
        flag = ord(self.__read(1))
        self.__read(6)
        if flag & 4:
            xlen = ord(self.__read(1)) + 256 * ord(self.__read(1))
            self.read(xlen)
        if flag & 8:
            while True:
                s = self.__read(1)
                if not s or s == NUL:
                    break

        if flag & 16:
            while True:
                s = self.__read(1)
                if not s or s == NUL:
                    break

        if flag & 2:
            self.__read(2)

    def tell(self):
        return self.pos

    def seek(self, pos=0):
        if pos - self.pos >= 0:
            blocks, remainder = divmod(pos - self.pos, self.bufsize)
            for i in xrange(blocks):
                self.read(self.bufsize)

            self.read(remainder)
        else:
            raise StreamError('seeking backwards is not allowed')
        return self.pos

    def read(self, size=None):
        if size is None:
            t = []
            while True:
                buf = self._read(self.bufsize)
                if not buf:
                    break
                t.append(buf)

            buf = ''.join(t)
        else:
            buf = self._read(size)
        self.pos += len(buf)
        return buf

    def _read(self, size):
        if self.comptype == 'tar':
            return self.__read(size)
        c = len(self.dbuf)
        t = [self.dbuf]
        while c < size:
            buf = self.__read(self.bufsize)
            if not buf:
                break
            try:
                buf = self.cmp.decompress(buf)
            except IOError:
                raise ReadError('invalid compressed data')

            t.append(buf)
            c += len(buf)

        t = ''.join(t)
        self.dbuf = t[size:]
        return t[:size]

    def __read(self, size):
        c = len(self.buf)
        t = [self.buf]
        while c < size:
            buf = self.fileobj.read(self.bufsize)
            if not buf:
                break
            t.append(buf)
            c += len(buf)

        t = ''.join(t)
        self.buf = t[size:]
        return t[:size]


class _StreamProxy(object):

    def __init__(self, fileobj):
        self.fileobj = fileobj
        self.buf = self.fileobj.read(BLOCKSIZE)

    def read(self, size):
        self.read = self.fileobj.read
        return self.buf

    def getcomptype(self):
        if self.buf.startswith('\x1f\x8b\x08'):
            return 'gz'
        return 'bz2' if self.buf[0:3] == 'BZh' and self.buf[4:10] == '1AY&SY' else 'tar'

    def close(self):
        self.fileobj.close()


class _BZ2Proxy(object):
    blocksize = 16384

    def __init__(self, fileobj, mode):
        self.fileobj = fileobj
        self.mode = mode
        self.name = getattr(self.fileobj, 'name', None)
        self.init()
        return

    def init(self):
        import bz2
        self.pos = 0
        if self.mode == 'r':
            self.bz2obj = bz2.BZ2Decompressor()
            self.fileobj.seek(0)
            self.buf = ''
        else:
            self.bz2obj = bz2.BZ2Compressor()

    def read(self, size):
        b = [self.buf]
        x = len(self.buf)
        while x < size:
            raw = self.fileobj.read(self.blocksize)
            if not raw:
                break
            data = self.bz2obj.decompress(raw)
            b.append(data)
            x += len(data)

        self.buf = ''.join(b)
        buf = self.buf[:size]
        self.buf = self.buf[size:]
        self.pos += len(buf)
        return buf

    def seek(self, pos):
        if pos < self.pos:
            self.init()
        self.read(pos - self.pos)

    def tell(self):
        return self.pos

    def write(self, data):
        self.pos += len(data)
        raw = self.bz2obj.compress(data)
        self.fileobj.write(raw)

    def close(self):
        if self.mode == 'w':
            raw = self.bz2obj.flush()
            self.fileobj.write(raw)


class _FileInFile(object):

    def __init__(self, fileobj, offset, size, sparse=None):
        self.fileobj = fileobj
        self.offset = offset
        self.size = size
        self.sparse = sparse
        self.position = 0

    def tell(self):
        return self.position

    def seek(self, position):
        self.position = position

    def read(self, size=None):
        if size is None:
            size = self.size - self.position
        else:
            size = min(size, self.size - self.position)
        if self.sparse is None:
            return self.readnormal(size)
        else:
            return self.readsparse(size)
            return

    def readnormal(self, size):
        self.fileobj.seek(self.offset + self.position)
        self.position += size
        return self.fileobj.read(size)

    def readsparse(self, size):
        data = []
        while size > 0:
            buf = self.readsparsesection(size)
            if not buf:
                break
            size -= len(buf)
            data.append(buf)

        return ''.join(data)

    def readsparsesection(self, size):
        section = self.sparse.find(self.position)
        if section is None:
            return ''
        else:
            size = min(size, section.offset + section.size - self.position)
            if isinstance(section, _data):
                realpos = section.realpos + self.position - section.offset
                self.fileobj.seek(self.offset + realpos)
                self.position += size
                return self.fileobj.read(size)
            self.position += size
            return NUL * size
            return


class ExFileObject(object):
    blocksize = 1024

    def __init__(self, tarfile, tarinfo):
        self.fileobj = _FileInFile(tarfile.fileobj, tarinfo.offset_data, tarinfo.size, getattr(tarinfo, 'sparse', None))
        self.name = tarinfo.name
        self.mode = 'r'
        self.closed = False
        self.size = tarinfo.size
        self.position = 0
        self.buffer = ''
        return

    def read(self, size=None):
        if self.closed:
            raise ValueError('I/O operation on closed file')
        buf = ''
        if self.buffer:
            if size is None:
                buf = self.buffer
                self.buffer = ''
            else:
                buf = self.buffer[:size]
                self.buffer = self.buffer[size:]
        if size is None:
            buf += self.fileobj.read()
        else:
            buf += self.fileobj.read(size - len(buf))
        self.position += len(buf)
        return buf

    def readline(self, size=-1):
        if self.closed:
            raise ValueError('I/O operation on closed file')
        if '\n' in self.buffer:
            pos = self.buffer.find('\n') + 1
        else:
            buffers = [self.buffer]
            while True:
                buf = self.fileobj.read(self.blocksize)
                buffers.append(buf)
                if not buf or '\n' in buf:
                    self.buffer = ''.join(buffers)
                    pos = self.buffer.find('\n') + 1
                    if pos == 0:
                        pos = len(self.buffer)
                    break

        if size != -1:
            pos = min(size, pos)
        buf = self.buffer[:pos]
        self.buffer = self.buffer[pos:]
        self.position += len(buf)
        return buf

    def readlines(self):
        result = []
        while True:
            line = self.readline()
            if not line:
                break
            result.append(line)

        return result

    def tell(self):
        if self.closed:
            raise ValueError('I/O operation on closed file')
        return self.position

    def seek(self, pos, whence=os.SEEK_SET):
        if self.closed:
            raise ValueError('I/O operation on closed file')
        if whence == os.SEEK_SET:
            self.position = min(max(pos, 0), self.size)
        elif whence == os.SEEK_CUR:
            if pos < 0:
                self.position = max(self.position + pos, 0)
            else:
                self.position = min(self.position + pos, self.size)
        elif whence == os.SEEK_END:
            self.position = max(min(self.size + pos, self.size), 0)
        else:
            raise ValueError('Invalid argument')
        self.buffer = ''
        self.fileobj.seek(self.position)

    def close(self):
        self.closed = True

    def __iter__(self):
        while True:
            line = self.readline()
            if not line:
                break
            yield line


class TarInfo(object):

    def __init__(self, name=''):
        self.name = name
        self.mode = 420
        self.uid = 0
        self.gid = 0
        self.size = 0
        self.mtime = 0
        self.chksum = 0
        self.type = REGTYPE
        self.linkname = ''
        self.uname = ''
        self.gname = ''
        self.devmajor = 0
        self.devminor = 0
        self.offset = 0
        self.offset_data = 0
        self.pax_headers = {}

    def _getpath(self):
        return self.name

    def _setpath(self, name):
        self.name = name

    path = property(_getpath, _setpath)

    def _getlinkpath(self):
        return self.linkname

    def _setlinkpath(self, linkname):
        self.linkname = linkname

    linkpath = property(_getlinkpath, _setlinkpath)

    def __repr__(self):
        return '<%s %r at %#x>' % (self.__class__.__name__, self.name, id(self))

    def get_info(self, encoding, errors):
        info = {'name': self.name,
         'mode': self.mode & 4095,
         'uid': self.uid,
         'gid': self.gid,
         'size': self.size,
         'mtime': self.mtime,
         'chksum': self.chksum,
         'type': self.type,
         'linkname': self.linkname,
         'uname': self.uname,
         'gname': self.gname,
         'devmajor': self.devmajor,
         'devminor': self.devminor}
        if info['type'] == DIRTYPE and not info['name'].endswith('/'):
            info['name'] += '/'
        for key in ('name', 'linkname', 'uname', 'gname'):
            if type(info[key]) is unicode:
                info[key] = info[key].encode(encoding, errors)

        return info

    def tobuf(self, format=DEFAULT_FORMAT, encoding=ENCODING, errors='strict'):
        info = self.get_info(encoding, errors)
        if format == USTAR_FORMAT:
            return self.create_ustar_header(info)
        if format == GNU_FORMAT:
            return self.create_gnu_header(info)
        if format == PAX_FORMAT:
            return self.create_pax_header(info, encoding, errors)
        raise ValueError('invalid format')

    def create_ustar_header(self, info):
        info['magic'] = POSIX_MAGIC
        if len(info['linkname']) > LENGTH_LINK:
            raise ValueError('linkname is too long')
        if len(info['name']) > LENGTH_NAME:
            info['prefix'], info['name'] = self._posix_split_name(info['name'])
        return self._create_header(info, USTAR_FORMAT)

    def create_gnu_header(self, info):
        info['magic'] = GNU_MAGIC
        buf = ''
        if len(info['linkname']) > LENGTH_LINK:
            buf += self._create_gnu_long_header(info['linkname'], GNUTYPE_LONGLINK)
        if len(info['name']) > LENGTH_NAME:
            buf += self._create_gnu_long_header(info['name'], GNUTYPE_LONGNAME)
        return buf + self._create_header(info, GNU_FORMAT)

    def create_pax_header(self, info, encoding, errors):
        info['magic'] = POSIX_MAGIC
        pax_headers = self.pax_headers.copy()
        for name, hname, length in (('name', 'path', LENGTH_NAME),
         ('linkname', 'linkpath', LENGTH_LINK),
         ('uname', 'uname', 32),
         ('gname', 'gname', 32)):
            if hname in pax_headers:
                continue
            val = info[name].decode(encoding, errors)
            try:
                val.encode('ascii')
            except UnicodeEncodeError:
                pax_headers[hname] = val
                continue

            if len(info[name]) > length:
                pax_headers[hname] = val

        for name, digits in (('uid', 8),
         ('gid', 8),
         ('size', 12),
         ('mtime', 12)):
            if name in pax_headers:
                info[name] = 0
                continue
            val = info[name]
            if not 0 <= val < 8 ** (digits - 1) or isinstance(val, float):
                pax_headers[name] = unicode(val)
                info[name] = 0

        if pax_headers:
            buf = self._create_pax_generic_header(pax_headers)
        else:
            buf = ''
        return buf + self._create_header(info, USTAR_FORMAT)

    @classmethod
    def create_pax_global_header(cls, pax_headers):
        return cls._create_pax_generic_header(pax_headers, type=XGLTYPE)

    def _posix_split_name(self, name):
        prefix = name[:LENGTH_PREFIX + 1]
        while prefix and prefix[-1] != '/':
            prefix = prefix[:-1]

        name = name[len(prefix):]
        prefix = prefix[:-1]
        if not prefix or len(name) > LENGTH_NAME:
            raise ValueError('name is too long')
        return (prefix, name)

    @staticmethod
    def _create_header(info, format):
        parts = [stn(info.get('name', ''), 100),
         itn(info.get('mode', 0) & 4095, 8, format),
         itn(info.get('uid', 0), 8, format),
         itn(info.get('gid', 0), 8, format),
         itn(info.get('size', 0), 12, format),
         itn(info.get('mtime', 0), 12, format),
         '        ',
         info.get('type', REGTYPE),
         stn(info.get('linkname', ''), 100),
         stn(info.get('magic', POSIX_MAGIC), 8),
         stn(info.get('uname', ''), 32),
         stn(info.get('gname', ''), 32),
         itn(info.get('devmajor', 0), 8, format),
         itn(info.get('devminor', 0), 8, format),
         stn(info.get('prefix', ''), 155)]
        buf = struct.pack('%ds' % BLOCKSIZE, ''.join(parts))
        chksum = calc_chksums(buf[-BLOCKSIZE:])[0]
        buf = buf[:-364] + '%06o\x00' % chksum + buf[-357:]
        return buf

    @staticmethod
    def _create_payload(payload):
        blocks, remainder = divmod(len(payload), BLOCKSIZE)
        if remainder > 0:
            payload += (BLOCKSIZE - remainder) * NUL
        return payload

    @classmethod
    def _create_gnu_long_header(cls, name, type):
        name += NUL
        info = {}
        info['name'] = '././@LongLink'
        info['type'] = type
        info['size'] = len(name)
        info['magic'] = GNU_MAGIC
        return cls._create_header(info, USTAR_FORMAT) + cls._create_payload(name)

    @classmethod
    def _create_pax_generic_header(cls, pax_headers, type=XHDTYPE):
        records = []
        for keyword, value in pax_headers.iteritems():
            keyword = keyword.encode('utf8')
            value = value.encode('utf8')
            l = len(keyword) + len(value) + 3
            n = p = 0
            while True:
                n = l + len(str(p))
                if n == p:
                    break
                p = n

            records.append('%d %s=%s\n' % (p, keyword, value))

        records = ''.join(records)
        info = {}
        info['name'] = '././@PaxHeader'
        info['type'] = type
        info['size'] = len(records)
        info['magic'] = POSIX_MAGIC
        return cls._create_header(info, USTAR_FORMAT) + cls._create_payload(records)

    @classmethod
    def frombuf(cls, buf):
        if len(buf) == 0:
            raise EmptyHeaderError('empty header')
        if len(buf) != BLOCKSIZE:
            raise TruncatedHeaderError('truncated header')
        if buf.count(NUL) == BLOCKSIZE:
            raise EOFHeaderError('end of file header')
        chksum = nti(buf[148:156])
        if chksum not in calc_chksums(buf):
            raise InvalidHeaderError('bad checksum')
        obj = cls()
        obj.buf = buf
        obj.name = nts(buf[0:100])
        obj.mode = nti(buf[100:108])
        obj.uid = nti(buf[108:116])
        obj.gid = nti(buf[116:124])
        obj.size = nti(buf[124:136])
        obj.mtime = nti(buf[136:148])
        obj.chksum = chksum
        obj.type = buf[156:157]
        obj.linkname = nts(buf[157:257])
        obj.uname = nts(buf[265:297])
        obj.gname = nts(buf[297:329])
        obj.devmajor = nti(buf[329:337])
        obj.devminor = nti(buf[337:345])
        prefix = nts(buf[345:500])
        if obj.type == AREGTYPE and obj.name.endswith('/'):
            obj.type = DIRTYPE
        if obj.isdir():
            obj.name = obj.name.rstrip('/')
        if prefix and obj.type not in GNU_TYPES:
            obj.name = prefix + '/' + obj.name
        return obj

    @classmethod
    def fromtarfile(cls, tarfile):
        buf = tarfile.fileobj.read(BLOCKSIZE)
        obj = cls.frombuf(buf)
        obj.offset = tarfile.fileobj.tell() - BLOCKSIZE
        return obj._proc_member(tarfile)

    def _proc_member(self, tarfile):
        if self.type in (GNUTYPE_LONGNAME, GNUTYPE_LONGLINK):
            return self._proc_gnulong(tarfile)
        elif self.type == GNUTYPE_SPARSE:
            return self._proc_sparse(tarfile)
        elif self.type in (XHDTYPE, XGLTYPE, SOLARIS_XHDTYPE):
            return self._proc_pax(tarfile)
        else:
            return self._proc_builtin(tarfile)

    def _proc_builtin(self, tarfile):
        self.offset_data = tarfile.fileobj.tell()
        offset = self.offset_data
        if self.isreg() or self.type not in SUPPORTED_TYPES:
            offset += self._block(self.size)
        tarfile.offset = offset
        self._apply_pax_info(tarfile.pax_headers, tarfile.encoding, tarfile.errors)
        return self

    def _proc_gnulong(self, tarfile):
        buf = tarfile.fileobj.read(self._block(self.size))
        try:
            next = self.fromtarfile(tarfile)
        except HeaderError:
            raise SubsequentHeaderError('missing or bad subsequent header')

        next.offset = self.offset
        if self.type == GNUTYPE_LONGNAME:
            next.name = nts(buf)
        elif self.type == GNUTYPE_LONGLINK:
            next.linkname = nts(buf)
        return next

    def _proc_sparse(self, tarfile):
        buf = self.buf
        sp = _ringbuffer()
        pos = 386
        lastpos = 0L
        realpos = 0L
        for i in xrange(4):
            try:
                offset = nti(buf[pos:pos + 12])
                numbytes = nti(buf[pos + 12:pos + 24])
            except ValueError:
                break

            if offset > lastpos:
                sp.append(_hole(lastpos, offset - lastpos))
            sp.append(_data(offset, numbytes, realpos))
            realpos += numbytes
            lastpos = offset + numbytes
            pos += 24

        isextended = ord(buf[482])
        origsize = nti(buf[483:495])
        while isextended == 1:
            buf = tarfile.fileobj.read(BLOCKSIZE)
            pos = 0
            for i in xrange(21):
                try:
                    offset = nti(buf[pos:pos + 12])
                    numbytes = nti(buf[pos + 12:pos + 24])
                except ValueError:
                    break

                if offset > lastpos:
                    sp.append(_hole(lastpos, offset - lastpos))
                sp.append(_data(offset, numbytes, realpos))
                realpos += numbytes
                lastpos = offset + numbytes
                pos += 24

            isextended = ord(buf[504])

        if lastpos < origsize:
            sp.append(_hole(lastpos, origsize - lastpos))
        self.sparse = sp
        self.offset_data = tarfile.fileobj.tell()
        tarfile.offset = self.offset_data + self._block(self.size)
        self.size = origsize
        return self

    def _proc_pax(self, tarfile):
        buf = tarfile.fileobj.read(self._block(self.size))
        if self.type == XGLTYPE:
            pax_headers = tarfile.pax_headers
        else:
            pax_headers = tarfile.pax_headers.copy()
        regex = re.compile('(\\d+) ([^=]+)=', re.U)
        pos = 0
        while True:
            match = regex.match(buf, pos)
            if not match:
                break
            length, keyword = match.groups()
            length = int(length)
            value = buf[match.end(2) + 1:match.start(1) + length - 1]
            keyword = keyword.decode('utf8')
            value = value.decode('utf8')
            pax_headers[keyword] = value
            pos += length

        try:
            next = self.fromtarfile(tarfile)
        except HeaderError:
            raise SubsequentHeaderError('missing or bad subsequent header')

        if self.type in (XHDTYPE, SOLARIS_XHDTYPE):
            next._apply_pax_info(pax_headers, tarfile.encoding, tarfile.errors)
            next.offset = self.offset
            if 'size' in pax_headers:
                offset = next.offset_data
                if next.isreg() or next.type not in SUPPORTED_TYPES:
                    offset += next._block(next.size)
                tarfile.offset = offset
        return next

    def _apply_pax_info(self, pax_headers, encoding, errors):
        for keyword, value in pax_headers.iteritems():
            if keyword not in PAX_FIELDS:
                continue
            if keyword == 'path':
                value = value.rstrip('/')
            if keyword in PAX_NUMBER_FIELDS:
                try:
                    value = PAX_NUMBER_FIELDS[keyword](value)
                except ValueError:
                    value = 0

            else:
                value = uts(value, encoding, errors)
            setattr(self, keyword, value)

        self.pax_headers = pax_headers.copy()

    def _block(self, count):
        blocks, remainder = divmod(count, BLOCKSIZE)
        if remainder:
            blocks += 1
        return blocks * BLOCKSIZE

    def isreg(self):
        return self.type in REGULAR_TYPES

    def isfile(self):
        return self.isreg()

    def isdir(self):
        return self.type == DIRTYPE

    def issym(self):
        return self.type == SYMTYPE

    def islnk(self):
        return self.type == LNKTYPE

    def ischr(self):
        return self.type == CHRTYPE

    def isblk(self):
        return self.type == BLKTYPE

    def isfifo(self):
        return self.type == FIFOTYPE

    def issparse(self):
        return self.type == GNUTYPE_SPARSE

    def isdev(self):
        return self.type in (CHRTYPE, BLKTYPE, FIFOTYPE)


class TarFile(object):
    debug = 0
    dereference = False
    ignore_zeros = False
    errorlevel = 1
    format = DEFAULT_FORMAT
    encoding = ENCODING
    errors = None
    tarinfo = TarInfo
    fileobject = ExFileObject

    def __init__(self, name=None, mode='r', fileobj=None, format=None, tarinfo=None, dereference=None, ignore_zeros=None, encoding=None, errors=None, pax_headers=None, debug=None, errorlevel=None):
        modes = {'r': 'rb',
         'a': 'r+b',
         'w': 'wb'}
        if mode not in modes:
            raise ValueError("mode must be 'r', 'a' or 'w'")
        self.mode = mode
        self._mode = modes[mode]
        if not fileobj:
            if self.mode == 'a' and not os.path.exists(name):
                self.mode = 'w'
                self._mode = 'wb'
            fileobj = bltn_open(name, self._mode)
            self._extfileobj = False
        else:
            if name is None and hasattr(fileobj, 'name'):
                name = fileobj.name
            if hasattr(fileobj, 'mode'):
                self._mode = fileobj.mode
            self._extfileobj = True
        self.name = os.path.abspath(name) if name else None
        self.fileobj = fileobj
        if format is not None:
            self.format = format
        if tarinfo is not None:
            self.tarinfo = tarinfo
        if dereference is not None:
            self.dereference = dereference
        if ignore_zeros is not None:
            self.ignore_zeros = ignore_zeros
        if encoding is not None:
            self.encoding = encoding
        if errors is not None:
            self.errors = errors
        elif mode == 'r':
            self.errors = 'utf-8'
        else:
            self.errors = 'strict'
        if pax_headers is not None and self.format == PAX_FORMAT:
            self.pax_headers = pax_headers
        else:
            self.pax_headers = {}
        if debug is not None:
            self.debug = debug
        if errorlevel is not None:
            self.errorlevel = errorlevel
        self.closed = False
        self.members = []
        self._loaded = False
        self.offset = self.fileobj.tell()
        self.inodes = {}
        try:
            if self.mode == 'r':
                self.firstmember = None
                self.firstmember = self.next()
            if self.mode == 'a':
                while True:
                    self.fileobj.seek(self.offset)
                    try:
                        tarinfo = self.tarinfo.fromtarfile(self)
                        self.members.append(tarinfo)
                    except EOFHeaderError:
                        self.fileobj.seek(self.offset)
                        break
                    except HeaderError as e:
                        raise ReadError(str(e))

            if self.mode in 'aw':
                self._loaded = True
                if self.pax_headers:
                    buf = self.tarinfo.create_pax_global_header(self.pax_headers.copy())
                    self.fileobj.write(buf)
                    self.offset += len(buf)
        except:
            if not self._extfileobj:
                self.fileobj.close()
            self.closed = True
            raise

        return

    def _getposix(self):
        return self.format == USTAR_FORMAT

    def _setposix(self, value):
        import warnings
        warnings.warn('use the format attribute instead', DeprecationWarning, 2)
        if value:
            self.format = USTAR_FORMAT
        else:
            self.format = GNU_FORMAT

    posix = property(_getposix, _setposix)

    @classmethod
    def open(cls, name=None, mode='r', fileobj=None, bufsize=RECORDSIZE, **kwargs):
        if not name and not fileobj:
            raise ValueError('nothing to open')
        if mode in ('r', 'r:*'):
            for comptype in cls.OPEN_METH:
                func = getattr(cls, cls.OPEN_METH[comptype])
                if fileobj is not None:
                    saved_pos = fileobj.tell()
                try:
                    return func(name, 'r', fileobj, **kwargs)
                except (ReadError, CompressionError) as e:
                    if fileobj is not None:
                        fileobj.seek(saved_pos)
                    continue

            raise ReadError('file could not be opened successfully')
        else:
            if ':' in mode:
                filemode, comptype = mode.split(':', 1)
                filemode = filemode or 'r'
                comptype = comptype or 'tar'
                if comptype in cls.OPEN_METH:
                    func = getattr(cls, cls.OPEN_METH[comptype])
                else:
                    raise CompressionError('unknown compression type %r' % comptype)
                return func(name, filemode, fileobj, **kwargs)
            if '|' in mode:
                filemode, comptype = mode.split('|', 1)
                filemode = filemode or 'r'
                comptype = comptype or 'tar'
                if filemode not in ('r', 'w'):
                    raise ValueError("mode must be 'r' or 'w'")
                t = cls(name, filemode, _Stream(name, filemode, comptype, fileobj, bufsize), **kwargs)
                t._extfileobj = False
                return t
            if mode in ('a', 'w'):
                return cls.taropen(name, mode, fileobj, **kwargs)
        raise ValueError('undiscernible mode')
        return

    @classmethod
    def taropen(cls, name, mode='r', fileobj=None, **kwargs):
        if mode not in ('r', 'a', 'w'):
            raise ValueError("mode must be 'r', 'a' or 'w'")
        return cls(name, mode, fileobj, **kwargs)

    @classmethod
    def gzopen(cls, name, mode='r', fileobj=None, compresslevel=9, **kwargs):
        if mode not in ('r', 'w'):
            raise ValueError("mode must be 'r' or 'w'")
        try:
            import gzip
            gzip.GzipFile
        except (ImportError, AttributeError):
            raise CompressionError('gzip module is not available')

        if fileobj is None:
            fileobj = bltn_open(name, mode + 'b')
        try:
            t = cls.taropen(name, mode, gzip.GzipFile(name, mode, compresslevel, fileobj), **kwargs)
        except IOError:
            if mode == 'r':
                raise ReadError('not a gzip file')
            raise

        t._extfileobj = False
        return t

    @classmethod
    def bz2open(cls, name, mode='r', fileobj=None, compresslevel=9, **kwargs):
        if mode not in ('r', 'w'):
            raise ValueError("mode must be 'r' or 'w'.")
        try:
            import bz2
        except ImportError:
            raise CompressionError('bz2 module is not available')

        if fileobj is not None:
            fileobj = _BZ2Proxy(fileobj, mode)
        else:
            fileobj = bz2.BZ2File(name, mode, compresslevel=compresslevel)
        try:
            t = cls.taropen(name, mode, fileobj, **kwargs)
        except (IOError, EOFError):
            if mode == 'r':
                raise ReadError('not a bzip2 file')
            raise

        t._extfileobj = False
        return t

    OPEN_METH = {'tar': 'taropen',
     'gz': 'gzopen',
     'bz2': 'bz2open'}

    def close(self):
        if self.closed:
            return
        if self.mode in 'aw':
            self.fileobj.write(NUL * (BLOCKSIZE * 2))
            self.offset += BLOCKSIZE * 2
            blocks, remainder = divmod(self.offset, RECORDSIZE)
            if remainder > 0:
                self.fileobj.write(NUL * (RECORDSIZE - remainder))
        if not self._extfileobj:
            self.fileobj.close()
        self.closed = True

    def getmember(self, name):
        tarinfo = self._getmember(name)
        if tarinfo is None:
            raise KeyError('filename %r not found' % name)
        return tarinfo

    def getmembers(self):
        self._check()
        if not self._loaded:
            self._load()
        return self.members

    def getnames(self):
        return [ tarinfo.name for tarinfo in self.getmembers() ]

    def gettarinfo(self, name=None, arcname=None, fileobj=None):
        self._check('aw')
        if fileobj is not None:
            name = fileobj.name
        if arcname is None:
            arcname = name
        drv, arcname = os.path.splitdrive(arcname)
        arcname = arcname.replace(os.sep, '/')
        arcname = arcname.lstrip('/')
        tarinfo = self.tarinfo()
        tarinfo.tarfile = self
        if fileobj is None:
            if hasattr(os, 'lstat') and not self.dereference:
                statres = os.lstat(name)
            else:
                statres = os.stat(name)
        else:
            statres = os.fstat(fileobj.fileno())
        linkname = ''
        stmd = statres.st_mode
        if stat.S_ISREG(stmd):
            inode = (statres.st_ino, statres.st_dev)
            if not self.dereference and statres.st_nlink > 1 and inode in self.inodes and arcname != self.inodes[inode]:
                type = LNKTYPE
                linkname = self.inodes[inode]
            else:
                type = REGTYPE
                if inode[0]:
                    self.inodes[inode] = arcname
        elif stat.S_ISDIR(stmd):
            type = DIRTYPE
        elif stat.S_ISFIFO(stmd):
            type = FIFOTYPE
        elif stat.S_ISLNK(stmd):
            type = SYMTYPE
            linkname = os.readlink(name)
        elif stat.S_ISCHR(stmd):
            type = CHRTYPE
        elif stat.S_ISBLK(stmd):
            type = BLKTYPE
        else:
            return
        tarinfo.name = arcname
        tarinfo.mode = stmd
        tarinfo.uid = statres.st_uid
        tarinfo.gid = statres.st_gid
        if type == REGTYPE:
            tarinfo.size = statres.st_size
        else:
            tarinfo.size = 0L
        tarinfo.mtime = statres.st_mtime
        tarinfo.type = type
        tarinfo.linkname = linkname
        if pwd:
            try:
                tarinfo.uname = pwd.getpwuid(tarinfo.uid)[0]
            except KeyError:
                pass

        if grp:
            try:
                tarinfo.gname = grp.getgrgid(tarinfo.gid)[0]
            except KeyError:
                pass

        if type in (CHRTYPE, BLKTYPE):
            if hasattr(os, 'major') and hasattr(os, 'minor'):
                tarinfo.devmajor = os.major(statres.st_rdev)
                tarinfo.devminor = os.minor(statres.st_rdev)
        return tarinfo

    def list(self, verbose=True):
        self._check()
        for tarinfo in self:
            if verbose:
                print filemode(tarinfo.mode),
                print '%s/%s' % (tarinfo.uname or tarinfo.uid, tarinfo.gname or tarinfo.gid),
                if tarinfo.ischr() or tarinfo.isblk():
                    print '%10s' % ('%d,%d' % (tarinfo.devmajor, tarinfo.devminor)),
                else:
                    print '%10d' % tarinfo.size,
                print '%d-%02d-%02d %02d:%02d:%02d' % time.localtime(tarinfo.mtime)[:6],
            print tarinfo.name + ('/' if tarinfo.isdir() else ''),
            if verbose:
                if tarinfo.issym():
                    print '->', tarinfo.linkname,
                if tarinfo.islnk():
                    print 'link to', tarinfo.linkname,
            print

    def add(self, name, arcname=None, recursive=True, exclude=None, filter=None):
        self._check('aw')
        if arcname is None:
            arcname = name
        if exclude is not None:
            import warnings
            warnings.warn('use the filter argument instead', DeprecationWarning, 2)
            if exclude(name):
                self._dbg(2, 'tarfile: Excluded %r' % name)
                return
        if self.name is not None and os.path.abspath(name) == self.name:
            self._dbg(2, 'tarfile: Skipped %r' % name)
            return
        else:
            self._dbg(1, name)
            tarinfo = self.gettarinfo(name, arcname)
            if tarinfo is None:
                self._dbg(1, 'tarfile: Unsupported type %r' % name)
                return
            if filter is not None:
                tarinfo = filter(tarinfo)
                if tarinfo is None:
                    self._dbg(2, 'tarfile: Excluded %r' % name)
                    return
            if tarinfo.isreg():
                with bltn_open(name, 'rb') as f:
                    self.addfile(tarinfo, f)
            elif tarinfo.isdir():
                self.addfile(tarinfo)
                if recursive:
                    for f in os.listdir(name):
                        self.add(os.path.join(name, f), os.path.join(arcname, f), recursive, exclude, filter)

            else:
                self.addfile(tarinfo)
            return

    def addfile(self, tarinfo, fileobj=None):
        self._check('aw')
        tarinfo = copy.copy(tarinfo)
        buf = tarinfo.tobuf(self.format, self.encoding, self.errors)
        self.fileobj.write(buf)
        self.offset += len(buf)
        if fileobj is not None:
            copyfileobj(fileobj, self.fileobj, tarinfo.size)
            blocks, remainder = divmod(tarinfo.size, BLOCKSIZE)
            if remainder > 0:
                self.fileobj.write(NUL * (BLOCKSIZE - remainder))
                blocks += 1
            self.offset += blocks * BLOCKSIZE
        self.members.append(tarinfo)
        return

    def extractall(self, path='.', members=None):
        directories = []
        if members is None:
            members = self
        for tarinfo in members:
            if tarinfo.isdir():
                directories.append(tarinfo)
                tarinfo = copy.copy(tarinfo)
                tarinfo.mode = 448
            self.extract(tarinfo, path)

        directories.sort(key=operator.attrgetter('name'))
        directories.reverse()
        for tarinfo in directories:
            dirpath = os.path.join(path, tarinfo.name)
            try:
                self.chown(tarinfo, dirpath)
                self.utime(tarinfo, dirpath)
                self.chmod(tarinfo, dirpath)
            except ExtractError as e:
                if self.errorlevel > 1:
                    raise
                else:
                    self._dbg(1, 'tarfile: %s' % e)

        return

    def extract(self, member, path=''):
        self._check('r')
        if isinstance(member, basestring):
            tarinfo = self.getmember(member)
        else:
            tarinfo = member
        if tarinfo.islnk():
            tarinfo._link_target = os.path.join(path, tarinfo.linkname)
        try:
            self._extract_member(tarinfo, os.path.join(path, tarinfo.name))
        except EnvironmentError as e:
            if self.errorlevel > 0:
                raise
            elif e.filename is None:
                self._dbg(1, 'tarfile: %s' % e.strerror)
            else:
                self._dbg(1, 'tarfile: %s %r' % (e.strerror, e.filename))
        except ExtractError as e:
            if self.errorlevel > 1:
                raise
            else:
                self._dbg(1, 'tarfile: %s' % e)

        return

    def extractfile(self, member):
        self._check('r')
        if isinstance(member, basestring):
            tarinfo = self.getmember(member)
        else:
            tarinfo = member
        if tarinfo.isreg():
            return self.fileobject(self, tarinfo)
        elif tarinfo.type not in SUPPORTED_TYPES:
            return self.fileobject(self, tarinfo)
        else:
            if tarinfo.islnk() or tarinfo.issym():
                if isinstance(self.fileobj, _Stream):
                    raise StreamError('cannot extract (sym)link as file object')
                else:
                    return self.extractfile(self._find_link_target(tarinfo))
            else:
                return None
            return None

    def _extract_member(self, tarinfo, targetpath):
        targetpath = targetpath.rstrip('/')
        targetpath = targetpath.replace('/', os.sep)
        upperdirs = os.path.dirname(targetpath)
        if upperdirs and not os.path.exists(upperdirs):
            os.makedirs(upperdirs)
        if tarinfo.islnk() or tarinfo.issym():
            self._dbg(1, '%s -> %s' % (tarinfo.name, tarinfo.linkname))
        else:
            self._dbg(1, tarinfo.name)
        if tarinfo.isreg():
            self.makefile(tarinfo, targetpath)
        elif tarinfo.isdir():
            self.makedir(tarinfo, targetpath)
        elif tarinfo.isfifo():
            self.makefifo(tarinfo, targetpath)
        elif tarinfo.ischr() or tarinfo.isblk():
            self.makedev(tarinfo, targetpath)
        elif tarinfo.islnk() or tarinfo.issym():
            self.makelink(tarinfo, targetpath)
        elif tarinfo.type not in SUPPORTED_TYPES:
            self.makeunknown(tarinfo, targetpath)
        else:
            self.makefile(tarinfo, targetpath)
        self.chown(tarinfo, targetpath)
        if not tarinfo.issym():
            self.chmod(tarinfo, targetpath)
            self.utime(tarinfo, targetpath)

    def makedir(self, tarinfo, targetpath):
        try:
            os.mkdir(targetpath, 448)
        except EnvironmentError as e:
            if e.errno != errno.EEXIST:
                raise

    def makefile(self, tarinfo, targetpath):
        source = self.extractfile(tarinfo)
        try:
            with bltn_open(targetpath, 'wb') as target:
                copyfileobj(source, target)
        finally:
            source.close()

    def makeunknown(self, tarinfo, targetpath):
        self.makefile(tarinfo, targetpath)
        self._dbg(1, 'tarfile: Unknown file type %r, extracted as regular file.' % tarinfo.type)

    def makefifo(self, tarinfo, targetpath):
        if hasattr(os, 'mkfifo'):
            os.mkfifo(targetpath)
        else:
            raise ExtractError('fifo not supported by system')

    def makedev(self, tarinfo, targetpath):
        if not hasattr(os, 'mknod') or not hasattr(os, 'makedev'):
            raise ExtractError('special devices not supported by system')
        mode = tarinfo.mode
        if tarinfo.isblk():
            mode |= stat.S_IFBLK
        else:
            mode |= stat.S_IFCHR
        os.mknod(targetpath, mode, os.makedev(tarinfo.devmajor, tarinfo.devminor))

    def makelink(self, tarinfo, targetpath):
        if hasattr(os, 'symlink') and hasattr(os, 'link'):
            if tarinfo.issym():
                if os.path.lexists(targetpath):
                    os.unlink(targetpath)
                os.symlink(tarinfo.linkname, targetpath)
            elif os.path.exists(tarinfo._link_target):
                if os.path.lexists(targetpath):
                    os.unlink(targetpath)
                os.link(tarinfo._link_target, targetpath)
            else:
                self._extract_member(self._find_link_target(tarinfo), targetpath)
        else:
            try:
                self._extract_member(self._find_link_target(tarinfo), targetpath)
            except KeyError:
                raise ExtractError('unable to resolve link inside archive')

    def chown(self, tarinfo, targetpath):
        if pwd and hasattr(os, 'geteuid') and os.geteuid() == 0:
            try:
                g = grp.getgrnam(tarinfo.gname)[2]
            except KeyError:
                g = tarinfo.gid

            try:
                u = pwd.getpwnam(tarinfo.uname)[2]
            except KeyError:
                u = tarinfo.uid

            try:
                if tarinfo.issym() and hasattr(os, 'lchown'):
                    os.lchown(targetpath, u, g)
                elif sys.platform != 'os2emx':
                    os.chown(targetpath, u, g)
            except EnvironmentError as e:
                raise ExtractError('could not change owner')

    def chmod(self, tarinfo, targetpath):
        if hasattr(os, 'chmod'):
            try:
                os.chmod(targetpath, tarinfo.mode)
            except EnvironmentError as e:
                raise ExtractError('could not change mode')

    def utime(self, tarinfo, targetpath):
        if not hasattr(os, 'utime'):
            return
        try:
            os.utime(targetpath, (tarinfo.mtime, tarinfo.mtime))
        except EnvironmentError as e:
            raise ExtractError('could not change modification time')

    def next(self):
        self._check('ra')
        if self.firstmember is not None:
            m = self.firstmember
            self.firstmember = None
            return m
        else:
            self.fileobj.seek(self.offset)
            tarinfo = None
            while True:
                try:
                    tarinfo = self.tarinfo.fromtarfile(self)
                except EOFHeaderError as e:
                    if self.ignore_zeros:
                        self._dbg(2, '0x%X: %s' % (self.offset, e))
                        self.offset += BLOCKSIZE
                        continue
                except InvalidHeaderError as e:
                    if self.ignore_zeros:
                        self._dbg(2, '0x%X: %s' % (self.offset, e))
                        self.offset += BLOCKSIZE
                        continue
                    elif self.offset == 0:
                        raise ReadError(str(e))
                except EmptyHeaderError:
                    if self.offset == 0:
                        raise ReadError('empty file')
                except TruncatedHeaderError as e:
                    if self.offset == 0:
                        raise ReadError(str(e))
                except SubsequentHeaderError as e:
                    raise ReadError(str(e))

                break

            if tarinfo is not None:
                self.members.append(tarinfo)
            else:
                self._loaded = True
            return tarinfo

    def _getmember(self, name, tarinfo=None, normalize=False):
        members = self.getmembers()
        if tarinfo is not None:
            members = members[:members.index(tarinfo)]
        if normalize:
            name = os.path.normpath(name)
        for member in reversed(members):
            if normalize:
                member_name = os.path.normpath(member.name)
            else:
                member_name = member.name
            if name == member_name:
                return member

        return

    def _load(self):
        while True:
            tarinfo = self.next()
            if tarinfo is None:
                break

        self._loaded = True
        return

    def _check(self, mode=None):
        if self.closed:
            raise IOError('%s is closed' % self.__class__.__name__)
        if mode is not None and self.mode not in mode:
            raise IOError('bad operation for mode %r' % self.mode)
        return

    def _find_link_target(self, tarinfo):
        if tarinfo.issym():
            linkname = '/'.join(filter(None, (os.path.dirname(tarinfo.name), tarinfo.linkname)))
            limit = None
        else:
            linkname = tarinfo.linkname
            limit = tarinfo
        member = self._getmember(linkname, tarinfo=limit, normalize=True)
        if member is None:
            raise KeyError('linkname %r not found' % linkname)
        return member

    def __iter__(self):
        if self._loaded:
            return iter(self.members)
        else:
            return TarIter(self)

    def _dbg(self, level, msg):
        if level <= self.debug:
            print >> sys.stderr, msg

    def __enter__(self):
        self._check()
        return self

    def __exit__(self, type, value, traceback):
        if type is None:
            self.close()
        else:
            if not self._extfileobj:
                self.fileobj.close()
            self.closed = True
        return


class TarIter():

    def __init__(self, tarfile):
        self.tarfile = tarfile
        self.index = 0

    def __iter__(self):
        return self

    def next(self):
        if self.index == 0 and self.tarfile.firstmember is not None:
            tarinfo = self.tarfile.next()
        elif self.index < len(self.tarfile.members):
            tarinfo = self.tarfile.members[self.index]
        elif not self.tarfile._loaded:
            tarinfo = self.tarfile.next()
            if not tarinfo:
                self.tarfile._loaded = True
                raise StopIteration
        else:
            raise StopIteration
        self.index += 1
        return tarinfo


class _section():

    def __init__(self, offset, size):
        self.offset = offset
        self.size = size

    def __contains__(self, offset):
        return self.offset <= offset < self.offset + self.size


class _data(_section):

    def __init__(self, offset, size, realpos):
        _section.__init__(self, offset, size)
        self.realpos = realpos


class _hole(_section):
    pass


class _ringbuffer(list):

    def __init__(self):
        self.idx = 0

    def find(self, offset):
        idx = self.idx
        while True:
            item = self[idx]
            if offset in item:
                break
            idx += 1
            if idx == len(self):
                idx = 0
            if idx == self.idx:
                return None

        self.idx = idx
        return item


TAR_PLAIN = 0
TAR_GZIPPED = 8

class TarFileCompat():

    def __init__(self, file, mode='r', compression=TAR_PLAIN):
        from warnings import warnpy3k
        warnpy3k('the TarFileCompat class has been removed in Python 3.0', stacklevel=2)
        if compression == TAR_PLAIN:
            self.tarfile = TarFile.taropen(file, mode)
        elif compression == TAR_GZIPPED:
            self.tarfile = TarFile.gzopen(file, mode)
        else:
            raise ValueError('unknown compression constant')
        if mode[0:1] == 'r':
            members = self.tarfile.getmembers()
            for m in members:
                m.filename = m.name
                m.file_size = m.size
                m.date_time = time.gmtime(m.mtime)[:6]

    def namelist(self):
        return map(lambda m: m.name, self.infolist())

    def infolist(self):
        return filter(lambda m: m.type in REGULAR_TYPES, self.tarfile.getmembers())

    def printdir(self):
        self.tarfile.list()

    def testzip(self):
        pass

    def getinfo(self, name):
        return self.tarfile.getmember(name)

    def read(self, name):
        return self.tarfile.extractfile(self.tarfile.getmember(name)).read()

    def write(self, filename, arcname=None, compress_type=None):
        self.tarfile.add(filename, arcname)

    def writestr(self, zinfo, bytes):
        try:
            from cStringIO import StringIO
        except ImportError:
            from StringIO import StringIO

        import calendar
        tinfo = TarInfo(zinfo.filename)
        tinfo.size = len(bytes)
        tinfo.mtime = calendar.timegm(zinfo.date_time)
        self.tarfile.addfile(tinfo, StringIO(bytes))

    def close(self):
        self.tarfile.close()


def is_tarfile(name):
    try:
        t = open(name)
        t.close()
        return True
    except TarError:
        return False


bltn_open = open
open = TarFile.open
