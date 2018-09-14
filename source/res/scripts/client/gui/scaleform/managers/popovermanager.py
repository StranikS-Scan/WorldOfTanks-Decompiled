# Embedded file name: scripts/client/gui/Scaleform/managers/PopoverManager.py
from gui.Scaleform.framework import g_entitiesFactories
from gui.Scaleform.framework.entities.abstract.PopoverManagerMeta import PopoverManagerMeta
from gui.shared.events import HidePopoverEvent

class PopoverManager(PopoverManagerMeta):

    def __init__(self, scope):
        super(PopoverManager, self).__init__()
        self.__scope = scope
        self.addListener(HidePopoverEvent.POPOVER_DESTROYED, self.__handlerDestroyPopover)

    def requestShowPopover(self, alias, data):
        self.fireEvent(g_entitiesFactories.makeShowPopoverEvent(alias, {'data': data}), self.__scope)

    def requestHidePopover(self):
        self.fireEvent(HidePopoverEvent(HidePopoverEvent.HIDE_POPOVER))

    def destroy(self):
        self.removeListener(HidePopoverEvent.POPOVER_DESTROYED, self.__handlerDestroyPopover)
        super(PopoverManager, self).destroy()

    def __handlerDestroyPopover(self, _):
        self.as_onPopoverDestroyS()
