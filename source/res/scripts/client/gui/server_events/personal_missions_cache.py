# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/server_events/personal_missions_cache.py
import operator
from collections import defaultdict
import BigWorld
import personal_missions
from constants import MIN_VEHICLE_LEVEL, MAX_VEHICLE_LEVEL
from gui.server_events.finders import BRANCH_TO_OPERATION_IDS
from personal_missions import PM_BRANCH, PM_BRANCH_TO_FREE_TOKEN_NAME
from adisp import async, process
from gui.server_events import event_items
from gui.server_events.pm_constants import PM_TUTOR_FIELDS
from gui.shared.utils.requesters.ItemsRequester import REQ_CRITERIA
from gui.shared.utils.requesters.QuestsProgressRequester import PersonalMissionsProgressRequester
from helpers import dependency
from items import tankmen
from shared_utils import first
from skeletons.account_helpers.settings_core import ISettingsCore, ISettingsCache
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
_SETTINGS_SYNCED = 1
_EVENTS_CACHE_UPDATED = 2
_ALL_SYNCED = _SETTINGS_SYNCED | _EVENTS_CACHE_UPDATED

def vehicleRequirementsCheck(quest, invVehicles):
    level = quest.getVehMinLevel()
    classifier = quest.getQuestClassifier()
    for veh in invVehicles:
        if veh.level >= level and classifier.matchVehicle(veh.descriptor.type) and not veh.isOnlyForEventBattles:
            return True

    return False


def processDisabledFlag(collection, disabledIdsSet):
    for itemId, _ in collection.iteritems():
        if itemId in disabledIdsSet:
            collection[itemId].setDisabledState(True)
        collection[itemId].setDisabledState(False)


class _PMBranch(object):
    __slots__ = ('branch', 'questsProgress', 'vehRequirementsCache', 'hasQuestsForSelect', 'hasQuestsForReward', 'freeTokensCount', 'pawnedTokensCount', 'campaigns', 'operations', 'quests')

    def __init__(self, branch):
        self.branch = branch
        self.questsProgress = PersonalMissionsProgressRequester(branch)
        self.vehRequirementsCache = {}
        self.hasQuestsForSelect = False
        self.hasQuestsForReward = False
        self.freeTokensCount = 0
        self.pawnedTokensCount = 0
        self.campaigns = {}
        self.operations = {}
        self.quests = {}

    def clear(self):
        self.campaigns = {}
        self.operations = {}
        self.quests = {}
        self.vehRequirementsCache = {}
        self.freeTokensCount = 0
        self.pawnedTokensCount = 0

    def stop(self):
        self.freeTokensCount = 0
        self.pawnedTokensCount = 0


