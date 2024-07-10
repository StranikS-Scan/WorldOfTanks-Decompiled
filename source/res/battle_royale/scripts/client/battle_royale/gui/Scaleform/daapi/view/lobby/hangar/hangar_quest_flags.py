# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/Scaleform/daapi/view/lobby/hangar/hangar_quest_flags.py
from battle_royale.gui.Scaleform.daapi.view.lobby.hangar_constants import QuestFlagTypes
from gui.impl import backport
from gui.impl.gen import R
from gui.Scaleform.genConsts.HANGAR_HEADER_QUESTS import HANGAR_HEADER_QUESTS
from gui.Scaleform.daapi.view.lobby.hangar.header_helpers.quest_flags import BattleQuestsFlag
from gui.Scaleform.daapi.view.lobby.hangar.header_helpers.flag_helpers import getActiveQuestLabel
from gui.Scaleform.daapi.view.lobby.hangar.header_helpers.quest_flags_getters import BaseQuestFlagsGetter
from gui.server_events.events_constants import BATTLE_ROYALE_GROUPS_ID
from gui.server_events.events_dispatcher import showMissionsCategories
from gui.shared.formatters import icons
from gui.shared.system_factory import registerQuestFlag
from helpers import time_utils, dependency
from helpers.time_utils import ONE_DAY
from skeletons.gui.game_control import IBattleRoyaleController

class BattleRoyaleQuestFlagsGetter(BaseQuestFlagsGetter):
    _SUPPORTED_FLAGS = ()


class _BattleRoyaleQuestsFlag(BattleQuestsFlag):
    __slots__ = ()
    _QUEST_TYPE = HANGAR_HEADER_QUESTS.QUEST_TYPE_BATTLE_ROYALE
    __battleRoyaleController = dependency.descriptor(IBattleRoyaleController)

    @classmethod
    def showQuestsInfo(cls, questType, _):
        showMissionsCategories(groupID=BATTLE_ROYALE_GROUPS_ID)

    @classmethod
    def _getLabelAndFlagType(cls, totalCount, completedQuests):
        libraryIcons = R.images.gui.maps.icons.library
        if completedQuests != totalCount:
            label = getActiveQuestLabel(totalCount, completedQuests)
        else:
            currentCycleEndTime, _ = cls.__battleRoyaleController.getCurrentCycleInfo()
            cycleTimeLeft = currentCycleEndTime - time_utils.getCurrentLocalServerTimestamp()
            if cycleTimeLeft < ONE_DAY or not cls.__battleRoyaleController.isDailyQuestsRefreshAvailable():
                label = icons.makeImageTag(backport.image(libraryIcons.ConfirmIcon_1()))
            else:
                label = icons.makeImageTag(backport.image(libraryIcons.time_icon()))
        return (label, cls._QUEST_TYPE)


def registerQuestFlags():
    registerQuestFlag(QuestFlagTypes.BATTLE_ROYALE, _BattleRoyaleQuestsFlag)
