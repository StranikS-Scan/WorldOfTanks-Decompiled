# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/epicBattle/after_battle_reward_view_helpers.py
import logging
from collections import namedtuple
from helpers import dependency, int2roman
from skeletons.gui.game_control import IEpicBattleMetaGameController
from skeletons.gui.server_events import IEventsCache
_logger = logging.getLogger(__name__)
_BACKGROUND_LEVEL_IMAGE = ((0,),
 (1, 2, 3, 4),
 (5, 6, 7, 8, 9),
 (10, 11, 12, 13, 14),
 (15,))
ProgressionLevelIconVO = namedtuple('MetaLevelVO', ('seasonLevel', 'playerLevel', 'bgImageId'))

@dependency.replace_none_kwargs(eventsCache=IEventsCache)
def getQuestBonuses(questsProgressData, questIDs, currentLevelQuestID, eventsCache=None):
    allQuests = eventsCache.getAllQuests()
    currentLevelQuest = allQuests.get(currentLevelQuestID, None)
    bonuses = []
    if currentLevelQuest and questsProgressData:
        for questID in questIDs:
            for q in questsProgressData:
                if questID in q:
                    bonuses.extend(allQuests.get(q).getBonuses())

    return bonuses


@dependency.replace_none_kwargs(epicController=IEpicBattleMetaGameController)
def getProgressionIconVO(cycleNumber, playerLevel, epicController=None):
    playerLevelStr = str(playerLevel) if playerLevel is not None else None
    season = epicController.getCurrentSeason() or epicController.getNextSeason()
    return ProgressionLevelIconVO('' if season and season.isSingleCycleSeason() else int2roman(cycleNumber), playerLevelStr, _getProgressionIconBackgroundId(playerLevel))


def getProgressionIconVODict(cycleNumber, playerLevel):
    return getProgressionIconVO(cycleNumber, playerLevel)._asdict()


def _getProgressionIconBackgroundId(level):
    if level is None:
        return 0
    else:
        for index, levelRange in enumerate(_BACKGROUND_LEVEL_IMAGE):
            if level in levelRange:
                return index

        return
