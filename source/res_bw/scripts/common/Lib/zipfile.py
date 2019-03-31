# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/zipfile.py
# Compiled at: 2010-05-25 20:46:16
"""
Read and write ZIP files.
"""
import struct, os, time, sys, shutil
import binascii, cStringIO, stat
try:
    import zlib
    crc32 = zlib.crc32
except ImportError:
    zlib = None
    crc32 = binascii.crc32

__all__ = ['BadZipfile',
 'error',
 'ZIP_STORED',
 'ZIP_DEFLATED',
 'is_zipfile',
 'ZipInfo',
 'ZipFile',
 'PyZipFile',
 'LargeZipFile']

class BadZipfile(Exception):
    pass


class LargeZipFile(Exception):
    """
    Raised when writing a zipfile, the zipfile requires ZIP64 extensions
    and those extensions are disabled.
    """
    pass


error = BadZipfile
ZIP64_LIMIT = (1 << 31) - 1
ZIP_FILECOUNT_LIMIT = 1 << 16
ZIP_MAX_COMMENT = (1 << 16) - 1
ZIP_STORED = 0
ZIP_DEFLATED = 8
structEndArchive = '<4s4H2LH'
stringEndArchive = 'PK\x05\x06'
sizeEndCentDir = struct.calcsize(structEndArchive)
_ECD_SIGNATURE = 0
_ECD_DISK_NUMBER = 1
_ECD_DISK_START = 2
_ECD_ENTRIES_THIS_DISK = 3
_ECD_ENTRIES_TOTAL = 4
_ECD_SIZE = 5
_ECD_OFFSET = 6
_ECD_COMMENT_SIZE = 7
_ECD_COMMENT = 8
_ECD_LOCATION = 9
structCentralDir = '<4s4B4HL2L5H2L'
stringCentralDir = 'PK\x01\x02'
sizeCentralDir = struct.calcsize(structCentralDir)
_CD_SIGNATURE = 0
_CD_CREATE_VERSION = 1
_CD_CREATE_SYSTEM = 2
_CD_EXTRACT_VERSION = 3
_CD_EXTRACT_SYSTEM = 4
_CD_FLAG_BITS = 5
_CD_COMPRESS_TYPE = 6
_CD_TIME = 7
_CD_DATE = 8
_CD_CRC = 9
_CD_COMPRESSED_SIZE = 10
_CD_UNCOMPRESSED_SIZE = 11
_CD_FILENAME_LENGTH = 12
_CD_EXTRA_FIELD_LENGTH = 13
_CD_COMMENT_LENGTH = 14
_CD_DISK_NUMBER_START = 15
_CD_INTERNAL_FILE_ATTRIBUTES = 16
_CD_EXTERNAL_FILE_ATTRIBUTES = 17
_CD_LOCAL_HEADER_OFFSET = 18
structFileHeader = '<4s2B4HL2L2H'
stringFileHeader = 'PK\x03\x04'
sizeFileHeader = struct.calcsize(structFileHeader)
_FH_SIGNATURE = 0
_FH_EXTRACT_VERSION = 1
_FH_EXTRACT_SYSTEM = 2
_FH_GENERAL_PURPOSE_FLAG_BITS = 3
_FH_COMPRESSION_METHOD = 4
_FH_LAST_MOD_TIME = 5
_FH_LAST_MOD_DATE = 6
_FH_CRC = 7
_FH_COMPRESSED_SIZE = 8
_FH_UNCOMPRESSED_SIZE = 9
_FH_FILENAME_LENGTH = 10
_FH_EXTRA_FIELD_LENGTH = 11
structEndArchive64Locator = '<4sLQL'
stringEndArchive64Locator = 'PK\x06\x07'
sizeEndCentDir64Locator = struct.calcsize(structEndArchive64Locator)
structEndArchive64 = '<4sQ2H2L4Q'
stringEndArchive64 = 'PK\x06\x06'
sizeEndCentDir64 = struct.calcsize(structEndArchive64)
_CD64_SIGNATURE = 0
_CD64_DIRECTORY_RECSIZE = 1
_CD64_CREATE_VERSION = 2
_CD64_EXTRACT_VERSION = 3
_CD64_DISK_NUMBER = 4
_CD64_DISK_NUMBER_START = 5
_CD64_NUMBER_ENTRIES_THIS_DISK = 6
_CD64_NUMBER_ENTRIES_TOTAL = 7
_CD64_DIRECTORY_SIZE = 8
_CD64_OFFSET_START_CENTDIR = 9

def is_zipfile(filename):
    """Quickly see if file is a ZIP file by checking the magic number."""
    try:
        fpin = open(filename, 'rb')
        endrec = _EndRecData(fpin)
        fpin.close()
        if endrec:
            return True
    except IOError:
        pass

    return False


def _EndRecData64(fpin, offset, endrec):
    """
    Read the ZIP64 end-of-archive records and use that to update endrec
    """
    fpin.seek(offset - sizeEndCentDir64Locator, 2)
    data = fpin.read(sizeEndCentDir64Locator)
    sig, diskno, reloff, disks = struct.unpack(structEndArchive64Locator, data)
    if sig != stringEndArchive64Locator:
        return endrec
    if diskno != 0 or disks != 1:
        raise BadZipfile('zipfiles that span multiple disks are not supported')
    fpin.seek(offset - sizeEndCentDir64Locator - sizeEndCentDir64, 2)
    data = fpin.read(sizeEndCentDir64)
    sig, sz, create_version, read_version, disk_num, disk_dir, dircount, dircount2, dirsize, diroffset = struct.unpack(structEndArchive64, data)
    if sig != stringEndArchive64:
        return endrec
    endrec[_ECD_SIGNATURE] = sig
    endrec[_ECD_DISK_NUMBER] = disk_num
    endrec[_ECD_DISK_START] = disk_dir
    endrec[_ECD_ENTRIES_THIS_DISK] = dircount
    endrec[_ECD_ENTRIES_TOTAL] = dircount2
    endrec[_ECD_SIZE] = dirsize
    endrec[_ECD_OFFSET] = diroffset
    return endrec


