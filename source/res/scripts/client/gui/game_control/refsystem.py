# Embedded file name: scripts/client/gui/game_control/RefSystem.py
from collections import defaultdict
from operator import methodcaller, itemgetter
import BigWorld
from Event import Event, EventManager
from PlayerEvents import g_playerEvents
from constants import REF_SYSTEM_FLAG, EVENT_TYPE
from debug_utils import LOG_ERROR, LOG_CURRENT_EXCEPTION, LOG_DEBUG
from helpers import time_utils
from helpers.i18n import makeString as _ms
from shared_utils import findFirst
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.AwardWindow import AwardAbstract
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.game_control.controllers import Controller
from gui.shared.formatters import icons, text_styles
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.LobbyContext import g_lobbyContext
from gui.Scaleform.locale.MENU import MENU
from gui.shared import g_itemsCache, events, g_eventBus, event_dispatcher as shared_events, EVENT_BUS_SCOPE
from gui.server_events import g_eventsCache
from messenger.m_constants import USER_TAG
from messenger.proto.entities import SharedUserEntity, ClanInfo
from messenger.proto.events import g_messengerEvents
from messenger.storage import storage_getter

def _getRefSysCfg():
    return g_itemsCache.items.shop.refSystem or {}


def _getRefSystemPeriods():
    return _getRefSysCfg()['periods']


def _getMaxReferralXPPool():
    return _getRefSysCfg()['maxReferralXPPool']


def _getMaxNumberOfReferrals():
    return _getRefSysCfg()['maxNumberOfReferrals']


class CreditsAward(AwardAbstract):

    def __init__(self, creditsValue):
        self.__creditsValue = long(creditsValue)

    def getWindowTitle(self):
        return _ms(MENU.AWARDWINDOW_TITLE_CREDITS)

    def getBackgroundImage(self):
        return RES_ICONS.MAPS_ICONS_REFERRAL_AWARDBACK

    def getAwardImage(self):
        return RES_ICONS.MAPS_ICONS_REFERRAL_AWARD_CREDITS_GLOW

    def getHeader(self):
        return text_styles.highTitle(_ms(MENU.AWARDWINDOW_REFERRAL_CREDITS_HEADER))

    def getDescription(self):
        creditsCount = '%s<nobr>%s' % (text_styles.credits(BigWorld.wg_getIntegralFormat(self.__creditsValue)), icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_CREDITSICON_2, 16, 16, -4, 0))
        return text_styles.main(_ms(MENU.AWARDWINDOW_REFERRAL_CREDITS_DESCRIPTION, credits=creditsCount))


class VehicleAward(AwardAbstract):

    def __init__(self, vehicle, boughtVehicle, achievedXp):
        self.__vehicle = vehicle
        self.__boughtVehicle = boughtVehicle
        self.__achievedXp = achievedXp

    def getWindowTitle(self):
        return _ms(MENU.AWARDWINDOW_TITLE_NEWVEHICLE)

    def getBackgroundImage(self):
        return RES_ICONS.MAPS_ICONS_REFERRAL_AWARDBACK

    def getAwardImage(self):
        return self.__vehicle.iconUniqueLight

    def getHeader(self):
        return text_styles.highTitle(_ms(MENU.AWARDWINDOW_REFERRAL_VEHICLE_HEADER, vehicleName=self.__vehicle.userName))

    def getDescription(self):
        if self.__boughtVehicle:
            descriptionText = _ms(MENU.AWARDWINDOW_REFERRAL_VEHICLE_DESCRIPTION_BOUGHT, vehicleName=self.__vehicle.userName)
        elif self.__achievedXp is not None:
            descriptionText = _ms(MENU.AWARDWINDOW_REFERRAL_VEHICLE_DESCRIPTION_NORMAL, expCount=BigWorld.wg_getIntegralFormat(self.__achievedXp), vehicleName=self.__vehicle.userName)
        else:
            descriptionText = _ms(MENU.AWARDWINDOW_REFERRAL_VEHICLE_DESCRIPTION_NOXP, vehicleName=self.__vehicle.userName)
        return text_styles.main(descriptionText)

    def getAdditionalText(self):
        result = []
        for _, xpFactor in _getRefSystemPeriods():
            result.append('%s<nobr>x%s' % (icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_XPCOSTICON, 18, 18, -8, 0), BigWorld.wg_getNiceNumberFormat(xpFactor)))

        return text_styles.main(_ms(MENU.AWARDWINDOW_REFERRAL_COMPLETE, modifiers=', '.join(result)))


