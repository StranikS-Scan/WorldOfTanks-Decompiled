# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/hangar_presets/hangar_presets_getters.py
from battle_modifiers_common import BattleModifiers
from comp7.gui.Scaleform.daapi.view.lobby.hangar.header_helpers.quest_flags_getters import Comp7QuestFlagsGetter
from comp7.gui.Scaleform.daapi.view.lobby.header.helpers.controls_helpers import Comp7LobbyHeaderHelper
from constants import QUEUE_TYPE, ARENA_BONUS_TYPE
from gui.hangar_presets.hangar_presets_getters import DefaultPresetsGetter
from helpers import dependency
from skeletons.gui.game_control import IComp7Controller

class Comp7PresetsGetter(DefaultPresetsGetter):
    __slots__ = ()
    _QUEUE_TYPE = QUEUE_TYPE.COMP7
    _BONUS_TYPES = (ARENA_BONUS_TYPE.COMP7,)
    _QUEST_FLAGS_GETTER = Comp7QuestFlagsGetter
    _LOBBY_HEADER_HELPER = Comp7LobbyHeaderHelper
    __comp7Controller = dependency.descriptor(IComp7Controller)

    @classmethod
    def getBattleModifiers(cls):
        return BattleModifiers(cls.__comp7Controller.battleModifiers)

    def getHangarAlertBlock(self):
        return self.__comp7Controller.getAlertBlock()