def _EndRecData(fpin):
    """Return data from the "End of Central Directory" record, or None.
    
    The data is a list of the nine items in the ZIP "End of central dir"
    record followed by a tenth item, the file seek offset of this record."""
    fpin.seek(0, 2)
    filesize = fpin.tell()
    fpin.seek(-sizeEndCentDir, 2)
    data = fpin.read()
    if data[0:4] == stringEndArchive and data[-2:] == '\x00\x00':
        endrec = struct.unpack(structEndArchive, data)
        endrec = list(endrec)
        endrec.append('')
        endrec.append(filesize - sizeEndCentDir)
        return _EndRecData64(fpin, -sizeEndCentDir, endrec)
    maxCommentStart = max(filesize - 65536 - sizeEndCentDir, 0)
    fpin.seek(maxCommentStart, 0)
    data = fpin.read()
    start = data.rfind(stringEndArchive)
    if start >= 0:
        recData = data[start:start + sizeEndCentDir]
        endrec = list(struct.unpack(structEndArchive, recData))
        comment = data[start + sizeEndCentDir:]
        if endrec[_ECD_COMMENT_SIZE] == len(comment):
            endrec.append(comment)
            endrec.append(maxCommentStart + start)
            return _EndRecData64(fpin, maxCommentStart + start - filesize, endrec)


class ZipInfo(object):
    """Class with attributes describing each file in the ZIP archive."""
    __slots__ = ('orig_filename', 'filename', 'date_time', 'compress_type', 'comment', 'extra', 'create_system', 'create_version', 'extract_version', 'reserved', 'flag_bits', 'volume', 'internal_attr', 'external_attr', 'header_offset', 'CRC', 'compress_size', 'file_size', '_raw_time')

    def __init__(self, filename='NoName', date_time=(1980, 1, 1, 0, 0, 0)):
        self.orig_filename = filename
        null_byte = filename.find(chr(0))
        if null_byte >= 0:
            filename = filename[0:null_byte]
        if os.sep != '/' and os.sep in filename:
            filename = filename.replace(os.sep, '/')
        self.filename = filename
        self.date_time = date_time
        self.compress_type = ZIP_STORED
        self.comment = ''
        self.extra = ''
        if sys.platform == 'win32':
            self.create_system = 0
        else:
            self.create_system = 3
        self.create_version = 20
        self.extract_version = 20
        self.reserved = 0
        self.flag_bits = 0
        self.volume = 0
        self.internal_attr = 0
        self.external_attr = 0

    def FileHeader(self):
        """Return the per-file header as a string."""
        dt = self.date_time
        dosdate = dt[0] - 1980 << 9 | dt[1] << 5 | dt[2]
        dostime = dt[3] << 11 | dt[4] << 5 | dt[5] // 2
        if self.flag_bits & 8:
            CRC = compress_size = file_size = 0
        else:
            CRC = self.CRC
            compress_size = self.compress_size
            file_size = self.file_size
        extra = self.extra
        if file_size > ZIP64_LIMIT or compress_size > ZIP64_LIMIT:
            fmt = '<HHQQ'
            extra = extra + struct.pack(fmt, 1, struct.calcsize(fmt) - 4, file_size, compress_size)
            file_size = 4294967295L
            compress_size = 4294967295L
            self.extract_version = max(45, self.extract_version)
            self.create_version = max(45, self.extract_version)
        filename, flag_bits = self._encodeFilenameFlags()
        header = struct.pack(structFileHeader, stringFileHeader, self.extract_version, self.reserved, flag_bits, self.compress_type, dostime, dosdate, CRC, compress_size, file_size, len(filename), len(extra))
        return header + filename + extra

    def _encodeFilenameFlags(self):
        if isinstance(self.filename, unicode):
            try:
                return (self.filename.encode('ascii'), self.flag_bits)
            except UnicodeEncodeError:
                return (self.filename.encode('utf-8'), self.flag_bits | 2048)

        else:
            return (self.filename, self.flag_bits)

    def _decodeFilename(self):
        if self.flag_bits & 2048:
            return self.filename.decode('utf-8')
        else:
            return self.filename

    def _decodeExtra(self):
        extra = self.extra
        unpack = struct.unpack
        while 1:
            if extra:
                tp, ln = unpack('<HH', extra[:4])
                if tp == 1:
                    if ln >= 24:
                        counts = unpack('<QQQ', extra[4:28])
                    elif ln == 16:
                        counts = unpack('<QQ', extra[4:20])
                    elif ln == 8:
                        counts = unpack('<Q', extra[4:12])
                    elif ln == 0:
                        counts = ()
                    else:
                        raise RuntimeError, 'Corrupt extra field %s' % (ln,)
                    idx = 0
                    if self.file_size in (18446744073709551615L, 4294967295L):
                        self.file_size = counts[idx]
                        idx += 1
                    if self.compress_size == 4294967295L:
                        self.compress_size = counts[idx]
                        idx += 1
                    old = self.header_offset == 4294967295L and self.header_offset
                    self.header_offset = counts[idx]
                    idx += 1
            extra = extra[ln + 4:]


