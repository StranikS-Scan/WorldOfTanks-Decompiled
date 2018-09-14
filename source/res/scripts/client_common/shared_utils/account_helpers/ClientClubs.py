# Python 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client_common/shared_utils/account_helpers/ClientClubs.py
from collections import namedtuple
import time
import BigWorld
import AccountCommands
from functools import partial
from club_shared import CLIENT_CLUB_COMMANDS, CLUB_SUBSCRIPTION_TYPE, ACCOUNT_NOTIFICATION_TYPE, WEB_CMD_RESULT
import cPickle
from Event import Event, EventManager
from debug_utils import LOG_DAN, LOG_CURRENT_EXCEPTION, LOG_DEBUG, LOG_SVAN_DEV
from ClubDescr import ClubDescr
from pprint import pformat
CLIENT_CLUB_COMMANDS_NAMES = {v:k for k, v in CLIENT_CLUB_COMMANDS.__dict__.iteritems() if isinstance(v, int)}

def _logClubResponse(*args):
    LOG_SVAN_DEV('\n\n[SERVER CMD RESPONSE]\n{}\n', args)


OK = 0
ClubContender = namedtuple('ClubContender', ('clubDBID', 'clubName', 'clubEmblem', 'ladderPoints', 'ladderRank', 'battlesCount', 'winsCount'))
InviteNotice = namedtuple('InviteNotice', ('actionType', 'clubDBID', 'accountDBID', 'inviterDBID', 'revision'))
ApplicationNotice = namedtuple('ApplicationNotice', ('actionType', 'clubDBID', 'accountDBID', 'revision'))
ClubNotice = namedtuple('ClubNotice', ('actionType', 'clubDBID', 'accountDBID', 'revision', 'accountIDs'))

