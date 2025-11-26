# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_light/scripts/client/comp7_light/gui/hangar_presets/comp7_light_dynamic_gui_provider.py
from comp7_light.gui.Scaleform.daapi.view.lobby.header.helpers.controls_helpers import Comp7LightLobbyHeaderHelper
from comp7_light.gui.impl.lobby.missions.missions_helpers import Comp7LightMissionsGuiHelper
from constants import QUEUE_TYPE, ARENA_BONUS_TYPE
from gui.hangar_presets.providers.default_dynamic_gui_provider import DefaultHangarDynamicGuiProvider

class Comp7LightHangarDynamicGuiProvider(DefaultHangarDynamicGuiProvider):
    _QUEUE_TYPE = QUEUE_TYPE.COMP7_LIGHT
    _BONUS_TYPES = (ARENA_BONUS_TYPE.COMP7_LIGHT,)
    _LOBBY_HEADER_HELPER = Comp7LightLobbyHeaderHelper
    _MISSIONS_HELPER = Comp7LightMissionsGuiHelper