class PersonalMissionsCache(object):
    __lobbyContext = dependency.descriptor(ILobbyContext)
    itemsCache = dependency.descriptor(IItemsCache)
    __settingsCache = dependency.descriptor(ISettingsCache)

    def __init__(self):
        self.__questsData = {k:_PMBranch(PM_BRANCH.TYPE_TO_NAME[k]) for k in PM_BRANCH.ACTIVE_BRANCHES}
        self.__clearCaches()
        self.__syncStatus = 0
        self.__vehLevelsRestrictions = defaultdict(lambda : (MAX_VEHICLE_LEVEL, MIN_VEHICLE_LEVEL))

    def init(self):
        self.itemsCache.onSyncCompleted += self.__updateVehRequirementsCache
        self.__settingsCache.onSyncCompleted += self.__onSettingsCacheSynced
        invVehicles = self.itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY).values()
        for _, personalMissionID in personal_missions.g_cache:
            branch = personal_missions.g_cache.questByPotapovQuestID(personalMissionID).branch
            if branch in PM_BRANCH.ACTIVE_BRANCHES:
                questData = personal_missions.g_cache.questByPersonalMissionID(personalMissionID)
                operation = self.__makeOperation(branch, questData.tileID)
                campaign = self.__makeCampaign(branch, operation.getCampaignID())
                quest = self.__makeQuest(branch, questData, personalMissionID, campaign.getID())
                operation.addQuest(quest)
                campaign.addOperation(operation)
                self.__cacheQuestRequirement(branch, quest, invVehicles)
                self.__updateVehLevelRestrictions(quest)

    def fini(self):
        self.__settingsCache.onSyncCompleted -= self.__onSettingsCacheSynced
        self.itemsCache.onSyncCompleted -= self.__updateVehRequirementsCache
        self.__clearCaches()

    def stop(self):
        for questData in self.__questsData.itervalues():
            questData.stop()

        self.__syncStatus = 0

    def getQuestsProgress(self, branch):
        questData = self.__questsData.get(branch)
        return questData.questsProgress if questData else None

    def getNextTankwomanIDs(self, branch, nationID, isPremium, fnGroup, lnGroup, iGroupID):
        lastFirstNameID, lastLastNameID, lastIconID = self.getQuestsProgress(branch).getTankmanLastIDs(nationID)
        return map(operator.itemgetter(1), tankmen.getNextUniqueIDs(BigWorld.player().databaseID, lastFirstNameID, lastLastNameID, lastIconID, nationID, isPremium, fnGroup, lnGroup, iGroupID))

    def getAllQuests(self):
        result = {}
        for branch in PM_BRANCH.ACTIVE_BRANCHES:
            result.update(self.getQuestsForBranch(branch))

        return result

    def getQuestsForBranch(self, branch):
        questData = self.__questsData.get(branch)
        return questData.quests if questData else {}

    def getAllOperations(self):
        result = {}
        for branch in PM_BRANCH.ACTIVE_BRANCHES:
            result.update(self.getOperationsForBranch(branch))

        return result

    def getOperationsForBranch(self, branch):
        questData = self.__questsData.get(branch, None)
        return questData.operations if questData else {}

    def getAllCampaigns(self):
        result = {}
        for branch in PM_BRANCH.ACTIVE_BRANCHES:
            result.update(self.getCampaignsForBranch(branch))

        return result

    def getCampaignsForBranch(self, branch):
        questData = self.__questsData.get(branch, None)
        return questData.campaigns if questData else {}

    def getAllSelectedQuests(self):
        result = {}
        for branch in PM_BRANCH.ACTIVE_BRANCHES:
            result.update(self.getSelectedQuestsForBranch(branch))

        return result

    def getSelectedQuestsForBranch(self, branch):
        result = {}
        questData = self.__questsData.get(branch, None)
        if questData:
            quests = questData.quests
            qp = questData.questsProgress
            for qID in qp.getSelectedPersonalMissionsIDs():
                if qID in quests:
                    result[qID] = quests[qID]

        return result

    def getFreeTokensCount(self, branch):
        questData = self.__questsData.get(branch, None)
        return questData.freeTokensCount if questData else 0

    def getPawnedTokensCount(self, branch):
        questData = self.__questsData.get(branch, None)
        return questData.pawnedTokensCount if questData else 0

    def mayPawnQuest(self, quest):
        branch = quest.getPMType().branch
        return self.getFreeTokensCount(branch) >= quest.getPawnCost() and quest.canBePawned()

    def getAllTokens(self):
        result = {}
        for branch in PM_BRANCH.ACTIVE_BRANCHES:
            result.update(self.getTokensForPmType(branch))

        return result

    def getTokensForBranch(self, branch):
        result = set()
        for operation in self.getOperationsForBranch(branch).itervalues():
            result |= operation.getTokens().keys()

        return result

    def getVehicleLevelRestrictions(self, operationID):
        return self.__vehLevelsRestrictions[operationID]

    def hasVehicleForQuests(self, branch):
        questsData = self.__questsData.get(branch, None)
        return self.isEnabled(branch) and any(questsData.vehRequirementsCache.itervalues()) if questsData else False

    def hasQuestsForSelect(self, branch):
        questsData = self.__questsData.get(branch, None)
        return questsData.hasQuestsForSelect if questsData else False

    def hasQuestsForReward(self, branch):
        questsData = self.__questsData.get(branch, None)
        return questsData.hasQuestsForReward and self.isEnabled(branch) if questsData else False

    @async
    @process
    def questsProgressRequest(self, callback=None):
        for branch in PM_BRANCH.ACTIVE_BRANCHES:
            qp = self.getQuestsProgress(branch)
            if qp:
                yield qp.request()

        callback(self)

    def isQuestsProgressSynced(self):
        for qd in self.__questsData.itervalues():
            if not qd.questsProgress.isSynced():
                return False

        return True

    def isEnabled(self, branch=None):
        return self.__lobbyContext.getServerSettings().isPersonalMissionsEnabled(branch)

    def getDisabledPMOperations(self):
        disabledOpIds = {}
        for branch in PM_BRANCH.ACTIVE_BRANCHES:
            if not self.__lobbyContext.getServerSettings().isPersonalMissionsEnabled(branch):
                disabledOpIds.update({opId:None for opId in BRANCH_TO_OPERATION_IDS[branch]})

        disabledOpIds.update(self.__lobbyContext.getServerSettings().getDisabledPMOperations())
        return disabledOpIds

    def updateDisabledStateForQuests(self):
        if not self.__lobbyContext:
            return
        processDisabledFlag(self.getAllOperations(), self.getDisabledPMOperations())
        processDisabledFlag(self.getAllQuests(), self.__lobbyContext.getServerSettings().getDisabledPersonalMissions())

    def update(self, eventsCache, diff=None):
        for branch, questsData in self.__questsData.iteritems():
            qp = questsData.questsProgress
            quests = questsData.quests
            questsData.hasQuestsForSelect = False
            questsData.hasQuestsForReward = False
            freeSlotsCount = qp.getPersonalMissionsFreeSlots()
            for _, quest in quests.iteritems():
                quest.updateProgress(qp)

            selectedQuests = qp.getSelectedPersonalMissionsIDs()
            selectedChains = set()
            for questID in selectedQuests:
                if questID in quests:
                    selectedChains.add(quests[questID].getChainID())

            for _, quest in quests.iteritems():
                if not questsData.hasQuestsForSelect and freeSlotsCount and quest.canBeSelected() and quest.getChainID() not in selectedChains:
                    questsData.hasQuestsForSelect = True
                if not questsData.hasQuestsForReward and quest.needToGetReward():
                    questsData.hasQuestsForReward = True
                if questsData.hasQuestsForSelect and questsData.hasQuestsForReward:
                    break

            questsData.pawnedTokensCount = 0
            for operation in questsData.operations.itervalues():
                operation.updateProgress(eventsCache)
                questsData.pawnedTokensCount += operation.getTokensPawnedCount()
                canBePawned = operation.isUnlocked()
                for chain in operation.getQuests().itervalues():
                    for quest in chain.itervalues():
                        quest.setCanBePawned(canBePawned)

            questsData.freeTokensCount = eventsCache.questsProgress.getTokenCount(PM_BRANCH_TO_FREE_TOKEN_NAME[branch])
            self.__syncStatus |= _EVENTS_CACHE_UPDATED
            self.__tryToPreserveInitialFreeAwardSheetsCount()
            for campaign in questsData.campaigns.itervalues():
                campaign.updateProgress()

            eventsCache.onProgressUpdated(branch)

        self.updateDisabledStateForQuests()

    def getIncompleteOperation(self, branch):
        operations = self.getOperationsForBranch(branch)
        sortedOID = sorted(operations.keys())
        for oID in sortedOID:
            if operations[oID].isUnlocked() and not operations[oID].isAwardAchieved():
                return operations[oID]

        return operations[sortedOID[-1]]

    def __clearCaches(self):
        for qd in self.__questsData.itervalues():
            qd.clear()

    def __makeCampaign(self, branch, campaignID):
        campaigns = self.getCampaignsForBranch(branch)
        if campaignID not in campaigns:
            campaign = campaigns[campaignID] = event_items.PMCampaign(campaignID, personal_missions.g_campaignsCache.getCampaignInfo(campaignID))
        else:
            campaign = campaigns[campaignID]
        return campaign

    def __makeOperation(self, branch, operationID):
        operations = self.getOperationsForBranch(branch)
        if operationID not in operations:
            operation = operations[operationID] = event_items.PMOperation(operationID, personal_missions.g_operationsCache.getOperationInfo(operationID), branch=branch)
        else:
            operation = operations[operationID]
        return operation

    def __makeQuest(self, branch, questData, pmID, campaignID):
        quests = self.getQuestsForBranch(branch)
        if pmID not in quests:
            quest = quests[pmID] = event_items.PersonalMission(pmID, questData, campaignID=campaignID)
        else:
            quest = quests[pmID]
        return quest

    def __cacheQuestRequirement(self, branch, q, invVehicles):
        qd = self.__questsData.get(branch)
        if not qd:
            return
        operationID = q.getOperationID()
        chainID = q.getChainID()
        key = (operationID, chainID)
        if key not in qd.vehRequirementsCache:
            hasRequiredVehicle = vehicleRequirementsCheck(q, invVehicles)
            qd.vehRequirementsCache[key] = hasRequiredVehicle
        else:
            hasRequiredVehicle = qd.vehRequirementsCache[key]
        q.setRequiredVehiclesPresence(hasRequiredVehicle)

    def __updateVehRequirementsCache(self, *_):
        invVehicles = self.itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY).values()
        for qd in self.__questsData.itervalues():
            for key, value in qd.vehRequirementsCache.iteritems():
                operationID, chainID = key
                quests = qd.operations[operationID].getQuests()[chainID]
                firstQuest = first(quests.itervalues())
                newValue = vehicleRequirementsCheck(firstQuest, invVehicles)
                if value != newValue:
                    qd.vehRequirementsCache[key] = newValue
                    for q in quests.itervalues():
                        q.setRequiredVehiclesPresence(newValue)

    def __onSettingsCacheSynced(self):
        self.__syncStatus |= _SETTINGS_SYNCED
        self.__tryToPreserveInitialFreeAwardSheetsCount()

    def __tryToPreserveInitialFreeAwardSheetsCount(self):
        if self.__settingsCache.waitForSync or self.__syncStatus != _ALL_SYNCED:
            return
        else:
            settingsCore = dependency.instance(ISettingsCore)
            storageData = settingsCore.serverSettings.getUIStorage()
            if storageData.get(PM_TUTOR_FIELDS.INITIAL_FAL_COUNT) is None:
                settingsCore.serverSettings.saveInUIStorage({PM_TUTOR_FIELDS.INITIAL_FAL_COUNT: self.getFreeTokensCount(PM_BRANCH.REGULAR)})
            return

    def __updateVehLevelRestrictions(self, quest):
        operationID = quest.getOperationID()
        currMin, currMax = self.__vehLevelsRestrictions[operationID]
        self.__vehLevelsRestrictions[operationID] = (min(currMin, quest.getVehMinLevel()), max(currMax, quest.getVehMaxLevel()))
