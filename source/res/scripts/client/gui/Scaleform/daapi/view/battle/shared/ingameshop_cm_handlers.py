# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/ingameshop_cm_handlers.py
from gui.Scaleform.framework.entities.EventSystemEntity import EventSystemEntity
from gui.Scaleform.framework.managers.context_menu import AbstractContextMenuHandler
from gui.Scaleform.locale.MENU import MENU
from gui.shared import events, EVENT_BUS_SCOPE

class MODULE(object):
    UNEQUIP = 'unequip'
    UNLOAD = 'unload'


class IngameShopCMHandler(AbstractContextMenuHandler, EventSystemEntity):

    def __init__(self, cmProxy, ctx=None):
        super(IngameShopCMHandler, self).__init__(cmProxy, ctx, {MODULE.UNEQUIP: 'resetSlot',
         MODULE.UNLOAD: 'resetSlot'})

    def resetSlot(self):
        self.fireEvent(events.TechnicalMaintenanceEvent(events.TechnicalMaintenanceEvent.RESET_EQUIPMENT, ctx={'eqCD': self._equipmentCD}), scope=EVENT_BUS_SCOPE.LOBBY)

    def _initFlashValues(self, ctx):
        self._equipmentCD = ctx.equipmentCD
        self._isCanceled = bool(ctx.isCanceled)

    def _clearFlashValues(self):
        self._equipmentCD = None
        self._isCanceled = None
        return

    def _generateOptions(self, ctx=None):
        options = []
        if self._isCanceled:
            options.append(self._makeItem(MODULE.UNEQUIP, MENU.contextmenu(MODULE.UNEQUIP)))
        else:
            options.append(self._makeItem(MODULE.UNLOAD, MENU.contextmenu(MODULE.UNLOAD)))
        return options
