# Python 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/clans/clan_account_profile.py
import weakref
from collections import namedtuple, defaultdict
from adisp import process
from client_request_lib.exceptions import ResponseCodes
from helpers import time_utils
from account_helpers import getAccountDatabaseID
from messenger.ext import passCensor
from shared_utils import CONST_CONTAINER
from debug_utils import LOG_DEBUG
from gui.shared import g_itemsCache
from gui.clans import contexts, formatters as clans_fmts
from gui.clans.restrictions import ClanMemberPermissions, DefaultClanMemberPermissions
from gui.clans.settings import CLAN_REQUESTED_DATA_TYPE, CLAN_INVITE_STATES, INVITE_LIMITS_LIFE_TIME
from gui.clans.clan_helpers import ClanCache, CachedValue
from gui.wgnc.settings import WGNC_DATA_PROXY_TYPE

class SYNC_KEYS(CONST_CONTAINER):
    INVITES = 1
    APPS = 2
    CLAN_INFO = 4
    ALL = INVITES | APPS | CLAN_INFO


_ClanInfo = namedtuple('_ClanInfo', ['clanName',
 'clanAbbrev',
 'chatChannelDBID',
 'memberFlags',
 'enteringTime'])

class _CACHE_KEYS(CONST_CONTAINER):
    INVITES = 1
    APPS = 2


