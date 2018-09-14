# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/managers/PopoverManager.py
from debug_utils import LOG_ERROR
from gui.Scaleform.framework import g_entitiesFactories
from gui.Scaleform.framework.entities.abstract.PopoverManagerMeta import PopoverManagerMeta
from gui.shared.events import HidePopoverEvent
from constants import IS_BOOTCAMP_ENABLED

class PopoverManager(PopoverManagerMeta):

    def __init__(self, scope):
        super(PopoverManager, self).__init__()
        self.__scope = scope
        self.addListener(HidePopoverEvent.POPOVER_DESTROYED, self.__handlerDestroyPopover)

    def requestShowPopover(self, alias, data):
        if IS_BOOTCAMP_ENABLED:
            from bootcamp.Bootcamp import g_bootcamp
            if g_bootcamp.isRunning():
                if data is not None and hasattr(data, 'slotType') and data.slotType != 'optionalDevice' and not g_bootcamp.isResearchFreeLesson():
                    return
                if data is None and alias != 'bootcampBattleTypeSelectPopover':
                    return
        event = g_entitiesFactories.makeShowPopoverEvent(alias, {'data': data})
        if event is not None:
            self.fireEvent(event, scope=self.__scope)
        else:
            LOG_ERROR('Event of opening popover can not be created', alias)
        return

    def requestHidePopover(self):
        self.fireEvent(HidePopoverEvent(HidePopoverEvent.HIDE_POPOVER))

    def destroy(self):
        self.removeListener(HidePopoverEvent.POPOVER_DESTROYED, self.__handlerDestroyPopover)
        super(PopoverManager, self).destroy()

    def __handlerDestroyPopover(self, _):
        self.as_onPopoverDestroyS()
