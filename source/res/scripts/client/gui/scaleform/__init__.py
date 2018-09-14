# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/__init__.py
import os
from nations import NAMES
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
BUTTON_FILTER_ICONS_DIR_PARH = '../maps/icons/filters/buttons/'
LEVEL_FILTER_ICONS_DIR_PARH = '../maps/icons/filters/levels/'
NATIONS_ICON_FILENAME = '../maps/icons/nations/%s_%s.%s'
NATION_ICON_PREFIX_131x31 = '131x31'

def getVehicleTypeAssetPath(vehicleType, extension='.png'):
    return ''.join([VEHICLE_TYPES_ICONS_DIR_PATH, vehicleType, extension])


def getButtonsAssetPath(button, extension='.png'):
    return ''.join([BUTTON_FILTER_ICONS_DIR_PARH, button, extension])


def getNationsFilterAssetPath(nationName, extension='.png'):
    return ''.join([NATION_FILTER_ICONS_DIR_PATH, nationName, extension])


def getNationsAssetPath(nation, namePrefix='', extension='png'):
    return NATIONS_ICON_FILENAME % (NAMES[nation], namePrefix, extension)


def getLevelsAssetPath(level, extension='.png'):
    return ''.join([LEVEL_FILTER_ICONS_DIR_PARH, 'level_%d' % level, extension])


def getNecessaryArenaFrameName(arenaSubType, hasBase=None):
    return '{0}{1}'.format('assault', '1' if hasBase else '2') if arenaSubType.startswith('assault') else arenaSubType


def getPathForFlash(path, base=SCALEFORM_SWF_PATH_V3):
    """
    Converts resource path to relative one, which can be used in flash
    Example:
    gui/maps/icons/map/screen/86_himmelsdorf_winter.dds -> ../maps/icons/map/screen/86_himmelsdorf_winter.dds
    
    :param path: relative path which is relative to resources folder (res/wot)
    :param base: path which should be used as starting point
    :return: relative path from specified starting point
    """
    return os.path.relpath(path, base)
