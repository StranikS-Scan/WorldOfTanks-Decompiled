# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/encodings/rot_13.py
import codecs

class Codec(codecs.Codec):

    def encode(self, input, errors='strict'):
        return codecs.charmap_encode(input, errors, encoding_map)

    def decode(self, input, errors='strict'):
        return codecs.charmap_decode(input, errors, decoding_map)


class IncrementalEncoder(codecs.IncrementalEncoder):

    def encode(self, input, final=False):
        return codecs.charmap_encode(input, self.errors, encoding_map)[0]


class IncrementalDecoder(codecs.IncrementalDecoder):

    def decode(self, input, final=False):
        return codecs.charmap_decode(input, self.errors, decoding_map)[0]


class StreamWriter(Codec, codecs.StreamWriter):
    pass


class StreamReader(Codec, codecs.StreamReader):
    pass


def getregentry():
    return codecs.CodecInfo(name='rot-13', encode=Codec().encode, decode=Codec().decode, incrementalencoder=IncrementalEncoder, incrementaldecoder=IncrementalDecoder, streamwriter=StreamWriter, streamreader=StreamReader)


decoding_map = codecs.make_identity_dict(range(256))
decoding_map.update({65: 78,
 66: 79,
 67: 80,
 68: 81,
 69: 82,
 70: 83,
 71: 84,
 72: 85,
 73: 86,
 74: 87,
 75: 88,
 76: 89,
 77: 90,
 78: 65,
 79: 66,
 80: 67,
 81: 68,
 82: 69,
 83: 70,
 84: 71,
 85: 72,
 86: 73,
 87: 74,
 88: 75,
 89: 76,
 90: 77,
 97: 110,
 98: 111,
 99: 112,
 100: 113,
 101: 114,
 102: 115,
 103: 116,
 104: 117,
 105: 118,
 106: 119,
 107: 120,
 108: 121,
 109: 122,
 110: 97,
 111: 98,
 112: 99,
 113: 100,
 114: 101,
 115: 102,
 116: 103,
 117: 104,
 118: 105,
 119: 106,
 120: 107,
 121: 108,
 122: 109})
encoding_map = codecs.make_encoding_map(decoding_map)

def rot13(infile, outfile):
    outfile.write(infile.read().encode('rot-13'))


if __name__ == '__main__':
    import sys
    rot13(sys.stdin, sys.stdout)
