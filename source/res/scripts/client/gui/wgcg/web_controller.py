# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/wgcg/web_controller.py
from collections import defaultdict
import BigWorld
from PlayerEvents import g_playerEvents
from adisp import async, process
from client_request_lib.exceptions import ResponseCodes
from gui import SystemMessages
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.clans import formatters as clan_formatters, items
from gui.clans.clan_account_profile import MyClanAccountProfile
from gui.clans.clan_helpers import ClanCache, CachedValue
from gui.clans.settings import CLAN_APPLICATION_STATES, CLAN_DOSSIER_LIFE_TIME
from gui.clans.settings import CLAN_INVITE_STATES
from gui.clans.users import UserCache
from gui.shared.utils.decorators import ReprInjector
from gui.wgcg.clan.contexts import ClanInfoCtx, ClanGlobalMapStatsCtx, GetClanInvitesCount, GetClanAppsCount, ClanMembersCtx, GetProvincesCtx, ClanFavouriteAttributesCtx, ClanRatingsCtx
from gui.wgcg.hof.contexts import HofUserInfoCtx, HofUserExcludeCtx, HofUserRestoreCtx
from gui.wgcg.rank.contexts import RankedPositionCtx
from gui.wgcg.settings import WebRequestDataType
from gui.wgcg.states import UndefinedState
from gui.wgcg.strongholds.contexts import StrongholdInfoCtx, StrongholdStatisticsCtx
from gui.wgcg.subscriptions import WebListeners
from gui.wgnc import g_wgncEvents
from gui.wgnc.settings import WGNC_DATA_PROXY_TYPE
from helpers import dependency
from shared_utils import CONST_CONTAINER
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.web import IWebController

def _showError(result, ctx):
    i18nMsg = clan_formatters.getRequestErrorMsg(result, ctx)
    if i18nMsg:
        SystemMessages.pushMessage(i18nMsg, type=SystemMessages.SM_TYPE.Error)


class SYNC_KEYS(CONST_CONTAINER):
    INVITES = 1
    APPS = 2
    CLAN_INFO = 4
    ALL = INVITES | APPS


class _CACHE_KEYS(CONST_CONTAINER):
    INVITES = 1
    APPS = 2


_CLAN_WGNC_NOTIFICATION_TYPES = (WGNC_DATA_PROXY_TYPE.CLAN_APP,
 WGNC_DATA_PROXY_TYPE.CLAN_INVITE,
 WGNC_DATA_PROXY_TYPE.CLAN_APP_DECLINED,
 WGNC_DATA_PROXY_TYPE.CLAN_APP_ACCEPTED,
 WGNC_DATA_PROXY_TYPE.CLAN_INVITE_ACCEPTED,
 WGNC_DATA_PROXY_TYPE.CLAN_INVITE_DECLINED,
 WGNC_DATA_PROXY_TYPE.CLAN_INVITES_CREATED,
 WGNC_DATA_PROXY_TYPE.CLAN_APP_DECLINED_FOR_MEMBERS,
 WGNC_DATA_PROXY_TYPE.CLAN_APP_ACCEPTED_FOR_MEMBERS)

