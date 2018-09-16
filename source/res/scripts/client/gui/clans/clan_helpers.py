# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/clans/clan_helpers.py
from collections import namedtuple
from datetime import datetime
import Event
from adisp import async, process
from client_request_lib.exceptions import ResponseCodes
from debug_utils import LOG_DEBUG, LOG_WARNING, LOG_CURRENT_EXCEPTION
from gui import SystemMessages, GUI_SETTINGS
from gui.Scaleform.daapi.view.dialogs import I18nConfirmDialogMeta
from gui.Scaleform.locale.DIALOGS import DIALOGS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.clans import interfaces, items, formatters
from gui.clans.items import ClanInviteWrapper, ClanPersonalInviteWrapper
from gui.clans.settings import CLAN_INVITE_STATES, DATA_UNAVAILABLE_PLACEHOLDER
from gui.clans.settings import COUNT_THRESHOLD, PERSONAL_INVITES_COUNT_THRESHOLD
from gui.shared.formatters import icons, text_styles
from gui.shared.utils import getPlayerDatabaseID, getPlayerName
from gui.shared.utils import sortByFields
from gui.shared.utils.ListPaginator import ListPaginator
from gui.shared.view_helpers import UsersInfoHelper
from gui.wgcg.clan.contexts import ClansInfoCtx, AcceptInviteCtx, DeclineInviteCtx, DeclineInvitesCtx
from gui.wgcg.clan.contexts import SearchClansCtx, GetRecommendedClansCtx, AccountInvitesCtx, ClanRatingsCtx
from helpers import dependency
from helpers import i18n
from helpers import time_utils
from helpers.local_cache import FileLocalCache
from shared_utils import CONST_CONTAINER
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.web import IWebController
_RequestData = namedtuple('_RequestData', ['pattern',
 'offset',
 'count',
 'isReset',
 'isRecommended'])

def showClanInviteSystemMsg(userName, isSuccess, code):
    if isSuccess:
        msg = formatters.getInvitesSentSysMsg((userName,))
        msgType = SystemMessages.SM_TYPE.Information
    else:
        error = None
        if code == ResponseCodes.ACCOUNT_ALREADY_INVITED:
            error = 'clans/request/errors/Account already invited'
        if code == ResponseCodes.ACCOUNT_ALREADY_IN_CLAN:
            error = 'clans/request/errors/user is in clan already'
        msg = formatters.getInviteNotSentSysMsg(userName, error)
        msgType = SystemMessages.SM_TYPE.Error
    SystemMessages.pushMessage(msg, msgType)
    return


@async
def showAcceptClanInviteDialog(clanName, clanAbbrev, callback):
    from gui import DialogsInterface
    DialogsInterface.showDialog(I18nConfirmDialogMeta('clanConfirmJoining', messageCtx={'icon': icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_ATTENTIONICON, 16, 16, -4, 0),
     'clanName': text_styles.stats(i18n.makeString(DIALOGS.CLANCONFIRMJOINING_MESSAGE_CLANNAME, clanAbbr=clanAbbrev, clanName=clanName)),
     'clanExit': text_styles.standard(i18n.makeString(DIALOGS.CLANCONFIRMJOINING_MESSAGE_CLANEXIT))}), callback)


def isInClanEnterCooldown(clanCooldownTill):
    return time_utils.getCurrentTimestamp() - clanCooldownTill <= 0


class ClanListener(interfaces.IClanListener):
    webCtrl = dependency.descriptor(IWebController)
    settingsCore = dependency.descriptor(ISettingsCore)

    def startClanListening(self):
        self.webCtrl.addListener(self)

    def stopClanListening(self):
        self.webCtrl.removeListener(self)


