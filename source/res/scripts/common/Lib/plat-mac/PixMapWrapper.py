# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/plat-mac/PixMapWrapper.py
from warnings import warnpy3k
warnpy3k('In 3.x, the PixMapWrapper module is removed.', stacklevel=2)
from Carbon import Qd
from Carbon import QuickDraw
import struct
import MacOS
import img
import imgformat
_pmElemFormat = {'baseAddr': 'l',
 'rowBytes': 'H',
 'bounds': 'hhhh',
 'top': 'h',
 'left': 'h',
 'bottom': 'h',
 'right': 'h',
 'pmVersion': 'h',
 'packType': 'h',
 'packSize': 'l',
 'hRes': 'l',
 'vRes': 'l',
 'pixelType': 'h',
 'pixelSize': 'h',
 'cmpCount': 'h',
 'cmpSize': 'h',
 'planeBytes': 'l',
 'pmTable': 'l',
 'pmReserved': 'l'}
_pmElemOffset = {'baseAddr': 0,
 'rowBytes': 4,
 'bounds': 6,
 'top': 6,
 'left': 8,
 'bottom': 10,
 'right': 12,
 'pmVersion': 14,
 'packType': 16,
 'packSize': 18,
 'hRes': 22,
 'vRes': 26,
 'pixelType': 30,
 'pixelSize': 32,
 'cmpCount': 34,
 'cmpSize': 36,
 'planeBytes': 38,
 'pmTable': 42,
 'pmReserved': 46}

class PixMapWrapper:

    def __init__(self):
        self.__dict__['data'] = ''
        self._header = struct.pack('lhhhhhhhlllhhhhlll', id(self.data) + MacOS.string_id_to_buffer, 0, 0, 0, 0, 0, 0, 0, 0, 4718592, 4718592, QuickDraw.RGBDirect, 16, 2, 5, 0, 0, 0)
        self.__dict__['_pm'] = Qd.RawBitMap(self._header)

    def _stuff(self, element, bytes):
        offset = _pmElemOffset[element]
        fmt = _pmElemFormat[element]
        self._header = self._header[:offset] + struct.pack(fmt, bytes) + self._header[offset + struct.calcsize(fmt):]
        self.__dict__['_pm'] = None
        return

    def _unstuff(self, element):
        offset = _pmElemOffset[element]
        fmt = _pmElemFormat[element]
        return struct.unpack(fmt, self._header[offset:offset + struct.calcsize(fmt)])[0]

    def __setattr__(self, attr, val):
        if attr == 'baseAddr':
            raise 'UseErr', "don't assign to .baseAddr -- assign to .data instead"
        elif attr == 'data':
            self.__dict__['data'] = val
            self._stuff('baseAddr', id(self.data) + MacOS.string_id_to_buffer)
        elif attr == 'rowBytes':
            self._stuff('rowBytes', val | 32768)
        elif attr == 'bounds':
            self._stuff('left', val[0])
            self._stuff('top', val[1])
            self._stuff('right', val[2])
            self._stuff('bottom', val[3])
        elif attr == 'hRes' or attr == 'vRes':
            self._stuff(attr, int(val) << 16)
        elif attr in _pmElemFormat.keys():
            self._stuff(attr, val)
        else:
            self.__dict__[attr] = val

    def __getattr__(self, attr):
        if attr == 'rowBytes':
            return self._unstuff('rowBytes') & 32767
        elif attr == 'bounds':
            return (self._unstuff('left'),
             self._unstuff('top'),
             self._unstuff('right'),
             self._unstuff('bottom'))
        elif attr == 'hRes' or attr == 'vRes':
            return self._unstuff(attr) >> 16
        elif attr in _pmElemFormat.keys():
            return self._unstuff(attr)
        else:
            return self.__dict__[attr]

    def PixMap(self):
        if not self.__dict__['_pm']:
            self.__dict__['_pm'] = Qd.RawBitMap(self._header)
        return self.__dict__['_pm']

    def blit(self, x1=0, y1=0, x2=None, y2=None, port=None):
        src = self.bounds
        dest = [x1,
         y1,
         x2,
         y2]
        if x2 is None:
            dest[2] = x1 + src[2] - src[0]
        if y2 is None:
            dest[3] = y1 + src[3] - src[1]
        if not port:
            port = Qd.GetPort()
        Qd.CopyBits(self.PixMap(), port.GetPortBitMapForCopyBits(), src, tuple(dest), QuickDraw.srcCopy, None)
        return

    def fromstring(self, s, width, height, format=imgformat.macrgb):
        if format != imgformat.macrgb and format != imgformat.macrgb16:
            raise 'NotImplementedError', 'conversion to macrgb or macrgb16'
        self.data = s
        self.bounds = (0,
         0,
         width,
         height)
        self.cmpCount = 3
        self.pixelType = QuickDraw.RGBDirect
        if format == imgformat.macrgb:
            self.pixelSize = 32
            self.cmpSize = 8
        else:
            self.pixelSize = 16
            self.cmpSize = 5
        self.rowBytes = width * self.pixelSize / 8

    def tostring(self, format=imgformat.macrgb):
        if format == imgformat.macrgb and self.pixelSize == 32 or format == imgformat.macrgb16 and self.pixelsize == 16:
            return self.data
            raise 'NotImplementedError', 'data format conversion'

    def fromImage(self, im):
        if im.mode != 'RGBA':
            im = im.convert('RGBA')
        data = chr(0) + im.tostring()
        self.fromstring(data, im.size[0], im.size[1])

    def toImage(self):
        import Image
        data = self.tostring()[1:] + chr(0)
        bounds = self.bounds
        return Image.fromstring('RGBA', (bounds[2] - bounds[0], bounds[3] - bounds[1]), data)


def test():
    import MacOS
    import EasyDialogs
    import Image
    path = EasyDialogs.AskFileForOpen('Image File:')
    if not path:
        return
    pm = PixMapWrapper()
    pm.fromImage(Image.open(path))
    pm.blit(20, 20)
    return pm
