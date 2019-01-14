# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/skeletons/gui/server_events.py
from Event import Event

class IEventsCache(object):
    onSyncStarted = None
    onSyncCompleted = None
    onProgressUpdated = None
    onEventsVisited = None
    onProfileVisited = None
    onPersonalQuestsVisited = None

    def init(self):
        raise NotImplementedError

    def fini(self):
        raise NotImplementedError

    def start(self):
        raise NotImplementedError

    def stop(self):
        raise NotImplementedError

    def clear(self):
        raise NotImplementedError

    @property
    def waitForSync(self):
        raise NotImplementedError

    @property
    def prefetcher(self):
        raise NotImplementedError

    @property
    def questsProgress(self):
        raise NotImplementedError

    def getPersonalMissions(self):
        raise NotImplementedError

    def getLockedQuestTypes(self, branch):
        raise NotImplementedError

    def update(self, diff=None, callback=None):
        raise NotImplementedError

    def getQuests(self, filterFunc=None):
        raise NotImplementedError

    def getMotiveQuests(self, filterFunc=None):
        raise NotImplementedError

    def getLinkedSetQuests(self, filterFunc=None):
        raise NotImplementedError

    def getBattleQuests(self, filterFunc=None):
        raise NotImplementedError

    def getGroups(self, filterFunc=None):
        raise NotImplementedError

    def getHiddenQuests(self, filterFunc=None):
        raise NotImplementedError

    def getRankedQuests(self, filterFunc=None):
        raise NotImplementedError

    def getAllQuests(self, filterFunc=None, includePersonalMissions=False):
        raise NotImplementedError

    def getActions(self, filterFunc=None):
        raise NotImplementedError

    def getActionEntities(self):
        raise NotImplementedError

    def getAnnouncedActions(self):
        raise NotImplementedError

    def getEventBattles(self):
        raise NotImplementedError

    def isEventEnabled(self):
        raise NotImplementedError

    def getEventVehicles(self, itemsCache=None):
        raise NotImplementedError

    def getEvents(self, filterFunc=None):
        raise NotImplementedError

    def getCurrentEvents(self):
        raise NotImplementedError

    def getFutureEvents(self):
        raise NotImplementedError

    def getAffectedAction(self, item):
        raise NotImplementedError

    def getItemAction(self, item, isBuying=True, forCredits=False):
        raise NotImplementedError

    def getBoosterAction(self, booster, isBuying=True, forCredits=False):
        raise NotImplementedError

    def getRentAction(self, item, rentPackage):
        raise NotImplementedError

    def getEconomicsAction(self, name):
        raise NotImplementedError

    def isBalancedSquadEnabled(self):
        raise NotImplementedError

    def getBalancedSquadBounds(self):
        raise NotImplementedError

    def isSquadXpFactorsEnabled(self):
        raise NotImplementedError

    def getSquadBonusLevelDistance(self):
        raise NotImplementedError

    def getSquadPenaltyLevelDistance(self):
        raise NotImplementedError

    def getSquadZeroBonuses(self):
        raise NotImplementedError

    def getQuestsDossierBonuses(self):
        raise NotImplementedError

    def getQuestsByTokenRequirement(self, token):
        raise NotImplementedError

    def getQuestsByTokenBonus(self, token):
        raise NotImplementedError

    def getCompensation(self, tokenID):
        raise NotImplementedError

    def hasQuestDelayedRewards(self, questID):
        raise NotImplementedError

    def getAdvisableQuests(self, filterFunc=None):
        raise NotImplementedError

    def getActiveQuests(self, filterFunc=None):
        raise NotImplementedError
