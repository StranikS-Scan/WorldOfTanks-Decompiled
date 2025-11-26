# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/hangar_presets/providers/event_dynamic_gui_provider.py
from constants import QUEUE_TYPE, ARENA_BONUS_TYPE
from gui.Scaleform.daapi.view.lobby.header.helpers.controls_helpers import EventLobbyHeaderHelper
from gui.hangar_presets.providers import DefaultHangarDynamicGuiProvider

class EventHangarDynamicGuiProvider(DefaultHangarDynamicGuiProvider):
    _QUEUE_TYPE = QUEUE_TYPE.EVENT_BATTLES
    _BONUS_TYPES = (ARENA_BONUS_TYPE.EVENT_BATTLES, ARENA_BONUS_TYPE.EVENT_BATTLES_2)
    _LOBBY_HEADER_HELPER = EventLobbyHeaderHelper

    def getLobbyHeaderHelper(self):
        return self._LOBBY_HEADER_HELPER(self.getSuggestedBonusType(), self.getBonusCapsOverrides())
