# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/hangar_presets/providers/mapbox_dynamic_gui_provider.py
from constants import QUEUE_TYPE, ARENA_BONUS_TYPE
from gui.hangar_presets.obsolete.hangar_presets_getters import MapboxPresetsGetter
from gui.hangar_presets.providers import DefaultHangarDynamicGuiProvider
from gui.impl.lobby.missions.missions_helpers import MapboxMissionsGuiHelper
from gui.Scaleform.daapi.view.lobby.header.helpers.controls_helpers import MapboxLobbyHeaderHelper

class MapboxHangarDynamicGuiProvider(DefaultHangarDynamicGuiProvider):
    _QUEUE_TYPE = QUEUE_TYPE.MAPBOX
    _BONUS_TYPES = (ARENA_BONUS_TYPE.MAPBOX,)
    _LOBBY_HEADER_HELPER = MapboxLobbyHeaderHelper
    _MISSIONS_HELPER = MapboxMissionsGuiHelper
    _PRESETS_GETTER = MapboxPresetsGetter
