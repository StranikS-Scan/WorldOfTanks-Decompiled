# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/codecs.py
import __builtin__, sys
try:
    from _codecs import *
except ImportError as why:
    raise SystemError('Failed to load the builtin codecs: %s' % why)

__all__ = ['register',
 'lookup',
 'open',
 'EncodedFile',
 'BOM',
 'BOM_BE',
 'BOM_LE',
 'BOM32_BE',
 'BOM32_LE',
 'BOM64_BE',
 'BOM64_LE',
 'BOM_UTF8',
 'BOM_UTF16',
 'BOM_UTF16_LE',
 'BOM_UTF16_BE',
 'BOM_UTF32',
 'BOM_UTF32_LE',
 'BOM_UTF32_BE',
 'CodecInfo',
 'Codec',
 'IncrementalEncoder',
 'IncrementalDecoder',
 'StreamReader',
 'StreamWriter',
 'StreamReaderWriter',
 'StreamRecoder',
 'getencoder',
 'getdecoder',
 'getincrementalencoder',
 'getincrementaldecoder',
 'getreader',
 'getwriter',
 'encode',
 'decode',
 'iterencode',
 'iterdecode',
 'strict_errors',
 'ignore_errors',
 'replace_errors',
 'xmlcharrefreplace_errors',
 'backslashreplace_errors',
 'register_error',
 'lookup_error']
BOM_UTF8 = '\xef\xbb\xbf'
BOM_LE = BOM_UTF16_LE = '\xff\xfe'
BOM_BE = BOM_UTF16_BE = '\xfe\xff'
BOM_UTF32_LE = '\xff\xfe\x00\x00'
BOM_UTF32_BE = '\x00\x00\xfe\xff'
if sys.byteorder == 'little':
    BOM = BOM_UTF16 = BOM_UTF16_LE
    BOM_UTF32 = BOM_UTF32_LE
else:
    BOM = BOM_UTF16 = BOM_UTF16_BE
    BOM_UTF32 = BOM_UTF32_BE
BOM32_LE = BOM_UTF16_LE
BOM32_BE = BOM_UTF16_BE
BOM64_LE = BOM_UTF32_LE
BOM64_BE = BOM_UTF32_BE

class CodecInfo(tuple):
    _is_text_encoding = True

    def __new__(cls, encode, decode, streamreader=None, streamwriter=None, incrementalencoder=None, incrementaldecoder=None, name=None, _is_text_encoding=None):
        self = tuple.__new__(cls, (encode,
         decode,
         streamreader,
         streamwriter))
        self.name = name
        self.encode = encode
        self.decode = decode
        self.incrementalencoder = incrementalencoder
        self.incrementaldecoder = incrementaldecoder
        self.streamwriter = streamwriter
        self.streamreader = streamreader
        if _is_text_encoding is not None:
            self._is_text_encoding = _is_text_encoding
        return self

    def __repr__(self):
        return '<%s.%s object for encoding %s at 0x%x>' % (self.__class__.__module__,
         self.__class__.__name__,
         self.name,
         id(self))


class Codec:

    def encode(self, input, errors='strict'):
        raise NotImplementedError

    def decode(self, input, errors='strict'):
        raise NotImplementedError


class IncrementalEncoder(object):

    def __init__(self, errors='strict'):
        self.errors = errors
        self.buffer = ''

    def encode(self, input, final=False):
        raise NotImplementedError

    def reset(self):
        pass

    def getstate(self):
        pass

    def setstate(self, state):
        pass


class BufferedIncrementalEncoder(IncrementalEncoder):

    def __init__(self, errors='strict'):
        IncrementalEncoder.__init__(self, errors)
        self.buffer = ''

    def _buffer_encode(self, input, errors, final):
        raise NotImplementedError

    def encode(self, input, final=False):
        data = self.buffer + input
        result, consumed = self._buffer_encode(data, self.errors, final)
        self.buffer = data[consumed:]
        return result

    def reset(self):
        IncrementalEncoder.reset(self)
        self.buffer = ''

    def getstate(self):
        return self.buffer or 0

    def setstate(self, state):
        self.buffer = state or ''


class IncrementalDecoder(object):

    def __init__(self, errors='strict'):
        self.errors = errors

    def decode(self, input, final=False):
        raise NotImplementedError

    def reset(self):
        pass

    def getstate(self):
        pass

    def setstate(self, state):
        pass


class BufferedIncrementalDecoder(IncrementalDecoder):

    def __init__(self, errors='strict'):
        IncrementalDecoder.__init__(self, errors)
        self.buffer = ''

    def _buffer_decode(self, input, errors, final):
        raise NotImplementedError

    def decode(self, input, final=False):
        data = self.buffer + input
        result, consumed = self._buffer_decode(data, self.errors, final)
        self.buffer = data[consumed:]
        return result

    def reset(self):
        IncrementalDecoder.reset(self)
        self.buffer = ''

    def getstate(self):
        return (self.buffer, 0)

    def setstate(self, state):
        self.buffer = state[0]