class _ZipDecrypter():
    """Class to handle decryption of files stored within a ZIP archive.
    
    ZIP supports a password-based form of encryption. Even though known
    plaintext attacks have been found against it, it is still useful
    to be able to get data out of such a file.
    
    Usage:
        zd = _ZipDecrypter(mypwd)
        plain_char = zd(cypher_char)
        plain_text = map(zd, cypher_text)
    """

    def _GenerateCRCTable():
        """Generate a CRC-32 table.
        
        ZIP encryption uses the CRC32 one-byte primitive for scrambling some
        internal keys. We noticed that a direct implementation is faster than
        relying on binascii.crc32().
        """
        poly = 3988292384L
        table = [0] * 256
        for i in range(256):
            crc = i
            for j in range(8):
                if crc & 1:
                    crc = crc >> 1 & 2147483647 ^ poly
                else:
                    crc = crc >> 1 & 2147483647

            table[i] = crc

        return table

    crctable = _GenerateCRCTable()

    def _crc32(self, ch, crc):
        """Compute the CRC32 primitive on one byte."""
        return crc >> 8 & 16777215 ^ self.crctable[(crc ^ ord(ch)) & 255]

    def __init__(self, pwd):
        self.key0 = 305419896
        self.key1 = 591751049
        self.key2 = 878082192
        for p in pwd:
            self._UpdateKeys(p)

    def _UpdateKeys(self, c):
        self.key0 = self._crc32(c, self.key0)
        self.key1 = self.key1 + (self.key0 & 255) & 4294967295L
        self.key1 = self.key1 * 134775813 + 1 & 4294967295L
        self.key2 = self._crc32(chr(self.key1 >> 24 & 255), self.key2)

    def __call__(self, c):
        """Decrypt a single character."""
        c = ord(c)
        k = self.key2 | 2
        c = c ^ k * (k ^ 1) >> 8 & 255
        c = chr(c)
        self._UpdateKeys(c)
        return c


class ZipExtFile():
    """File-like object for reading an archive member.
       Is returned by ZipFile.open().
    """

    def __init__(self, fileobj, zipinfo, decrypt=None):
        self.fileobj = fileobj
        self.decrypter = decrypt
        self.bytes_read = 0L
        self.rawbuffer = ''
        self.readbuffer = ''
        self.linebuffer = ''
        self.eof = False
        self.univ_newlines = False
        self.nlSeps = ('\n',)
        self.lastdiscard = ''
        self.compress_type = zipinfo.compress_type
        self.compress_size = zipinfo.compress_size
        self.closed = False
        self.mode = 'r'
        self.name = zipinfo.filename
        self.compreadsize = 65536
        if self.compress_type == ZIP_DEFLATED:
            self.dc = zlib.decompressobj(-15)

    def set_univ_newlines(self, univ_newlines):
        self.univ_newlines = univ_newlines
        self.nlSeps = ('\n',)
        if self.univ_newlines:
            self.nlSeps = ('\r\n', '\r', '\n')

    def __iter__(self):
        return self

    def next(self):
        nextline = self.readline()
        if not nextline:
            raise StopIteration()
        return nextline

    def close(self):
        self.closed = True

    def _checkfornewline(self):
        nl, nllen = (-1, -1)
        if self.linebuffer:
            if (self.lastdiscard, self.linebuffer[0]) == ('\r', '\n'):
                self.linebuffer = self.linebuffer[1:]
            for sep in self.nlSeps:
                nl = self.linebuffer.find(sep)
                if nl >= 0:
                    nllen = len(sep)
                    return (nl, nllen)

        return (nl, nllen)

    def readline(self, size=-1):
        """Read a line with approx. size. If size is negative,
           read a whole line.
        """
        if size < 0:
            size = sys.maxint
        elif size == 0:
            return ''
        nl, nllen = self._checkfornewline()
        if nl >= 0:
            nl = min(nl, size)
        else:
            size -= len(self.linebuffer)
            while 1:
                buf = nl < 0 and size > 0 and self.read(min(size, 100))
                if not buf:
                    break
                self.linebuffer += buf
                size -= len(buf)
                nl, nllen = self._checkfornewline()

            if nl < 0:
                s = self.linebuffer
                self.linebuffer = ''
                return s
        buf = self.linebuffer[:nl]
        self.lastdiscard = self.linebuffer[nl:nl + nllen]
        self.linebuffer = self.linebuffer[nl + nllen:]
        return buf + '\n'

    def readlines(self, sizehint=-1):
        """Return a list with all (following) lines. The sizehint parameter
        is ignored in this implementation.
        """
        result = []
        while 1:
            line = True and self.readline()
            if not line:
                break
            result.append(line)

        return result

    def read(self, size=None):
        if size == 0:
            return ''
        else:
            bytesToRead = self.compress_size - self.bytes_read
            if self.decrypter is not None:
                bytesToRead -= 12
            if size is not None and size >= 0:
                if self.compress_type == ZIP_STORED:
                    lr = len(self.readbuffer)
                    bytesToRead = min(bytesToRead, size - lr)
                elif self.compress_type == ZIP_DEFLATED:
                    if len(self.readbuffer) > size:
                        bytesToRead = 0
                    else:
                        lr = len(self.rawbuffer)
                        bytesToRead = min(bytesToRead, self.compreadsize - lr)
            if bytesToRead + self.bytes_read > self.compress_size:
                bytesToRead = self.compress_size - self.bytes_read
            if bytesToRead > 0:
                bytes = self.fileobj.read(bytesToRead)
                self.bytes_read += len(bytes)
                self.rawbuffer += bytes
                if self.rawbuffer:
                    newdata = self.rawbuffer
                    self.rawbuffer = ''
                    if newdata and self.decrypter is not None:
                        newdata = ''.join(map(self.decrypter, newdata))
                    if newdata and self.compress_type == ZIP_DEFLATED:
                        newdata = self.dc.decompress(newdata)
                        self.rawbuffer = self.dc.unconsumed_tail
                        if self.eof and len(self.rawbuffer) == 0:
                            newdata += self.dc.flush()
                            self.dc = None
                    self.readbuffer += newdata
            if size is None or len(self.readbuffer) <= size:
                bytes = self.readbuffer
                self.readbuffer = ''
            else:
                bytes = self.readbuffer[:size]
                self.readbuffer = self.readbuffer[size:]
            return bytes