class _ClanDossier(object):

    def __init__(self, clanDbID, webCtrl, isMy):
        self._webCtrl = webCtrl
        self.__isMy = isMy
        self.__clanDbID = clanDbID
        self.__webCache = {}
        self.__cache = defaultdict(lambda : None)
        self.__processingRequests = defaultdict(list)
        self.__vitalInfo = defaultdict(lambda : None)
        self.__waitForSync = 0
        self.__syncState = 0
        self.__responseHandlers = {(WebRequestDataType.DECLINE_APPLICATION, WebRequestDataType.ACCEPT_APPLICATION): self.__applicationHandler,
         (WebRequestDataType.CREATE_INVITES,): self.__createInvitesHandler,
         (WebRequestDataType.CLAN_INVITES,): self.__clanInvitesHandler,
         (WebRequestDataType.CLAN_APPLICATIONS,): self.__clanApplicationHandler}
        self.__notificationHandlers = {(WGNC_DATA_PROXY_TYPE.CLAN_APP,): self.__clanAppNotificationHandler,
         (WGNC_DATA_PROXY_TYPE.CLAN_APP_ACCEPTED_FOR_MEMBERS, WGNC_DATA_PROXY_TYPE.CLAN_APP_DECLINED_FOR_MEMBERS): self.__clanMembersNotificationHandler,
         (WGNC_DATA_PROXY_TYPE.CLAN_INVITE_DECLINED, WGNC_DATA_PROXY_TYPE.CLAN_INVITE_ACCEPTED): self.__clanInviteNotificationHandler,
         (WGNC_DATA_PROXY_TYPE.CLAN_INVITES_CREATED,): self.__clanInviteCreatedNotificationHandler}

    def fini(self):
        self._webCtrl = None
        self.__webCache.clear()
        self.__cache.clear()
        self.__vitalInfo.clear()
        self.__waitForSync = 0
        self.__syncState = 0
        self.__responseHandlers = None
        self.__notificationHandlers = None
        return

    def isSynced(self, key=None):
        if key is None:
            for syncKey in self.__vitalInfo.keys():
                if not self.__syncState & syncKey:
                    return False

            return True
        else:
            return self.__syncState & key

    def getDbID(self):
        return self.__clanDbID

    def isMyClan(self):
        return self.__isMy

    def canIHandleClanInvites(self):
        return self.getLimits().canHandleClanInvites(self).success

    def isClanValid(self):
        return self.__clanDbID != 0

    def getLimits(self):
        return self._webCtrl.getLimits()

    def hasClanApplication(self, accountDbID):
        return accountDbID in self.__cache[_CACHE_KEYS.APPS] if self.__cache[_CACHE_KEYS.APPS] else False

    def isClanInviteSent(self, accountDbID):
        return accountDbID in self.__cache[_CACHE_KEYS.INVITES] if self.__cache[_CACHE_KEYS.INVITES] else False

    def resync(self, force=False):
        self.resyncClanInfo(force=force)
        self.resyncAppsCount(force=force)
        self.resyncInvitesCount(force=force)

    @process
    def resyncClanInfo(self, force=False):
        if self.__waitForSync & SYNC_KEYS.CLAN_INFO:
            return
        else:
            cachedValue = self.__webCache.get(WebRequestDataType.CLAN_INFO, None)
            isSynced = cachedValue is not None and not cachedValue.isExpired()
            if isSynced and not force:
                return
            self.__waitForSync |= SYNC_KEYS.CLAN_INFO
            if WebRequestDataType.CLAN_INFO in self.__webCache:
                del self.__webCache[WebRequestDataType.CLAN_INFO]
            clanInfo = yield self.requestClanInfo()
            self.__syncState |= SYNC_KEYS.CLAN_INFO
            self.__changeWebInfo(SYNC_KEYS.CLAN_INFO, clanInfo, 'onClanInfoReceived')
            self.__waitForSync ^= SYNC_KEYS.CLAN_INFO
            return

    def resyncAppsCount(self, force=False):
        if self.__waitForSync & SYNC_KEYS.APPS:
            return
        if self.isSynced(SYNC_KEYS.APPS) and not force:
            return
        self.__waitForSync |= SYNC_KEYS.APPS
        if self.__isMy and self.canIHandleClanInvites():
            self.__syncState |= SYNC_KEYS.APPS
        else:
            self.__vitalInfo[SYNC_KEYS.APPS] = 0
            self.__syncState |= SYNC_KEYS.APPS
        self.__waitForSync ^= SYNC_KEYS.APPS

    def resyncInvitesCount(self, force=False):
        if self.__waitForSync & SYNC_KEYS.INVITES:
            return
        if self.isSynced(SYNC_KEYS.INVITES) and not force:
            return
        self.__waitForSync |= SYNC_KEYS.INVITES
        if self.__isMy and self.canIHandleClanInvites():
            self.__syncState |= SYNC_KEYS.INVITES
        else:
            self.__vitalInfo[SYNC_KEYS.APPS] = 0
            self.__syncState |= SYNC_KEYS.INVITES
        self.__waitForSync ^= SYNC_KEYS.INVITES

    def getClanInfo(self):
        self.resyncClanInfo()
        cachedValue = self.__webCache.get(WebRequestDataType.CLAN_INFO, None)
        return cachedValue.getCachedValue() if cachedValue is not None else items.ClanExtInfoData()

    def canAcceptsJoinRequests(self):
        return self.getClanInfo().isOpened()

    def hasFreePlaces(self):
        return self.getClanInfo().hasFreePlaces()

    def getInvitesCount(self):
        self.resyncInvitesCount()
        return self.__vitalInfo[SYNC_KEYS.INVITES]

    def getAppsCount(self):
        self.resyncAppsCount()
        return self.__vitalInfo[SYNC_KEYS.APPS]

    @async
    def requestClanInfo(self, callback):
        self.__doRequest(ClanInfoCtx(self.__clanDbID), callback)

    @async
    @process
    def requestClanRatings(self, callback):
        result = yield self.__requestClanRatings()
        if result:
            callback(result[0])
        else:
            callback(items.ClanRatingsData())

    @async
    def requestGlobalMapStats(self, callback):
        self.__doRequest(ClanGlobalMapStatsCtx(self.__clanDbID), callback)

    @async
    def requestStrongholdInfo(self, callback):
        self.__doRequest(StrongholdInfoCtx(self.__clanDbID), callback)

    @async
    def requestStrongholdStatistics(self, callback):
        self.__doRequest(StrongholdStatisticsCtx(self.__clanDbID), callback)

    @async
    def requestInvitationsCount(self, callback):
        self.__doRequest(GetClanInvitesCount(self.__clanDbID, statuses=[CLAN_INVITE_STATES.ACTIVE]), callback)

    @async
    def requestApplicationsCount(self, callback, isForced):
        self.__doRequest(GetClanAppsCount(self.__clanDbID, not isForced, statuses=[CLAN_INVITE_STATES.ACTIVE]), callback)

    @async
    def requestMembers(self, callback):
        self.__doRequest(ClanMembersCtx(self.__clanDbID), callback)

    @async
    def requestProvinces(self, callback):
        self.__doRequest(GetProvincesCtx(self.__clanDbID), callback)

    @async
    def requestFavouriteAttributes(self, callback):
        self.__doRequest(ClanFavouriteAttributesCtx(self.__clanDbID), callback)

    @async
    def requestRankedPosition(self, callback):
        self.__doRequest(RankedPositionCtx(), callback)

    @async
    def requestHofUserInfo(self, callback):
        self.__doRequest(HofUserInfoCtx(), callback)

    @async
    def requestHofUserExclude(self, callback):
        self.__doRequest(HofUserExcludeCtx(), callback)

    @async
    def requestHofUserRestore(self, callback):
        self.__doRequest(HofUserRestoreCtx(), callback)

    def processRequestResponse(self, ctx, response):
        requestType = ctx.getRequestType()
        for types, handler in self.__responseHandlers.items():
            if requestType in types:
                handler(ctx, response)
                break

    def processWgncNotification(self, notifID, item):
        itemType = item.getType()
        for types, handler in self.__notificationHandlers.items():
            if itemType in types:
                handler(notifID, item)
                break

    def processClanMembersListChange(self, memberIDs):
        cachedValue = self.__webCache.get(WebRequestDataType.CLAN_INFO, None)
        if cachedValue is not None:
            needResync = cachedValue.getCachedValue().getMembersCount() != len(memberIDs)
        else:
            needResync = True
        if needResync:
            self.__syncState &= ~SYNC_KEYS.CLAN_INFO
            if WebRequestDataType.CLAN_INFO in self.__webCache:
                del self.__webCache[WebRequestDataType.CLAN_INFO]
            if WebRequestDataType.CLAN_MEMBERS in self.__webCache:
                del self.__webCache[WebRequestDataType.CLAN_MEMBERS]
        return

    def updateClanCache(self, cache):
        apps = self.__vitalInfo[SYNC_KEYS.APPS] or 0
        invites = self.__vitalInfo[SYNC_KEYS.INVITES] or 0
        cache.set(ClanCache.KEYS.CLAN_APPS, apps)
        cache.set(ClanCache.KEYS.CLAN_INVITES, invites)

    def processClanCache(self, cache):
        apps = cache.get(ClanCache.KEYS.CLAN_APPS) or 0
        if apps:
            count = self.__vitalInfo[SYNC_KEYS.APPS] or 0
            count += apps
            self.__changeWebInfo(SYNC_KEYS.APPS, count, 'onClanAppsCountReceived')
        invites = cache.get(ClanCache.KEYS.CLAN_INVITES) or 0
        if invites:
            count = self.__vitalInfo[SYNC_KEYS.INVITES] or 0
            count += invites
            self.__changeWebInfo(SYNC_KEYS.INVITES, count, 'onClanInvitesCountReceived')

    @async
    def __requestClanRatings(self, callback):
        self.__doRequest(ClanRatingsCtx([self.__clanDbID]), callback)

    @process
    def __doRequest(self, ctx, callback):
        requestType = ctx.getRequestType()
        cachedValue = self.__webCache.get(requestType, None)
        if cachedValue is not None and cachedValue.isExpired():
            cachedValue = None
        if cachedValue is None:
            if requestType not in self.__processingRequests:
                self.__processingRequests[requestType].append(callback)
                result = yield self._webCtrl.sendRequest(ctx)
                if result.isSuccess():
                    formattedData = ctx.getDataObj(result.data)
                    if ctx.isCaching():
                        cachedValue = CachedValue(CLAN_DOSSIER_LIFE_TIME)
                        cachedValue.set(formattedData)
                        self.__webCache[requestType] = cachedValue
                else:
                    formattedData = ctx.getDefDataObj()
                for cb in self.__processingRequests[requestType]:
                    cb(formattedData)

                del self.__processingRequests[requestType]
            else:
                self.__processingRequests[requestType].append(callback)
        else:
            callback(cachedValue.getCachedValue())
        return

    def __changeWebInfo(self, fieldName, value, eventName):
        self.__vitalInfo[fieldName] = value
        self._webCtrl.notify(eventName, self.__clanDbID, value)
        self._webCtrl.notify('onClanWebVitalInfoChanged', self.__clanDbID, fieldName, value)

    def __cantResync(self, force, waitForSync):
        return not self.isClanValid() or waitForSync or self.isSynced() and not force

    def __applicationHandler(self, ctx, response):
        if not response.isSuccess():
            return
        requestType = ctx.getRequestType()
        cached = self.__cache[_CACHE_KEYS.APPS] or set()
        cached.discard(ctx.getDataObj(response.data).getAccountDbID())
        self.__cache[_CACHE_KEYS.APPS] = cached
        count = self.__vitalInfo[SYNC_KEYS.APPS]
        if count:
            self.__changeWebInfo(SYNC_KEYS.APPS, count - 1, 'onClanAppsCountReceived')
        if requestType == WebRequestDataType.DECLINE_APPLICATION:
            state = CLAN_APPLICATION_STATES.DECLINED
        else:
            state = CLAN_APPLICATION_STATES.ACCEPTED
        self._webCtrl.notify('onClanAppStateChanged', ctx.getApplicationDbID(), state)

    def __createInvitesHandler(self, ctx, response):
        if response.isSuccess():
            count = len(response.data)
            if count:
                result = ctx.getDataObj(response.data)
                cached = self.__cache[_CACHE_KEYS.INVITES] or set()
                for item in result:
                    cached.add(item.getAccountDbID())

                self.__cache[_CACHE_KEYS.INVITES] = cached
                invites = self.__vitalInfo[SYNC_KEYS.INVITES] or 0
                count = count + invites
                self.__changeWebInfo(SYNC_KEYS.INVITES, count, 'onClanInvitesCountReceived')
        else:
            code = response.getCode()
            if code not in (ResponseCodes.ACCOUNT_ALREADY_APPLIED, ResponseCodes.ACCOUNT_ALREADY_INVITED):
                return
            successAccounts = [ item.getAccountDbID() for item in ctx.getDataObj(response.data) ]
            failedAccounts = set(ctx.getAccountDbIDs()) - set(successAccounts)
            if code == ResponseCodes.ACCOUNT_ALREADY_APPLIED:
                cached = self.__cache[_CACHE_KEYS.APPS] or set()
                cached.update(failedAccounts)
                self.__cache[_CACHE_KEYS.APPS] = cached
            elif code == ResponseCodes.ACCOUNT_ALREADY_INVITED:
                cached = self.__cache[_CACHE_KEYS.INVITES] or set()
                cached.update(failedAccounts)
                self.__cache[_CACHE_KEYS.INVITES] = cached

    def __clanInvitesHandler(self, ctx, response):
        if not response.isSuccess():
            return
        else:
            statuses = ctx.getStatuses() or []
            if len(statuses) == 1 and statuses[0] == CLAN_INVITE_STATES.ACTIVE:
                count = ctx.getTotalCount(response.data)
                result = ctx.getDataObj(response.data)
                if count is not None and count <= len(result):
                    cached = set()
                else:
                    cached = self.__cache[_CACHE_KEYS.INVITES] or set()
                for item in result:
                    cached.add(item.getAccountDbID())

                self.__cache[_CACHE_KEYS.INVITES] = cached
                if count is not None and count != self.__vitalInfo[SYNC_KEYS.INVITES]:
                    self.__changeWebInfo(SYNC_KEYS.INVITES, count, 'onClanInvitesCountReceived')
            return

    def __clanApplicationHandler(self, ctx, response):
        if not response.isSuccess():
            return
        else:
            statuses = ctx.getStatuses() or []
            if len(statuses) == 1 and statuses[0] == CLAN_INVITE_STATES.ACTIVE:
                count = ctx.getTotalCount(response.data)
                result = ctx.getDataObj(response.data)
                if count is not None and count <= len(result):
                    cached = set()
                else:
                    cached = self.__cache[_CACHE_KEYS.APPS] or set()
                for item in result:
                    cached.add(item.getAccountDbID())

                self.__cache[_CACHE_KEYS.APPS] = cached
                if count is not None and count != self.__vitalInfo[SYNC_KEYS.APPS]:
                    self.__changeWebInfo(SYNC_KEYS.APPS, count, 'onClanAppsCountReceived')
            return

    def __clanAppNotificationHandler(self, notifID, item):
        cached = self.__cache[_CACHE_KEYS.APPS] or set()
        cached.add(item.getAccountID())
        self.__cache[_CACHE_KEYS.APPS] = cached
        count = item.getActiveApplicationsCount()
        if count != self.__vitalInfo[SYNC_KEYS.APPS]:
            self.__changeWebInfo(SYNC_KEYS.APPS, count, 'onClanAppsCountReceived')
        self.__syncState |= SYNC_KEYS.APPS

    def __clanMembersNotificationHandler(self, notifID, item):
        cached = self.__cache[_CACHE_KEYS.APPS] or set()
        oldLength = len(cached)
        cached.discard(item.getAccountID())
        self.__cache[_CACHE_KEYS.APPS] = cached
        newLength = len(cached)
        if oldLength != newLength:
            self.__changeWebInfo(SYNC_KEYS.APPS, newLength, 'onClanAppsCountReceived')

    def __clanInviteNotificationHandler(self, notifID, item):
        itemType = item.getType()
        cached = self.__cache[_CACHE_KEYS.INVITES] or set()
        cached.discard(item.getAccountID())
        self.__cache[_CACHE_KEYS.INVITES] = cached
        if itemType == WGNC_DATA_PROXY_TYPE.CLAN_INVITE_ACCEPTED:
            self.__syncState &= ~SYNC_KEYS.CLAN_INFO
            if WebRequestDataType.CLAN_INFO in self.__webCache:
                del self.__webCache[WebRequestDataType.CLAN_INFO]
            if WebRequestDataType.CLAN_MEMBERS in self.__webCache:
                del self.__webCache[WebRequestDataType.CLAN_MEMBERS]
        count = self.__vitalInfo[SYNC_KEYS.INVITES]
        if count:
            self.__changeWebInfo(SYNC_KEYS.INVITES, count - 1, 'onClanInvitesCountReceived')

    def __clanInviteCreatedNotificationHandler(self, notifID, item):
        currentInvitesCount = self.__vitalInfo[SYNC_KEYS.INVITES] or 0
        self.__changeWebInfo(SYNC_KEYS.INVITES, item.getNewInvitesCount() + currentInvitesCount, 'onClanInvitesCountReceived')

    def __repr__(self):
        return 'ClanDossier(dbID = %d, my = %s, web = %s, cache = %s)' % (self.__clanDbID,
         self.__isMy,
         self.__vitalInfo,
         self.__webCache.keys())


