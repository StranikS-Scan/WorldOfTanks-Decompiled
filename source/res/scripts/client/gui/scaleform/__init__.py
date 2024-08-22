# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/__init__.py
import os
from gui.Scaleform.locale.MENU import MENU
from nations import NAMES
from skeletons.gui.system_messages import ISystemMessages
from skeletons.gui.techtree_events import ITechTreeEventsListener
SCALEFORM_SUPPORT = False
try:
    import _Scaleform
    SCALEFORM_SUPPORT = True
except ImportError:
    raise NotImplementedError('Client not support Scaleform')

SCALEFORM_SWF_PATH_V3 = 'gui/flash'
VEHICLE_TYPES_ICONS_DIR_PATH = '../maps/icons/filters/tanks/'
NATION_FILTER_ICONS_DIR_PATH = '../maps/icons/filters/nations/'
BUTTON_FILTER_ICONS_DIR_PARH = '../maps/icons/library/'
LEVEL_FILTER_ICONS_DIR_PARH = '../maps/icons/filters/levels/'
DEFAULT_VIDEO_BUFFERING_TIME = 2.0

def getVehicleTypeAssetPath(vehicleType, extension='.png'):
    return ''.join([VEHICLE_TYPES_ICONS_DIR_PATH, vehicleType, extension])


def getButtonsAssetPath(button, extension='.png'):
    return ''.join((BUTTON_FILTER_ICONS_DIR_PARH, button, extension))


def getNationsFilterAssetPath(nationName, extension='.png'):
    return ''.join((NATION_FILTER_ICONS_DIR_PATH, nationName, extension))


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
    from gui.Scaleform.daapi.view.lobby.techtree.techtree_events import TechTreeEventsListener
    listener = TechTreeEventsListener()
    listener.init()
    manager.addInstance(ITechTreeEventsListener, listener, finalizer='fini')