class ClanFinder(ListPaginator, UsersInfoHelper):

    def __init__(self, requester, offset=0, count=18):
        super(ClanFinder, self).__init__(requester, offset, count)
        self.__pattern = str()
        self.__lastResult = []
        self.__listMapping = {}
        self.__lastStatus = True
        self.__totalCount = None
        self.__isRecommended = False
        self.__lastSuccessRequestData = None
        self.__isSynced = False
        self.__hasNextPage = False
        return

    def isSynced(self):
        return self.__isSynced

    def setPattern(self, pattern):
        self.__pattern = pattern

    def getPattern(self):
        return self.__pattern

    def getTotalCount(self):
        return self.__totalCount

    def getLastStatus(self):
        return self.__lastStatus

    def getLastResult(self):
        return self.__lastResult

    def isRecommended(self):
        return self.__isRecommended

    def setRecommended(self, isRecommended):
        self.__isRecommended = isRecommended

    def getItemByID(self, clanDbID):
        return self.__lastResult[self.__listMapping[clanDbID]] if clanDbID in self.__listMapping else None

    def canMoveLeft(self):
        return self.__lastStatus and self._offset > 0

    def canMoveRight(self):
        return self.__lastStatus and self.__hasNextPage

    def hasSuccessRequest(self):
        return self.__lastSuccessRequestData is not None

    def requestLastSuccess(self):
        if self.hasSuccessRequest():
            self.__isRecommended = self.__lastSuccessRequestData.isRecommended
            self.__pattern = self.__lastSuccessRequestData.pattern
            self._count = self.__lastSuccessRequestData.count
            self._offset = self.__lastSuccessRequestData.offset
            self._request(self.__lastSuccessRequestData.isReset)
        else:
            LOG_DEBUG('Has not been success result yet. Operation is unavailable.')

    @process
    def _request(self, isReset=False):
        self._offset = max(self._offset, 0)
        count = self._count + 1
        if self.__isRecommended:
            ctx = GetRecommendedClansCtx(self._offset, count, True)
        else:
            ctx = SearchClansCtx(self.__pattern, self._offset, count, True)
        result = yield self._requester.sendRequest(ctx, allowDelay=True)
        self.__lastResult = ctx.getDataObj(result.data)
        if self.__lastResult and len(self.__lastResult) == count:
            self.__hasNextPage = True
            self.__lastResult.pop()
        else:
            self.__hasNextPage = False
        self.__lastStatus = result.isSuccess()
        self.__totalCount = ctx.getTotalCount(result.data)
        self._invalidateMapping()
        for item in self.__lastResult:
            self.getUserName(item.getLeaderDbID())

        if result.isSuccess():
            self.__isSynced = True
            if not result.data:
                if not isReset:
                    self.revertOffset()
            elif self.isRecommended():
                self.__lastSuccessRequestData = _RequestData(self.__pattern, self._offset, self._count, isReset, self.__isRecommended)
        else:
            self.revertOffset()
        self.syncUsersInfo()
        self.onListUpdated(self._selectedID, True, True, (self.__lastStatus, self.__lastResult))

    def _invalidateMapping(self):
        self.__listMapping = {}
        if self.__lastResult is not None:
            for index, item in enumerate(self.__lastResult):
                self.__listMapping[item.getClanDbID()] = index

        return


