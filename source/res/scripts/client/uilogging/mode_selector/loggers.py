# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/uilogging/mode_selector/loggers.py
import typing
from gui.Scaleform.daapi.view.lobby.header import battle_selector_items
from gui.prb_control.dispatcher import g_prbLoader
from uilogging.base.logger import BaseLogger, ifUILoggingEnabled
from uilogging.base.mixins import TimedActionMixin
from uilogging.mode_selector.constants import FEATURE, LOG_ACTIONS, LOG_KEYS
from wotdecorators import noexcept
if typing.TYPE_CHECKING:
    from typing import Optional
    from gui.Scaleform.daapi.view.lobby.header.battle_selector_items import _SelectorItem
_TOOLTIP_TIME_LIMIT = 2.0

class BaseModeSelectorLogger(BaseLogger):
    __slots__ = ()

    def __init__(self, group):
        super(BaseModeSelectorLogger, self).__init__(FEATURE, group)

    @noexcept
    @ifUILoggingEnabled()
    def log(self, action, isNew=None, isWidget=None, isFeatured=None, details=None, mode=None, prevMode=None, tooltip=None, size=None, isSelected=None):
        data = {'is_new': isNew,
         'is_widget': isWidget,
         'is_featured': isFeatured,
         'details': details,
         'mode': mode,
         'prev_mode': prevMode,
         'tooltip': tooltip,
         'size': size,
         'is_selected': isSelected}
        strippedNones = {k:v for k, v in data.items() if v is not None}
        super(BaseModeSelectorLogger, self).log(action, **strippedNones)


class ModeSelectorEntryPointLogger(TimedActionMixin, BaseLogger):
    __slots__ = ('__prevMode', '__openedTooltip')

    def __init__(self):
        super(ModeSelectorEntryPointLogger, self).__init__(FEATURE, LOG_KEYS.ENTRY_POINT)
        self.__openedTooltip = None
        self.__prevMode = None
        return

    @noexcept
    @ifUILoggingEnabled()
    def initialize(self):
        self.__prevMode = self.__getSelectedModeName()

    @noexcept
    def reset(self):
        super(ModeSelectorEntryPointLogger, self).reset()
        self.__openedTooltip = None
        self.__prevMode = None
        return

    @noexcept
    @ifUILoggingEnabled()
    def tooltipOpened(self, tooltip):
        self.__openedTooltip = tooltip
        self.startAction(LOG_ACTIONS.TOOLTIP_WATCHED)

    @noexcept
    @ifUILoggingEnabled()
    def tooltipClosed(self, tooltip):
        if self.__openedTooltip and self.__openedTooltip == tooltip:
            self.__openedTooltip = None
            self.stopAction(LOG_ACTIONS.TOOLTIP_WATCHED, tooltip=tooltip, timeLimit=_TOOLTIP_TIME_LIMIT)
        return

    @noexcept
    @ifUILoggingEnabled()
    def onPrbEntitySwitched(self):
        newMode = self.__getSelectedModeName()
        if newMode != self.__prevMode:
            if self.__prevMode and newMode:
                self.log(LOG_ACTIONS.CHANGED, prevMode=self.__prevMode, mode=newMode)
                self.__prevMode = newMode

    @staticmethod
    def __getSelectedModeName():
        dispatcher = g_prbLoader.getDispatcher()
        if dispatcher is None:
            return
        else:
            state = g_prbLoader.getDispatcher().getFunctionalState()
            selected = battle_selector_items.getItems().update(state)
            return selected.getData() if selected else None
