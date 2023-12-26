# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/graphics_optimization_controller/utils.py
import Math
import typing
PERMANENT_SETTING_ID = ''

class OptimizationSetting(object):
    __slots__ = ('__id', '__isInvert')

    def __init__(self, settingID=PERMANENT_SETTING_ID, isInvert=False):
        super(OptimizationSetting, self).__init__()
        self.__id = settingID
        self.__isInvert = isInvert

    @property
    def id(self):
        return self.__id

    @property
    def isInvert(self):
        return self.__isInvert


def getRectBounds(x, y, width, height):
    x, y, width, height = (int(x),
     int(y),
     int(width),
     int(height))
    return Math.Vector4(x, y, x + width, y + height)


def rescaleRectBounds(scale, x, y, width, height):
    return (x * scale,
     y * scale,
     width * scale,
     height * scale)


def getSettingsNames(config):
    return set([ setting.id for setting in config.itervalues() if setting.id != PERMANENT_SETTING_ID ])