class ZipFile():
    """ Class with methods to open, read, write, close, list zip files.
    
    z = ZipFile(file, mode="r", compression=ZIP_STORED, allowZip64=False)
    
    file: Either the path to the file, or a file-like object.
          If it is a path, the file will be opened and closed by ZipFile.
    mode: The mode can be either read "r", write "w" or append "a".
    compression: ZIP_STORED (no compression) or ZIP_DEFLATED (requires zlib).
    allowZip64: if True ZipFile will create files with ZIP64 extensions when
                needed, otherwise it will raise an exception when this would
                be necessary.
    
    """
    fp = None

    def __init__(self, file, mode='r', compression=ZIP_STORED, allowZip64=False):
        """Open the ZIP file with mode read "r", write "w" or append "a"."""
        if mode not in ('r', 'w', 'a'):
            raise RuntimeError('ZipFile() requires mode "r", "w", or "a"')
        if compression == ZIP_STORED:
            pass
        elif compression == ZIP_DEFLATED:
            if not zlib:
                raise RuntimeError, 'Compression requires the (missing) zlib module'
        else:
            raise RuntimeError, 'That compression method is not supported'
        self._allowZip64 = allowZip64
        self._didModify = False
        self.debug = 0
        self.NameToInfo = {}
        self.filelist = []
        self.compression = compression
        self.mode = key = mode.replace('b', '')[0]
        self.pwd = None
        self.comment = ''
        if isinstance(file, basestring):
            self._filePassed = 0
            self.filename = file
            modeDict = {'r': 'rb',
             'w': 'wb',
             'a': 'r+b'}
            try:
                self.fp = open(file, modeDict[mode])
            except IOError:
                if mode == 'a':
                    mode = key = 'w'
                    self.fp = open(file, modeDict[mode])
                else:
                    raise

        else:
            self._filePassed = 1
            self.fp = file
            self.filename = getattr(file, 'name', None)
        if key == 'r':
            self._GetContents()
        elif key == 'w':
            pass
        elif key == 'a':
            try:
                self._RealGetContents()
                self.fp.seek(self.start_dir, 0)
            except BadZipfile:
                self.fp.seek(0, 2)

        else:
            if not self._filePassed:
                self.fp.close()
                self.fp = None
            raise RuntimeError, 'Mode must be "r", "w" or "a"'
        return

    def _GetContents(self):
        """Read the directory, making sure we close the file if the format
        is bad."""
        try:
            self._RealGetContents()
        except BadZipfile:
            if not self._filePassed:
                self.fp.close()
                self.fp = None
            raise

        return

    def _RealGetContents(self):
        """Read in the table of contents for the ZIP file."""
        fp = self.fp
        endrec = _EndRecData(fp)
        if not endrec:
            raise BadZipfile, 'File is not a zip file'
        if self.debug > 1:
            print endrec
        size_cd = endrec[_ECD_SIZE]
        offset_cd = endrec[_ECD_OFFSET]
        self.comment = endrec[_ECD_COMMENT]
        concat = endrec[_ECD_LOCATION] - size_cd - offset_cd
        if endrec[_ECD_SIGNATURE] == stringEndArchive64:
            concat -= sizeEndCentDir64 + sizeEndCentDir64Locator
        if self.debug > 2:
            inferred = concat + offset_cd
            print 'given, inferred, offset', offset_cd, inferred, concat
        self.start_dir = offset_cd + concat
        fp.seek(self.start_dir, 0)
        data = fp.read(size_cd)
        fp = cStringIO.StringIO(data)
        total = 0
        while 1:
            if total < size_cd:
                centdir = fp.read(sizeCentralDir)
                if centdir[0:4] != stringCentralDir:
                    raise BadZipfile, 'Bad magic number for central directory'
                centdir = struct.unpack(structCentralDir, centdir)
                if self.debug > 2:
                    print centdir
                filename = fp.read(centdir[_CD_FILENAME_LENGTH])
                x = ZipInfo(filename)
                x.extra = fp.read(centdir[_CD_EXTRA_FIELD_LENGTH])
                x.comment = fp.read(centdir[_CD_COMMENT_LENGTH])
                x.header_offset = centdir[_CD_LOCAL_HEADER_OFFSET]
                x.create_version, x.create_system, x.extract_version, x.reserved, x.flag_bits, x.compress_type, t, d, x.CRC, x.compress_size, x.file_size = centdir[1:12]
                x.volume, x.internal_attr, x.external_attr = centdir[15:18]
                x._raw_time = t
                x.date_time = ((d >> 9) + 1980,
                 d >> 5 & 15,
                 d & 31,
                 t >> 11,
                 t >> 5 & 63,
                 (t & 31) * 2)
                x._decodeExtra()
                x.header_offset = x.header_offset + concat
                x.filename = x._decodeFilename()
                self.filelist.append(x)
                self.NameToInfo[x.filename] = x
                total = total + sizeCentralDir + centdir[_CD_FILENAME_LENGTH] + centdir[_CD_EXTRA_FIELD_LENGTH] + centdir[_CD_COMMENT_LENGTH]
                print self.debug > 2 and 'total', total

    def namelist(self):
        """Return a list of file names in the archive."""
        l = []
        for data in self.filelist:
            l.append(data.filename)

        return l

    def infolist(self):
        """Return a list of class ZipInfo instances for files in the
        archive."""
        return self.filelist

    def printdir(self):
        """Print a table of contents for the zip file."""
        print '%-46s %19s %12s' % ('File Name', 'Modified    ', 'Size')
        for zinfo in self.filelist:
            date = '%d-%02d-%02d %02d:%02d:%02d' % zinfo.date_time[:6]
            print '%-46s %s %12d' % (zinfo.filename, date, zinfo.file_size)

    def testzip--- This code section failed: ---

 805       0	LOAD_CONST        1048576
           3	STORE_FAST        'chunk_size'

 806       6	SETUP_LOOP        '97'
           9	LOAD_FAST         'self'
          12	LOAD_ATTR         'filelist'
          15	GET_ITER          ''
          16	FOR_ITER          '96'
          19	STORE_FAST        'zinfo'

 807      22	SETUP_EXCEPT      '72'

 810      25	LOAD_FAST         'self'
          28	LOAD_ATTR         'open'
          31	LOAD_FAST         'zinfo'
          34	LOAD_ATTR         'filename'
          37	LOAD_CONST        'r'
          40	CALL_FUNCTION_2   ''
          43	STORE_FAST        'f'

 811      46	SETUP_LOOP        '68'
          49	LOAD_FAST         'f'
          52	LOAD_ATTR         'read'
          55	LOAD_FAST         'chunk_size'
          58	CALL_FUNCTION_1   ''
          61	JUMP_IF_FALSE     '67'

 812      64	JUMP_BACK         '49'
          67	POP_BLOCK         ''
        68_0	COME_FROM         '46'
          68	POP_BLOCK         ''
          69	JUMP_BACK         '16'
        72_0	COME_FROM         '22'

 813      72	DUP_TOP           ''
          73	LOAD_GLOBAL       'BadZipfile'
          76	COMPARE_OP        'exception match'
          79	JUMP_IF_FALSE     '92'
          82	POP_TOP           ''
          83	POP_TOP           ''
          84	POP_TOP           ''

 814      85	LOAD_FAST         'zinfo'
          88	LOAD_ATTR         'filename'
          91	RETURN_VALUE      ''
          92	END_FINALLY       ''
        93_0	COME_FROM         '92'
          93	JUMP_BACK         '16'
          96	POP_BLOCK         ''
        97_0	COME_FROM         '6'

