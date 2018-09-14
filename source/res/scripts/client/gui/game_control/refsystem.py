# Embedded file name: scripts/client/gui/game_control/RefSystem.py
from collections import defaultdict
from operator import methodcaller, itemgetter
from Event import Event, EventManager
from PlayerEvents import g_playerEvents
from constants import REF_SYSTEM_FLAG, EVENT_TYPE
from gui.Scaleform.genConsts.REFERRAL_SYSTEM import REFERRAL_SYSTEM
from helpers import time_utils
from debug_utils import LOG_ERROR, LOG_WARNING, LOG_CURRENT_EXCEPTION, LOG_DEBUG
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.LobbyContext import g_lobbyContext
from gui.Scaleform.locale.MENU import MENU
from gui.shared import g_itemsCache, g_eventsCache, events, g_eventBus
from gui.shared.utils import findFirst

def _getRefSysCfg():
    return g_itemsCache.items.shop.refSystem or {}


def _getRefSystemPeriods():
    return _getRefSysCfg()['periods']


def _getMaxReferralXPPool():
    return _getRefSysCfg()['maxReferralXPPool']


def _getMaxNumberOfReferrals():
    return _getRefSysCfg()['maxNumberOfReferrals']


class RefSystem(object):

    def init(self):
        self.__referrers = []
        self.__referrals = []
        self.__quests = []
        self.__xpPoolOfDeletedRals = 0
        self.__totalXP = 0
        self.__isTotallyCompleted = False
        self.__posByXPinTeam = 0
        self.__eventMgr = EventManager()
        self.onUpdated = Event(self.__eventMgr)
        self.onQuestsUpdated = Event(self.__eventMgr)
        self.onPlayerBecomeReferrer = Event(self.__eventMgr)
        self.onPlayerBecomeReferral = Event(self.__eventMgr)

    def start(self):
        g_clientUpdateManager.addCallbacks({'stats.refSystem': self.__onRefStatsUpdated})
        g_eventsCache.onSyncCompleted += self.__onEventsUpdated
        g_playerEvents.onShopResync += self.__onShopUpdated
        self.__update(g_itemsCache.items.stats.refSystem)
        self.__updateQuests()

    def stop(self):
        g_playerEvents.onShopResync -= self.__onShopUpdated
        g_eventsCache.onSyncCompleted -= self.__onEventsUpdated
        g_clientUpdateManager.removeObjectCallbacks(self)

    def fini(self):
        self.__referrers = None
        self.__referrals = None
        self.__eventMgr.clear()
        self.__clearQuestsData()
        return

    def getReferrers(self):
        return self.__referrers

    def getReferrals(self):
        return self.__referrals

    def getQuests(self):
        return self.__quests

    def isTotallyCompleted(self):
        return self.__isTotallyCompleted

    def getPosByXPinTeam(self):
        return self.__posByXPinTeam

    def getTotalXP(self):
        return self.__totalXP

    def getReferralsXPPool(self):
        result = self.__xpPoolOfDeletedRals
        for i in self.getReferrals():
            result += i.getXPPool()

        return result

    def getAvailableReferralsCount(self):
        return _getMaxNumberOfReferrals() - len(self.__referrals)

    def showTankmanAwardWindow(self, tankman, completedQuestIDs):
        self.__showAwardWindow(tankman, completedQuestIDs)

    def showVehicleAwardWindow(self, vehicle, completedQuestIDs):
        self.__showAwardWindow(vehicle, completedQuestIDs)

    @classmethod
    def getRefPeriods(cls):
        return _getRefSystemPeriods()

    @classmethod
    def getMaxReferralXPPool(cls):
        return _getMaxReferralXPPool()

    @classmethod
    def getMaxNumberOfReferrals(cls):
        return _getMaxNumberOfReferrals()

    def getUserType(self, userDBID):
        if findFirst(lambda x: x.getAccountDBID() == userDBID, self.getReferrals()):
            return REFERRAL_SYSTEM.TYPE_REFERRAL
        if findFirst(lambda x: x.getAccountDBID() == userDBID, self.getReferrers()):
            return REFERRAL_SYSTEM.TYPE_REFERRER
        return REFERRAL_SYSTEM.TYPE_NO_REFERRAL

    def showReferrerIntroWindow(self):
        g_eventBus.handleEvent(events.ShowWindowEvent(events.ShowWindowEvent.SHOW_REFERRAL_REFERRER_INTRO_WINDOW))
        self.onPlayerBecomeReferrer()

    def showReferralIntroWindow(self, nickname, isNewbie = False):
        g_eventBus.handleEvent(events.ShowWindowEvent(events.ShowWindowEvent.SHOW_REFERRAL_REFERRALS_INTRO_WINDOW, ctx={'referrerName': nickname,
         'newbie': isNewbie}))
        self.onPlayerBecomeReferral()

    def __showAwardWindow(self, item, completedQuestIDs):
        LOG_DEBUG('Referrer has been get award', item, completedQuestIDs)
        completedQuestID = completedQuestIDs.pop() if len(completedQuestIDs) else -1
        currentXP = nextXP = None
        for xp, quests in reversed(self.getQuests()):
            if completedQuestID in map(methodcaller('getID'), quests):
                currentXP = xp
                break
            else:
                nextXP = xp

        g_eventBus.handleEvent(events.ShowWindowEvent(events.ShowWindowEvent.SHOW_AWARD_WINDOW, {'item': item,
         'xp': currentXP,
         'nextXp': nextXP,
         'boughtVehicle': self.getReferralsXPPool() < self.getTotalXP()}))
        return

    def __clearQuestsData(self):
        self.__quests = []
        self.__isTotallyCompleted = False
        self.__totalXP = 0

    def __update(self, data):
        self.__referrers = []
        self.__referrals = []
        self.__xpPoolOfDeletedRals = 0
        self.__posByXPinTeam = g_itemsCache.items.shop.refSystem['posByXPinTeam']
        self.__buildReferrers(data)
        self.__buildReferrals(data)
        self.onUpdated()

    @classmethod
    def __makeRefItem(cls, dbID, **data):
        try:
            return _RefItem(dbID, **data)
        except:
            LOG_ERROR('There is error while building ref system item')
            LOG_CURRENT_EXCEPTION()

    def __buildReferrers(self, data):
        for key, item in (data.get('referrers') or {}).iteritems():
            referrer = self.__makeRefItem(key, **item)
            if referrer is not None:
                self.__referrers.append(referrer)

        return

    def __buildReferrals(self, data):
        for key, item in (data.get('referrals') or {}).iteritems():
            if key == 'xpPoolOfDeletedRals':
                self.__xpPoolOfDeletedRals = item
            else:
                referral = self.__makeRefItem(key, **item)
                if referral is not None:
                    self.__referrals.append(referral)

        return

    def __updateQuests(self):
        self.__clearQuestsData()
        refSystemQuests = g_eventsCache.getSystemQuests(lambda x: x.getType() == EVENT_TYPE.REF_SYSTEM_QUEST)
        if refSystemQuests:
            self.__quests = self.__mapQuests(refSystemQuests.values())
            self.__totalXP, _ = self.__quests[-1]
            notCompleted = findFirst(lambda q: not q.isCompleted(), refSystemQuests.values())
            self.__isTotallyCompleted = notCompleted is None
        self.onQuestsUpdated()
        return

    @classmethod
    def __mapQuests(cls, events):
        result = defaultdict(list)
        for event in sorted(events, key=methodcaller('getID')):
            result[event.accountReqs.getConditions().find('refSystemRalXPPool').getValue()].append(event)

        return sorted(result.iteritems(), key=itemgetter(0))

    def __onRefStatsUpdated(self, diff):
        self.__update(g_itemsCache.items.stats.refSystem)

    def __onEventsUpdated(self):
        self.__updateQuests()

    def __onShopUpdated(self):
        self.__update(g_itemsCache.items.stats.refSystem)
        self.__updateQuests()