@ReprInjector.simple(('__state', 'state'), ('__profile', 'profile'))
class WebController(WebListeners, IWebController):
    lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self):
        super(WebController, self).__init__()
        self.__cache = {}
        self.__searchDataCache = {}
        self.__state = None
        self.__profile = None
        self.__userCache = None
        self.__clanCache = None
        self.__simWGCGEnabled = True
        return

    def simEnableWGCG(self, enable):
        self.__simWGCGEnabled = enable
        if self.__profile:
            self.__profile.resync(force=True)

    def simEnableClan(self, enable):
        settings = self.lobbyContext.getServerSettings()
        clanSettings = {'wgcgProfile': {'isEnabled': enable,
                         'gateUrl': settings.wgcg.getGateUrl()}}
        settings.update(clanSettings)
        g_clientUpdateManager.update({'serverSettings': clanSettings})

    def simWGCGEnabled(self):
        return self.__simWGCGEnabled

    def init(self):
        self.__userCache = UserCache(self)
        self.__state = UndefinedState(self)
        self.__state.init()

    def fini(self):
        self.stop()
        self.__state.fini()
        self.__state = None
        self.__userCache = None
        return

    def start(self):
        self.__profile = MyClanAccountProfile(self)
        self.__clanCache = ClanCache(self.__profile.getDbID())
        self.__clanCache.onRead += self._onClanCacheRead
        self.__clanCache.read()
        self.invalidate()
        g_clientUpdateManager.addCallbacks({'stats.clanInfo': self.__onClanInfoChanged,
         'serverSettings.wgcg.isEnabled': self.__onServerSettingChanged,
         'serverSettings.clanProfile.isEnabled': self.__onClanEnableChanged})
        g_wgncEvents.onProxyDataItemShowByDefault += self._onProxyDataItemShowByDefault
        g_playerEvents.onClanMembersListChanged += self._onClanMembersListChanged

    def stop(self, logout=True):
        g_playerEvents.onClanMembersListChanged -= self._onClanMembersListChanged
        g_wgncEvents.onProxyDataItemShowByDefault -= self._onProxyDataItemShowByDefault
        g_clientUpdateManager.removeObjectCallbacks(self)
        if self.__clanCache is not None:
            self.__clanCache.onRead -= self._onClanCacheRead
            self.__profile.updateClanCache(self.__clanCache)
            self.__clanCache.write()
            self.__clanCache = None
        if self.__profile is not None:
            self.__profile.fini()
            self.__profile = None
        if logout:
            self.__state.logout()
        self.__cleanDossiers()
        return

    def invalidate(self):
        self.__state.update()

    def getClanDossier(self, clanDbID=None):
        if clanDbID in self.__cache:
            dossier = self.__cache[clanDbID]
        else:
            dossier = self.__cache[clanDbID] = _ClanDossier(clanDbID, self, isMy=clanDbID == self.__profile.getClanDbID())
        return dossier

    @async
    @process
    def login(self, callback):
        yield self.__state.loginAsync()
        callback(True)

    def resyncLogin(self, forceLogin=False):
        perms = self.__profile.getMyClanPermissions()
        if forceLogin or perms.canHandleClanInvites() and perms.canTrade() and perms.canExchangeMoney():
            self.__state.login()

    @async
    @process
    def sendRequest(self, ctx, callback=None, allowDelay=None):
        result = yield self.__state.sendRequest(ctx, allowDelay=allowDelay)
        if self.__profile is not None:
            self.__profile.processRequestResponse(ctx, result)
        if not result.isSuccess():
            _showError(result, ctx)
        callback(result)
        return

    def getStateID(self):
        return self.__state.getStateID()

    def isEnabled(self):
        settings = self.lobbyContext.getServerSettings()
        return settings.wgcg.isEnabled() if settings is not None else True

    def compareStates(self, state):
        return self.__state.compare(state)

    def isAvailable(self):
        return self.__state.isAvailable()

    def getWebRequester(self):
        return self.__state.getWebRequester()

    def getAccountProfile(self):
        return self.__profile

    def getLimits(self):
        return self.__state.getLimits(self.__profile)

    def getClanDbID(self):
        return self.__profile.getClanDbID() if self.__profile else None

    def changeState(self, state):
        self.__state = state

    def onStateUpdated(self):
        if self.__profile and self.__state.isLoggedOn():
            self.__profile.resync()

    def isLoggedOn(self):
        return self.__state.isLoggedOn()

    @async
    @process
    def getAccessTokenData(self, force, callback=None):
        accessToken = yield self.__state.getAccessTokenData(force)
        callback(accessToken)

    def updateClanCommonDataCache(self, cache):
        for item in cache or {}:
            self.__searchDataCache[item.getDbID()] = item

    def clearClanCommonDataCache(self):
        self.__searchDataCache = {}

    def getClanCommonData(self, clanDbID):
        return self.__searchDataCache.get(clanDbID, None)

    @async
    @process
    def requestUsers(self, dbIDs, callback):
        result = yield self.__userCache.requestUsers(dbIDs)
        callback(result)

    def _onProxyDataItemShowByDefault(self, notifID, item):
        if item.getType() in _CLAN_WGNC_NOTIFICATION_TYPES:
            if self.__profile is not None:
                self.__profile.processWgncNotification(notifID, item)
            self.notify('onWgncNotificationReceived', notifID, item)
        return

    def _onClanMembersListChanged(self):
        memberIDs = getattr(BigWorld.player(), 'clanMembers', {}).keys()
        if self.__profile is not None:
            self.__profile.processClanMembersListChange(memberIDs)
        self.notify('onMembersListChanged', memberIDs)
        return

    def _onClanCacheRead(self):
        if self.__profile is not None and self.__clanCache is not None:
            self.__profile.processClanCache(self.__clanCache)
        return

    def __onClanInfoChanged(self, _):
        self.__profile.resyncBwInfo()
        self.resyncLogin()

    def __onServerSettingChanged(self, *args):
        self.invalidate()

    def __onClanEnableChanged(self, *args):
        settings = self.lobbyContext.getServerSettings()
        self.notify('onClanEnableChanged', settings.clanProfile.isEnabled())

    def __cleanDossiers(self):
        for _, v in self.__cache.iteritems():
            v.fini()

        self.__cache.clear()