class ClanInvitesPaginator(ListPaginator, UsersInfoHelper):

    def __init__(self, requester, contextClass, clanDbID, statuses=None, offset=0, count=50):
        super(ClanInvitesPaginator, self).__init__(requester, offset, count)
        statuses = statuses or []
        self.__ctxClass = contextClass
        self.__clanDbID = clanDbID
        self.__statuses = statuses
        self.__invitesCache = []
        self.__cacheMapping = {}
        self.__accountNameMapping = {}
        self.__senderNameMapping = {}
        self.__changerNameMapping = {}
        self.__lastStatus = True
        self.__lastResult = []
        self.__totalCount = None
        self.__allInvitesCached = False
        self.__lastSort = tuple()
        self.__isSynced = False
        self.__sentRequestCount = 0
        self.onListItemsUpdated = Event.Event(self._eManager)
        return

    def setStatuses(self, statuses):
        self.__statuses = statuses

    def getStatuses(self):
        return self.__statuses

    def getTotalCount(self):
        return self.__totalCount

    def canMoveLeft(self):
        return self.__lastStatus and self._offset > 0

    def canMoveRight(self):
        return self.__lastStatus and self.__totalCount > self._offset + self._count

    def isInProgress(self):
        return self.__sentRequestCount > 0

    def isSynced(self):
        return self.__isSynced

    def markAsUnSynced(self):
        self.__isSynced = False

    def getLastStatus(self):
        return self.__lastStatus

    def getLastResult(self):
        return self.__lastResult

    def getLastSort(self):
        return self.__lastSort

    def sort(self, sort):
        self._selectedID = None
        self._offset = self.getInitialOffset()
        self._prevOffset = self._offset
        self._request(isReset=True, sort=sort)
        return

    def refresh(self, *args, **kwargs):
        sort = kwargs.get('sort') or self.__lastSort
        self.__invitesCache = []
        self.__lastStatus = False
        self.__allInvitesCached = False
        self.__lastSort = tuple()
        self._selectedID = None
        self._offset = self.getInitialOffset()
        self._prevOffset = self._offset
        self._request(isReset=True, sort=sort)
        return

    def accept(self, inviteDbId, context):
        invite = self.getInviteByDbID(inviteDbId)
        if invite is not None:
            self.__sendRequest(invite, context, CLAN_INVITE_STATES.ACCEPTED)
        return

    def decline(self, inviteDbId, context):
        invite = self.getInviteByDbID(inviteDbId)
        if invite is not None:
            self.__sendRequest(invite, context, CLAN_INVITE_STATES.DECLINED)
        return

    def resend(self, inviteDbId, context):
        invite = self.getInviteByDbID(inviteDbId)
        if invite is not None:
            if invite.getStatus() == CLAN_INVITE_STATES.EXPIRED:
                self.__sendRequest(invite, context, CLAN_INVITE_STATES.EXPIRED_RESENT)
            elif invite.getStatus() == CLAN_INVITE_STATES.DECLINED:
                self.__sendRequest(invite, context, CLAN_INVITE_STATES.DECLINED_RESENT)
        return

    def getInviteByDbID(self, inviteDbID):
        index = self.__cacheMapping.get(inviteDbID, -1)
        return self.__invitesCache[index] if 0 <= index < len(self.__invitesCache) else None

    def onUserNamesReceived(self, names):
        updatedInvites = set()
        for userID, name in names.iteritems():
            for inviteID in self.__accountNameMapping.get(userID, tuple()):
                invite = self.getInviteByDbID(inviteID)
                if invite is not None:
                    invite.setUserName(name)
                    updatedInvites.add(inviteID)

            for inviteID in self.__senderNameMapping.get(userID, tuple()):
                invite = self.getInviteByDbID(inviteID)
                if invite is not None:
                    invite.setSenderName(name)
                    updatedInvites.add(inviteID)

            for inviteID in self.__changerNameMapping.get(userID, tuple()):
                invite = self.getInviteByDbID(inviteID)
                if invite is not None:
                    invite.setChangerName(name)
                    updatedInvites.add(inviteID)

        if updatedInvites:
            self.onListItemsUpdated(self, [ self.__invitesCache[self.__cacheMapping[invID]] for invID in updatedInvites ])
        return

    @process
    def _request(self, isReset=False, sort=tuple()):
        self.__sentRequestCount += 1
        self._offset = max(self._offset, 0)
        offset = 0
        count = self._offset + self._count
        if not self.__lastStatus or not self.__allInvitesCached:
            if sort:
                yield self.__requestInvites(0, COUNT_THRESHOLD, isReset)
                self.__allInvitesCached = self.__lastStatus
            else:
                yield self.__requestInvites(offset, count, isReset)
        self.__lastResult = []
        if self.__lastStatus:
            if sort is not None and sort != self.__lastSort:
                self.__invitesCache = sortByFields(sort, self.__invitesCache, valueGetter=getattr)
                self.__lastSort = sort
                self.__rebuildMapping()
            self.__lastResult = self.__getSlice(offset, count)
        self.__sentRequestCount -= 1
        self.onListUpdated(self._selectedID, True, True, (self.__lastStatus, self.__lastResult))
        return

    def __getSlice(self, offset, count):
        result = list()
        total = len(self.__invitesCache)
        if total > offset + count:
            result = self.__invitesCache[offset:count]
        elif total > offset:
            result = self.__invitesCache[offset:]
        return result

    def getUserName(self, userDbID):
        return super(ClanInvitesPaginator, self).getUserName(userDbID) if userDbID else None

    @async
    @process
    def __requestInvites(self, offset, count, isReset, callback):
        ctx = self.__ctxClass(clanDbID=self.__clanDbID, offset=offset, limit=count, statuses=self.__statuses, getTotalCount=isReset)
        result = yield self._requester.sendRequest(ctx, allowDelay=True)
        invites = ctx.getDataObj(result.data)
        self.__lastStatus = result.isSuccess()
        if isReset:
            self.__totalCount = ctx.getTotalCount(result.data)
        if result.isSuccess():
            if not invites and not isReset:
                self.revertOffset()
            usrIDs = set()
            for item in invites:
                usrIDs.add(item.getAccountDbID())
                temp = self.__accountNameMapping.get(item.getAccountDbID(), set())
                temp.add(item.getDbID())
                self.__accountNameMapping[item.getAccountDbID()] = temp
                usrIDs.add(item.getChangedBy())
                temp = self.__changerNameMapping.get(item.getChangedBy(), set())
                temp.add(item.getDbID())
                self.__changerNameMapping[item.getChangedBy()] = temp
                usrIDs.add(item.getSenderDbID())
                temp = self.__senderNameMapping.get(item.getSenderDbID(), set())
                temp.add(item.getDbID())
                self.__senderNameMapping[item.getSenderDbID()] = temp

            self.__lastStatus, users = yield self._requester.requestUsers(usrIDs)
            if self.__lastStatus:
                self.__invitesCache = [ ClanInviteWrapper(invite, users.get(invite.getAccountDbID(), items.AccountClanRatingsData(invite.getAccountDbID())), self.getUserName(invite.getAccountDbID()), users.get(invite.getChangedBy(), items.AccountClanRatingsData(invite.getChangedBy())), senderName=self.getUserName(invite.getSenderDbID()), changerName=self.getUserName(invite.getChangedBy())) for invite in invites ]
            else:
                self.__invitesCache = []
                self.revertOffset()
        else:
            self.__invitesCache = []
            self.revertOffset()
        self.__rebuildMapping()
        self.syncUsersInfo()
        self.__isSynced = self.__lastStatus
        callback((self.__lastStatus, self.__invitesCache))

    def __rebuildMapping(self):
        self.__cacheMapping = dict(((invite.getDbID(), index) for index, invite in enumerate(self.__invitesCache)))

    @process
    def __sendRequest(self, invite, context, successStatus):
        self.__sentRequestCount += 1
        userDbID = getPlayerDatabaseID()
        temp = self.__accountNameMapping.get(userDbID, set())
        temp.add(invite.getDbID())
        self.__accountNameMapping[userDbID] = temp
        result = yield self._requester.sendRequest(context, allowDelay=True)
        if result.isSuccess():
            status = (successStatus, None)
        else:
            status = (CLAN_INVITE_STATES.ERROR, result.getCode())
        result, users = yield self._requester.requestUsers([userDbID])
        sender = users.get(userDbID, items.AccountClanRatingsData(userDbID))
        senderName = self.getUserName(userDbID)
        changerName = getPlayerName()
        item = self.__updateInvite(invite, status, sender, senderName, changerName)
        self.syncUsersInfo()
        self.__sentRequestCount -= 1
        self.onListItemsUpdated(self, [item])
        return

    def __updateInvite(self, inviteWrapper, statusData, sender, senderName, changerName):
        status, code = statusData
        utc = datetime.utcnow()
        invite = inviteWrapper.invite.update(status=status, status_changer_id=sender.getAccountDbID(), updated_at=utc)
        inviteWrapper.setInvite(invite)
        inviteWrapper.setSender(sender)
        inviteWrapper.setSenderName(senderName)
        inviteWrapper.setChangerName(changerName)
        inviteWrapper.setStatusCode(code)
        return inviteWrapper

    def __checkUserName(self, name):
        return DATA_UNAVAILABLE_PLACEHOLDER if not name else name