class _RefItem(object):

    def __init__(self, accountDBID, inviteCreationTime, nickName, clanDBID, clanAbbrev, firstBattleTime, xpPool, lastBattleTime, state):
        super(_RefItem, self).__init__()
        self.__accountDBID = accountDBID
        self.__inviteCreationTime = inviteCreationTime
        self.__nickName = nickName
        self.__clanDBID = clanDBID
        self.__clanAbbrev = clanAbbrev
        self.__firstBattleTime = firstBattleTime
        self.__xpPool = xpPool
        self.__lastBattleTime = lastBattleTime
        self.__state = state

    def getAccountDBID(self):
        return self.__accountDBID

    def getInviteCreationTime(self):
        return self.__inviteCreationTime

    def getNickName(self):
        return self.__nickName

    def getClanAbbrev(self):
        return self.__clanAbbrev

    def getClanDBID(self):
        return self.__clanDBID

    def getFullName(self):
        g_lobbyContext.getPlayerFullName(self.__nickName, clanAbbrev=self.__clanAbbrev, pDBID=self.__accountDBID)

    def getFirstBattleTime(self):
        return self.__firstBattleTime

    def getXPPool(self):
        return self.__xpPool

    def getLastBattleTime(self):
        return self.__lastBattleTime

    def getState(self):
        return self.__state

    def isNewbie(self):
        return bool(self.__state & REF_SYSTEM_FLAG.REFERRAL_NEW_PLAYER)

    def isPhoenix(self):
        return bool(self.__state & REF_SYSTEM_FLAG.REFERRAL_PHOENIX)

    def isConfirmedFirstBattle(self):
        return bool(self.__state & REF_SYSTEM_FLAG.CONFIRMED_FIRST_BATTLE)

    def isConfirmedInvite(self):
        return bool(self.__state & REF_SYSTEM_FLAG.CONFIRMED_INVITE)

    def getBonus(self):
        if self.isConfirmedFirstBattle():
            delta = time_utils.getTimeDeltaTilNow(self.__firstBattleTime)
            try:
                maxXPPool = _getMaxReferralXPPool()
                for period, bonus in _getRefSystemPeriods():
                    periodTime = period * time_utils.ONE_HOUR
                    if delta <= periodTime and self.__xpPool < maxXPPool:
                        timeLeft = 0
                        if periodTime <= time_utils.ONE_YEAR:
                            timeLeft = periodTime - delta
                        return (bonus, timeLeft)

            except KeyError:
                LOG_ERROR('Cannot read refSystem from shop')

        elif self.isConfirmedInvite():
            return (3.0, 0)
        return (1.0, 0)

    def getBonusTimeLeftStr(self):
        _, timeLeft = self.getBonus()
        if timeLeft:
            return time_utils.getTillTimeString(timeLeft, MENU.TIME_TIMEVALUE)
        return ''
