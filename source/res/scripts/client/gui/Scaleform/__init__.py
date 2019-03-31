# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/__init__.py
# Compiled at: 2019-01-18 14:45:16
from types import InstanceType
SCALEFORM_SUPPORT = False
try:
    import _Scaleform
    SCALEFORM_SUPPORT = True
except ImportError:
    raise NotImplementedError, 'Client not support Scaleform'

SCALEFORM_SWF_PATH = 'gui/flash'
SCALEFORM_STARTUP_VIDEO_PATH = 'gui/flash/video'
SCALEFORM_STARTUP_VIDEO_MASK = 'video/%s'
SCALEFORM_FONT_LIB_PATH = 'gui/flash'
SCALEFORM_FONT_CONFIG_FILE = 'fontconfig.xml'
SCALEFORM_FONT_CONFIG_PATH = 'gui/flash/%s' % SCALEFORM_FONT_CONFIG_FILE
SCALEFORM_DEFAULT_CONFIG_NAME = 'All'

class FEATURES(object):
    MINIMAP_SIZE = True
    GOLD_TRANSFER = False
    VOICE_CHAT = True
    TECHNICAL_INFO = True
    CUSTOMIZATION_CAMOUFLAGES = True
    CUSTOMIZATION_HORNS = False
    MARKER_HIT_SPLASH_DURATION = 1000
    MARKER_SCALE_SETTINGS = (40, 100, 100, 3.0)
    MARKER_BG_SETTINGS = (0, 100, 100, 3.0)


class VehicleActions(object):
    """
    Represent vehicleActionMarker convertion action to bitMask
    """
    __ACTIONS = {'hunting': 1}

    @staticmethod
    def getBitMask(actions):
        bitMask = 0
        for key, value in actions.items():
            mask = VehicleActions.__ACTIONS.get(key, 0)
            if isinstance(mask, dict):
                mask = mask.get(value, 0)
            bitMask |= mask

        return bitMask

    @staticmethod
    def isHunting(actions):
        return 'hunting' in actions.keys()
