# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/client/fort_rush/gui/hangar_presets/fort_rush_dynamic_gui_provider.py
from __future__ import absolute_import
from fort_rush.gui.impl.lobby.user_missions.fort_rush_missions_helper import FortRushMissionsGuiHelper
from fort_rush_common.fort_rush_constants import QUEUE_TYPE, ARENA_BONUS_TYPE
from fort_rush.gui.scaleform.daapi.view.lobby.header.helpers.controls_helpers import FortRushLobbyHeaderHelper
from gui.hangar_presets.providers.default_dynamic_gui_provider import DefaultHangarDynamicGuiProvider

class FortRushHangarDynamicGuiProvider(DefaultHangarDynamicGuiProvider):
    _QUEUE_TYPE = QUEUE_TYPE.FORT_RUSH
    _BONUS_TYPES = (ARENA_BONUS_TYPE.FORT_RUSH,)
    _LOBBY_HEADER_HELPER = FortRushLobbyHeaderHelper
    _MISSIONS_HELPER = FortRushMissionsGuiHelper
