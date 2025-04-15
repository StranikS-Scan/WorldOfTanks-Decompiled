# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/personal_missions_controller.py
from typing import Union, Any, Dict, List
from Event import Event, EventManager
import personal_missions
from account_helpers import AccountSettings
from account_helpers.AccountSettings import PersonalMissions
from constants import MIN_VEHICLE_LEVEL, MAX_VEHICLE_LEVEL, DOSSIER_TYPE
from dossiers2.ui.achievements import BADGES_BLOCK
from frameworks.wulf import Array
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.impl.lobby.personal_missions.personal_missions_window_events import showPersonalMissionsVideoRewardView
from gui.server_events import finders
from gui.server_events.bonuses import DossierBonus
from gui.server_events.event_items import PMOperation, PersonalMission
from gui.server_events.finders import BRANCH_TO_OPERATION_IDS, CHAMPION_BADGE_AT_OPERATION_ID
from gui.shared.utils.scheduled_notifications import Notifiable
from helpers import dependency, time_utils
from personal_missions import PM_BRANCH
from shared_utils import first
from skeletons.gui.game_control import IPersonalMissionsController
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from skeletons.gui.lobby_context import ILobbyContext
from helpers import int2roman

class PersonalMissionsController(IPersonalMissionsController):
    __eventsCache = dependency.descriptor(IEventsCache)
    __itemsCache = dependency.descriptor(IItemsCache)
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self):
        self.__eventManager = EventManager()
        self.onQuestsUpdated = Event(self.__eventManager)
        self.onUpdated = Event(self.__eventManager)
        self.onItemCacheUpdated = Event(self.__eventManager)
        self.onRewardsViewClose = Event(self.__eventManager)
        self.__sysMessagesController = _PersonalMissionsSystemMessagesController()
        self.sysMessageController.init()
        self.__postProgressionVehicles = None
        return

    def fini(self):
        self.onQuestsUpdated.clear()
        self.onUpdated.clear()
        self.onItemCacheUpdated.clear()
        self.onRewardsViewClose.clear()

    def onAccountBecomeNonPlayer(self):
        self.__eventsCache.onProgressUpdated -= self.__onProgressUpdated

    @property
    def sysMessageController(self):
        return self.__sysMessagesController

    def onLobbyInited(self, event):
        self.sysMessageController.startNotify()
        self.__eventsCache.onProgressUpdated += self.__onProgressUpdated
        self.__itemsCache.onSyncCompleted += self.__onItemCacheUpdated
        g_clientUpdateManager.addCallbacks({'quests': self.__onQuestsUpdated})
        settings = AccountSettings.getPersonalMissions(PersonalMissions.OPERATIONS_VIDEO_REWARDS_STATUS)
        for operationId in BRANCH_TO_OPERATION_IDS[personal_missions.PM_BRANCH.PERSONAL_MISSION_3]:
            operation = self.getOperationById(operationId)
            if not operation or not operation.isCompleted():
                continue
            if settings.get(operationId, False):
                continue
            settings.setdefault(operationId, False)
            settings[operationId] = True
            showPersonalMissionsVideoRewardView(operationId)

        AccountSettings.setPersonalMissions(PersonalMissions.OPERATIONS_VIDEO_REWARDS_STATUS, settings)

    def getAllQuests(self):
        return self.__eventsCache.getPersonalMissions().getAllQuests()

    def getAllQuestsPM3(self):
        quests = {}
        quests.update(self.__eventsCache.getPersonalMissions().getQuestsForBranch(PM_BRANCH.PERSONAL_MISSION_3))
        return quests

    def getFinalQuests(self):
        quests = self.__eventsCache.getPersonalMissions().getAllFilteredQuests(lambda q: q.getQuestBranch() == PM_BRANCH.PERSONAL_MISSION_3 and q.isFinal())
        return quests

    def getFullCompletedFinalQuests(self):
        quests = self.__eventsCache.getPersonalMissions().getAllFilteredQuests(lambda q: q.getQuestBranch() == PM_BRANCH.PERSONAL_MISSION_3 and q.isFinal() and q.isFullCompleted())
        return quests

    def getOperations(self):
        return self.__eventsCache.getPersonalMissions().getOperationsForBranch(PM_BRANCH.PERSONAL_MISSION_3)

    @staticmethod
    def getGeneralIdFromUserQuestId(questId):
        return str(questId).replace('_main', '').replace('_add', '')

    def getQuestFromGeneralID(self, generalID):
        gID = self.getGeneralIdFromUserQuestId(generalID)
        quest = self.__eventsCache.getPersonalMissions().getAllFilteredQuests(lambda q: q.getGeneralQuestID() == gID)
        return first(quest.values())

    def getOperationById(self, operationId):
        operation = self.__eventsCache.getPersonalMissions().getOperationsForBranch(PM_BRANCH.PERSONAL_MISSION_3).get(operationId, None)
        return operation

    def getInitialQuestsByChainAndOperationId(self, chainId, operationId):
        return personal_missions.g_cache.initialMissionQuestIDsByOperationIDChainID(operationId, chainId)

    def getFinalQuestsByChainAndOperationId(self, chainId, operationId):
        return personal_missions.g_cache.finalMissionIDsByOperationIDChainID(operationId, chainId)

    def getQuestsByChainAndOperationId(self, chainId, operationId):
        quests = self.__eventsCache.getPersonalMissions().getAllFilteredQuests(lambda q: q.getChainID() == chainId and q.getOperationID() == operationId)
        return quests

    def getQuestsByOperationId(self, operationId):
        quests = self.__eventsCache.getPersonalMissions().getAllFilteredQuests(lambda q: q.getOperationID() == operationId)
        return quests

    def getCompletedQuestsByOperationId(self, operationId):
        quests = self.__eventsCache.getPersonalMissions().getAllFilteredQuests(lambda q: q.isCompleted() and q.getOperationID() == operationId)
        return quests

    def getFullCompletedQuestsByOperationId(self, operationId):
        quests = self.__eventsCache.getPersonalMissions().getAllFilteredQuests(lambda q: q.isFullCompleted() and q.getOperationID() == operationId)
        return quests

    def getCompletedQuestsByChainAndOperationId(self, chainId, operationId):
        quests = self.__eventsCache.getPersonalMissions().getAllFilteredQuests(lambda q: q.isCompleted() and q.getChainID() == chainId and q.getOperationID() == operationId)
        return quests

    def getQuestsChainsByOperationId(self, operationId):
        questsChains = {}
        quests = self.__eventsCache.getPersonalMissions().getAllFilteredQuests(lambda q: q.getOperationID() == operationId)
        for _, quest in quests.iteritems():
            chainID = quest.getChainID()
            if chainID not in questsChains:
                questsChains[chainID] = {'data': [],
                 'minLevel': quest.getVehMinLevel(),
                 'maxLevel': quest.getVehMaxLevel()}
            questsChains[chainID]['data'].append(quest)

        return questsChains

    def getQuest(self, questId):
        return self.getAllQuests().get(questId, None)

    def getLinesIdsByChainAndOperationId(self, chainId, operationId):
        initialQuestsSortedIds = sorted(self.getInitialQuestsByChainAndOperationId(chainId, operationId))
        finalQuestsSortedIds = sorted(self.getFinalQuestsByChainAndOperationId(chainId, operationId))
        return zip(initialQuestsSortedIds, finalQuestsSortedIds)

    def getNextQuestId(self, currentQuestId):
        currentQuest = self.getQuest(currentQuestId)
        if currentQuest and currentQuest.isFinal():
            return currentQuestId
        else:
            nextQuestId = currentQuestId + 1
            nextQuest = self.getQuest(nextQuestId)
            while nextQuest and nextQuest.isDisabled():
                if nextQuest.isFinal():
                    return currentQuestId
                nextQuestId = nextQuestId + 1
                nextQuest = self.getQuest(nextQuestId)

            return currentQuestId if nextQuest is None or nextQuest.isDisabled() else nextQuestId

    def getSelectedQuestForChain(self, chainId, operationId):
        chainQuests = self.getQuestsByChainAndOperationId(chainId, operationId)
        for quest in chainQuests.itervalues():
            if quest.isInProgress():
                return quest

        return None

    def getPrevQuestId(self, currentQuestId):
        currentQuest = self.getQuest(currentQuestId)
        if currentQuest and currentQuest.isInitial():
            return currentQuestId
        else:
            prevQuestId = currentQuestId - 1
            prevQuest = self.getQuest(prevQuestId)
            while prevQuest and prevQuest.isDisabled():
                if prevQuest.isInitial():
                    return currentQuestId
                prevQuestId = prevQuestId - 1
                prevQuest = self.getQuest(prevQuestId)

            return currentQuestId if prevQuest is None or prevQuest.isDisabled() else prevQuestId

    def getAddBadgesForOperation(self, operation):
        bonuses = self.getAddBonusesForOperation(operation)
        return self.__getBadgesFromBonuses(bonuses)

    def getAddDossierBonusesForOperation(self, operation):
        return self.__getDossiersFromBonuses(self.getAddBonusesForOperation(operation))

    def getAddBonusesForOperation(self, operation):
        ctx = {'branch': operation.getBranch()}
        hiddenQuests = self.__eventsCache.getHiddenQuests()
        finder = finders.getQuestByTokenAndBonus
        baseQuest = finder(hiddenQuests, finders.addQuestTokenFinder(operation))
        return baseQuest.getBonuses(ctx=ctx) if baseQuest is not None else {}

    def getMainBadgesForOperation(self, operation):
        result = []
        for bonuses in operation.getBonuses().itervalues():
            result.extend(self.__getBadgesFromBonuses(bonuses))

        return result

    def getMainDossierBonusesForOperation(self, operation):
        result = []
        for bonuses in operation.getBonuses().itervalues():
            result.extend(self.__getDossiersFromBonuses(bonuses))

        return result

    def getOperationChainsData(self, operation):
        quests = operation.getQuests()
        chainsIds = quests.keys()
        result = {}
        isHonor = operation.isCompleted() and not operation.isFullCompleted()
        for chainId in chainsIds:
            if isHonor:
                chainSize = len(self.getFinalQuestsByChainAndOperationId(chainId=chainId, operationId=operation.getID()))
            else:
                chainSize = operation.getChainSize()
            completedSize = len(operation.getQuestsInChainByFilter(chainId, lambda q: q.isCompleted() and not isHonor or isHonor and q.isFullCompleted() and q.isFinal()))
            questsChain = quests[chainId]
            quest = questsChain[questsChain.keys()[0]]
            chainName = '{}-{}'.format(int2roman(quest.getVehMinLevel()), int2roman(quest.getVehMaxLevel()))
            result[chainId] = {'name': chainName,
             'size': chainSize,
             'completed': completedSize}

        return result

    def getMinMaxVehicleLevelForOperation(self, operation):
        minLevel = MAX_VEHICLE_LEVEL
        maxLevel = MIN_VEHICLE_LEVEL
        questsDict = operation.getQuests()
        for quests in questsDict.itervalues():
            if not quests:
                continue
            quest = first(quests.values())
            minLevel = min(quest.getVehMinLevel(), minLevel)
            maxLevel = max(quest.getVehMaxLevel(), maxLevel)

        return (minLevel, maxLevel)

    def getPreviousOperationName(self, currentOperationId):
        previousOperationId = currentOperationId - 1
        operations = self.getOperations()
        return '' if previousOperationId not in operations.keys() else operations[previousOperationId].getShortUserName()

    def getBadgesForChampionQuestPM3(self):
        lastPM3Operation = BRANCH_TO_OPERATION_IDS[PM_BRANCH.PERSONAL_MISSION_3][-1]
        pm3ChampionTokenQuestID = CHAMPION_BADGE_AT_OPERATION_ID[lastPM3Operation]
        championQuest = self.__eventsCache.getQuestByID(pm3ChampionTokenQuestID)
        bonusList = []
        if championQuest:
            for name, value in championQuest.getRawBonuses().iteritems():
                for (blockName, idx), data in value.get(DOSSIER_TYPE.ACCOUNT, {}).iteritems():
                    if blockName == BADGES_BLOCK:
                        bonusList.append(DossierBonus(name, {DOSSIER_TYPE.ACCOUNT: {(blockName, idx): data}}))

        return bonusList

    def __onQuestsUpdated(self, diff):
        if any((questId.startswith('pm3') for questId in set(diff))):
            self.onQuestsUpdated()

    def __onProgressUpdated(self, branch):
        if branch == PM_BRANCH.PERSONAL_MISSION_3:
            self.onQuestsUpdated()

    def __onItemCacheUpdated(self, *_):
        self.onItemCacheUpdated()

    @staticmethod
    def __getBadgesFromBonuses(bonuses):
        result = []
        for bonus in bonuses:
            if bonus.getName() == 'dossier':
                badges = bonus.getBadges()
                for badge in badges:
                    result.append(badge)

        return result

    @staticmethod
    def __getDossiersFromBonuses(bonuses):
        result = []
        for bonus in bonuses:
            if bonus.getName() == 'dossier':
                result.append(bonus)

        return result


class _PersonalMissionsSystemMessagesController(object):
    __PersonalMissionsController = dependency.descriptor(IPersonalMissionsController)
    __HOURS_COUNTDOWN = time_utils.ONE_DAY

    def __init__(self):
        self.__notificationManager = Notifiable()

    def init(self):
        pass

    def startNotify(self):
        self.__notificationManager.startNotification()