class TankmanAward(AwardAbstract):

    def __init__(self, tankman, achievedXp, nextXp):
        self.__tankman = tankman
        self.__achievedXp = achievedXp
        self.__nextXp = nextXp

    def getWindowTitle(self):
        return _ms(MENU.AWARDWINDOW_TITLE_NEWTANKMAN)

    def getBackgroundImage(self):
        return RES_ICONS.MAPS_ICONS_REFERRAL_AWARDBACK

    def getAwardImage(self):
        return RES_ICONS.MAPS_ICONS_REFERRAL_TANKMANMALE

    def getHeader(self):
        return text_styles.highTitle(_ms(MENU.AWARDWINDOW_REFERRAL_TANKMAN_HEADER))

    def getDescription(self):
        if self.__achievedXp is not None:
            description = _ms(MENU.AWARDWINDOW_REFERRAL_TANKMAN_DESCRIPTION_NORMAL, expCount=BigWorld.wg_getIntegralFormat(self.__achievedXp), tankman=self.__tankman.roleUserName)
        else:
            description = _ms(MENU.AWARDWINDOW_REFERRAL_TANKMAN_DESCRIPTION_NOXP, tankman=self.__tankman.roleUserName)
        return text_styles.main(description)

    def getAdditionalText(self):
        if self.__nextXp is not None:
            expCount = '%s<nobr>%s' % (BigWorld.wg_getIntegralFormat(self.__nextXp), icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_XPCOSTICON, 18, 18, -8, 0))
            additionalText = _ms(MENU.AWARDWINDOW_REFERRAL_NEXTTANKMAN, expCount=text_styles.credits(expCount))
        else:
            additionalText = ''
        return text_styles.main(additionalText)


