# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/wave.py
import __builtin__
__all__ = ['open', 'openfp', 'Error']

class Error(Exception):
    pass


WAVE_FORMAT_PCM = 1
_array_fmts = (None, 'b', 'h', None, 'i')
import struct
import sys
from chunk import Chunk

def _byteswap3(data):
    ba = bytearray(data)
    ba[::3] = data[2::3]
    ba[2::3] = data[::3]
    return bytes(ba)


class Wave_read:

    def initfp(self, file):
        self._convert = None
        self._soundpos = 0
        self._file = Chunk(file, bigendian=0)
        if self._file.getname() != 'RIFF':
            raise Error, 'file does not start with RIFF id'
        if self._file.read(4) != 'WAVE':
            raise Error, 'not a WAVE file'
        self._fmt_chunk_read = 0
        self._data_chunk = None
        while 1:
            self._data_seek_needed = 1
            try:
                chunk = Chunk(self._file, bigendian=0)
            except EOFError:
                break

            chunkname = chunk.getname()
            if chunkname == 'fmt ':
                self._read_fmt_chunk(chunk)
                self._fmt_chunk_read = 1
            elif chunkname == 'data':
                if not self._fmt_chunk_read:
                    raise Error, 'data chunk before fmt chunk'
                self._data_chunk = chunk
                self._nframes = chunk.chunksize // self._framesize
                self._data_seek_needed = 0
                break
            chunk.skip()

        if not self._fmt_chunk_read or not self._data_chunk:
            raise Error, 'fmt chunk and/or data chunk missing'
        return

    def __init__(self, f):
        self._i_opened_the_file = None
        if isinstance(f, basestring):
            f = __builtin__.open(f, 'rb')
            self._i_opened_the_file = f
        try:
            self.initfp(f)
        except:
            if self._i_opened_the_file:
                f.close()
            raise

        return

    def __del__(self):
        self.close()

    def getfp(self):
        return self._file

    def rewind(self):
        self._data_seek_needed = 1
        self._soundpos = 0

    def close(self):
        if self._i_opened_the_file:
            self._i_opened_the_file.close()
            self._i_opened_the_file = None
        self._file = None
        return

    def tell(self):
        return self._soundpos

    def getnchannels(self):
        return self._nchannels

    def getnframes(self):
        return self._nframes

    def getsampwidth(self):
        return self._sampwidth

    def getframerate(self):
        return self._framerate

    def getcomptype(self):
        return self._comptype

    def getcompname(self):
        return self._compname

    def getparams(self):
        return (self.getnchannels(),
         self.getsampwidth(),
         self.getframerate(),
         self.getnframes(),
         self.getcomptype(),
         self.getcompname())

    def getmarkers(self):
        return None

    def getmark(self, id):
        raise Error, 'no marks'

    def setpos(self, pos):
        if pos < 0 or pos > self._nframes:
            raise Error, 'position not in range'
        self._soundpos = pos
        self._data_seek_needed = 1

    def readframes(self, nframes):
        if self._data_seek_needed:
            self._data_chunk.seek(0, 0)
            pos = self._soundpos * self._framesize
            if pos:
                self._data_chunk.seek(pos, 0)
            self._data_seek_needed = 0
        if nframes == 0:
            return ''
        if self._sampwidth in (2, 4) and sys.byteorder == 'big':
            import array
            chunk = self._data_chunk
            data = array.array(_array_fmts[self._sampwidth])
            nitems = nframes * self._nchannels
            if nitems * self._sampwidth > chunk.chunksize - chunk.size_read:
                nitems = (chunk.chunksize - chunk.size_read) / self._sampwidth
            data.fromfile(chunk.file.file, nitems)
            chunk.size_read = chunk.size_read + nitems * self._sampwidth
            chunk = chunk.file
            chunk.size_read = chunk.size_read + nitems * self._sampwidth
            data.byteswap()
            data = data.tostring()
        else:
            data = self._data_chunk.read(nframes * self._framesize)
            if self._sampwidth == 3 and sys.byteorder == 'big':
                data = _byteswap3(data)
        if self._convert and data:
            data = self._convert(data)
        self._soundpos = self._soundpos + len(data) // (self._nchannels * self._sampwidth)
        return data

    def _read_fmt_chunk(self, chunk):
        wFormatTag, self._nchannels, self._framerate, dwAvgBytesPerSec, wBlockAlign = struct.unpack('<HHLLH', chunk.read(14))
        if wFormatTag == WAVE_FORMAT_PCM:
            sampwidth = struct.unpack('<H', chunk.read(2))[0]
            self._sampwidth = (sampwidth + 7) // 8
        else:
            raise Error, 'unknown format: %r' % (wFormatTag,)
        self._framesize = self._nchannels * self._sampwidth
        self._comptype = 'NONE'
        self._compname = 'not compressed'


