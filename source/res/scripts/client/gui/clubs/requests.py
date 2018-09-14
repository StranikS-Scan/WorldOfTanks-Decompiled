# Embedded file name: scripts/client/gui/clubs/requests.py
import weakref
from debug_utils import LOG_WARNING
from gui.shared.rq_cooldown import RequestCooldownManager, REQUEST_SCOPE
from gui.shared.utils.requesters.abstract import ClientRequestsByIDProcessor
from gui.shared.utils.requesters.RequestsController import RequestsController
from gui.clubs import formatters as club_fmts
from gui.clubs.items import OtherPlayerClubInfo
from gui.clubs.settings import CLUB_REQUEST_TYPE as _CRT, DEFAULT_COOLDOWN, REQUEST_TIMEOUT
from gui.clubs.club_helpers import getClientClubsMgr

class ClubCooldownManager(RequestCooldownManager):

    def __init__(self):
        super(ClubCooldownManager, self).__init__(REQUEST_SCOPE.CLUB, DEFAULT_COOLDOWN)

    def lookupName(self, rqTypeID):
        if _CRT.hasValue(rqTypeID):
            requestName = club_fmts.getRequestUserName(rqTypeID)
        else:
            requestName = str(rqTypeID)
            LOG_WARNING('Request type is not found', rqTypeID)
        return requestName

    def getDefaultCoolDown(self):
        return DEFAULT_COOLDOWN


class ClubRequester(ClientRequestsByIDProcessor):

    def getSender(self):
        return self._sender or getClientClubsMgr()


