# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/hangar_presets/fun_hangar_dynamic_gui_provider.py
from __future__ import absolute_import
from constants import ARENA_BONUS_TYPE
from fun_random.gui.feature.util.fun_wrappers import hasDesiredSubMode
from fun_random.gui.feature.util.fun_mixins import FunSubModesWatcher
from fun_random.gui.Scaleform.daapi.view.lobby.header.helpers.controls_helpers import FunRandomLobbyHeaderHelper
from gui.hangar_presets.providers.base_dynamic_gui_provider import BaseHangarDynamicGuiProvider
from gui.impl.lobby.missions.missions_helpers import DefaultMissionsGuiHelper

class FunRandomHangarDynamicGuiProvider(BaseHangarDynamicGuiProvider, FunSubModesWatcher):
    _BONUS_TYPES = (ARENA_BONUS_TYPE.FUN_RANDOM,)
    _LOBBY_HEADER_HELPER = FunRandomLobbyHeaderHelper
    _MISSIONS_HELPER = DefaultMissionsGuiHelper

    @hasDesiredSubMode(abortAction='getDefaultBattleModifiers')
    def getBattleModifiers(self):
        return self.getDesiredSubMode().getModifiersDataProvider().getModifiers()
