# Embedded file name: scripts/client/account_helpers/ClientClubs.py
import AccountCommands
from functools import partial
from club_shared import CLIENT_CLUB_COMMANDS, CLUB_SUBSCRIPTION_TYPE
import cPickle
from debug_utils import LOG_DAN, LOG_CURRENT_EXCEPTION
from ClubDescr import ClubDescr

def _logClubResponse(self, *args):
    LOG_DAN('_logClubResponse', args)


OK = 0

class ClientClubs(object):

    def __init__(self, syncData):
        self.__account = None
        self.__syncData = syncData
        self.__cache = {}
        self.__subscriptions = {}
        self._lastClub = None
        return

    def __repr__(self):
        return str(self.__cache)

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

    def synchronize(self, isFullSync, diff):
        if isFullSync:
            self.__cache.clear()

    def getCache(self, callback = None):
        if self.__ignore:
            if callback is not None:
                callback(AccountCommands.RES_NON_PLAYER, None)
            return
        else:
            self.__syncData.waitForSync(partial(self.__onGetCacheResponse, callback))
            return

    def onClubResponse(self, requestID, responseCode, responseError, extra, cmd = 0, arg2 = 0, arg3 = 0, callback = None):
        if responseCode == OK:
            if cmd == CLIENT_CLUB_COMMANDS.GET_MY_CLUBS:
                self.__cache['myClubs'] = extra
            elif cmd == CLIENT_CLUB_COMMANDS.GET_APPLICATIONS:
                self.__cache['applications'] = extra
            elif cmd == CLIENT_CLUB_COMMANDS.GET_ACCOUNT_INVITES:
                self.__cache['invites'] = extra
        if callback:
            callback(requestID, responseCode, responseError, extra)

    def onClubUpdated(self, clubDBID, serializedUpdate):
        updater = self.__subscriptions.get(clubDBID, None)
        club = ClubDescr(clubDBID, serializedUpdate)
        LOG_DAN('onClubUpdated', club)
        if updater is None:
            self._lastClub = club
            return
        else:
            clubsCache = self.__cache.setdefault('clubs', {})
            clubsCache[clubDBID] = club
            if updater is True:
                return
            updater(clubDBID, serializedUpdate)
            return

    def _doClubCmd(self, cmd, arg2, arg3, callback):
        LOG_DAN('_doClubCmd', cmd, arg2, arg3)
        clubCallback = partial(self.onClubResponse, cmd=cmd, arg2=arg2, arg3=arg3, callback=callback)
        self.__account._doCmdInt3(AccountCommands.CMD_DO_CLUB_CMD, cmd, arg2, arg3, clubCallback)

    def createClub(self, callback = _logClubResponse):
        self._doClubCmd(CLIENT_CLUB_COMMANDS.CREATE, 0, 0, callback)

    def getMyClubs(self, callback = _logClubResponse):
        self._doClubCmd(CLIENT_CLUB_COMMANDS.GET_MY_CLUBS, 0, 0, callback)

    def disbandClub(self, clubDBID, callback = _logClubResponse):
        self._doClubCmd(CLIENT_CLUB_COMMANDS.DISBAND, clubDBID, 0, callback)

    def leaveClub(self, clubDBID, callback = _logClubResponse):
        self._doClubCmd(CLIENT_CLUB_COMMANDS.LEAVE, clubDBID, 0, callback)

    def getClubData(self, clubDBID, callback = _logClubResponse):
        self._doClubCmd(CLIENT_CLUB_COMMANDS.GET, clubDBID, 0, callback)

    def openClub(self, clubDBID, callback = _logClubResponse):
        self._doClubCmd(CLIENT_CLUB_COMMANDS.OPEN_CLUB, clubDBID, 0, callback)

    def closeClub(self, clubDBID, callback = _logClubResponse):
        self._doClubCmd(CLIENT_CLUB_COMMANDS.CLOSE_CLUB, clubDBID, 0, callback)

    def getClubs(self, start, count, callback = _logClubResponse):
        self._doClubCmd(CLIENT_CLUB_COMMANDS.GET_CLUBS, start, count, callback)

    def getOpenClubs(self, offset, count, callback = _logClubResponse):
        self._doClubCmd(CLIENT_CLUB_COMMANDS.GET_OPEN_CLUBS, offset, count, callback)

    def changeClubName(self, clubDBID, name, callback = _logClubResponse):
        self.__account._doCmdInt2Str(AccountCommands.CMD_DO_CLUB_CMD, CLIENT_CLUB_COMMANDS.CHANGE_CLUB_NAME, clubDBID, name, callback)

    def changeClubEmblem(self, clubDBID, emblemDBID, callback = _logClubResponse):
        self._doClubCmd(CLIENT_CLUB_COMMANDS.CHANGE_CLUB_EMBLEM, clubDBID, emblemDBID, callback)

    def subscribe(self, clubDBID, subscriptionType = 0, callback = _logClubResponse, updater = True):
        shouldSubscribe = subscriptionType != CLUB_SUBSCRIPTION_TYPE.NONE
        if shouldSubscribe:
            self.__subscriptions[clubDBID] = updater
        else:
            self.__subscriptions.pop(clubDBID, None)
        self._doClubCmd(CLIENT_CLUB_COMMANDS.SUBSCRIBE, clubDBID, subscriptionType, callback)
        return

    def unsubscribe(self, clubDBID):
        self.__subscriptions.pop(clubDBID, None)
        cacheClubs = self.__cache.get('clubs', {})
        cacheClubs.pop(clubDBID, None)
        return

    def sendInvite(self, clubDBID, accountDBID, callback = _logClubResponse):
        self._doClubCmd(CLIENT_CLUB_COMMANDS.SEND_INVITE, clubDBID, accountDBID, callback)

    def revokeInvite(self, clubDBID, accountDBID, callback = _logClubResponse):
        self._doClubCmd(CLIENT_CLUB_COMMANDS.REVOKE_INVITE, clubDBID, accountDBID, callback)

    def sendApplication(self, clubDBID, callback = _logClubResponse):
        self._doClubCmd(CLIENT_CLUB_COMMANDS.SEND_APPLICATION, clubDBID, 0, callback)

    def revokeApplication(self, clubDBID, callback = _logClubResponse):
        self._doClubCmd(CLIENT_CLUB_COMMANDS.REVOKE_APPLICATION, clubDBID, 0, callback)

    def acceptApplication(self, clubDBID, applicantDBID, callback = _logClubResponse):
        self._doClubCmd(CLIENT_CLUB_COMMANDS.ACCEPT_APPLICATION, clubDBID, applicantDBID, callback)

    def declineApplication(self, clubDBID, applicantDBID, callback = _logClubResponse):
        self._doClubCmd(CLIENT_CLUB_COMMANDS.DECLINE_APPLICATION, clubDBID, applicantDBID, callback)

    def joinUnit(self, clubDBID, callback = _logClubResponse):
        self._doClubCmd(CLIENT_CLUB_COMMANDS.JOIN_UNIT, clubDBID, 0, callback)

    def acceptInvite(self, clubDBID, callback = _logClubResponse):
        self._doClubCmd(CLIENT_CLUB_COMMANDS.ACCEPT_INVITE, clubDBID, 0, callback)

    def declineInvite(self, clubDBID, callback = _logClubResponse):
        self._doClubCmd(CLIENT_CLUB_COMMANDS.DECLINE_INVITE, clubDBID, 0, callback)

    def getApplications(self, callback = _logClubResponse):
        self._doClubCmd(CLIENT_CLUB_COMMANDS.GET_APPLICATIONS, 0, 0, callback)

    def getClubApplicants(self, clubDBID, callback = _logClubResponse):
        self._doClubCmd(CLIENT_CLUB_COMMANDS.GET_CLUB_APPLICANTS, clubDBID, 0, callback)

    def getInvites(self, callback = _logClubResponse):
        self._doClubCmd(CLIENT_CLUB_COMMANDS.GET_ACCOUNT_INVITES, 0, 0, callback)

    def transferOwnership(self, clubDBID, playerDBID, callback = _logClubResponse):
        self._doClubCmd(CLIENT_CLUB_COMMANDS.TRANSFER_OWNERSHIP, clubDBID, playerDBID, callback)

    def assignOfficer(self, clubDBID, memberDBID, callback = _logClubResponse):
        self._doClubCmd(CLIENT_CLUB_COMMANDS.ASSIGN_OFFICER, clubDBID, memberDBID, callback)

    def assignPrivate(self, clubDBID, memberDBID, callback = _logClubResponse):
        self._doClubCmd(CLIENT_CLUB_COMMANDS.ASSIGN_PRIVATE, clubDBID, memberDBID, callback)

    def expelMember(self, clubDBID, memberDBID, callback = _logClubResponse):
        self._doClubCmd(CLIENT_CLUB_COMMANDS.EXPEL_MEMBER, clubDBID, memberDBID, callback)

    def setClubRequirements(self, clubDBID, minWinRate, minBattleCount, callback = _logClubResponse):
        self.__account._doCmdInt4(AccountCommands.CMD_DO_CLUB_CMD, CLIENT_CLUB_COMMANDS.SET_CLUB_REQUIREMENTS, clubDBID, minWinRate, minBattleCount, callback)

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
