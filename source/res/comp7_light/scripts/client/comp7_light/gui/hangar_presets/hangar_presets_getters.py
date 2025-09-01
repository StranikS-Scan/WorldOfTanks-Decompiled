# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_light/scripts/client/comp7_light/gui/hangar_presets/hangar_presets_getters.py
from comp7_light.gui.Scaleform.daapi.view.lobby.header.helpers.controls_helpers import Comp7LightLobbyHeaderHelper
from constants import QUEUE_TYPE, ARENA_BONUS_TYPE
from gui.hangar_presets.hangar_presets_getters import DefaultPresetsGetter

class Comp7LightPresetsGetter(DefaultPresetsGetter):
    __slots__ = ()
    _QUEUE_TYPE = QUEUE_TYPE.COMP7_LIGHT
    _BONUS_TYPES = (ARENA_BONUS_TYPE.COMP7_LIGHT,)
    _LOBBY_HEADER_HELPER = Comp7LightLobbyHeaderHelper