Syntax error at or near 'POP_BLOCK' token at offset 67

    def getinfo(self, name):
        """Return the instance of ZipInfo given 'name'."""
        info = self.NameToInfo.get(name)
        if info is None:
            raise KeyError('There is no item named %r in the archive' % name)
        return info

    def setpassword(self, pwd):
        """Set default password for encrypted files."""
        self.pwd = pwd

    def read(self, name, pwd=None):
        """Return file bytes (as a string) for name."""
        return self.open(name, 'r', pwd).read()

    def open(self, name, mode='r', pwd=None):
        """Return file-like object for 'name'."""
        if mode not in ('r', 'U', 'rU'):
            raise RuntimeError, 'open() requires mode "r", "U", or "rU"'
        if not self.fp:
            raise RuntimeError, 'Attempt to read ZIP archive that was already closed'
        if self._filePassed:
            zef_file = self.fp
        else:
            zef_file = open(self.filename, 'rb')
        if isinstance(name, ZipInfo):
            zinfo = name
        else:
            zinfo = self.getinfo(name)
        zef_file.seek(zinfo.header_offset, 0)
        fheader = zef_file.read(sizeFileHeader)
        if fheader[0:4] != stringFileHeader:
            raise BadZipfile, 'Bad magic number for file header'
        fheader = struct.unpack(structFileHeader, fheader)
        fname = zef_file.read(fheader[_FH_FILENAME_LENGTH])
        if fheader[_FH_EXTRA_FIELD_LENGTH]:
            zef_file.read(fheader[_FH_EXTRA_FIELD_LENGTH])
        if fname != zinfo.orig_filename:
            raise BadZipfile, 'File name in directory "%s" and header "%s" differ.' % (zinfo.orig_filename, fname)
        is_encrypted = zinfo.flag_bits & 1
        zd = None
        if is_encrypted:
            if not pwd:
                pwd = self.pwd
            if not pwd:
                raise RuntimeError, 'File %s is encrypted, password required for extraction' % name
            zd = _ZipDecrypter(pwd)
            bytes = zef_file.read(12)
            h = map(zd, bytes[0:12])
            if zinfo.flag_bits & 8:
                check_byte = zinfo._raw_time >> 8 & 255
            else:
                check_byte = zinfo.CRC >> 24 & 255
            if ord(h[11]) != check_byte:
                raise RuntimeError('Bad password for file', name)
        if zd is None:
            zef = ZipExtFile(zef_file, zinfo)
        else:
            zef = ZipExtFile(zef_file, zinfo, zd)
        if 'U' in mode:
            zef.set_univ_newlines(True)
        return zef

    def extract(self, member, path=None, pwd=None):
        """Extract a member from the archive to the current working directory,
           using its full name. Its file information is extracted as accurately
           as possible. `member' may be a filename or a ZipInfo object. You can
           specify a different directory using `path'.
        """
        if not isinstance(member, ZipInfo):
            member = self.getinfo(member)
        if path is None:
            path = os.getcwd()
        return self._extract_member(member, path, pwd)

    def extractall(self, path=None, members=None, pwd=None):
        """Extract all members from the archive to the current working
           directory. `path' specifies a different directory to extract to.
           `members' is optional and must be a subset of the list returned
           by namelist().
        """
        if members is None:
            members = self.namelist()
        for zipinfo in members:
            self.extract(zipinfo, path, pwd)

        return

    def _extract_member(self, member, targetpath, pwd):
        """Extract the ZipInfo object 'member' to a physical
           file on the path targetpath.
        """
        if targetpath[-1:] in (os.path.sep, os.path.altsep) and len(os.path.splitdrive(targetpath)[1]) > 1:
            targetpath = targetpath[:-1]
        if member.filename[0] == '/':
            targetpath = os.path.join(targetpath, member.filename[1:])
        else:
            targetpath = os.path.join(targetpath, member.filename)
        targetpath = os.path.normpath(targetpath)
        upperdirs = os.path.dirname(targetpath)
        if upperdirs and not os.path.exists(upperdirs):
            os.makedirs(upperdirs)
        if member.filename[-1] == '/':
            if not os.path.isdir(targetpath):
                os.mkdir(targetpath)
            return targetpath
        source = self.open(member, pwd=pwd)
        target = file(targetpath, 'wb')
        shutil.copyfileobj(source, target)
        source.close()
        target.close()
        return targetpath

    def _writecheck(self, zinfo):
        """Check for errors before writing a file to the archive."""
        if zinfo.filename in self.NameToInfo:
            if self.debug:
                print 'Duplicate name:', zinfo.filename
        if self.mode not in ('w', 'a'):
            raise RuntimeError, 'write() requires mode "w" or "a"'
        if not self.fp:
            raise RuntimeError, 'Attempt to write ZIP archive that was already closed'
        if zinfo.compress_type == ZIP_DEFLATED and not zlib:
            raise RuntimeError, 'Compression requires the (missing) zlib module'
        if zinfo.compress_type not in (ZIP_STORED, ZIP_DEFLATED):
            raise RuntimeError, 'That compression method is not supported'
        if zinfo.file_size > ZIP64_LIMIT:
            if not self._allowZip64:
                raise LargeZipFile('Filesize would require ZIP64 extensions')
        if zinfo.header_offset > ZIP64_LIMIT:
            if not self._allowZip64:
                raise LargeZipFile('Zipfile size would require ZIP64 extensions')

    def write(self, filename, arcname=None, compress_type=None):
        """Put the bytes from filename into the archive under the name
        arcname."""
        if not self.fp:
            raise RuntimeError('Attempt to write to ZIP archive that was already closed')
        st = os.stat(filename)
        isdir = stat.S_ISDIR(st.st_mode)
        mtime = time.localtime(st.st_mtime)
        date_time = mtime[0:6]
        if arcname is None:
            arcname = filename
        arcname = os.path.normpath(os.path.splitdrive(arcname)[1])
        while 1:
            arcname = arcname[0] in (os.sep, os.altsep) and arcname[1:]

        if isdir:
            arcname += '/'
        zinfo = ZipInfo(arcname, date_time)
        zinfo.external_attr = (st[0] & 65535) << 16L
        if compress_type is None:
            zinfo.compress_type = self.compression
        else:
            zinfo.compress_type = compress_type
        zinfo.file_size = st.st_size
        zinfo.flag_bits = 0
        zinfo.header_offset = self.fp.tell()
        self._writecheck(zinfo)
        self._didModify = True
        if isdir:
            zinfo.file_size = 0
            zinfo.compress_size = 0
            zinfo.CRC = 0
            self.filelist.append(zinfo)
            self.NameToInfo[zinfo.filename] = zinfo
            self.fp.write(zinfo.FileHeader())
            return
        else:
            fp = open(filename, 'rb')
            zinfo.CRC = CRC = 0
            zinfo.compress_size = compress_size = 0
            zinfo.file_size = file_size = 0
            self.fp.write(zinfo.FileHeader())
            if zinfo.compress_type == ZIP_DEFLATED:
                cmpr = zlib.compressobj(zlib.Z_DEFAULT_COMPRESSION, zlib.DEFLATED, -15)
            else:
                cmpr = None
            while 1:
                buf = fp.read(8192)
                if not buf:
                    break
                file_size = file_size + len(buf)
                CRC = crc32(buf, CRC) & 4294967295L
                if cmpr:
                    buf = cmpr.compress(buf)
                    compress_size = compress_size + len(buf)
                self.fp.write(buf)

            fp.close()
            if cmpr:
                buf = cmpr.flush()
                compress_size = compress_size + len(buf)
                self.fp.write(buf)
                zinfo.compress_size = compress_size
            else:
                zinfo.compress_size = file_size
            zinfo.CRC = CRC
            zinfo.file_size = file_size
            position = self.fp.tell()
            self.fp.seek(zinfo.header_offset + 14, 0)
            self.fp.write(struct.pack('<LLL', zinfo.CRC, zinfo.compress_size, zinfo.file_size))
            self.fp.seek(position, 0)
            self.filelist.append(zinfo)
            self.NameToInfo[zinfo.filename] = zinfo
            return

    def writestr(self, zinfo_or_arcname, bytes):
        """Write a file into the archive.  The contents is the string
        'bytes'.  'zinfo_or_arcname' is either a ZipInfo instance or
        the name of the file in the archive."""
        if not isinstance(zinfo_or_arcname, ZipInfo):
            zinfo = ZipInfo(filename=zinfo_or_arcname, date_time=time.localtime(time.time())[:6])
            zinfo.compress_type = self.compression
            zinfo.external_attr = 25165824
        else:
            zinfo = zinfo_or_arcname
        if not self.fp:
            raise RuntimeError('Attempt to write to ZIP archive that was already closed')
        zinfo.file_size = len(bytes)
        zinfo.header_offset = self.fp.tell()
        self._writecheck(zinfo)
        self._didModify = True
        zinfo.CRC = crc32(bytes) & 4294967295L
        if zinfo.compress_type == ZIP_DEFLATED:
            co = zlib.compressobj(zlib.Z_DEFAULT_COMPRESSION, zlib.DEFLATED, -15)
            bytes = co.compress(bytes) + co.flush()
            zinfo.compress_size = len(bytes)
        else:
            zinfo.compress_size = zinfo.file_size
        zinfo.header_offset = self.fp.tell()
        self.fp.write(zinfo.FileHeader())
        self.fp.write(bytes)
        self.fp.flush()
        if zinfo.flag_bits & 8:
            self.fp.write(struct.pack('<LLL', zinfo.CRC, zinfo.compress_size, zinfo.file_size))
        self.filelist.append(zinfo)
        self.NameToInfo[zinfo.filename] = zinfo

    def __del__(self):
        """Call the "close()" method in case the user forgot."""
        self.close()

    def close(self):
        """Close the file, and for mode "w" and "a" write the ending
        records."""
        if self.fp is None:
            return
        else:
            if self.mode in ('w', 'a') and self._didModify:
                count = 0
                pos1 = self.fp.tell()
                for zinfo in self.filelist:
                    count = count + 1
                    dt = zinfo.date_time
                    dosdate = dt[0] - 1980 << 9 | dt[1] << 5 | dt[2]
                    dostime = dt[3] << 11 | dt[4] << 5 | dt[5] // 2
                    extra = []
                    if zinfo.file_size > ZIP64_LIMIT or zinfo.compress_size > ZIP64_LIMIT:
                        extra.append(zinfo.file_size)
                        extra.append(zinfo.compress_size)
                        file_size = 4294967295L
                        compress_size = 4294967295L
                    else:
                        file_size = zinfo.file_size
                        compress_size = zinfo.compress_size
                    if zinfo.header_offset > ZIP64_LIMIT:
                        extra.append(zinfo.header_offset)
                        header_offset = 4294967295L
                    else:
                        header_offset = zinfo.header_offset
                    extra_data = zinfo.extra
                    if extra:
                        extra_data = struct.pack(('<HH' + 'Q' * len(extra)), 1, (8 * len(extra)), *extra) + extra_data
                        extract_version = max(45, zinfo.extract_version)
                        create_version = max(45, zinfo.create_version)
                    else:
                        extract_version = zinfo.extract_version
                        create_version = zinfo.create_version
                    try:
                        filename, flag_bits = zinfo._encodeFilenameFlags()
                        centdir = struct.pack(structCentralDir, stringCentralDir, create_version, zinfo.create_system, extract_version, zinfo.reserved, flag_bits, zinfo.compress_type, dostime, dosdate, zinfo.CRC, compress_size, file_size, len(filename), len(extra_data), len(zinfo.comment), 0, zinfo.internal_attr, zinfo.external_attr, header_offset)
                    except DeprecationWarning:
                        print >> sys.stderr, (structCentralDir,
                         stringCentralDir,
                         create_version,
                         zinfo.create_system,
                         extract_version,
                         zinfo.reserved,
                         zinfo.flag_bits,
                         zinfo.compress_type,
                         dostime,
                         dosdate,
                         zinfo.CRC,
                         compress_size,
                         file_size,
                         len(zinfo.filename),
                         len(extra_data),
                         len(zinfo.comment),
                         0,
                         zinfo.internal_attr,
                         zinfo.external_attr,
                         header_offset)
                        raise

                    self.fp.write(centdir)
                    self.fp.write(filename)
                    self.fp.write(extra_data)
                    self.fp.write(zinfo.comment)

                pos2 = self.fp.tell()
                centDirCount = count
                centDirSize = pos2 - pos1
                centDirOffset = pos1
                if centDirCount >= ZIP_FILECOUNT_LIMIT or centDirOffset > ZIP64_LIMIT or centDirSize > ZIP64_LIMIT:
                    zip64endrec = struct.pack(structEndArchive64, stringEndArchive64, 44, 45, 45, 0, 0, centDirCount, centDirCount, centDirSize, centDirOffset)
                    self.fp.write(zip64endrec)
                    zip64locrec = struct.pack(structEndArchive64Locator, stringEndArchive64Locator, 0, pos2, 1)
                    self.fp.write(zip64locrec)
                    centDirCount = min(centDirCount, 65535)
                    centDirSize = min(centDirSize, 4294967295L)
                    centDirOffset = min(centDirOffset, 4294967295L)
                if len(self.comment) >= ZIP_MAX_COMMENT:
                    if self.debug > 0:
                        msg = 'Archive comment is too long; truncating to %d bytes' % ZIP_MAX_COMMENT
                    self.comment = self.comment[:ZIP_MAX_COMMENT]
                endrec = struct.pack(structEndArchive, stringEndArchive, 0, 0, centDirCount, centDirCount, centDirSize, centDirOffset, len(self.comment))
                self.fp.write(endrec)
                self.fp.write(self.comment)
                self.fp.flush()
            if not self._filePassed:
                self.fp.close()
            self.fp = None
            return


