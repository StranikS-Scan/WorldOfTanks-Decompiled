# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/hangar_presets/battle_royale_presets_getter.py
from battle_royale.gui.constants import BR_AMMO_PANEL_TYPE
from battle_royale.gui.Scaleform.daapi.view.lobby.hangar.hangar_quest_flags import BattleRoyaleQuestFlagsGetter
from battle_royale.gui.Scaleform.daapi.view.lobby.header.helpers.controls_helpers import BattleRoyaleLobbyHeaderHelper, BRTournamentLobbyHeaderHelper
from constants import QUEUE_TYPE, ARENA_BONUS_TYPE
from gui.hangar_presets.hangar_presets_getters import DefaultPresetsGetter
from helpers import dependency
from skeletons.gui.game_control import IPlatoonController

class BattleRoyalePresetsGetter(DefaultPresetsGetter):
    __slots__ = ()
    _QUEUE_TYPE = QUEUE_TYPE.BATTLE_ROYALE
    _BONUS_TYPES = (ARENA_BONUS_TYPE.BATTLE_ROYALE_SOLO, ARENA_BONUS_TYPE.BATTLE_ROYALE_SQUAD)
    _QUEST_FLAGS_GETTER = BattleRoyaleQuestFlagsGetter
    _LOBBY_HEADER_HELPER = BattleRoyaleLobbyHeaderHelper
    _DEFAULT_AMMO_INJECT_VIEW_ALIAS = BR_AMMO_PANEL_TYPE
    _platoonCtrl = dependency.descriptor(IPlatoonController)

    def getSuggestedBonusType(self):
        return ARENA_BONUS_TYPE.BATTLE_ROYALE_SQUAD if self._platoonCtrl.isInPlatoon() else ARENA_BONUS_TYPE.BATTLE_ROYALE_SOLO


class BattleRoyaleTournamentPresetsGetter(DefaultPresetsGetter):
    __slots__ = ()
    _QUEUE_TYPE = QUEUE_TYPE.BATTLE_ROYALE_TOURNAMENT
    _BONUS_TYPES = (ARENA_BONUS_TYPE.BATTLE_ROYALE_TRN_SOLO, ARENA_BONUS_TYPE.BATTLE_ROYALE_TRN_SQUAD)
    _QUEST_FLAGS_GETTER = None
    _LOBBY_HEADER_HELPER = BRTournamentLobbyHeaderHelper
    _DEFAULT_AMMO_INJECT_VIEW_ALIAS = BR_AMMO_PANEL_TYPE
