# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/new_year/ui_switcher.py
from functools import partial
from .abstract_switch_handler import AbstractSwitchHandler
from .mappings import Mappings, UiStates
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS

class UiSwitcher(AbstractSwitchHandler):

    def switchTo(self, state, callback=None):
        if all((s in Mappings.ANCHOR_TO_ID for s in (self._state, state))):
            switch = partial(super(UiSwitcher, self).switchTo, state)
        else:
            switch = partial(self.__onSwitch, self._state)
        self._state = state
        switch()
        if callback is not None:
            callback()
        return

    def __onSwitch(self, prevState):
        if self._state in Mappings.ANCHOR_TO_ID:
            ctx = {'previewAlias': VIEW_ALIAS.LOBBY_HANGAR,
             'tabId': Mappings.ANCHOR_TO_ID[self._state]}
            g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.LOBBY_NY_SCREEN, ctx=ctx), EVENT_BUS_SCOPE.LOBBY)
        super(UiSwitcher, self).switchTo(self._state)