class RefSystem(Controller):

    def __init__(self, proxy):
        super(RefSystem, self).__init__(proxy)
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

    @storage_getter('users')
    def usersStorage(self):
        return None

    def fini(self):
        self.__referrers = None
        self.__referrals = None
        self.__eventMgr.clear()
        self.__clearQuestsData()
        super(RefSystem, self).fini()
        return

    def onLobbyStarted(self, ctx):
        g_clientUpdateManager.addCallbacks({'stats.refSystem': self.__onRefStatsUpdated})
        g_eventsCache.onSyncCompleted += self.__onEventsUpdated
        g_playerEvents.onShopResync += self.__onShopUpdated
        self.__update(g_itemsCache.items.stats.refSystem)
        self.__updateQuests()

    def onAvatarBecomePlayer(self):
        self.__stop()

    def onDisconnected(self):
        self.__stop()

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
        LOG_DEBUG('Referrer has been get tankman award', tankman, completedQuestIDs)
        curXp, nextXp, _ = self.__getAwardParams(completedQuestIDs)
        shared_events.showAwardWindow(TankmanAward(tankman, curXp, nextXp))

    def showVehicleAwardWindow(self, vehicle, completedQuestIDs):
        LOG_DEBUG('Referrer has been get vehicle award', vehicle, completedQuestIDs)
        curXp, nextXp, isBoughtVehicle = self.__getAwardParams(completedQuestIDs)
        shared_events.showAwardWindow(VehicleAward(vehicle, isBoughtVehicle, curXp))

    def showCreditsAwardWindow(self, creditsValue, completedQuestIDs):
        if creditsValue > 0:
            LOG_DEBUG('Referrer has been get credits award', creditsValue, completedQuestIDs)
            shared_events.showAwardWindow(CreditsAward(creditsValue))

    @classmethod
    def getRefPeriods(cls):
        return _getRefSystemPeriods()

    @classmethod
    def getMaxReferralXPPool(cls):
        return _getMaxReferralXPPool()

    @classmethod
    def getMaxNumberOfReferrals(cls):
        return _getMaxNumberOfReferrals()

    @classmethod
    def isReferrer(cls):
        refSystemStats = g_itemsCache.items.stats.refSystem
        return refSystemStats.get('activeInvitations', 0) > 0 or len(refSystemStats.get('referrals', {})) > 0

    def showReferrerIntroWindow(self, invitesCount):
        g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.REFERRAL_REFERRER_INTRO_WINDOW, ctx={'invitesCount': invitesCount}), EVENT_BUS_SCOPE.LOBBY)
        self.onPlayerBecomeReferrer()

    def showReferralIntroWindow(self, nickname, isNewbie = False):
        g_eventBus.handleEvent(events.LoadViewEvent(VIEW_ALIAS.REFERRAL_REFERRALS_INTRO_WINDOW, ctx={'referrerName': nickname,
         'newbie': isNewbie}), EVENT_BUS_SCOPE.LOBBY)
        self.onPlayerBecomeReferral()

    def __stop(self):
        g_playerEvents.onShopResync -= self.__onShopUpdated
        g_eventsCache.onSyncCompleted -= self.__onEventsUpdated
        g_clientUpdateManager.removeObjectCallbacks(self)

    def __getAwardParams(self, completedQuestIDs):
        completedQuestID = completedQuestIDs.pop() if len(completedQuestIDs) else -1
        currentXP = nextXP = None
        for xp, quests in reversed(self.getQuests()):
            if completedQuestID in map(methodcaller('getID'), quests):
                currentXP = xp
                break
            else:
                nextXP = xp

        return (currentXP, nextXP, self.getReferralsXPPool() < self.getTotalXP())

    def __clearQuestsData(self):
        self.__quests = []
        self.__isTotallyCompleted = False
        self.__totalXP = 0

    def __update(self, data):
        self.__referrers = []
        self.__referrals = []
        self.__xpPoolOfDeletedRals = 0
        self.__posByXPinTeam = g_itemsCache.items.shop.refSystem['posByXPinTeam']
        storage = self.usersStorage
        userGetter = storage.getUser
        userSetter = storage.addUser
        storage.removeTags({USER_TAG.REFERRER, USER_TAG.REFERRAL})

        def updateUser(item, tags):
            dbID = item.getAccountDBID()
            user = userGetter(dbID)
            if user:
                user.addTags(tags)
                if USER_TAG.INVALID_NAME in user.getTags():
                    user.update(name=item.getNickName())
            else:
                userSetter(SharedUserEntity(dbID, name=item.getNickName(), tags=tags, clanInfo=ClanInfo(abbrev=item.getClanAbbrev())))

        for referrer in self.__buildReferrers(data):
            self.__referrers.append(referrer)
            updateUser(referrer, {USER_TAG.REFERRER})

        for referral in self.__buildReferrals(data):
            self.__referrals.append(referral)
            updateUser(referral, {USER_TAG.REFERRAL})

        self.onUpdated()
        g_messengerEvents.users.onUsersListReceived({USER_TAG.REFERRER, USER_TAG.REFERRAL})

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
                yield referrer

        return

    def __buildReferrals(self, data):
        for key, item in (data.get('referrals') or {}).iteritems():
            if key == 'xpPoolOfDeletedRals':
                self.__xpPoolOfDeletedRals = item
            else:
                referral = self.__makeRefItem(key, **item)
                if referral is not None:
                    yield referral

        return

    def __updateQuests(self):
        self.__clearQuestsData()
        refSystemQuests = g_eventsCache.getHiddenQuests(lambda x: x.getType() == EVENT_TYPE.REF_SYSTEM_QUEST)
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
        return g_lobbyContext.getPlayerFullName(self.__nickName, clanAbbrev=self.__clanAbbrev, pDBID=self.__accountDBID)

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
                periodTime = 0
                for period, bonus in _getRefSystemPeriods():
                    periodTime += period * time_utils.ONE_HOUR
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