class ClanAccountProfile(object):

    def __init__(self, clansCtrl, accountDbID, clanDbID = 0, clanBwInfo = None):
        self._clansCtrl = weakref.proxy(clansCtrl)
        self._accountDbID = accountDbID
        self._clanDbID = clanDbID
        self._clanBwInfo = clanBwInfo
        self._waitForSync = 0
        self._syncState = 0
        self._vitalWebInfo = defaultdict(lambda : None)
        self._cache = defaultdict(lambda : None)
        self._isInvitesLimitReached = CachedValue(INVITE_LIMITS_LIFE_TIME)

    def fini(self):
        self._waitForSync = 0
        self._syncState = 0
        self._vitalWebInfo.clear()
        self._cache.clear()

    def getPermissions(self, clanDossier):
        if clanDossier and clanDossier.getDbID() == self._clanDbID:
            return ClanMemberPermissions(self.getRole())
        return DefaultClanMemberPermissions()

    def getMyClanPermissions(self):
        if self.isInClan():
            return self.getPermissions(self.getClanDossier())
        return DefaultClanMemberPermissions()

    def getClanDossier(self):
        return self._clansCtrl.getClanDossier(self._clanDbID)

    def isSynced(self, key = None):
        if key is None:
            for key in self._vitalWebInfo.keys():
                if not self._syncState & key:
                    return False

            return True
        else:
            return self._syncState & key

    def getDbID(self):
        return self._accountDbID

    def getRole(self):
        return self._getClanInfoValue(3, 0)

    def getRoleUserString(self):
        return clans_fmts.getClanRoleString(self.getRole())

    def isInClan(self):
        return self._clanDbID != 0

    def getClanDbID(self):
        return self._clanDbID

    def getClanName(self):
        return passCensor(self._getClanInfoValue(0, ''))

    def getClanFullName(self):
        return '{} {}'.format(clans_fmts.getClanAbbrevString(self.getClanAbbrev()), self.getClanName())

    def getClanAbbrev(self):
        return passCensor(self._getClanInfoValue(1, ''))

    def getJoinedAt(self):
        return self._getClanInfoValue(4, 0)

    def isInClanEnterCooldown(self):
        self.resyncWebClanInfo()
        if self._vitalWebInfo[SYNC_KEYS.CLAN_INFO]:
            return time_utils.getCurrentTimestamp() - self._vitalWebInfo[SYNC_KEYS.CLAN_INFO].getClanCooldownTill() <= 0
        return False

    def hasClanInvite(self, clanDbID):
        if self._cache[_CACHE_KEYS.INVITES]:
            return clanDbID in self._cache[_CACHE_KEYS.INVITES]
        return False

    def isClanApplicationSent(self, clanDbID):
        if self._cache[_CACHE_KEYS.APPS]:
            return clanDbID in self._cache[_CACHE_KEYS.APPS]
        return False

    def getInvitesCount(self):
        self.resyncInvites()
        return self._vitalWebInfo[SYNC_KEYS.INVITES]

    def getApplicationsCount(self):
        self.resyncApps()
        return self._vitalWebInfo[SYNC_KEYS.APPS]

    def isInvitesLimitReached(self):
        return self._isInvitesLimitReached.get(defValue=False)

    def resync(self, force = False):
        LOG_DEBUG('Full account clan profile resync initiated')
        self.resyncInvites(force=force)
        self.resyncApps(force=force)
        self.resyncWebClanInfo(force=force)
        if self.isInClan():
            self.getClanDossier().resync(force=force)

    @process
    def resyncWebClanInfo(self, force = False):
        if self._waitForSync & SYNC_KEYS.CLAN_INFO:
            return
        if self.isSynced(SYNC_KEYS.CLAN_INFO) and not force:
            return
        self._waitForSync |= SYNC_KEYS.CLAN_INFO
        ctx = contexts.GetClanInfoCtx(self._accountDbID)
        if self.isInClan():
            self._vitalWebInfo[SYNC_KEYS.CLAN_INFO] = ctx.getDefDataObj()
            self._syncState |= SYNC_KEYS.CLAN_INFO
        else:
            response = yield self._clansCtrl.sendRequest(ctx)
            if response.isSuccess():
                info = ctx.getDataObj(response.data)
                if self._vitalWebInfo[SYNC_KEYS.CLAN_INFO] != info:
                    self._syncState |= SYNC_KEYS.CLAN_INFO
                    self.__changeWebInfo(SYNC_KEYS.CLAN_INFO, info, 'onAccountClanInfoReceived')
            else:
                self._vitalWebInfo[SYNC_KEYS.CLAN_INFO] = ctx.getDefDataObj()
        self._waitForSync ^= SYNC_KEYS.CLAN_INFO

    def resyncInvites(self, force = False):
        if self._waitForSync & SYNC_KEYS.INVITES:
            return
        if self.isSynced(SYNC_KEYS.INVITES) and not force:
            return
        self._waitForSync |= SYNC_KEYS.INVITES
        if self.isInClan():
            self._vitalWebInfo[SYNC_KEYS.INVITES] = 0
            self._syncState |= SYNC_KEYS.INVITES
        else:
            self._syncState |= SYNC_KEYS.INVITES
        self._waitForSync ^= SYNC_KEYS.INVITES

    def resyncApps(self, force = False):
        if self._waitForSync & SYNC_KEYS.APPS:
            return
        if self.isSynced(SYNC_KEYS.APPS) and not force:
            return
        self._waitForSync |= SYNC_KEYS.APPS
        if self.isInClan():
            self._vitalWebInfo[SYNC_KEYS.APPS] = 0
            self._syncState |= SYNC_KEYS.APPS
        else:
            self._syncState |= SYNC_KEYS.APPS
        self._waitForSync ^= SYNC_KEYS.APPS

    def resyncBwInfo(self):
        pass

    def processRequestResponse(self, ctx, response):
        requestType = ctx.getRequestType()
        if response.isSuccess():
            if requestType == CLAN_REQUESTED_DATA_TYPE.CREATE_APPLICATIONS:
                apps = ctx.getDataObj(response.data)
                if apps:
                    appsCount = self._vitalWebInfo[SYNC_KEYS.APPS] or 0
                    appsCount += len(response.data)
                    cached = self._cache[_CACHE_KEYS.APPS] or set()
                    for item in apps:
                        cached.add(item.getClanDbID())

                    self._cache[_CACHE_KEYS.APPS] = cached
                    self.__changeWebInfo(SYNC_KEYS.APPS, appsCount, 'onAccountAppsReceived')
            elif requestType == CLAN_REQUESTED_DATA_TYPE.DECLINE_INVITE:
                self.__changeInvitesState([ctx.getDataObj(response.data)], CLAN_INVITE_STATES.DECLINED)
            elif requestType == CLAN_REQUESTED_DATA_TYPE.DECLINE_INVITES:
                self.__changeInvitesState(ctx.getDataObj(response.data), CLAN_INVITE_STATES.DECLINED)
            elif requestType == CLAN_REQUESTED_DATA_TYPE.ACCEPT_INVITE:
                self.__changeInvitesState([ctx.getDataObj(response.data)], CLAN_INVITE_STATES.ACCEPTED)
            elif requestType == CLAN_REQUESTED_DATA_TYPE.ACCOUNT_INVITES:
                statuses = ctx.getStatuses() or []
                if len(statuses) == 1 and statuses[0] == CLAN_INVITE_STATES.ACTIVE:
                    count = ctx.getTotalCount(response.data)
                    items = ctx.getDataObj(response.data)
                    if count is not None and count <= len(items):
                        cached = set()
                    else:
                        cached = self._cache[_CACHE_KEYS.INVITES] or set()
                    for item in items:
                        cached.add(item.getClanDbID())

                    self._cache[_CACHE_KEYS.INVITES] = cached
                    if count is not None and count != self._vitalWebInfo[SYNC_KEYS.INVITES]:
                        self.__changeWebInfo(SYNC_KEYS.INVITES, count, 'onAccountInvitesReceived')
            elif requestType == CLAN_REQUESTED_DATA_TYPE.GET_ACCOUNT_APPLICATIONS:
                statuses = ctx.getStatuses() or []
                if len(statuses) == 1 and statuses[0] == CLAN_INVITE_STATES.ACTIVE:
                    count = ctx.getTotalCount(response.data)
                    items = ctx.getDataObj(response.data)
                    if count is not None and count <= len(items):
                        cached = set()
                    else:
                        cached = self._cache[_CACHE_KEYS.APPS] or set()
                    for item in items:
                        cached.add(item.getClanDbID())

                    self._cache[_CACHE_KEYS.APPS] = cached
                    count = ctx.getTotalCount(response.data)
                    if count is not None and count != self._vitalWebInfo[SYNC_KEYS.APPS]:
                        self.__changeWebInfo(SYNC_KEYS.APPS, count, 'onAccountAppsReceived')
        elif requestType == CLAN_REQUESTED_DATA_TYPE.CREATE_APPLICATIONS:
            code = response.getCode()
            if code == ResponseCodes.ACCOUNT_ALREADY_APPLIED:
                cached = self._cache[_CACHE_KEYS.APPS] or set()
                for clanDbID in ctx.getClanDbIDs():
                    cached.add(clanDbID)

                self._cache[_CACHE_KEYS.APPS] = cached
            elif code == ResponseCodes.ACCOUNT_ALREADY_INVITED:
                cached = self._cache[_CACHE_KEYS.INVITES] or set()
                for clanDbID in ctx.getClanDbIDs():
                    cached.add(clanDbID)

                self._cache[_CACHE_KEYS.INVITES] = cached
            elif code == ResponseCodes.ACCOUNT_IN_COOLDOWN:
                self.resyncWebClanInfo()
            elif code == ResponseCodes.TOO_MANY_APPLICATIONS:
                self._isInvitesLimitReached.set(True)
        if self.isInClan():
            self.getClanDossier().processRequestResponse(ctx, response)
        return

    def processWgncNotification(self, notifID, item):
        """
        Method handles actions received trough WGNC
        :param notifID:
        :param item: instance of gui.wgnc.proxy_data._ProxyDataItem
        """
        if item.getType() == WGNC_DATA_PROXY_TYPE.CLAN_INVITE:
            invites = self._cache[_CACHE_KEYS.INVITES] or set()
            invites.add(item.getClanId())
            self._cache[_CACHE_KEYS.INVITES] = invites
            count = item.getActiveInvitesCount()
            if count != self._vitalWebInfo[SYNC_KEYS.INVITES]:
                self.__changeWebInfo(SYNC_KEYS.INVITES, count, 'onAccountInvitesReceived')
            self._syncState |= SYNC_KEYS.INVITES
        elif item.getType() == WGNC_DATA_PROXY_TYPE.CLAN_APP_ACCEPTED or item.getType() == WGNC_DATA_PROXY_TYPE.CLAN_APP_DECLINED:
            apps = self._cache[_CACHE_KEYS.APPS] or set()
            apps.discard(item.getClanId())
            self._cache[_CACHE_KEYS.APPS] = apps
            count = self._vitalWebInfo[SYNC_KEYS.APPS]
            if count:
                self.__changeWebInfo(SYNC_KEYS.APPS, count - 1, 'onAccountAppsReceived')
        if self.isInClan():
            self.getClanDossier().processWgncNotification(notifID, item)

    def processClanMembersListChange(self, memberIDs):
        if self.isInClan():
            self.getClanDossier().processClanMembersListChange(memberIDs)

    def updateClanCache(self, cache):
        if self.isInClan():
            cache.set(ClanCache.KEYS.PERSONAL_INVITES, 0)
            cache.set(ClanCache.KEYS.PERSONAL_APPS, 0)
            self.getClanDossier().updateClanCache(cache)
        else:
            invites = self._vitalWebInfo[SYNC_KEYS.INVITES] or 0
            apps = self._vitalWebInfo[SYNC_KEYS.APPS] or 0
            cache.set(ClanCache.KEYS.PERSONAL_INVITES, invites)
            cache.set(ClanCache.KEYS.PERSONAL_APPS, apps)
            cache.set(ClanCache.KEYS.CLAN_APPS, 0)
            cache.set(ClanCache.KEYS.CLAN_INVITES, 0)

    def processClanCache(self, cache):
        if self.isInClan():
            self.getClanDossier().processClanCache(cache)
        else:
            apps = cache.get(ClanCache.KEYS.PERSONAL_APPS) or 0
            if apps:
                count = self._vitalWebInfo[SYNC_KEYS.APPS] or 0
                count += apps
                self.__changeWebInfo(SYNC_KEYS.APPS, count, 'onAccountAppsReceived')
            invites = cache.get(ClanCache.KEYS.PERSONAL_INVITES) or 0
            if invites:
                count = self._vitalWebInfo[SYNC_KEYS.INVITES] or 0
                count += invites
                self.__changeWebInfo(SYNC_KEYS.INVITES, count, 'onAccountInvitesReceived')

    def _getClanInfoValue(self, index, default):
        if self._clanBwInfo is not None:
            return self._clanBwInfo[index]
        else:
            return default
            return

    def _resyncBwInfo(self, clanDbID = 0, clanBwInfo = None):
        needToRaiseEvent = self._clanDbID != clanDbID or self._clanBwInfo != clanBwInfo
        if self._clanDbID != clanDbID:
            self._syncState = 0
            self._vitalWebInfo[SYNC_KEYS.CLAN_INFO] = None
            self._vitalWebInfo[SYNC_KEYS.INVITES] = None
            self._vitalWebInfo[SYNC_KEYS.APPS] = None
        self._clanDbID, self._clanBwInfo = clanDbID, clanBwInfo
        if needToRaiseEvent:
            self._clansCtrl.notify('onAccountClanProfileChanged', self)
        return

    def __changeWebInfo(self, fieldName, value, eventName):
        self._vitalWebInfo[fieldName] = value
        self._clansCtrl.notify(eventName, value)
        self._clansCtrl.notify('onAccountWebVitalInfoChanged', fieldName, value)

    def __changeInvitesState(self, invites, state):
        self._clansCtrl.notify('onClanInvitesStateChanged', [ invite.getDbID() for invite in invites ], state)
        self.__removeInvites(invites)

    def __removeInvites(self, invites):
        if invites:
            invitesCount = self._vitalWebInfo[SYNC_KEYS.INVITES] or 0
            count = max(invitesCount - len(invites), 0)
            removed = set([ invite.getClanDbID() for invite in invites ])
            if self._cache[_CACHE_KEYS.INVITES]:
                self._cache[_CACHE_KEYS.INVITES] = self._cache[_CACHE_KEYS.INVITES].difference(removed)
            if self._cache[_CACHE_KEYS.APPS]:
                self._cache[_CACHE_KEYS.APPS] = self._cache[_CACHE_KEYS.APPS].difference(removed)
            if count != invitesCount:
                self.__changeWebInfo(SYNC_KEYS.INVITES, count, 'onAccountInvitesReceived')

    def __repr__(self):
        args = []
        if self.isInClan():
            args.extend(['dbID = %s' % self._clanDbID, 'abbrev = %s' % self.getClanAbbrev()])
        else:
            args.append('no clan')
        if self._vitalWebInfo[SYNC_KEYS.CLAN_INFO]:
            args.append('cooldown = %s' % self._vitalWebInfo[SYNC_KEYS.CLAN_INFO].getClanCooldownTill())
        if self._vitalWebInfo[SYNC_KEYS.INVITES]:
            args.append('invites = %d' % len(self._vitalWebInfo[SYNC_KEYS.INVITES]))
        if self._vitalWebInfo[SYNC_KEYS.APPS]:
            args.append('apps = %d' % len(self._vitalWebInfo[SYNC_KEYS.APPS]))
        return '%s(%s)' % (self.__class__.__name__, ', '.join(args))


class MyClanAccountProfile(ClanAccountProfile):

    def __init__(self, clansCtrl):
        stats = g_itemsCache.items.stats
        ClanAccountProfile.__init__(self, clansCtrl, getAccountDatabaseID(), stats.clanDBID, stats.clanInfo)

    def resyncBwInfo(self):
        stats = g_itemsCache.items.stats
        self._resyncBwInfo(stats.clanDBID, stats.clanInfo)