class ClubRequestsController(RequestsController):

    def __init__(self, clubsCtrl):
        super(ClubRequestsController, self).__init__(ClubRequester(), ClubCooldownManager())
        self.__clubsCtrl = weakref.proxy(clubsCtrl)
        self.__handlers = {_CRT.GET_MY_CLUBS: self.getMyClubs,
         _CRT.GET_PRIVATE_PROFILE: self.getPrivateProfile,
         _CRT.GET_MY_CLUBS_HISTORY: self.getMyClubsHistory,
         _CRT.GET_CLUBS: self.getClubs,
         _CRT.FIND_CLUBS: self.findClubs,
         _CRT.SUBSCRIBE: self.subscribe,
         _CRT.UNSUBSCRIBE: self.unsubscribe,
         _CRT.CREATE_CLUB: self.createClub,
         _CRT.DESTROY_CLUB: self.destroyClub,
         _CRT.LEAVE_CLUB: self.leaveClub,
         _CRT.GET_CLUB: self.getClub,
         _CRT.OPEN_CLUB: self.openClub,
         _CRT.CLOSE_CLUB: self.closeClub,
         _CRT.SEND_INVITE: self.sendInvite,
         _CRT.REVOKE_INVITE: self.revokeInvite,
         _CRT.ACCEPT_INVITE: self.acceptInvite,
         _CRT.DECLINE_INVITE: self.declineInvite,
         _CRT.SEND_APPLICATION: self.sendApplication,
         _CRT.REVOKE_APPLICATION: self.revokeApplication,
         _CRT.ACCEPT_APPLICATION: self.acceptApplication,
         _CRT.DECLINE_APPLICATION: self.declineApplication,
         _CRT.JOIN_UNIT: self.joinUnit,
         _CRT.GET_APPLICATIONS: self.getApplications,
         _CRT.GET_CLUB_APPLICANTS: self.getClubApplicants,
         _CRT.GET_INVITES: self.getInvites,
         _CRT.TRANSFER_OWNERSHIP: self.transferOwnership,
         _CRT.ASSIGN_OFFICER: self.assignOfficer,
         _CRT.ASSIGN_PRIVATE: self.assignPrivate,
         _CRT.KICK_MEMBER: self.kickMember,
         _CRT.GET_CLUBS_CONTENDERS: self.getClubsContenders,
         _CRT.SET_APPLICANT_REQUIREMENTS: self.setApplicantsRequirements,
         _CRT.GET_PLAYER_INFO: self.getPlayerInfo,
         _CRT.GET_SEASONS: self.getClubSeasons,
         _CRT.GET_COMPLETED_SEASONS: self.getCompletedSeasons}

    def fini(self):
        self.__handlers.clear()
        super(ClubRequestsController, self).fini()

    def getMyClubs(self, ctx, callback = None):
        return self._requester.doRequestEx(ctx, callback, 'getMyClubs')

    def getPrivateProfile(self, ctx, callback = None):
        return self._requester.doRequestEx(ctx, callback, 'getAccountProfile')

    def getMyClubsHistory(self, ctx, callback = None):
        return self._requester.doRequestEx(ctx, callback, 'getMyClubsHistory')

    def getApplications(self, ctx, callback = None):
        return self._requester.doRequestEx(ctx, callback, 'getApplications')

    def getInvites(self, ctx, callback = None):
        return self._requester.doRequestEx(ctx, callback, 'getInvites')

    def getClubs(self, ctx, callback = None):
        if ctx.isOnlyOpened():
            requestMethod = 'getOpenClubs'
        else:
            requestMethod = 'getClubs'
        return self._requester.doRequestEx(ctx, callback, requestMethod, ctx.getOffset(), ctx.getCount())

    def findClubs(self, ctx, callback = None):
        return self._requester.doRequestEx(ctx, callback, 'findOpenClubs', ctx.getPattern(), ctx.getOffset(), ctx.getCount())

    def subscribe(self, ctx, callback = None):
        return self._requester.doRequestEx(ctx, callback, 'subscribe', ctx.getClubDbID(), ctx.getSubscriptionType(), updater=ctx.getUpdater())

    def unsubscribe(self, ctx, callback = None):
        return self._requester.doRequestEx(ctx, callback, 'unsubscribe', ctx.getClubDbID())

    def getClub(self, ctx, callback = None):
        return self._requester.doRequestEx(ctx, callback, 'getClubData', ctx.getClubDbID())

    def createClub(self, ctx, callback = None):
        limits = self.__clubsCtrl.getLimits()
        isValid, reason = limits.canCreateClub(self.__clubsCtrl.getProfile())
        if not isValid:
            return self.__doFail(ctx, reason, callback)
        return self._requester.doRequestEx(ctx, callback, 'createClub')

    def acceptInvite(self, ctx, callback = None):
        limits = self.__clubsCtrl.getLimits()
        isValid, reason = limits.canAcceptInvite(self.__clubsCtrl.getProfile(), ctx.getInviteID())
        if not isValid:
            return self.__doFail(ctx, reason, callback)
        return self._requester.doRequestEx(ctx, callback, 'acceptInvite', ctx.getClubDbID())

    def declineInvite(self, ctx, callback = None):
        limits = self.__clubsCtrl.getLimits()
        isValid, reason = limits.canDeclineInvite(self.__clubsCtrl.getProfile(), ctx.getInviteID())
        if not isValid:
            return self.__doFail(ctx, reason, callback)
        return self._requester.doRequestEx(ctx, callback, 'declineInvite', ctx.getClubDbID())

    def sendApplication(self, ctx, callback = None):
        limits = self.__clubsCtrl.getLimits()
        clubDBID = ctx.getClubDbID()
        isValid, reason = limits.canSendApplication(self.__clubsCtrl.getProfile(), self.__clubsCtrl.getClub(clubDBID))
        if not isValid:
            return self.__doFail(ctx, reason, callback)
        return self._requester.doRequestEx(ctx, callback, 'sendApplication', ctx.getClubDbID(), ctx.getComment())

    def revokeApplication(self, ctx, callback = None):
        limits = self.__clubsCtrl.getLimits()
        clubDBID = ctx.getClubDbID()
        isValid, reason = limits.canRevokeApplication(self.__clubsCtrl.getProfile(), self.__clubsCtrl.getClub(clubDBID))
        if not isValid:
            return self.__doFail(ctx, reason, callback)
        return self._requester.doRequestEx(ctx, callback, 'revokeApplication', ctx.getClubDbID())

    def destroyClub(self, ctx, callback = None):
        limits = self.__clubsCtrl.getLimits()
        clubDBID = ctx.getClubDbID()
        isValid, reason = limits.canDestroyClub(self.__clubsCtrl.getProfile(), self.__clubsCtrl.getClub(clubDBID))
        if not isValid:
            return self.__doFail(ctx, reason, callback)
        return self._requester.doRequestEx(ctx, callback, 'disbandClub', ctx.getClubDbID())

    def leaveClub(self, ctx, callback = None):
        limits = self.__clubsCtrl.getLimits()
        clubDBID = ctx.getClubDbID()
        isValid, reason = limits.canLeaveClub(self.__clubsCtrl.getProfile(), self.__clubsCtrl.getClub(clubDBID))
        if not isValid:
            return self.__doFail(ctx, reason, callback)
        return self._requester.doRequestEx(ctx, callback, 'leaveClub', ctx.getClubDbID())

    def openClub(self, ctx, callback = None):
        limits = self.__clubsCtrl.getLimits()
        clubDBID = ctx.getClubDbID()
        isValid, reason = limits.canOpenClub(self.__clubsCtrl.getProfile(), self.__clubsCtrl.getClub(clubDBID))
        if not isValid:
            return self.__doFail(ctx, reason, callback)
        return self._requester.doRequestEx(ctx, callback, 'openClub', ctx.getClubDbID())

    def closeClub(self, ctx, callback = None):
        limits = self.__clubsCtrl.getLimits()
        clubDBID = ctx.getClubDbID()
        isValid, reason = limits.canCloseClub(self.__clubsCtrl.getProfile(), self.__clubsCtrl.getClub(clubDBID))
        if not isValid:
            return self.__doFail(ctx, reason, callback)
        return self._requester.doRequestEx(ctx, callback, 'closeClub', ctx.getClubDbID())

    def sendInvite(self, ctx, callback = None):
        limits = self.__clubsCtrl.getLimits()
        clubDBID = ctx.getClubDbID()
        usersIDs = ctx.getUserDbIDs()
        isValid, reason = limits.canSendInvite(self.__clubsCtrl.getProfile(), self.__clubsCtrl.getClub(clubDBID), usersIDs)
        if not isValid:
            return self.__doFail(ctx, reason, callback)
        if len(usersIDs) > 1:
            methodName, args = 'sendInvites', [usersIDs]
        else:
            methodName, args = 'sendInvite', usersIDs
        return self._requester.doRequestEx(ctx, callback, methodName, ctx.getClubDbID(), *args)

    def revokeInvite(self, ctx, callback = None):
        limits = self.__clubsCtrl.getLimits()
        clubDBID = ctx.getClubDbID()
        isValid, reason = limits.canRevokeInvite(self.__clubsCtrl.getProfile(), self.__clubsCtrl.getClub(clubDBID))
        if not isValid:
            return self.__doFail(ctx, reason, callback)
        return self._requester.doRequestEx(ctx, callback, 'revokeInvite', ctx.getClubDbID(), ctx.getUserDbID())

    def acceptApplication(self, ctx, callback = None):
        limits = self.__clubsCtrl.getLimits()
        clubDBID = ctx.getClubDbID()
        isValid, reason = limits.canAcceptApplication(self.__clubsCtrl.getProfile(), self.__clubsCtrl.getClub(clubDBID))
        if not isValid:
            return self.__doFail(ctx, reason, callback)
        return self._requester.doRequestEx(ctx, callback, 'acceptApplication', ctx.getClubDbID(), ctx.getUserDbID())

    def declineApplication(self, ctx, callback = None):
        limits = self.__clubsCtrl.getLimits()
        clubDBID = ctx.getClubDbID()
        isValid, reason = limits.canDeclineApplication(self.__clubsCtrl.getProfile(), self.__clubsCtrl.getClub(clubDBID))
        if not isValid:
            return self.__doFail(ctx, reason, callback)
        return self._requester.doRequestEx(ctx, callback, 'declineApplication', ctx.getClubDbID(), ctx.getUserDbID())

    def joinUnit(self, ctx, callback = None):
        limits = self.__clubsCtrl.getLimits()
        clubDBID = ctx.getClubDbID()
        club = self.__clubsCtrl.getClub(clubDBID)
        if club is not None and not club.hasActiveUnit():
            isValid, reason = limits.canCreateUnit(self.__clubsCtrl.getProfile(), club)
        else:
            isValid, reason = limits.canJoinUnit(self.__clubsCtrl.getProfile(), club)
        if not isValid:
            return self.__doFail(ctx, reason, callback)
        else:
            return self._requester.doRequestEx(ctx, callback, 'joinUnit', ctx.getClubDbID(), ctx.getJoiningTime())

    def getClubApplicants(self, ctx, callback = None):
        limits = self.__clubsCtrl.getLimits()
        clubDBID = ctx.getClubDbID()
        isValid, reason = limits.canSeeApplicants(self.__clubsCtrl.getProfile(), self.__clubsCtrl.getClub(clubDBID))
        if not isValid:
            return self.__doFail(ctx, reason, callback)
        return self._requester.doRequestEx(ctx, callback, 'getClubApplicants', ctx.getClubDbID())

    def transferOwnership(self, ctx, callback = None):
        limits = self.__clubsCtrl.getLimits()
        clubDBID = ctx.getClubDbID()
        isValid, reason = limits.canTransferOwnership(self.__clubsCtrl.getProfile(), self.__clubsCtrl.getClub(clubDBID))
        if not isValid:
            return self.__doFail(ctx, reason, callback)
        return self._requester.doRequestEx(ctx, callback, 'transferOwnership', ctx.getClubDbID(), ctx.getUserDbID())

    def assignOfficer(self, ctx, callback = None):
        limits = self.__clubsCtrl.getLimits()
        clubDBID = ctx.getClubDbID()
        isValid, reason = limits.canAssignOfficer(self.__clubsCtrl.getProfile(), self.__clubsCtrl.getClub(clubDBID))
        if not isValid:
            return self.__doFail(ctx, reason, callback)
        return self._requester.doRequestEx(ctx, callback, 'assignOfficer', ctx.getClubDbID(), ctx.getUserDbID())

    def assignPrivate(self, ctx, callback = None):
        limits = self.__clubsCtrl.getLimits()
        clubDBID = ctx.getClubDbID()
        isValid, reason = limits.canAssignPrivate(self.__clubsCtrl.getProfile(), self.__clubsCtrl.getClub(clubDBID))
        if not isValid:
            return self.__doFail(ctx, reason, callback)
        return self._requester.doRequestEx(ctx, callback, 'assignPrivate', ctx.getClubDbID(), ctx.getUserDbID())

    def kickMember(self, ctx, callback = None):
        limits = self.__clubsCtrl.getLimits()
        clubDBID = ctx.getClubDbID()
        userDbID = ctx.getUserDbID()
        isValid, reason = limits.canKickMember(self.__clubsCtrl.getProfile(), self.__clubsCtrl.getClub(clubDBID), userDbID)
        if not isValid:
            return self.__doFail(ctx, reason, callback)
        return self._requester.doRequestEx(ctx, callback, 'expelMember', ctx.getClubDbID(), ctx.getUserDbID())

    def setApplicantsRequirements(self, ctx, callback = None):
        limits = self.__clubsCtrl.getLimits()
        clubDBID = ctx.getClubDbID()
        isValid, reason = limits.canChangeClubRequirements(self.__clubsCtrl.getProfile(), self.__clubsCtrl.getClub(clubDBID))
        if not isValid:
            return self.__doFail(ctx, reason, callback)
        return self._requester.doRequestEx(ctx, callback, 'setClubRequirements', ctx.getClubDbID(), ctx.getMinWinRate(), ctx.getMinBattlesCount(), ctx.getDescription())

    def getClubsContenders(self, ctx, callback = None):
        limits = self.__clubsCtrl.getLimits()
        clubDBID = ctx.getClubDbID()
        isValid, reason = limits.canSeeContenders(self.__clubsCtrl.getProfile(), self.__clubsCtrl.getClub(clubDBID))
        if not isValid:
            return self.__doFail(ctx, reason, callback)
        return self._requester.doRequestEx(ctx, callback, 'getClubsContenders', ctx.getClubDbID())

    def getPlayerInfo(self, ctx, callback = None):
        limits = self.__clubsCtrl.getLimits()
        userDBID = ctx.getUserDbID()
        isValid, reason = limits.canSeeOtherPlayerInfo(self.__clubsCtrl.getProfile(), userDbID=userDBID)
        if not isValid:
            return self.__doFail(ctx, reason, callback)

        def _cbWrapper(result):
            if result.isSuccess() and result.data:
                data = OtherPlayerClubInfo(*result.data[0])
            else:
                data = None
            callback(result._replace(data=data))
            return

        return self._requester.doRequestEx(ctx, _cbWrapper, 'getPlayerClubs', userDBID)

    def getClubSeasons(self, ctx, callback = None):
        limits = self.__clubsCtrl.getLimits()
        clubDBID = ctx.getClubDbID()
        isValid, reason = limits.canGetClubSeasons(self.__clubsCtrl.getProfile(), self.__clubsCtrl.getClub(clubDBID))
        if not isValid:
            return self.__doFail(ctx, reason, callback)
        return self._requester.doRequestEx(ctx, callback, 'getClubBattleStatsHistory', clubDBID)

    def getCompletedSeasons(self, ctx, callback = None):
        return self._requester.doRequestEx(ctx, callback, 'getCompletedSeasons')

    def _getHandlerByRequestType(self, requestTypeID):
        return self.__handlers.get(requestTypeID)

    def _getRequestTimeOut(self):
        return REQUEST_TIMEOUT

    def __doFail(self, ctx, reason, callback):
        self._requester._stopProcessing(ctx, reason, callback)