class PyZipFile(ZipFile):
    """Class to create ZIP archives with Python library files and packages."""

    def writepy(self, pathname, basename=''):
        """Add all files from "pathname" to the ZIP archive.
        
        If pathname is a package directory, search the directory and
        all package subdirectories recursively for all *.py and enter
        the modules into the archive.  If pathname is a plain
        directory, listdir *.py and enter all modules.  Else, pathname
        must be a Python *.py file and the module will be put into the
        archive.  Added modules are always module.pyo or module.pyc.
        This method will compile the module.py into module.pyc if
        necessary.
        """
        dir, name = os.path.split(pathname)
        if os.path.isdir(pathname):
            initname = os.path.join(pathname, '__init__.py')
            if os.path.isfile(initname):
                if basename:
                    basename = '%s/%s' % (basename, name)
                else:
                    basename = name
                if self.debug:
                    print 'Adding package in', pathname, 'as', basename
                fname, arcname = self._get_codename(initname[0:-3], basename)
                if self.debug:
                    print 'Adding', arcname
                self.write(fname, arcname)
                dirlist = os.listdir(pathname)
                dirlist.remove('__init__.py')
                for filename in dirlist:
                    path = os.path.join(pathname, filename)
                    root, ext = os.path.splitext(filename)
                    if os.path.isdir(path):
                        if os.path.isfile(os.path.join(path, '__init__.py')):
                            self.writepy(path, basename)
                    elif ext == '.py':
                        fname, arcname = self._get_codename(path[0:-3], basename)
                        if self.debug:
                            print 'Adding', arcname
                        self.write(fname, arcname)

            else:
                if self.debug:
                    print 'Adding files from directory', pathname
                for filename in os.listdir(pathname):
                    path = os.path.join(pathname, filename)
                    root, ext = os.path.splitext(filename)
                    if ext == '.py':
                        fname, arcname = self._get_codename(path[0:-3], basename)
                        if self.debug:
                            print 'Adding', arcname
                        self.write(fname, arcname)

        else:
            if pathname[-3:] != '.py':
                raise RuntimeError, 'Files added with writepy() must end with ".py"'
            fname, arcname = self._get_codename(pathname[0:-3], basename)
            if self.debug:
                print 'Adding file', arcname
            self.write(fname, arcname)

    def _get_codename(self, pathname, basename):
        """Return (filename, archivename) for the path.
        
        Given a module name path, return the correct file path and
        archive name, compiling if necessary.  For example, given
        /python/lib/string, return (/python/lib/string.pyc, string).
        """
        file_py = pathname + '.py'
        file_pyc = pathname + '.pyc'
        file_pyo = pathname + '.pyo'
        if os.path.isfile(file_pyo) and os.stat(file_pyo).st_mtime >= os.stat(file_py).st_mtime:
            fname = file_pyo
        elif not os.path.isfile(file_pyc) or os.stat(file_pyc).st_mtime < os.stat(file_py).st_mtime:
            import py_compile
            if self.debug:
                print 'Compiling', file_py
            try:
                py_compile.compile(file_py, file_pyc, None, True)
            except py_compile.PyCompileError as err:
                print err.msg

            fname = file_pyc
        else:
            fname = file_pyc
        archivename = os.path.split(fname)[1]
        if basename:
            archivename = '%s/%s' % (basename, archivename)
        return (fname, archivename)


