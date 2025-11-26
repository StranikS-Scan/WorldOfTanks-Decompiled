# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/hangar_presets/providers/ranked_dynamic_gui_provider.py
from constants import QUEUE_TYPE, ARENA_BONUS_TYPE
from gui.hangar_presets.obsolete.hangar_presets_getters import RankedPresetsGetter
from gui.hangar_presets.providers import DefaultHangarDynamicGuiProvider
from gui.Scaleform.daapi.view.lobby.header.helpers.controls_helpers import RankedLobbyHeaderHelper

class RankedHangarDynamicGuiProvider(DefaultHangarDynamicGuiProvider):
    _QUEUE_TYPE = QUEUE_TYPE.RANKED
    _BONUS_TYPES = (ARENA_BONUS_TYPE.RANKED,)
    _LOBBY_HEADER_HELPER = RankedLobbyHeaderHelper
    _PRESETS_GETTER = RankedPresetsGetter
