# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/__init__.py
import os
from gui.Scaleform.locale.MENU import MENU
from nations import NAMES
from skeletons.gui.system_messages import ISystemMessages
SCALEFORM_SUPPORT = False
try:
    import _Scaleform
    SCALEFORM_SUPPORT = True
except ImportError:
    raise NotImplementedError('Client not support Scaleform')

SCALEFORM_SWF_PATH = 'gui/scaleform'
SCALEFORM_SWF_PATH_V3 = 'gui/flash'
SCALEFORM_STARTUP_VIDEO_PATH = 'gui/flash/video'
SCALEFORM_STARTUP_VIDEO_MASK = 'video/%s'
SCALEFORM_WALLPAPER_PATH = 'gui/maps/login'
SCALEFORM_FONT_LIB_PATH = 'gui/flash'
SCALEFORM_FONT_CONFIG_FILE = 'fontconfig.xml'
SCALEFORM_FONT_CONFIG_PATH = 'gui/flash/%s' % SCALEFORM_FONT_CONFIG_FILE
SCALEFORM_DEFAULT_CONFIG_NAME = 'All'
VEHICLE_TYPES_ICONS_DIR_PATH = '../maps/icons/filters/tanks/'
NATION_FILTER_ICONS_DIR_PATH = '../maps/icons/filters/nations/'
BUTTON_FILTER_ICONS_DIR_PARH = '../maps/icons/library/'
LEVEL_FILTER_ICONS_DIR_PARH = '../maps/icons/filters/levels/'
NATIONS_ICON_FILENAME = '../maps/icons/nations/%s_%s.%s'
NATION_ICON_PREFIX_131x31 = '131x31'
DEFAULT_VIDEO_BUFFERING_TIME = 2.0

def getVehicleTypeAssetPath(vehicleType, extension='.png'):
    return ''.join([VEHICLE_TYPES_ICONS_DIR_PATH, vehicleType, extension])


def getButtonsAssetPath(button, extension='.png'):
    return ''.join((BUTTON_FILTER_ICONS_DIR_PARH, button, extension))


def getNationsFilterAssetPath(nationName, extension='.png'):
    return ''.join((NATION_FILTER_ICONS_DIR_PATH, nationName, extension))


def getNationsAssetPath(nation, namePrefix='', extension='png'):
    return NATIONS_ICON_FILENAME % (NAMES[nation], namePrefix, extension)


def getLevelsAssetPath(level_str, extension='.png'):
    return ''.join([LEVEL_FILTER_ICONS_DIR_PARH, level_str, extension])


def getNecessaryArenaFrameName(arenaSubType, hasBase=None):
    return '{0}{1}'.format('assault', '1' if hasBase else '2') if arenaSubType.startswith('assault') else arenaSubType


def getPathForFlash(path, base=SCALEFORM_SWF_PATH_V3):
    return os.path.relpath(path, base)


def getScaleformConfig(manager):
    from gui.Scaleform.SystemMessagesInterface import SystemMessagesInterface
    messages = SystemMessagesInterface()
    messages.init()
    manager.addInstance(ISystemMessages, messages, finalizer='destroy')
