# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/scaleform/daapi/view/lobby/tank_setup/__init__.py
from __future__ import absolute_import
from halloween.gui.scaleform.genConsts.HALLOWEEN_CM_HANDLER_TYPE import HALLOWEEN_CM_HANDLER_TYPE
from halloween.gui.scaleform.daapi.view.lobby.tank_setup.context_menu.consumable import HWHangarConsumableSlotContextMenu

def getContextMenuHandlers():
    return ((HALLOWEEN_CM_HANDLER_TYPE.TANK_SETUP_HW_HANGAR_CONSUMABLE_SLOT, HWHangarConsumableSlotContextMenu),)


def getViewSettings():
    pass


def getBusinessHandlers():
    pass
