# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/scaleform/daapi/view/lobby/tank_setup/__init__.py
from last_stand.gui.scaleform.genConsts.LS_CM_HANDLER_TYPE import LS_CM_HANDLER_TYPE
from last_stand.gui.scaleform.daapi.view.lobby.tank_setup.context_menu.consumable import LSHangarConsumableSlotContextMenu

def getContextMenuHandlers():
    return ((LS_CM_HANDLER_TYPE.TANK_SETUP_LS_HANGAR_CONSUMABLE_SLOT, LSHangarConsumableSlotContextMenu),)


def getViewSettings():
    pass


def getBusinessHandlers():
    pass