class StreamWriter(Codec):

    def __init__(self, stream, errors='strict'):
        self.stream = stream
        self.errors = errors

    def write(self, object):
        data, consumed = self.encode(object, self.errors)
        self.stream.write(data)

    def writelines(self, list):
        self.write(''.join(list))

    def reset(self):
        pass

    def seek(self, offset, whence=0):
        self.stream.seek(offset, whence)
        if whence == 0 and offset == 0:
            self.reset()

    def __getattr__(self, name, getattr=getattr):
        return getattr(self.stream, name)

    def __enter__(self):
        return self

    def __exit__(self, type, value, tb):
        self.stream.close()


class StreamReader(Codec):

    def __init__(self, stream, errors='strict'):
        self.stream = stream
        self.errors = errors
        self.bytebuffer = ''
        self.charbuffer = ''
        self.linebuffer = None
        return

    def decode(self, input, errors='strict'):
        raise NotImplementedError

    def read(self, size=-1, chars=-1, firstline=False):
        if self.linebuffer:
            self.charbuffer = ''.join(self.linebuffer)
            self.linebuffer = None
        if chars < 0:
            chars = size
        while True:
            if chars >= 0:
                if len(self.charbuffer) >= chars:
                    break
            if size < 0:
                newdata = self.stream.read()
            else:
                newdata = self.stream.read(size)
            data = self.bytebuffer + newdata
            try:
                newchars, decodedbytes = self.decode(data, self.errors)
            except UnicodeDecodeError as exc:
                if firstline:
                    newchars, decodedbytes = self.decode(data[:exc.start], self.errors)
                    lines = newchars.splitlines(True)
                    if len(lines) <= 1:
                        raise
                else:
                    raise

            self.bytebuffer = data[decodedbytes:]
            self.charbuffer += newchars
            if not newdata:
                break

        if chars < 0:
            result = self.charbuffer
            self.charbuffer = ''
        else:
            result = self.charbuffer[:chars]
            self.charbuffer = self.charbuffer[chars:]
        return result

    def readline(self, size=None, keepends=True):
        if self.linebuffer:
            line = self.linebuffer[0]
            del self.linebuffer[0]
            if len(self.linebuffer) == 1:
                self.charbuffer = self.linebuffer[0]
                self.linebuffer = None
            if not keepends:
                line = line.splitlines(False)[0]
            return line
        else:
            readsize = size or 72
            line = ''
            while True:
                data = self.read(readsize, firstline=True)
                if data:
                    if data.endswith('\r'):
                        data += self.read(size=1, chars=1)
                line += data
                lines = line.splitlines(True)
                if lines:
                    if len(lines) > 1:
                        line = lines[0]
                        del lines[0]
                        if len(lines) > 1:
                            lines[-1] += self.charbuffer
                            self.linebuffer = lines
                            self.charbuffer = None
                        else:
                            self.charbuffer = lines[0] + self.charbuffer
                        if not keepends:
                            line = line.splitlines(False)[0]
                        break
                    line0withend = lines[0]
                    line0withoutend = lines[0].splitlines(False)[0]
                    if line0withend != line0withoutend:
                        self.charbuffer = ''.join(lines[1:]) + self.charbuffer
                        if keepends:
                            line = line0withend
                        else:
                            line = line0withoutend
                        break
                if not data or size is not None:
                    if line and not keepends:
                        line = line.splitlines(False)[0]
                    break
                if readsize < 8000:
                    readsize *= 2

            return line

    def readlines(self, sizehint=None, keepends=True):
        data = self.read()
        return data.splitlines(keepends)

    def reset(self):
        self.bytebuffer = ''
        self.charbuffer = u''
        self.linebuffer = None
        return

    def seek(self, offset, whence=0):
        self.stream.seek(offset, whence)
        self.reset()

    def next(self):
        line = self.readline()
        if line:
            return line
        raise StopIteration

    def __iter__(self):
        return self

    def __getattr__(self, name, getattr=getattr):
        return getattr(self.stream, name)

    def __enter__(self):
        return self

    def __exit__(self, type, value, tb):
        self.stream.close()


class StreamReaderWriter:
    encoding = 'unknown'

    def __init__(self, stream, Reader, Writer, errors='strict'):
        self.stream = stream
        self.reader = Reader(stream, errors)
        self.writer = Writer(stream, errors)
        self.errors = errors

    def read(self, size=-1):
        return self.reader.read(size)

    def readline(self, size=None):
        return self.reader.readline(size)

    def readlines(self, sizehint=None):
        return self.reader.readlines(sizehint)

    def next(self):
        return self.reader.next()

    def __iter__(self):
        return self

    def write(self, data):
        return self.writer.write(data)

    def writelines(self, list):
        return self.writer.writelines(list)

    def reset(self):
        self.reader.reset()
        self.writer.reset()

    def seek(self, offset, whence=0):
        self.stream.seek(offset, whence)
        self.reader.reset()
        if whence == 0 and offset == 0:
            self.writer.reset()

    def __getattr__(self, name, getattr=getattr):
        return getattr(self.stream, name)

    def __enter__(self):
        return self

    def __exit__(self, type, value, tb):
        self.stream.close()


