# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/Scaleform/daapi/view/lobby/hangar/hangar_quest_flags.py
from frontline.gui.gui_constants import QuestFlagTypes
from gui.impl import backport
from gui.impl.gen import R
from gui.Scaleform.genConsts.HANGAR_HEADER_QUESTS import HANGAR_HEADER_QUESTS
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.daapi.view.lobby.hangar.header_helpers.flag_helpers import getActiveQuestLabel, headerQuestFormatterVo, wrapQuestGroup
from gui.Scaleform.daapi.view.lobby.hangar.header_helpers.quest_flags_getters import BaseQuestFlagsGetter
from gui.Scaleform.daapi.view.lobby.hangar.header_helpers.quest_flags import BattleQuestsFlag
from gui.shared.formatters import icons
from gui.shared.system_factory import registerQuestFlag
from helpers import time_utils, dependency
from helpers.time_utils import ONE_DAY
from skeletons.gui.game_control import IEpicBattleMetaGameController

class EpicQuestFlagsGetter(BaseQuestFlagsGetter):
    _SUPPORTED_FLAGS = (QuestFlagTypes.EPIC,)


class _EpicQuestsFlag(BattleQuestsFlag):
    __slots__ = ()
    __epicController = dependency.descriptor(IEpicBattleMetaGameController)

    @classmethod
    def formatQuests(cls, vehicle, params):
        quests = cls.__epicController.getDailyBattleQuests()
        if quests is None:
            return
        else:
            totalCount = len(quests)
            completedQuests = len([ q for q in quests if q.isCompleted() ])
            libraryIcons = R.images.gui.maps.icons.library
            commonQuestsIcon = libraryIcons.outline.quests_available()
            if not totalCount:
                commonQuestsIcon = libraryIcons.outline.quests_disabled()
                label = ''
            elif not cls.__epicController.isDailyQuestsUnlocked():
                label = icons.makeImageTag(backport.image(libraryIcons.CancelIcon_1()))
            elif completedQuests != totalCount:
                label = getActiveQuestLabel(totalCount, completedQuests)
            else:
                currentCycleEndTime, _ = cls.__epicController.getCurrentCycleInfo()
                cycleTimeLeft = currentCycleEndTime - time_utils.getCurrentLocalServerTimestamp()
                if cycleTimeLeft < ONE_DAY or not cls.__epicController.isDailyQuestsRefreshAvailable():
                    label = icons.makeImageTag(backport.image(libraryIcons.ConfirmIcon_1()))
                else:
                    label = icons.makeImageTag(backport.image(libraryIcons.time_icon()))
            quests = [headerQuestFormatterVo(enable=totalCount > 0, icon=backport.image(commonQuestsIcon), label=label, questType=cls._QUEST_TYPE, flag=backport.image(R.images.gui.maps.icons.library.hangarFlag.flag_epic()), tooltip=TOOLTIPS_CONSTANTS.EPIC_QUESTS_PREVIEW, isTooltipSpecial=True)]
            return wrapQuestGroup(HANGAR_HEADER_QUESTS.QUEST_GROUP_COMMON, '', quests)


def registerQuestFlags():
    registerQuestFlag(QuestFlagTypes.EPIC, _EpicQuestsFlag)
