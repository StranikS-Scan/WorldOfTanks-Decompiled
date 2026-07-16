# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/hangar_presets/ls_dynamic_gui_providers.py
from __future__ import absolute_import
from gui.hangar_presets.providers.default_dynamic_gui_provider import DefaultHangarDynamicGuiProvider
from last_stand.gui.impl.lobby.vehicle_menu_helper import LSHangarVehicleMenuHelper
from last_stand_common.last_stand_constants import QUEUE_TYPE, ARENA_BONUS_TYPE
from last_stand.gui.scaleform.daapi.view.lobby.header.helpers.controls_helpers import LSLobbyHeaderHelper
from last_stand.gui.prb_control import LSVehicleAutoSearchHelper

class LSHangarDynamicGuiProvider(DefaultHangarDynamicGuiProvider):
    _QUEUE_TYPE = QUEUE_TYPE.LAST_STAND
    _BONUS_TYPES = (ARENA_BONUS_TYPE.LAST_STAND,)
    _LOBBY_HEADER_HELPER = LSLobbyHeaderHelper
    _VEHICLE_MENU_HELPER = LSHangarVehicleMenuHelper
    _VEHICLE_AUTO_SEARCH_HELPER = LSVehicleAutoSearchHelper


class LSMediumHangarDynamicGuiProvider(LSHangarDynamicGuiProvider):
    _QUEUE_TYPE = QUEUE_TYPE.LAST_STAND_MEDIUM
    _BONUS_TYPES = (ARENA_BONUS_TYPE.LAST_STAND_MEDIUM,)


class LSHardHangarDynamicGuiProvider(LSHangarDynamicGuiProvider):
    _QUEUE_TYPE = QUEUE_TYPE.LAST_STAND_HARD
    _BONUS_TYPES = (ARENA_BONUS_TYPE.LAST_STAND_HARD,)