class StreamRecoder:
    data_encoding = 'unknown'
    file_encoding = 'unknown'

    def __init__(self, stream, encode, decode, Reader, Writer, errors='strict'):
        self.stream = stream
        self.encode = encode
        self.decode = decode
        self.reader = Reader(stream, errors)
        self.writer = Writer(stream, errors)
        self.errors = errors

    def read(self, size=-1):
        data = self.reader.read(size)
        data, bytesencoded = self.encode(data, self.errors)
        return data

    def readline(self, size=None):
        if size is None:
            data = self.reader.readline()
        else:
            data = self.reader.readline(size)
        data, bytesencoded = self.encode(data, self.errors)
        return data

    def readlines(self, sizehint=None):
        data = self.reader.read()
        data, bytesencoded = self.encode(data, self.errors)
        return data.splitlines(1)

    def next(self):
        data = self.reader.next()
        data, bytesencoded = self.encode(data, self.errors)
        return data

    def __iter__(self):
        return self

    def write(self, data):
        data, bytesdecoded = self.decode(data, self.errors)
        return self.writer.write(data)

    def writelines(self, list):
        data = ''.join(list)
        data, bytesdecoded = self.decode(data, self.errors)
        return self.writer.write(data)

    def reset(self):
        self.reader.reset()
        self.writer.reset()

    def __getattr__(self, name, getattr=getattr):
        return getattr(self.stream, name)

    def __enter__(self):
        return self

    def __exit__(self, type, value, tb):
        self.stream.close()


def open(filename, mode='rb', encoding=None, errors='strict', buffering=1):
    if encoding is not None:
        if 'U' in mode:
            mode = mode.strip().replace('U', '')
            if mode[:1] not in set('rwa'):
                mode = 'r' + mode
        if 'b' not in mode:
            mode = mode + 'b'
    file = __builtin__.open(filename, mode, buffering)
    if encoding is None:
        return file
    else:
        info = lookup(encoding)
        srw = StreamReaderWriter(file, info.streamreader, info.streamwriter, errors)
        srw.encoding = encoding
        return srw


def EncodedFile(file, data_encoding, file_encoding=None, errors='strict'):
    if file_encoding is None:
        file_encoding = data_encoding
    data_info = lookup(data_encoding)
    file_info = lookup(file_encoding)
    sr = StreamRecoder(file, data_info.encode, data_info.decode, file_info.streamreader, file_info.streamwriter, errors)
    sr.data_encoding = data_encoding
    sr.file_encoding = file_encoding
    return sr


def getencoder(encoding):
    return lookup(encoding).encode


def getdecoder(encoding):
    return lookup(encoding).decode


def getincrementalencoder(encoding):
    encoder = lookup(encoding).incrementalencoder
    if encoder is None:
        raise LookupError(encoding)
    return encoder


def getincrementaldecoder(encoding):
    decoder = lookup(encoding).incrementaldecoder
    if decoder is None:
        raise LookupError(encoding)
    return decoder


def getreader(encoding):
    return lookup(encoding).streamreader


def getwriter(encoding):
    return lookup(encoding).streamwriter


def iterencode(iterator, encoding, errors='strict', **kwargs):
    encoder = getincrementalencoder(encoding)(errors, **kwargs)
    for input in iterator:
        output = encoder.encode(input)
        if output:
            yield output

    output = encoder.encode('', True)
    if output:
        yield output


def iterdecode(iterator, encoding, errors='strict', **kwargs):
    decoder = getincrementaldecoder(encoding)(errors, **kwargs)
    for input in iterator:
        output = decoder.decode(input)
        if output:
            yield output

    output = decoder.decode('', True)
    if output:
        yield output


def make_identity_dict(rng):
    res = {}
    for i in rng:
        res[i] = i

    return res


def make_encoding_map(decoding_map):
    m = {}
    for k, v in decoding_map.items():
        if v not in m:
            m[v] = k
        m[v] = None

    return m


try:
    strict_errors = lookup_error('strict')
    ignore_errors = lookup_error('ignore')
    replace_errors = lookup_error('replace')
    xmlcharrefreplace_errors = lookup_error('xmlcharrefreplace')
    backslashreplace_errors = lookup_error('backslashreplace')
except LookupError:
    strict_errors = None
    ignore_errors = None
    replace_errors = None
    xmlcharrefreplace_errors = None
    backslashreplace_errors = None

_false = 0
if _false:
    import encodings
if __name__ == '__main__':
    sys.stdout = EncodedFile(sys.stdout, 'latin-1', 'utf-8')
    sys.stdin = EncodedFile(sys.stdin, 'utf-8', 'latin-1')