class ClanPersonalInvitesPaginator(ListPaginator, UsersInfoHelper):

    def __init__(self, requester, accountDbID, statuses=None, offset=0, count=50):
        super(ClanPersonalInvitesPaginator, self).__init__(requester, offset, count)
        self.__accountDbID = accountDbID
        self.__statuses = statuses or []
        self.__invitesCache = []
        self.__cacheMapping = {}
        self.__lastStatus = True
        self.__lastResult = []
        self.__totalCount = None
        self.__allInvitesCached = False
        self.__lastSort = tuple()
        self.__isSynced = False
        self.__sentRequestCount = 0
        self.__senderNameMapping = {}
        self.onListItemsUpdated = Event.Event(self._eManager)
        return

    def setStatuses(self, statuses):
        self.__statuses = statuses

    def getStatuses(self):
        return self.__statuses

    def getTotalCount(self):
        return self.__totalCount

    def canMoveLeft(self):
        return self.__lastStatus and self._offset > 0

    def canMoveRight(self):
        return self.__lastStatus and self.__totalCount > self._offset + self._count

    def isInProgress(self):
        return self.__sentRequestCount > 0

    def isSynced(self):
        return self.__isSynced

    def markAsUnSynced(self):
        self.__isSynced = False

    def getLastStatus(self):
        return self.__lastStatus

    def getLastResult(self):
        return self.__lastResult

    def getLastSort(self):
        return self.__lastSort

    def sort(self, sort):
        self._selectedID = None
        self._offset = self.getInitialOffset()
        self._prevOffset = self._offset
        self._request(isReset=True, sort=sort)
        return

    def refresh(self, *args, **kwargs):
        sort = kwargs.get('sort') or self.__lastSort
        self.__invitesCache = []
        self.__lastStatus = False
        self.__allInvitesCached = False
        self.__lastSort = tuple()
        self._selectedID = None
        self._offset = self.getInitialOffset()
        self._prevOffset = self._offset
        self._request(isReset=True, sort=sort)
        return

    @process
    def accept(self, inviteID):
        inviteWrapper = self.getInviteByDbID(inviteID)
        if inviteWrapper:
            clanInfo = inviteWrapper.clanInfo
            clanName = clanInfo.getClanName()
            clanTag = clanInfo.getTag()
            result = yield showAcceptClanInviteDialog(clanName, clanTag)
            if result:
                self.__sendADRequest(AcceptInviteCtx(inviteID), CLAN_INVITE_STATES.ACCEPTED, lambda result: None)
        else:
            LOG_WARNING("Couldn't find invite by id = " + str(inviteID))

    def decline(self, inviteID):
        self.__sendADRequest(DeclineInviteCtx(inviteID), CLAN_INVITE_STATES.DECLINED)

    def declineList(self, inviteIDs):
        self.__sendADListRequest(DeclineInvitesCtx(inviteIDs), CLAN_INVITE_STATES.DECLINED)

    def getInviteByDbID(self, inviteDbID):
        index = self.__cacheMapping.get(inviteDbID, -1)
        return self.__invitesCache[index] if 0 <= index < len(self.__invitesCache) else None

    def onUserNamesReceived(self, names):
        updatedInvites = set()
        for userID, name in names.iteritems():
            for inviteID in self.__senderNameMapping.get(userID, tuple()):
                invite = self.getInviteByDbID(inviteID)
                if invite is not None:
                    invite.setSenderName(name)
                    updatedInvites.add(inviteID)

        if updatedInvites:
            self.onListItemsUpdated(self, [ self.__invitesCache[self.__cacheMapping[invID]] for invID in updatedInvites ])
        return

    @process
    def _request(self, isReset=False, sort=tuple()):
        self.__sentRequestCount += 1
        self._offset = max(self._offset, 0)
        offset = 0
        count = self._offset + self._count
        if not self.__lastStatus or not self.__allInvitesCached:
            if sort:
                yield self.__requestInvites(0, PERSONAL_INVITES_COUNT_THRESHOLD, isReset)
                self.__allInvitesCached = self.__lastStatus
            else:
                yield self.__requestInvites(offset, count, isReset)
        self.__lastResult = []
        if self.__lastStatus:
            if sort is not None and sort != self.__lastSort:
                self.__invitesCache = sortByFields(sort, self.__invitesCache, valueGetter=getattr)
                self.__lastSort = sort
                self.__rebuildMapping()
            self.__lastResult = self.__getSlice(offset, count)
        self.__sentRequestCount -= 1
        self.onListUpdated(self._selectedID, True, True, (self.__lastStatus, self.__lastResult))
        return

    def __getSlice(self, offset, count):
        result = list()
        total = len(self.__invitesCache)
        if total > offset + count:
            result = self.__invitesCache[offset:count]
        elif total > offset:
            result = self.__invitesCache[offset:]
        return result

    @async
    @process
    def __requestInvites(self, offset, count, isReset, callback):
        ctx = AccountInvitesCtx(accountDbID=self.__accountDbID, offset=offset, limit=count, statuses=self.__statuses, getTotalCount=isReset)
        result = yield self._requester.sendRequest(ctx, allowDelay=True)
        invites = ctx.getDataObj(result.data)
        success = result.isSuccess()
        self.__lastStatus = result.isSuccess()
        if isReset:
            self.__totalCount = ctx.getTotalCount(result.data)
        if result.isSuccess():
            if not invites and not isReset:
                self.revertOffset()
            if invites:
                clansIDs = [ item.getClanDbID() for item in invites ]
                ctx = ClanRatingsCtx(clansIDs)
                result = yield self._requester.sendRequest(ctx, allowDelay=True)
                if result.isSuccess():
                    clanRatings = dict(((item.getClanDbID(), item) for item in ctx.getDataObj(result.data)))
                else:
                    clanRatings = {}
                    success = False
                ctx = ClansInfoCtx(clansIDs)
                result = yield self._requester.sendRequest(ctx, allowDelay=True)
                if result.isSuccess():
                    clanInfo = dict(((item.getDbID(), item) for item in ctx.getDataObj(result.data)))
                else:
                    clanInfo = {}
                    success = False
                for item in clanInfo.itervalues():
                    self.getUserName(item.getLeaderDbID())

                def getSenderID(inviteItem):
                    changerDbID = inviteItem.getChangerDbID()
                    return inviteItem.getSenderDbID() if changerDbID == 0 else changerDbID

                for item in invites:
                    senderID = getSenderID(item)
                    temp = self.__senderNameMapping.get(senderID, set())
                    temp.add(item.getDbID())
                    self.__senderNameMapping[senderID] = temp

                if success:
                    self.__invitesCache = [ ClanPersonalInviteWrapper(invite, clanInfo.get(invite.getClanDbID(), items.ClanExtInfoData()), clanRatings.get(invite.getClanDbID(), items.ClanRatingsData()), self.getUserName(getSenderID(invite))) for invite in invites ]
                else:
                    self.__invitesCache = []
                    self.__lastStatus = False
                    self.revertOffset()
            else:
                self.__invitesCache = []
        else:
            self.__invitesCache = []
            self.revertOffset()
        self.__rebuildMapping()
        self.syncUsersInfo()
        self.__isSynced = self.__lastStatus
        callback((self.__lastStatus, self.__invitesCache))

    def __rebuildMapping(self):
        self.__cacheMapping = dict(((invite.getDbID(), index) for index, invite in enumerate(self.__invitesCache)))

    @process
    def __sendADRequest(self, context, sucessStatus, callback=None):
        self.__sentRequestCount += 1
        result = yield self._requester.sendRequest(context, allowDelay=True)
        inviteDbID = context.getInviteDbID()
        if result.isSuccess():
            status = sucessStatus
        else:
            status = CLAN_INVITE_STATES.ERROR
        self.__sentRequestCount -= 1
        self.__updateInvitesStatus([inviteDbID], status)
        if callback:
            callback(result)

    @process
    def __sendADListRequest(self, context, sucessStatus):
        self.__sentRequestCount += 1
        result = yield self._requester.sendRequest(context, allowDelay=True)
        sentInvites = [ item.getDbID() for item in context.getDataObj(result.data) ]
        failedInvites = set(context.getInviteDbIDs()) - set(sentInvites)
        self.__sentRequestCount -= 1
        self.__updateInvitesStatus(sentInvites, sucessStatus)
        self.__updateInvitesStatus(failedInvites, CLAN_INVITE_STATES.ERROR)

    def __updateInvitesStatus(self, inviteIDs, status):
        updatedInvites = list()
        for invID in inviteIDs:
            inviteWrapper = self.getInviteByDbID(invID)
            if inviteWrapper:
                invite = inviteWrapper.invite.update(status=status)
                inviteWrapper.setInvite(invite)
                updatedInvites.append(inviteWrapper)
            LOG_WARNING('Could not find invite with DB ID {} in the internal cache."'.format(invID))

        if updatedInvites:
            self.onListItemsUpdated(self, updatedInvites)


