# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_results/progress/progress_helpers.py
from copy import deepcopy
import typing
import BigWorld
from collections import namedtuple
from personal_missions import PM_BRANCH
from shared_utils import first
from gui.prestige.prestige_helpers import mapGradeIDToUI, getCurrentGrade, getCurrentProgress, prestigePointsToXP, hasVehiclePrestige, MAX_GRADE_ID
from helpers import dependency
from dog_tags_common.components_config import componentConfigAdapter
from skeletons.gui.battle_results import IBattleResultsService
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
if typing.TYPE_CHECKING:
    from gui.server_events.event_items import PersonalMission, PMOperation
PrestigeProgress = namedtuple('PrestigeProgress', ('vehCD', 'oldGradeType', 'currentGradeType', 'oldGrade', 'currentGrade', 'oldLvl', 'newLvl', 'currentXP', 'currentNextLvlXP', 'oldXP', 'oldNextLvlXP', 'gainedXP'))
DogTagProgress = namedtuple('DogTagProgress', ['componentId',
 'compGrade',
 'dogTagType',
 'unlockType'])

def getPrestigeProgress(reusable):
    prestigeResults = reusable.personal.getPrestigeResults()
    data = first(prestigeResults.items())
    if not data:
        return None
    else:
        vehCD, prestigeData = data
        if not hasVehiclePrestige(vehCD, checkElite=True):
            return None
        return None if not prestigeData or prestigeData['oldLevel'] <= 0 or prestigeData['newLevel'] <= 0 else createPrestigeInfo(vehCD, prestigeData)


def createPrestigeInfo(vehCD, prestigeData):
    oldLvl = prestigeData['oldLevel']
    gainedPoints = prestigeData['gainedPoints']
    if getCurrentGrade(oldLvl, vehCD) == MAX_GRADE_ID or gainedPoints == 0:
        return None
    else:
        newLvl = prestigeData['newLevel']
        newLvlPoints = prestigeData['newPoints']
        currentGradeType, currentGrade = mapGradeIDToUI(getCurrentGrade(newLvl, vehCD))
        currentXP, currentNextLvlXP = getCurrentProgress(vehCD, newLvl, newLvlPoints)
        oldPoints = prestigeData['oldPoints']
        oldGradeType, oldGrade = mapGradeIDToUI(getCurrentGrade(oldLvl, vehCD))
        oldXP, oldNextLvlXP = getCurrentProgress(vehCD, oldLvl, oldPoints)
        gainedXP = prestigePointsToXP(gainedPoints)
        return PrestigeProgress(vehCD=vehCD, oldGradeType=oldGradeType, currentGradeType=currentGradeType, oldGrade=oldGrade, currentGrade=currentGrade, oldLvl=oldLvl, newLvl=newLvl, currentXP=currentXP, currentNextLvlXP=currentNextLvlXP, oldXP=oldXP, oldNextLvlXP=oldNextLvlXP, gainedXP=gainedXP)


@dependency.replace_none_kwargs(lobbyContext=ILobbyContext)
def getDogTagsProgress(reusable, lobbyContext=None):
    if not lobbyContext.getServerSettings().isDogTagInPostBattleEnabled():
        return None
    else:
        dogTags = reusable.personal.getDogTagsProgress()
        unlockedDogTags = [ createDogTagInfo(compId, 'unlock') for compId in dogTags.get('unlockedComps', []) ]
        upgradedDogTags = [ createDogTagInfo(compId, 'upgrade') for compId in dogTags.get('upgradedComps', []) ]
        return (unlockedDogTags, upgradedDogTags)


def createDogTagInfo(componentId, dogTagType):
    compGrade = BigWorld.player().dogTags.getComponentProgress(componentId).grade
    unlockType = componentConfigAdapter.getComponentById(componentId).viewType.value.lower()
    return DogTagProgress(componentId, compGrade, dogTagType, unlockType)


def isQuestCompleted(_, pPrev, pCur):
    return pCur.get('bonusCount', 0) - pPrev.get('bonusCount', 0) > 0


def packQuestProgressData(qID, allCommonQuests, qProgress, isCompleted):
    pGroupBy, pPrev, pCur = qProgress
    quest = allCommonQuests.get(qID)
    data = None
    if quest is not None:
        isProgressReset = not isCompleted and quest.bonusCond.isInRow() and pCur.get('battlesCount', 0) == 0
        if pPrev or max(pCur.itervalues()) != 0:
            data = (quest,
             {pGroupBy: pCur},
             {pGroupBy: pPrev},
             isProgressReset,
             isCompleted)
    return data


@dependency.replace_none_kwargs(battleResultsService=IBattleResultsService)
def getReceivedTokensInfo(arenaUniqueID, battleResultsService=None):
    statsController = battleResultsService.getStatsCtrl(arenaUniqueID)
    reusable = statsController.getResults().reusable
    questTokensConvertion = deepcopy(reusable.personal.getQuestTokensConvertion())
    questTokensCount = reusable.personal.getQuestTokensCount()
    return (questTokensConvertion, questTokensCount)


@dependency.replace_none_kwargs(eventsCache=IEventsCache)
def isPMOperationAndMissionEnabled(quest, eventsCache=None):
    operationID = quest.getOperationID()
    operation = eventsCache.getPersonalMissions().getAllOperations(PM_BRANCH.V2_BRANCHES).get(operationID)
    return not operation.isDisabled()
