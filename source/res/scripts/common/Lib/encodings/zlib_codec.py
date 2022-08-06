# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/encodings/zlib_codec.py
import codecs
import zlib

def zlib_encode(input, errors='strict'):
    output = zlib.compress(input)
    return (output, len(input))


def zlib_decode(input, errors='strict'):
    output = zlib.decompress(input)
    return (output, len(input))


class Codec(codecs.Codec):

    def encode(self, input, errors='strict'):
        return zlib_encode(input, errors)

    def decode(self, input, errors='strict'):
        return zlib_decode(input, errors)


class IncrementalEncoder(codecs.IncrementalEncoder):

    def __init__(self, errors='strict'):
        self.errors = errors
        self.compressobj = zlib.compressobj()

    def encode(self, input, final=False):
        if final:
            c = self.compressobj.compress(input)
            return c + self.compressobj.flush()
        else:
            return self.compressobj.compress(input)

    def reset(self):
        self.compressobj = zlib.compressobj()


class IncrementalDecoder(codecs.IncrementalDecoder):

    def __init__(self, errors='strict'):
        self.errors = errors
        self.decompressobj = zlib.decompressobj()

    def decode(self, input, final=False):
        if final:
            c = self.decompressobj.decompress(input)
            return c + self.decompressobj.flush()
        else:
            return self.decompressobj.decompress(input)

    def reset(self):
        self.decompressobj = zlib.decompressobj()


class StreamWriter(Codec, codecs.StreamWriter):
    pass


class StreamReader(Codec, codecs.StreamReader):
    pass


def getregentry():
    return codecs.CodecInfo(name='zlib', encode=zlib_encode, decode=zlib_decode, incrementalencoder=IncrementalEncoder, incrementaldecoder=IncrementalDecoder, streamreader=StreamReader, streamwriter=StreamWriter, _is_text_encoding=False)
