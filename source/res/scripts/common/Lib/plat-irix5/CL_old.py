# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/plat-irix5/CL_old.py
from warnings import warnpy3k
warnpy3k('the CL_old module has been removed in Python 3.0', stacklevel=2)
del warnpy3k
MAX_NUMBER_OF_ORIGINAL_FORMATS = 32
MONO = 0
STEREO_INTERLEAVED = 1
RGB = 0
RGBX = 1
RGBA = 2
RGB332 = 3
GRAYSCALE = 4
Y = 4
YUV = 5
YCbCr = 5
YUV422 = 6
YCbCr422 = 6
YUV422HC = 7
YCbCr422HC = 7
YUV422DC = 7
YCbCr422DC = 7
BEST_FIT = -1

def BytesPerSample(s):
    if s in (MONO, YUV):
        return 2
    elif s == STEREO_INTERLEAVED:
        return 4
    else:
        return 0


def BytesPerPixel(f):
    if f in (RGB, YUV):
        return 3
    elif f in (RGBX, RGBA):
        return 4
    elif f in (RGB332, GRAYSCALE):
        return 1
    else:
        return 2


def AudioFormatName(f):
    if f == MONO:
        return 'MONO'
    elif f == STEREO_INTERLEAVED:
        return 'STEREO_INTERLEAVED'
    else:
        return 'Not a valid format'


def VideoFormatName(f):
    if f == RGB:
        return 'RGB'
    elif f == RGBX:
        return 'RGBX'
    elif f == RGBA:
        return 'RGBA'
    elif f == RGB332:
        return 'RGB332'
    elif f == GRAYSCALE:
        return 'GRAYSCALE'
    elif f == YUV:
        return 'YUV'
    elif f == YUV422:
        return 'YUV422'
    elif f == YUV422DC:
        return 'YUV422DC'
    else:
        return 'Not a valid format'


MAX_NUMBER_OF_AUDIO_ALGORITHMS = 32
MAX_NUMBER_OF_VIDEO_ALGORITHMS = 32
AUDIO = 0
VIDEO = 1

def AlgorithmNumber(scheme):
    return scheme & 32767


def AlgorithmType(scheme):
    return scheme >> 15 & 1


def Algorithm(type, n):
    return n | (type & 1) << 15


UNKNOWN_SCHEME = -1
UNCOMPRESSED_AUDIO = Algorithm(AUDIO, 0)
G711_ULAW = Algorithm(AUDIO, 1)
ULAW = Algorithm(AUDIO, 1)
G711_ALAW = Algorithm(AUDIO, 2)
ALAW = Algorithm(AUDIO, 2)
AWARE_MPEG_AUDIO = Algorithm(AUDIO, 3)
AWARE_MULTIRATE = Algorithm(AUDIO, 4)
UNCOMPRESSED = Algorithm(VIDEO, 0)
UNCOMPRESSED_VIDEO = Algorithm(VIDEO, 0)
RLE = Algorithm(VIDEO, 1)
JPEG = Algorithm(VIDEO, 2)
MPEG_VIDEO = Algorithm(VIDEO, 3)
MVC1 = Algorithm(VIDEO, 4)
RTR = Algorithm(VIDEO, 5)
RTR1 = Algorithm(VIDEO, 5)
MAX_NUMBER_OF_PARAMS = 256
IMAGE_WIDTH = 0
IMAGE_HEIGHT = 1
ORIGINAL_FORMAT = 2
INTERNAL_FORMAT = 3
COMPONENTS = 4
BITS_PER_COMPONENT = 5
FRAME_RATE = 6
COMPRESSION_RATIO = 7
EXACT_COMPRESSION_RATIO = 8
FRAME_BUFFER_SIZE = 9
COMPRESSED_BUFFER_SIZE = 10
BLOCK_SIZE = 11
PREROLL = 12
FRAME_TYPE = 13
ALGORITHM_ID = 14
ALGORITHM_VERSION = 15
ORIENTATION = 16
NUMBER_OF_FRAMES = 17
SPEED = 18
LAST_FRAME_INDEX = 19
NUMBER_OF_PARAMS = 20
QUALITY_FACTOR = NUMBER_OF_PARAMS + 0
END_OF_SEQUENCE = NUMBER_OF_PARAMS + 0
QUALITY_LEVEL = NUMBER_OF_PARAMS + 0
ZOOM_X = NUMBER_OF_PARAMS + 1
ZOOM_Y = NUMBER_OF_PARAMS + 2
ENUM_VALUE = 0
RANGE_VALUE = 1
FLOATING_ENUM_VALUE = 2
FLOATING_RANGE_VALUE = 3
DECOMPRESSOR = 1
COMPRESSOR = 2
CODEC = 3
NONE = 0
FRAME = 1
DATA = 2
NONE = 0
KEYFRAME = 1
INTRA = 1
PREDICTED = 2
BIDIRECTIONAL = 3
TOP_DOWN = 0
BOTTOM_UP = 1
HEADER_START_CODE = 203165164
BAD_NO_BUFFERSPACE = -2
BAD_PVBUFFER = -3
BAD_BUFFERLENGTH_NEG = -4
BAD_BUFFERLENGTH_ODD = -5
BAD_PARAM = -6
BAD_COMPRESSION_SCHEME = -7
BAD_COMPRESSOR_HANDLE = -8
BAD_COMPRESSOR_HANDLE_POINTER = -9
BAD_BUFFER_HANDLE = -10
BAD_BUFFER_QUERY_SIZE = -11
JPEG_ERROR = -12
BAD_FRAME_SIZE = -13
PARAM_OUT_OF_RANGE = -14
ADDED_ALGORITHM_ERROR = -15
BAD_ALGORITHM_TYPE = -16
BAD_ALGORITHM_NAME = -17
BAD_BUFFERING = -18
BUFFER_NOT_CREATED = -19
BAD_BUFFER_EXISTS = -20
BAD_INTERNAL_FORMAT = -21
BAD_BUFFER_POINTER = -22
FRAME_BUFFER_SIZE_ZERO = -23
BAD_STREAM_HEADER = -24
BAD_LICENSE = -25
AWARE_ERROR = -26
