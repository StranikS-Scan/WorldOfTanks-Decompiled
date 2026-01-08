# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/progress/progress_filters.py
import copy
import typing
import constants
import personal_missions
from future.utils import itervalues
from gui.battle_results.progress.progress_helpers import packQuestProgressData, isQuestCompleted, getPrestigeProgress, isPMOperationAndMissionEnabled
from gui.server_events.events_helpers import isPremium, isDailyQuest, isWeeklyQuest, isBattleMattersQuestID, isCommonBattleQuest
from potapov_quests import isPM3Quest
from skeletons.gui.server_events import IEventsCache
from helpers import dependency
from personal_missions import PM_BRANCH
from gui.battle_results.progress.research import VehicleProgressHelper
from skeletons.gui.game_control import IBattlePassController
if typing.TYPE_CHECKING:
    from gui.battle_results.reusable import _ReusableInfo
    from gui.server_events.event_items import PersonalMission
    from gui.server_events.personal_missions_cache import PersonalMissionsCache

def battleMattersProgressFilter(reusable, allCommonQuests):
    commonQuestsProgress = reusable.personal.getQuestsProgress()
    if not commonQuestsProgress:
        return []
    battleMattersWithProgress = []
    for qID, qProgress in commonQuestsProgress.items():
        if isBattleMattersQuestID(qID):
            data = packQuestProgressData(qID, allCommonQuests, qProgress, isQuestCompleted(*qProgress))
            if data:
                battleMattersWithProgress.append(data)

    return battleMattersWithProgress


def dailyQuestsProgressFilter(reusable, allCommonQuests):
    commonQuestsProgress = reusable.personal.getQuestsProgress()
    if not commonQuestsProgress:
        return []
    dailyQuestsWithProgress = []
    for qID, qProgress in commonQuestsProgress.items():
        if isPremium(qID) or isDailyQuest(qID):
            data = packQuestProgressData(qID, allCommonQuests, qProgress, isQuestCompleted(*qProgress))
            if data:
                dailyQuestsWithProgress.append(data)

    return dailyQuestsWithProgress


def weeklyQuestsProgressFilter(reusable, allCommonQuests):
    commonQuestsProgress = reusable.personal.getQuestsProgress()
    if not commonQuestsProgress:
        return []
    weeklyQuestsWithProgress = []
    for qID, qProgress in commonQuestsProgress.items():
        if isWeeklyQuest(qID):
            data = packQuestProgressData(qID, allCommonQuests, qProgress, isQuestCompleted(*qProgress))
            if data:
                weeklyQuestsWithProgress.append(data)

    return weeklyQuestsWithProgress


def battlePassProgressFilter(reusable):
    battlePassProgress = reusable.battlePassProgress
    isNewPoints = battlePassProgress.pointsAux > 0 or battlePassProgress.questPoints > 0 or battlePassProgress.bonusCapPoints > 0 or battlePassProgress.bpTopPoints > 0
    battlePassController = dependency.instance(IBattlePassController)
    return battlePassProgress if (battlePassProgress.hasProgress(battlePassProgress.currentChapterID) or isNewPoints) and not battlePassController.isDisabled() else None


def prestigeProgressFilter(reusable):
    return getPrestigeProgress(reusable)


@dependency.replace_none_kwargs(eventsCache=IEventsCache)
def personalMissionProgressFilter(reusable, eventsCache=None):
    personalMissions = eventsCache.getPersonalMissions()
    commonQuestsProgress = reusable.personal.getQuestsProgress()
    if not (personalMissions.isEnabled(PM_BRANCH.PERSONAL_MISSION_3) and commonQuestsProgress):
        return []
    pm3Quests = personalMissions.getQuestsForBranch(PM_BRANCH.PERSONAL_MISSION_3)
    personalMissionWithProgress = []
    for qID, qProgress in commonQuestsProgress.items():
        if isPM3Quest(qID) and personal_missions.g_cache.isPersonalMission(qID):
            pmID = personal_missions.g_cache.getPersonalMissionIDByUniqueID(qID)
            currentPM3Quest = pm3Quests[pmID]
            if isPMOperationAndMissionEnabled(currentPM3Quest):
                _, pPrev, pCur = qProgress
                if pPrev or max(itervalues(pCur)) != 0:
                    updatedPM3Quest = copy.deepcopy(currentPM3Quest)
                    currentBattlesUniqueVehicles = pCur.get('battlesUniqueVehicles', {})
                    updatedPM3Quest.getConditionsProgress().update({'battlesUniqueVehicles': currentBattlesUniqueVehicles})
                    data = (updatedPM3Quest, isQuestCompleted(*qProgress))
                    personalMissionWithProgress.append(data)

    return personalMissionWithProgress


def vehicleProgressFilter(reusable):
    results = {}
    xpEarnings = reusable.personal.xpProgress
    for intCD, xpEarningsForVehicle in xpEarnings.items():
        vehicleBattleXp = xpEarningsForVehicle.get('xp', 0)
        helper = VehicleProgressHelper(intCD)
        unlockVehicles, unlockModules = helper.getReady2UnlockItems(vehicleBattleXp)
        if unlockVehicles or unlockModules:
            results[intCD] = (unlockVehicles, unlockModules)
        helper.clear()

    return results


def commonBattleQuestsProgressFilter(reusable, allCommonQuests):
    commonQuestsProgress = reusable.personal.getQuestsProgress()
    if not commonQuestsProgress:
        return []
    else:
        commonBattleQuestsProgress = []
        for qID, qProgress in commonQuestsProgress.items():
            quest = allCommonQuests.get(qID)
            if quest is None:
                continue
            if quest.getType() in constants.EVENT_TYPE.QUEST_RANGE and isCommonBattleQuest(quest):
                data = packQuestProgressData(qID, allCommonQuests, qProgress, isQuestCompleted(*qProgress))
                if data:
                    commonBattleQuestsProgress.append(data)

        return commonBattleQuestsProgress
