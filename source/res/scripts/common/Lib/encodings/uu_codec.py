# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/encodings/uu_codec.py
import codecs, binascii

def uu_encode(input, errors='strict', filename='<data>', mode=438):
    from cStringIO import StringIO
    from binascii import b2a_uu
    infile = StringIO(str(input))
    outfile = StringIO()
    read = infile.read
    write = outfile.write
    filename = filename.replace('\n', '\\n')
    filename = filename.replace('\r', '\\r')
    write('begin %o %s\n' % (mode & 511, filename))
    chunk = read(45)
    while chunk:
        write(b2a_uu(chunk))
        chunk = read(45)

    write(' \nend\n')
    return (outfile.getvalue(), len(input))


def uu_decode(input, errors='strict'):
    from cStringIO import StringIO
    from binascii import a2b_uu
    infile = StringIO(str(input))
    outfile = StringIO()
    readline = infile.readline
    write = outfile.write
    while 1:
        s = readline()
        if not s:
            raise ValueError, 'Missing "begin" line in input data'
        if s[:5] == 'begin':
            break

    while 1:
        s = readline()
        if not s or s == 'end\n':
            break
        try:
            data = a2b_uu(s)
        except binascii.Error as v:
            nbytes = ((ord(s[0]) - 32 & 63) * 4 + 5) // 3
            data = a2b_uu(s[:nbytes])

        write(data)

    if not s:
        raise ValueError, 'Truncated input data'
    return (outfile.getvalue(), len(input))


class Codec(codecs.Codec):

    def encode(self, input, errors='strict'):
        return uu_encode(input, errors)

    def decode(self, input, errors='strict'):
        return uu_decode(input, errors)


class IncrementalEncoder(codecs.IncrementalEncoder):

    def encode(self, input, final=False):
        return uu_encode(input, self.errors)[0]


class IncrementalDecoder(codecs.IncrementalDecoder):

    def decode(self, input, final=False):
        return uu_decode(input, self.errors)[0]


class StreamWriter(Codec, codecs.StreamWriter):
    pass


class StreamReader(Codec, codecs.StreamReader):
    pass


def getregentry():
    return codecs.CodecInfo(name='uu', encode=uu_encode, decode=uu_decode, incrementalencoder=IncrementalEncoder, incrementaldecoder=IncrementalDecoder, streamreader=StreamReader, streamwriter=StreamWriter, _is_text_encoding=False)
