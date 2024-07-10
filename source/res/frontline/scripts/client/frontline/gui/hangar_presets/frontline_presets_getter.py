# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/hangar_presets/frontline_presets_getter.py
from constants import QUEUE_TYPE, ARENA_BONUS_TYPE
from frontline.gui.Scaleform.daapi.view.lobby.hangar.hangar_quest_flags import EpicQuestFlagsGetter
from frontline.gui.Scaleform.daapi.view.lobby.header.helpers.controls_helpers import FrontlineLobbyHeaderHelper
from gui.hangar_presets.hangar_presets_getters import DefaultPresetsGetter
from helpers import dependency
from skeletons.gui.game_control import IEpicBattleMetaGameController

class FrontlinePresetsGetter(DefaultPresetsGetter):
    __slots__ = ()
    _QUEUE_TYPE = QUEUE_TYPE.EPIC
    _BONUS_TYPES = (ARENA_BONUS_TYPE.EPIC_BATTLE, ARENA_BONUS_TYPE.EPIC_BATTLE_TRAINING)
    _QUEST_FLAGS_GETTER = EpicQuestFlagsGetter
    _LOBBY_HEADER_HELPER = FrontlineLobbyHeaderHelper
    __epicController = dependency.descriptor(IEpicBattleMetaGameController)

    def getHangarAlertBlock(self):
        return self.__epicController.getAlertBlock()