class Wave_write:

    def __init__(self, f):
        self._i_opened_the_file = None
        if isinstance(f, basestring):
            f = __builtin__.open(f, 'wb')
            self._i_opened_the_file = f
        try:
            self.initfp(f)
        except:
            if self._i_opened_the_file:
                f.close()
            raise

        return

    def initfp(self, file):
        self._file = file
        self._convert = None
        self._nchannels = 0
        self._sampwidth = 0
        self._framerate = 0
        self._nframes = 0
        self._nframeswritten = 0
        self._datawritten = 0
        self._datalength = 0
        self._headerwritten = False
        return

    def __del__(self):
        self.close()

    def setnchannels(self, nchannels):
        if self._datawritten:
            raise Error, 'cannot change parameters after starting to write'
        if nchannels < 1:
            raise Error, 'bad # of channels'
        self._nchannels = nchannels

    def getnchannels(self):
        if not self._nchannels:
            raise Error, 'number of channels not set'
        return self._nchannels

    def setsampwidth(self, sampwidth):
        if self._datawritten:
            raise Error, 'cannot change parameters after starting to write'
        if sampwidth < 1 or sampwidth > 4:
            raise Error, 'bad sample width'
        self._sampwidth = sampwidth

    def getsampwidth(self):
        if not self._sampwidth:
            raise Error, 'sample width not set'
        return self._sampwidth

    def setframerate(self, framerate):
        if self._datawritten:
            raise Error, 'cannot change parameters after starting to write'
        if framerate <= 0:
            raise Error, 'bad frame rate'
        self._framerate = framerate

    def getframerate(self):
        if not self._framerate:
            raise Error, 'frame rate not set'
        return self._framerate

    def setnframes(self, nframes):
        if self._datawritten:
            raise Error, 'cannot change parameters after starting to write'
        self._nframes = nframes

    def getnframes(self):
        return self._nframeswritten

    def setcomptype(self, comptype, compname):
        if self._datawritten:
            raise Error, 'cannot change parameters after starting to write'
        if comptype not in ('NONE',):
            raise Error, 'unsupported compression type'
        self._comptype = comptype
        self._compname = compname

    def getcomptype(self):
        return self._comptype

    def getcompname(self):
        return self._compname

    def setparams(self, params):
        nchannels, sampwidth, framerate, nframes, comptype, compname = params
        if self._datawritten:
            raise Error, 'cannot change parameters after starting to write'
        self.setnchannels(nchannels)
        self.setsampwidth(sampwidth)
        self.setframerate(framerate)
        self.setnframes(nframes)
        self.setcomptype(comptype, compname)

    def getparams(self):
        if not self._nchannels or not self._sampwidth or not self._framerate:
            raise Error, 'not all parameters set'
        return (self._nchannels,
         self._sampwidth,
         self._framerate,
         self._nframes,
         self._comptype,
         self._compname)

    def setmark(self, id, pos, name):
        raise Error, 'setmark() not supported'

    def getmark(self, id):
        raise Error, 'no marks'

    def getmarkers(self):
        return None

    def tell(self):
        return self._nframeswritten

    def writeframesraw(self, data):
        self._ensure_header_written(len(data))
        nframes = len(data) // (self._sampwidth * self._nchannels)
        if self._convert:
            data = self._convert(data)
        if self._sampwidth in (2, 4) and sys.byteorder == 'big':
            import array
            a = array.array(_array_fmts[self._sampwidth])
            a.fromstring(data)
            data = a
            data.byteswap()
            data.tofile(self._file)
            self._datawritten = self._datawritten + len(data) * self._sampwidth
        else:
            if self._sampwidth == 3 and sys.byteorder == 'big':
                data = _byteswap3(data)
            self._file.write(data)
            self._datawritten = self._datawritten + len(data)
        self._nframeswritten = self._nframeswritten + nframes

    def writeframes(self, data):
        self.writeframesraw(data)
        if self._datalength != self._datawritten:
            self._patchheader()

    def close(self):
        if self._file:
            try:
                self._ensure_header_written(0)
                if self._datalength != self._datawritten:
                    self._patchheader()
                self._file.flush()
            finally:
                self._file = None

        if self._i_opened_the_file:
            self._i_opened_the_file.close()
            self._i_opened_the_file = None
        return

    def _ensure_header_written(self, datasize):
        if not self._headerwritten:
            if not self._nchannels:
                raise Error, '# channels not specified'
            if not self._sampwidth:
                raise Error, 'sample width not specified'
            if not self._framerate:
                raise Error, 'sampling rate not specified'
            self._write_header(datasize)

    def _write_header(self, initlength):
        self._file.write('RIFF')
        if not self._nframes:
            self._nframes = initlength / (self._nchannels * self._sampwidth)
        self._datalength = self._nframes * self._nchannels * self._sampwidth
        self._form_length_pos = self._file.tell()
        self._file.write(struct.pack('<L4s4sLHHLLHH4s', 36 + self._datalength, 'WAVE', 'fmt ', 16, WAVE_FORMAT_PCM, self._nchannels, self._framerate, self._nchannels * self._framerate * self._sampwidth, self._nchannels * self._sampwidth, self._sampwidth * 8, 'data'))
        self._data_length_pos = self._file.tell()
        self._file.write(struct.pack('<L', self._datalength))
        self._headerwritten = True

    def _patchheader(self):
        if self._datawritten == self._datalength:
            return
        curpos = self._file.tell()
        self._file.seek(self._form_length_pos, 0)
        self._file.write(struct.pack('<L', 36 + self._datawritten))
        self._file.seek(self._data_length_pos, 0)
        self._file.write(struct.pack('<L', self._datawritten))
        self._file.seek(curpos, 0)
        self._datalength = self._datawritten


def open(f, mode=None):
    if mode is None:
        if hasattr(f, 'mode'):
            mode = f.mode
        else:
            mode = 'rb'
    if mode in ('r', 'rb'):
        return Wave_read(f)
    elif mode in ('w', 'wb'):
        return Wave_write(f)
    else:
        raise Error, "mode must be 'r', 'rb', 'w', or 'wb'"
        return


openfp = open
