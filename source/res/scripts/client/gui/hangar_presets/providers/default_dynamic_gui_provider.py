# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/hangar_presets/providers/default_dynamic_gui_provider.py
from constants import QUEUE_TYPE
from gui.hangar_presets.obsolete.hangar_presets_getters import DefaultPresetsGetter
from gui.hangar_presets.providers.base_dynamic_gui_provider import BaseHangarDynamicGuiProvider
from gui.impl.lobby.hangar.base.vehicle_playlists_helper import DefaultVehiclePlaylistsGuiHelper
from gui.impl.lobby.hangar.presenters.vehicle_menu_entries.vehicle_menu_helper import DefaultHangarVehicleMenuHelper
from gui.impl.lobby.missions.missions_helpers import DefaultMissionsGuiHelper
from gui.Scaleform.daapi.view.lobby.header.helpers.controls_helpers import DefaultLobbyHeaderHelper
from gui.prb_control.prb_helpers import DefaultVehicleAutoSearchHelper

class DefaultHangarDynamicGuiProvider(BaseHangarDynamicGuiProvider):
    _QUEUE_TYPE = QUEUE_TYPE.UNKNOWN
    _LOBBY_HEADER_HELPER = DefaultLobbyHeaderHelper
    _MISSIONS_HELPER = DefaultMissionsGuiHelper
    _PRESETS_GETTER = DefaultPresetsGetter
    _VEHICLE_MENU_HELPER = DefaultHangarVehicleMenuHelper
    _VEHICLE_PLAYLISTS_HELPER = DefaultVehiclePlaylistsGuiHelper
    _VEHICLE_AUTO_SEARCH_HELPER = DefaultVehicleAutoSearchHelper

    def __init__(self, config):
        super(DefaultHangarDynamicGuiProvider, self).__init__(config)
        self._presetGetter = self._PRESETS_GETTER(config.presets.get(config.modes.get(self._QUEUE_TYPE)))

    def getPresetsGetter(self):
        return self._presetGetter
