# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/dict2model/extensions/color.py
from __future__ import absolute_import
from Math import Vector4
from dict2model import models, validate
from dict2model.fields import Float, HexColorCode
from dict2model.schemas import Schema

class ColorModel(models.Model):
    __slots__ = ('code', 'alpha', '__red', '__green', '__blue')

    def __init__(self, code, alpha):
        super(ColorModel, self).__init__()
        self.code = code
        self.alpha = alpha
        self.__red = int(code[1:3], 16)
        self.__green = int(code[3:5], 16)
        self.__blue = int(code[5:7], 16)

    @property
    def red(self):
        return self.__red

    @property
    def green(self):
        return self.__green

    @property
    def blue(self):
        return self.__blue

    def toFloats(self):
        return Vector4(self.__red / 255.0, self.__green / 255.0, self.__blue / 255.0, self.alpha)

    def _reprArgs(self):
        return 'code={}, alpha={}'.format(self.code, self.alpha)


colorSchema = Schema(fields={'code': HexColorCode(),
 'alpha': Float(required=False, default=1.0, deserializedValidators=validate.Range(0.0, 1.0))}, modelClass=ColorModel)
