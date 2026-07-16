# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/lobby/battle_results/missions_progress/progress_filters.py
from __future__ import absolute_import
import typing
from comp7.gui.impl.lobby.battle_results.missions_progress.research import Comp7VehicleProgressHelper
from shared_utils import findFirst
from comp7.gui.impl.lobby.comp7_helpers.comp7_c11n_helpers import getComp7ProgressionStyle
from comp7.gui.impl.lobby.comp7_helpers.comp7_quest_helpers import isComp7Quest, getComp7QuestType
from comp7.skeletons.gui.game_control import IComp7WeeklyQuestsController
from comp7_common_const import Comp7QuestType
from gui.battle_results.progress.progress_filters import commonBattleQuestsProgressFilter
from gui.battle_results.progress.progress_helpers import isQuestCompleted
from gui.battle_results.progress.progress_helpers import packQuestProgressData
from helpers import dependency
if typing.TYPE_CHECKING:
    from gui.battle_results.reusable import _ReusableInfo

@dependency.replace_none_kwargs(comp7WeeklyQuestsCtrl=IComp7WeeklyQuestsController)
def comp7WeeklyQuestsProgressFilter(reusable, comp7WeeklyQuestsCtrl=None):
    questsProgress = reusable.personal.getQuestsProgress()
    if not questsProgress:
        return []
    comp7WeeklyWithProgress = []
    for qID, qProgress in questsProgress.items():
        if isComp7Quest(qID):
            questType = getComp7QuestType(qID)
            if questType in (Comp7QuestType.WEEKLY, Comp7QuestType.TOKENS):
                comp7Quests = comp7WeeklyQuestsCtrl.getQuests()
                questsByType = comp7Quests.sortedBattleQuests if questType == Comp7QuestType.WEEKLY else comp7Quests.sortedTokenQuests
                _, quest = findFirst(lambda item, i=qID: item[1].getID() == i, questsByType)
                isCompleted = isQuestCompleted(*qProgress)
                pGroupBy, pPrev, pCur = qProgress
                isProgressReset = not isCompleted and quest.bonusCond.isInRow() and pCur.get('battlesCount', 0) == 0
                if pPrev or any(pCur.values()) != 0:
                    data = (quest,
                     {pGroupBy: pCur},
                     {pGroupBy: pPrev},
                     isProgressReset,
                     isCompleted)
                    comp7WeeklyWithProgress.append(data)

    return comp7WeeklyWithProgress


def comp7CustomizationQuestsProgressFilter(reusable, allCommonQuests):
    questsProgress = reusable.personal.getQuestsProgress()
    if not questsProgress:
        return []
    else:
        style = getComp7ProgressionStyle()
        if style is None:
            return []
        customizationQuestProgress = []
        progressionStyleQuests = _getComp7StyleProgressionQuestIDs()
        for qID, qProgress in questsProgress.items():
            if qID in progressionStyleQuests:
                quest = allCommonQuests.get(qID)
                if quest is not None:
                    data = packQuestProgressData(qID, allCommonQuests, qProgress, isQuestCompleted(*qProgress))
                    if data:
                        customizationQuestProgress.append(data)

        return customizationQuestProgress


def comp7VehicleProgressFilter(reusable):
    results = {}
    xpEarnings = reusable.personal.xpProgress
    for intCD, xpEarningsForVehicle in xpEarnings.items():
        vehicleBattleXp = xpEarningsForVehicle.get('xp', 0)
        helper = Comp7VehicleProgressHelper(intCD)
        unlockVehicles, unlockModules = helper.getReady2UnlockItems(vehicleBattleXp)
        if unlockVehicles or unlockModules:
            results[intCD] = (unlockVehicles, unlockModules)
        helper.clear()

    return results


def comp7CommonBattleQuestsProgressFilter(reusable, allCommonQuests):
    progressionStyleQuests = _getComp7StyleProgressionQuestIDs()
    commonBattleQuests = commonBattleQuestsProgressFilter(reusable, allCommonQuests)
    result = []
    for quest, pCur, pPrev, isReset, isCompleted in commonBattleQuests:
        if quest.getID() not in progressionStyleQuests:
            result.append((quest,
             pCur,
             pPrev,
             isReset,
             isCompleted))

    return result


def _getComp7StyleProgressionQuestIDs():
    style = getComp7ProgressionStyle()
    if style is None:
        return []
    else:
        questIDs = []
        for item in style.alternateItems:
            quests = item.getUnlockingQuests()
            for quest in quests or ():
                questIDs.append(quest.getID())

        return questIDs