class ClanCache(FileLocalCache):

    class KEYS(CONST_CONTAINER):
        VERSION = ('VERSION',)
        CLAN_APPS = ('CLAN_APPS_COUNT',)
        CLAN_INVITES = ('CLAN_INVITES_COUNT',)
        PERSONAL_APPS = ('PERSONAL_APPS_COUNT',)
        PERSONAL_INVITES = ('PERSONAL_INVITES_COUNT',)

    def __init__(self, accountName):
        super(ClanCache, self).__init__('clan_cache', ('invites', accountName))
        self.__currentVersion = 1
        self.__cache = {}

    def __repr__(self):
        return 'ClanCache({0:s}): {1!r:s}'.format(hex(id(self)), self.__cache)

    def get(self, key):
        return self.__cache.get(key, None)

    def set(self, key, value):
        self.__cache[key] = value

    def write(self):
        self.__cache[ClanCache.KEYS.VERSION] = self.__currentVersion
        super(ClanCache, self).write()

    def clear(self):
        self.__cache.clear()
        super(ClanCache, self).clear()

    def _getCache(self):
        return self.__cache.copy()

    def _setCache(self, data):
        data = data or {}
        if ClanCache.KEYS.VERSION in data and data[ClanCache.KEYS.VERSION] == self.__currentVersion:
            self.__cache = data
        else:
            self.__cache = {}