class ClientClubs(object):

    def __init__(self, syncData):
        self.__account = None
        self.__syncData = syncData
        self.__eventsMgr = EventManager()
        self.onClientClubsChanged = Event(self.__eventsMgr)
        self.onClientClubsNotification = Event(self.__eventsMgr)
        self.onClientClubsUnitInfoChanged = Event(self.__eventsMgr)
        self.__cache = {}
        self.__subscriptions = {}
        return

    def __repr__(self):
        return str(pformat(self.__cache, indent=5, width=80, depth=3))

    def _unpack(self, serializedData):
        try:
            unpacked = cPickle.loads(serializedData)
        except:
            LOG_CURRENT_EXCEPTION()
            unpacked = {}

        return unpacked

    def onAccountBecomePlayer(self):
        self.__ignore = False

    def onAccountBecomeNonPlayer(self):
        self.__subscriptions.clear()
        self.__ignore = True

    def setAccount(self, account):
        self.__account = account

    def onUnitMgrCreated(self, unitMgr):
        unitMgr.onUnitResponseReceived += self.__onUnitResponseReceived
        unitMgr.onUnitErrorReceived += self.__onUnitErrorReceived

    def synchronize(self, isFullSync, diff):
        cacheDiff = diff.get('cache', None)
        if cacheDiff is not None:
            for key in ('relatedToClubs', 'eSportSeasonInProgress', 'eSportSeasonState', 'eSportSeasons', 'isEstbOnline'):
                if key in cacheDiff:
                    self.__cache[key] = cacheDiff[key]

        return

    def isRelatedToClubs(self):
        return self.__cache.get('relatedToClubs')

    def getESportSeasons(self):
        return self.__cache.get('eSportSeasons', {})

    def getESportSeasonState(self):
        return self.__cache.get('eSportSeasonState')

    def isSeasonInProgress(self):
        return self.__cache.get('eSportSeasonInProgress')

    def getCache(self, callback = None):
        if self.__ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER, None)
            return
        else:
            self.__syncData.waitForSync(partial(self.__onGetCacheResponse, callback))
            return

    def getClubUnit(self, clubDBID):
        unitCache = self.__cache.setdefault('units', {})
        if clubDBID in unitCache:
            return unitCache[clubDBID]
        else:
            return None

    def onCooldown(self, requestID, cmdID, cooldown):
        LOG_SVAN_DEV('requestID={} cmd={} cooldown={}', requestID, cmdID, int(cooldown) - int(time.time()))

    def onClubNotification(self, pickledNotification):
        item = cPickle.loads(pickledNotification)
        LOG_DEBUG('ClientClubs::onClubNotification', item)
        notificationType = item[0]
        if notificationType in ACCOUNT_NOTIFICATION_TYPE.REQUIRES_PROFILE_UPDATE:
            if notificationType in ACCOUNT_NOTIFICATION_TYPE.INVITE:
                notice = InviteNotice(*item)
            elif notificationType in ACCOUNT_NOTIFICATION_TYPE.APPLICATION:
                notice = ApplicationNotice(*item)
            elif notificationType in ACCOUNT_NOTIFICATION_TYPE.CLUB:
                notice = ClubNotice(*item)
            else:
                notice = item
            self.onClientClubsNotification(notificationType, notice)
        else:
            LOG_SVAN_DEV('\n unknown notification => \n {} \n', item)

    def onClubResponse(self, requestID, responseCode, responseError, extra = None, cmd = 0, arg2 = 0, arg3 = 0, callback = None):
        if responseCode == OK and extra:
            if cmd == CLIENT_CLUB_COMMANDS.GET_ACCOUNT_PROFILE:
                self.__cache['restrictions'] = extra.get('restrictions', tuple())
                self.__cache['myClubs'] = extra.get('clubs', tuple())
                self.__cache['invites'] = extra.get('invites', tuple())
                self.__cache['applications'] = extra.get('applications', tuple())
            elif cmd == CLIENT_CLUB_COMMANDS.GET_MY_CLUBS:
                self.__cache['myClubs'] = extra
            elif cmd == CLIENT_CLUB_COMMANDS.GET_MY_CLUBS_HISTORY:
                self.__cache['myClubsHistory'] = extra
            elif cmd == CLIENT_CLUB_COMMANDS.GET_APPLICATIONS:
                self.__cache['applications'] = extra
            elif cmd == CLIENT_CLUB_COMMANDS.GET_CLUB_APPLICANTS:
                self.__cache['clubApplicants'] = extra
            elif cmd == CLIENT_CLUB_COMMANDS.GET_ACCOUNT_INVITES:
                self.__cache['invites'] = extra
            elif cmd == CLIENT_CLUB_COMMANDS.GET:
                pass
            elif cmd == CLIENT_CLUB_COMMANDS.SEND_INVITES:
                pass
            elif cmd == CLIENT_CLUB_COMMANDS.GET_CLUBS_CONTENDERS:
                conteders = [ ClubContender(*club) for club in extra ]
                LOG_SVAN_DEV('Clubs from ladder : {}', conteders)
        if callback:
            callback(responseCode, responseError, extra)

    def onClubUpdated(self, clubDBID, clubData, unitData):
        updater = self.__subscriptions.get(clubDBID, None)
        club = ClubDescr(clubDBID, clubData)
        unit = cPickle.loads(unitData)
        clubsCache = self.__cache.setdefault('clubs', {})
        unitsCache = self.__cache.setdefault('units', {})
        clubsCache[clubDBID] = club
        if unitsCache.get(clubDBID, None) != unit:
            unitsCache[clubDBID] = unit
            self.onClientClubsUnitInfoChanged(clubDBID, unit)
        if updater is True or updater is None:
            return
        else:
            updater(clubDBID, clubData)
            return

    def _doClubCmd(self, cmd, arg2, arg3, callback):
        LOG_DAN('_doClubCmd', cmd, arg2, arg3)
        clubCallback = partial(self.onClubResponse, cmd=cmd, arg2=arg2, arg3=arg3, callback=callback)
        self.__account._doCmdInt3(AccountCommands.CMD_DO_CLUB_CMD, cmd, arg2, arg3, clubCallback)

    def doCustomClubCmd(self, cmd, arg2, arg3, callback = _logClubResponse):
        self._doClubCmd(cmd, arg2, arg3, callback)

    def getAccountProfile(self, callback = _logClubResponse):
        self._doClubCmd(CLIENT_CLUB_COMMANDS.GET_ACCOUNT_PROFILE, 0, 0, callback)

    def createClub(self, callback = _logClubResponse):
        self._doClubCmd(CLIENT_CLUB_COMMANDS.CREATE, 0, 0, partial(self.__onResponse_syncState, callback))

    def getMyClubs(self, callback = _logClubResponse):
        self._doClubCmd(CLIENT_CLUB_COMMANDS.GET_MY_CLUBS, 0, 0, callback)

    def getPlayerClubs(self, accountDBID, callback = _logClubResponse):
        self._doClubCmd(CLIENT_CLUB_COMMANDS.GET_PLAYER_CLUBS, accountDBID, 0, callback)

    def getMyClubsHistory(self, callback = _logClubResponse):
        self._doClubCmd(CLIENT_CLUB_COMMANDS.GET_MY_CLUBS_HISTORY, 0, 0, callback)

    def getClubsContenders(self, clubDBID, callback = _logClubResponse):
        self._doClubCmd(CLIENT_CLUB_COMMANDS.GET_CLUBS_CONTENDERS, clubDBID, 0, callback)

    def disbandClub(self, clubDBID, callback = _logClubResponse):
        self._doClubCmd(CLIENT_CLUB_COMMANDS.DISBAND, clubDBID, 0, partial(self.__onClubResponse_syncState, callback, clubDBID))

    def leaveClub(self, clubDBID, callback = _logClubResponse):
        self._doClubCmd(CLIENT_CLUB_COMMANDS.LEAVE, clubDBID, 0, partial(self.__onClubResponse_syncState, callback, clubDBID))

    def getClubData(self, clubDBID, callback = _logClubResponse):
        self._doClubCmd(CLIENT_CLUB_COMMANDS.GET, clubDBID, 0, callback)

    def openClub(self, clubDBID, callback = _logClubResponse):
        self._doClubCmd(CLIENT_CLUB_COMMANDS.OPEN_CLUB, clubDBID, 0, partial(self.__onClubResponse_noSyncState, callback, clubDBID))

    def closeClub(self, clubDBID, callback = _logClubResponse):
        self._doClubCmd(CLIENT_CLUB_COMMANDS.CLOSE_CLUB, clubDBID, 0, partial(self.__onClubResponse_noSyncState, callback, clubDBID))

    def getClubs(self, start, count, callback = _logClubResponse):
        self._doClubCmd(CLIENT_CLUB_COMMANDS.GET_CLUBS, start, count, callback)

    def getOpenClubs(self, offset, count, callback = _logClubResponse):
        self._doClubCmd(CLIENT_CLUB_COMMANDS.GET_OPEN_CLUBS, offset, count, callback)

    def findOpenClubs(self, pattern, offset, count, callback = _logClubResponse):
        int64Params = (CLIENT_CLUB_COMMANDS.FIND_OPEN_CLUBS, offset, count)
        strParams = (str(pattern),)
        proxy = lambda rqID, code, err, data: self.__onResponse_noSyncState(callback, code, err, data)
        self.__account._doCmdIntArrStrArr(AccountCommands.CMD_DO_CLUB_CMD, int64Params, strParams, proxy)

    def subscribe(self, clubDBID, subscriptionType = 0, callback = _logClubResponse, updater = True):
        shouldSubscribe = subscriptionType != CLUB_SUBSCRIPTION_TYPE.NONE
        if shouldSubscribe:
            self.__subscriptions[clubDBID] = updater
        else:
            self.__subscriptions.pop(clubDBID, None)
        self._doClubCmd(CLIENT_CLUB_COMMANDS.SUBSCRIBE, clubDBID, subscriptionType, callback)
        return

    def unsubscribe(self, clubDBID, callback = _logClubResponse):
        self.__subscriptions.pop(clubDBID, None)
        cacheClubs = self.__cache.get('clubs', {})
        cacheClubs.pop(clubDBID, None)
        BigWorld.callback(0.0, lambda : callback(AccountCommands.RES_SUCCESS, '', None))
        return

    def sendInvite(self, clubDBID, accountDBID, callback = _logClubResponse):
        self._doClubCmd(CLIENT_CLUB_COMMANDS.SEND_INVITE, clubDBID, accountDBID, partial(self.__onClubResponse_noSyncState, callback, clubDBID))

    def sendInvites(self, clubDBID, accountDBIDs, callback = _logClubResponse):
        clubCallback = partial(self.__onSendInvitesResponse, clubDBID, accountDBIDs, callback)
        int64Params = [CLIENT_CLUB_COMMANDS.SEND_INVITES, clubDBID]
        int64Params.extend(accountDBIDs)
        self.__account._doCmdIntArrStrArr(AccountCommands.CMD_DO_CLUB_CMD, int64Params, [], clubCallback)

    def revokeInvite(self, clubDBID, accountDBID, callback = _logClubResponse):
        self._doClubCmd(CLIENT_CLUB_COMMANDS.REVOKE_INVITE, clubDBID, accountDBID, partial(self.__onClubResponse_noSyncState, callback, clubDBID))

    def sendApplication(self, clubDBID, comment, callback = _logClubResponse):
        proxy = lambda rqID, code, err, data: self.__onClubResponse_noSyncState(callback, clubDBID, code, err, data)
        self.__account._doCmdInt2Str(AccountCommands.CMD_DO_CLUB_CMD, CLIENT_CLUB_COMMANDS.SEND_APPLICATION, clubDBID, comment, proxy)

    def revokeApplication(self, clubDBID, callback = _logClubResponse):
        self._doClubCmd(CLIENT_CLUB_COMMANDS.REVOKE_APPLICATION, clubDBID, 0, partial(self.__onClubResponse_syncState, callback, clubDBID))

    def acceptApplication(self, clubDBID, applicantDBID, callback = _logClubResponse):
        self._doClubCmd(CLIENT_CLUB_COMMANDS.ACCEPT_APPLICATION, clubDBID, applicantDBID, partial(self.__onClubResponse_noSyncState, callback, clubDBID))

    def declineApplication(self, clubDBID, applicantDBID, callback = _logClubResponse):
        self._doClubCmd(CLIENT_CLUB_COMMANDS.DECLINE_APPLICATION, clubDBID, applicantDBID, partial(self.__onClubResponse_noSyncState, callback, clubDBID))

    def __onUnitResponseReceived(self, requestID):
        self.__account.onCmdResponse(requestID, AccountCommands.RES_SUCCESS, '')

    def __onUnitErrorReceived(self, requestID, unitMgrID, unitIdx, errorCode, errorString):
        self.__account.onCmdResponse(requestID, WEB_CMD_RESULT.UNIT_ERROR, errorString)

    def joinUnit(self, clubDBID, timestamp, callback = _logClubResponse):
        self._doClubCmd(CLIENT_CLUB_COMMANDS.JOIN_UNIT, clubDBID, timestamp, callback)

    def acceptInvite(self, clubDBID, callback = _logClubResponse):
        self._doClubCmd(CLIENT_CLUB_COMMANDS.ACCEPT_INVITE, clubDBID, 0, partial(self.__onClubResponse_syncState, callback, clubDBID))

    def declineInvite(self, clubDBID, callback = _logClubResponse):
        self._doClubCmd(CLIENT_CLUB_COMMANDS.DECLINE_INVITE, clubDBID, 0, partial(self.__onClubResponse_syncState, callback, clubDBID))

    def getApplications(self, callback = _logClubResponse):
        self._doClubCmd(CLIENT_CLUB_COMMANDS.GET_APPLICATIONS, 0, 0, callback)

    def getClubApplicants(self, clubDBID, callback = _logClubResponse):
        self._doClubCmd(CLIENT_CLUB_COMMANDS.GET_CLUB_APPLICANTS, clubDBID, 0, callback)

    def getInvites(self, callback = _logClubResponse):
        self._doClubCmd(CLIENT_CLUB_COMMANDS.GET_ACCOUNT_INVITES, 0, 0, callback)

    def transferOwnership(self, clubDBID, playerDBID, callback = _logClubResponse):
        self._doClubCmd(CLIENT_CLUB_COMMANDS.TRANSFER_OWNERSHIP, clubDBID, playerDBID, partial(self.__onClubResponse_noSyncState, callback, clubDBID))

    def assignOfficer(self, clubDBID, memberDBID, callback = _logClubResponse):
        self._doClubCmd(CLIENT_CLUB_COMMANDS.ASSIGN_OFFICER, clubDBID, memberDBID, partial(self.__onClubResponse_noSyncState, callback, clubDBID))

    def assignPrivate(self, clubDBID, memberDBID, callback = _logClubResponse):
        self._doClubCmd(CLIENT_CLUB_COMMANDS.ASSIGN_PRIVATE, clubDBID, memberDBID, partial(self.__onClubResponse_noSyncState, callback, clubDBID))

    def expelMember(self, clubDBID, memberDBID, callback = _logClubResponse):
        self._doClubCmd(CLIENT_CLUB_COMMANDS.EXPEL_MEMBER, clubDBID, memberDBID, partial(self.__onClubResponse_noSyncState, callback, clubDBID))

    def getCompletedSeasons(self, callback = _logClubResponse):
        self._doClubCmd(CLIENT_CLUB_COMMANDS.GET_COMPLETED_SEASONS, 0, 0, callback)

    def getClubBattleStatsHistory(self, clubDBID, callback = _logClubResponse):
        self._doClubCmd(CLIENT_CLUB_COMMANDS.GET_CLUB_BATTLE_STATS_HISTORY, clubDBID, 0, callback)

    def setClubRequirements(self, clubDBID, minWinRate, minBattleCount, shortDescription = '', callback = _logClubResponse):
        intArr = [CLIENT_CLUB_COMMANDS.SET_CLUB_REQUIREMENTS,
         clubDBID,
         minWinRate,
         minBattleCount]
        strArr = [shortDescription]
        proxy = lambda rqID, code, err, data: self.__onClubResponse_noSyncState(callback, clubDBID, code, err, data)
        self.__account._doCmdIntArrStrArr(AccountCommands.CMD_DO_CLUB_CMD, intArr, strArr, proxy)

    def __onGetResponse(self, key, callback, resultID):
        if resultID < 0:
            if callback is not None:
                callback(resultID, None)
            return
        else:
            if callback is not None:
                callback(resultID, self.__cache.get(key, None))
            return

    def __onGetCacheResponse(self, callback, resultID):
        if resultID < 0:
            if callback is not None:
                callback(resultID, None)
            return
        else:
            if callback is not None:
                callback(resultID, self.__cache)
            return

    def __onSendInvitesResponse(self, clubDBID, accountDBIDs, callback, requestID, code, err, extra):
        self.onClubResponse(requestID, code, err, extra, cmd=CLIENT_CLUB_COMMANDS.SEND_INVITES, arg2=clubDBID, arg3=accountDBIDs, callback=callback)
        if code == OK:
            extra = extra or {}
            self.__updateClubData(clubDBID, extra.get('clubData'))

    def __onClubResponse_syncState(self, callback, clubDBID, code, err, data):
        self.__onClubResponse(callback, clubDBID, True, code, err, data)

    def __onClubResponse_noSyncState(self, callback, clubDBID, code, err, data):
        self.__onClubResponse(callback, clubDBID, False, code, err, data)

    def __onResponse_syncState(self, callback, code, err, data):
        self.__onClubResponse(callback, None, True, code, err, data)
        return

    def __onResponse_noSyncState(self, callback, code, err, data):
        self.__onClubResponse(callback, None, False, code, err, data)
        return

    def __onClubResponse(self, callback, clubDBID, isStateChanged, code, err, data):
        if callback is not None:
            callback(code, err, data)
        if code == OK:
            if clubDBID is not None:
                self.__updateClubData(clubDBID, data)
            if isStateChanged:
                self.onClientClubsChanged()
        return

    def __updateClubData(self, clubDBID, clubData):
        updater = self.__subscriptions.get(clubDBID, None)
        if callable(updater):
            updater(clubDBID, clubData)
        return
