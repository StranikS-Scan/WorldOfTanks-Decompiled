# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/hangar_preset/battle_royale_dynamic_gui_provider.py
from constants import QUEUE_TYPE, ARENA_BONUS_TYPE
from gui.hangar_presets.providers import DefaultHangarDynamicGuiProvider
from helpers import dependency
from skeletons.gui.game_control import IPlatoonController
from battle_royale.gui.Scaleform.daapi.view.lobby.header.helpers.controls_helpers import BattleRoyaleLobbyHeaderHelper

class BattleRoyaleHangarDynamicGuiProvider(DefaultHangarDynamicGuiProvider):
    __slots__ = ()
    _QUEUE_TYPE = QUEUE_TYPE.BATTLE_ROYALE
    _BONUS_TYPES = (ARENA_BONUS_TYPE.BATTLE_ROYALE_SOLO, ARENA_BONUS_TYPE.BATTLE_ROYALE_SQUAD)
    _LOBBY_HEADER_HELPER = BattleRoyaleLobbyHeaderHelper
    _platoonCtrl = dependency.descriptor(IPlatoonController)

    def getSuggestedBonusType(self):
        return ARENA_BONUS_TYPE.BATTLE_ROYALE_SQUAD if self._platoonCtrl.isInPlatoon() else ARENA_BONUS_TYPE.BATTLE_ROYALE_SOLO