class CachedValue(object):

    def __init__(self, lifeTime):
        super(CachedValue, self).__init__()
        self.__lifeTime = lifeTime
        self.__value = None
        self.__validTill = None
        return

    def set(self, value):
        self.__validTill = self._now() + self.__lifeTime
        self.__value = value

    def get(self, defValue=None):
        if self.isExpired():
            self.sync()
            return defValue
        return self.__value

    def getCachedValue(self):
        return self.__value

    def isExpired(self):
        return self.__validTill < self._now()

    def sync(self):
        pass

    def _now(self):
        return time_utils.getTimestampFromUTC(datetime.utcnow().timetuple())


@dependency.replace_none_kwargs(lobbyContext=ILobbyContext)
def isStrongholdsEnabled(lobbyContext=None):
    if lobbyContext is None:
        return False
    else:
        try:
            settings = lobbyContext.getServerSettings()
            return settings.isStrongholdsEnabled()
        except Exception:
            return False

        return


def getStrongholdUrl(urlName):
    try:
        return _getWgshHost() + GUI_SETTINGS.stronghold.get(urlName)
    except (AttributeError, TypeError):
        LOG_CURRENT_EXCEPTION()
        return None

    return None


def getStrongholdClanCardUrl(clanDBID):
    return getStrongholdUrl('clanCardUrl') + str(clanDBID)


@dependency.replace_none_kwargs(lobbyContext=ILobbyContext)
def _getWgshHost(lobbyContext=None):
    if lobbyContext is None:
        return
    else:
        try:
            return lobbyContext.getServerSettings().stronghold.wgshHostUrl
        except AttributeError:
            LOG_CURRENT_EXCEPTION()
            return

        return
