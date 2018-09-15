# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/server_events/personal_missions_controller.py
import operator
import BigWorld
import personal_missions
from constants import PERSONAL_QUEST_FREE_TOKEN_NAME
from gui.server_events import event_items
from gui.server_events.pm_constants import PM_TUTOR_FIELDS
from gui.shared.money import Currency
from gui.shared.utils.requesters.ItemsRequester import REQ_CRITERIA
from gui.shared.utils.requesters.QuestsProgressRequester import RandomQuestsProgressRequester
from helpers import dependency
from items import tankmen
from personal_missions import PM_BRANCH
from skeletons.account_helpers.settings_core import ISettingsCore, ISettingsCache
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
_SETTINGS_SYNCED = 1
_EVENTS_CACHE_UPDATED = 2
_ALL_SYNCED = _SETTINGS_SYNCED | _EVENTS_CACHE_UPDATED

class PersonalMissionsController(object):
    trackedStats = ('questsCompleted',
     'completionTokens',
     'tankwomanBonus',
     Currency.CREDITS)
    lobbyContext = dependency.descriptor(ILobbyContext)
    itemsCache = dependency.descriptor(IItemsCache)
    __settingsCache = dependency.descriptor(ISettingsCache)

    def __init__(self):
        self.__questsProgress = RandomQuestsProgressRequester()
        self.__clearCaches()
        self.__hasQuestsForSelect = False
        self.__hasQuestsForReward = False
        self._pqType = PM_BRANCH.TYPE_TO_NAME[PM_BRANCH.REGULAR]
        self.__vehRequirementsCache = {}
        self.__freeTokensCount = 0
        self.__pawnedTokensCount = 0
        self.__syncStatus = 0

    @property
    def questsProgress(self):
        return self.__questsProgress

    def init(self):
        self.itemsCache.onSyncCompleted += self.__updateVehRequirementsCache
        self.__settingsCache.onSyncCompleted += self.__onSettingsCacheSynced
        invVehicles = self.itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY).values()
        for _, personalMissionID in personal_missions.g_cache:
            questBranch = personal_missions.g_cache.branchByMissionID(personalMissionID)
            if questBranch == self._pqType:
                quest = self.__makeQuest(personalMissionID)
                operation = self.__makeOperation(quest.getOperationID())
                operation.addQuest(quest)
                campaign = self.__makeCampaign(operation.getCampaignID())
                campaign.addOperation(operation)
                quest.setCampaignID(campaign.getID())
                self.__cacheQuestRequirement(quest, invVehicles)

    def fini(self):
        self.__settingsCache.onSyncCompleted -= self.__onSettingsCacheSynced
        self.itemsCache.onSyncCompleted -= self.__updateVehRequirementsCache
        self.__clearCaches()

    def stop(self):
        self.__freeTokensCount = 0
        self.__pawnedTokensCount = 0
        self.__syncStatus = 0

    def getNextTankwomanIDs(self, nationID, isPremium, fnGroup, lnGroup, iGroupID):
        lastFirstNameID, lastLastNameID, lastIconID = self.questsProgress.getTankmanLastIDs(nationID)
        return map(operator.itemgetter(1), tankmen.getNextUniqueIDs(BigWorld.player().databaseID, lastFirstNameID, lastLastNameID, lastIconID, nationID, isPremium, fnGroup, lnGroup, iGroupID))

    def getQuests(self):
        return self.__quests

    def getOperations(self):
        return self.__operations

    def getCampaigns(self):
        return self.__campaigns

    def getSelectedQuests(self):
        result = {}
        for qID in self.questsProgress.getSelectedPersonalMissionsIDs():
            if qID in self.__quests:
                result[qID] = self.__quests[qID]

        return result

    def getFreeTokensCount(self):
        return self.__freeTokensCount

    def getPawnedTokensCount(self):
        return self.__pawnedTokensCount

    def mayPawnQuest(self, quest):
        return self.getFreeTokensCount() >= quest.getPawnCost() and quest.canBePawned()

    def getTokens(self):
        result = set()
        for operation in self.getOperations().itervalues():
            result |= operation.getTokens().keys()

        return result

    def hasVehicleForQuests(self):
        """
        Has this player required vehicle for any quest
        """
        return self.isEnabled() and any(self.__vehRequirementsCache.itervalues())

    def hasQuestsForSelect(self):
        return self.__hasQuestsForSelect

    def hasQuestsForReward(self):
        return self.__hasQuestsForReward and self.isEnabled()

    def isEnabled(self):
        return self.lobbyContext.getServerSettings().isPersonalMissionsEnabled()

    def update(self, eventsCache, diff=None):
        isNeedToUpdateProgress = False
        if diff is not None:
            missionsDiff = diff.get('potapovQuests', {})
            if missionsDiff:
                if 'selected' in missionsDiff:
                    eventsCache.onSelectedQuestsChanged(missionsDiff['selected'], self._pqType)
                if 'slots' in missionsDiff:
                    eventsCache.onSlotsCountChanged(missionsDiff['slots'], self._pqType)
                isNeedToUpdateProgress = True
            if 'tokens' in diff:
                isNeedToUpdateProgress = True
        else:
            isNeedToUpdateProgress = True
        if isNeedToUpdateProgress:
            self.__hasQuestsForSelect = False
            self.__hasQuestsForReward = False
            freeSlotsCount = self.questsProgress.getPersonalMissionsFreeSlots()
            for qID, quest in self.__quests.iteritems():
                quest.updateProgress(self.questsProgress)

            selectedQuests = self.questsProgress.getSelectedPersonalMissionsIDs()
            selectedChains = set()
            for questID in selectedQuests:
                if questID in self.__quests:
                    selectedChains.add(self.__quests[questID].getChainID())

            for qID, quest in self.__quests.iteritems():
                if not self.__hasQuestsForSelect and freeSlotsCount and quest.canBeSelected() and quest.getChainID() not in selectedChains:
                    self.__hasQuestsForSelect = True
                if not self.__hasQuestsForReward and quest.needToGetReward():
                    self.__hasQuestsForReward = True
                if self.__hasQuestsForSelect and self.__hasQuestsForReward:
                    break

            self.__pawnedTokensCount = 0
            for operation in self.__operations.itervalues():
                operation.updateProgress(eventsCache)
                self.__pawnedTokensCount += operation.getTokensPawnedCount()
                canBePawned = operation.isUnlocked()
                for chain in operation.getQuests().itervalues():
                    for quest in chain.itervalues():
                        quest.setCanBePawned(canBePawned)

            self.__freeTokensCount = eventsCache.questsProgress.getTokenCount(PERSONAL_QUEST_FREE_TOKEN_NAME)
            self.__syncStatus |= _EVENTS_CACHE_UPDATED
            self.__tryToPreserveInitialFreeAwardSheetsCount()
            for campaign in self.__campaigns.itervalues():
                campaign.updateProgress()

            eventsCache.onProgressUpdated(self._pqType)
        return

    def getAwardsStats(self, operationID):
        result = {}
        for statName in self.trackedStats:
            result[statName] = {'possible': 0,
             'acquired': 0}

        for quest in self.__quests.itervalues():
            if quest.getOperationID() != operationID:
                continue
            completed = quest.isMainCompleted()
            self.__addBonuses(result, quest.getBonuses(isMain=True), completed)
            self.__addBonuses(result, quest.getBonuses(isMain=False), quest.isFullCompleted())
            result['questsCompleted']['possible'] += 1
            if completed:
                result['questsCompleted']['acquired'] += 1

        return result

    def getIncompleteOperation(self):
        """
        return operation which is unlocked and with unachieved vehicle reward.
        If all operation are complete, return last operation
        """
        operations = self.getOperations()
        for operation in operations.values():
            if operation.isUnlocked() and not operation.isAwardAchieved():
                return operation

        return operations[len(operations)]

    def __addBonuses(self, target, bonusesList, acquired):
        for bonus in bonusesList:
            bonusName = bonus.getName()
            if bonusName not in self.trackedStats:
                continue
            bonusCount = bonus.getCount()
            target[bonusName]['possible'] += bonusCount
            if acquired:
                target[bonusName]['acquired'] += bonusCount

    def __clearCaches(self):
        self.__campaigns = {}
        self.__operations = {}
        self.__quests = {}
        self.__vehRequirementsCache = {}
        self.__freeTokensCount = 0
        self.__pawnedTokensCount = 0

    def __makeCampaign(self, campaignID):
        if campaignID not in self.__campaigns:
            campaign = self.__campaigns[campaignID] = event_items.PMCampaign(campaignID, personal_missions.g_campaignsCache.getCampaignInfo(campaignID))
        else:
            campaign = self.__campaigns[campaignID]
        return campaign

    def __makeOperation(self, operationID):
        if operationID not in self.__operations:
            operation = self.__operations[operationID] = event_items.PMOperation(operationID, personal_missions.g_operationsCache.getOperationInfo(operationID))
        else:
            operation = self.__operations[operationID]
        return operation

    def __makeQuest(self, pmID, campaignID=None):
        if pmID not in self.__quests:
            pmType = personal_missions.g_cache.questByPersonalMissionID(pmID)
            quest = self.__quests[pmID] = event_items.PersonalMission(pmID, pmType, campaignID=campaignID)
        else:
            quest = self.__quests[pmID]
        return quest

    def __cacheQuestRequirement(self, q, invVehicles):
        """
        Pre-cache info about required vehicles presence in players inventory inside operation's chain
        """
        types = tuple(q.getVehicleClasses())
        level = q.getVehMinLevel()
        key = (q.getOperationID(),
         q.getChainID(),
         types,
         level)
        if key not in self.__vehRequirementsCache:
            hasRequiredVehicle = self.__hasVehicle(types, level, invVehicles)
            self.__vehRequirementsCache[key] = hasRequiredVehicle
        else:
            hasRequiredVehicle = self.__vehRequirementsCache[key]
        q.setRequiredVehiclesPresence(hasRequiredVehicle)

    def __hasVehicle(self, vehTypes, level, invVehicles):
        for veh in invVehicles:
            if veh.level >= level and veh.type in vehTypes:
                return True

        return False

    def __updateVehRequirementsCache(self, *_):
        """
        Update info about required vehicles presence in players inventory inside operation's chains
        """
        invVehicles = self.itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY).values()
        for key, value in self.__vehRequirementsCache.iteritems():
            operationID, chainID, types, level = key
            newValue = self.__hasVehicle(types, level, invVehicles)
            if value != newValue:
                self.__vehRequirementsCache[key] = newValue
                quests = self.__operations[operationID].getQuests()[chainID]
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
                settingsCore.serverSettings.saveInUIStorage({PM_TUTOR_FIELDS.INITIAL_FAL_COUNT: self.__freeTokensCount})
            return