def main(args=None):
    import textwrap
    USAGE = textwrap.dedent('        Usage:\n            zipfile.py -l zipfile.zip        # Show listing of a zipfile\n            zipfile.py -t zipfile.zip        # Test if a zipfile is valid\n            zipfile.py -e zipfile.zip target # Extract zipfile into target dir\n            zipfile.py -c zipfile.zip src ... # Create zipfile from sources\n        ')
    if args is None:
        args = sys.argv[1:]
    if not args or args[0] not in ('-l', '-c', '-e', '-t'):
        print USAGE
        sys.exit(1)
    if args[0] == '-l':
        if len(args) != 2:
            print USAGE
            sys.exit(1)
        zf = ZipFile(args[1], 'r')
        zf.printdir()
        zf.close()
    elif args[0] == '-t':
        if len(args) != 2:
            print USAGE
            sys.exit(1)
        zf = ZipFile(args[1], 'r')
        zf.testzip()
        print 'Done testing'
    elif args[0] == '-e':
        if len(args) != 3:
            print USAGE
            sys.exit(1)
        zf = ZipFile(args[1], 'r')
        out = args[2]
        for path in zf.namelist():
            if path.startswith('./'):
                tgt = os.path.join(out, path[2:])
            else:
                tgt = os.path.join(out, path)
            tgtdir = os.path.dirname(tgt)
            if not os.path.exists(tgtdir):
                os.makedirs(tgtdir)
            fp = open(tgt, 'wb')
            fp.write(zf.read(path))
            fp.close()

        zf.close()
    elif args[0] == '-c':
        if len(args) < 3:
            print USAGE
            sys.exit(1)

        def addToZip(zf, path, zippath):
            if os.path.isfile(path):
                zf.write(path, zippath, ZIP_DEFLATED)
            elif os.path.isdir(path):
                for nm in os.listdir(path):
                    addToZip(zf, os.path.join(path, nm), os.path.join(zippath, nm))

        zf = ZipFile(args[1], 'w', allowZip64=True)
        for src in args[2:]:
            addToZip(zf, src, os.path.basename(src))

        zf.close()
    return


if __name__ == '__main__':
    main()