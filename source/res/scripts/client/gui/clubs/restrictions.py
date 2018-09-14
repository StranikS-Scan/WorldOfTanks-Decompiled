# Embedded file name: scripts/client/gui/clubs/restrictions.py
import operator
from itertools import chain
from collections import namedtuple, defaultdict
from debug_utils import LOG_WARNING
from helpers.time_utils import getCurrentTimestamp
from account_helpers import getAccountDatabaseID
from club_shared import ClubRolesHelper, RESTRICTION_REASONS_NAMES, RESTRICTION_OBJECT, CLUB_LIMITS
from shared_utils import first
from gui import GUI_SETTINGS
from gui.clubs import interfaces
from gui.clubs.settings import CLUB_REQUEST_TYPE as _CRT, CLIENT_CLUB_RESTRICTIONS as _CCR, CLIENT_CLUB_STATE as _CCB, error, success, THE_SAME_CLUB_SEND_APP_COOLDOWN, MAX_CLUB_ACTIVE_INVITES

class MemberPermissions(object):

    def __init__(self, roleMask):
        self.__roleMask = roleMask

    def isOwner(self):
        return ClubRolesHelper.isOwner(self.__roleMask)

    def isOfficer(self):
        return ClubRolesHelper.isOfficer(self.__roleMask)

    def canDestroyClub(self):
        return self.isOwner()

    def canLeaveClub(self):
        return True

    def canOpenClub(self):
        return self.isOwner()

    def canCloseClub(self):
        return self.isOwner()

    def canSendInvite(self):
        return self.isOwner()

    def canSendApplication(self):
        return True

    def canRevokeApplication(self):
        return True

    def canSeeContenders(self):
        return True

    def canSeeOtherPlayerInfo(self):
        return True

    def canGetClubSeasons(self):
        return True

    def canRevokeInvite(self):
        return self.isOwner()

    def canAcceptApplication(self):
        return self.isOwner()

    def canDeclineApplication(self):
        return self.isOwner()

    def canJoinUnit(self):
        return True

    def canCreateUnit(self):
        return self.isOwner() or self.isOfficer()

    def canSeeApplicants(self):
        return self.isOwner() or self.isOfficer()

    def canTransferOwnership(self):
        return self.isOwner()

    def canAssignOfficer(self):
        return self.isOwner()

    def canAssignPrivate(self):
        return self.isOwner()

    def canKickMember(self):
        return self.isOwner()

    def canChangeClubRequirements(self):
        return self.isOwner()

    def canChangeWebSettings(self):
        return self.isOwner()

    def canSetRanked(self):
        return self.isOwner() or self.isOfficer()


class DefaultMemberPermissions(MemberPermissions):

    def __init__(self):
        super(DefaultMemberPermissions, self).__init__(0)


class _Restriction(namedtuple('Restriction', ['reason',
 'cmdID',
 'expires',
 'object'])):

    def getReasonID(self):
        return self.reason

    def getReasonString(self):
        return RESTRICTION_REASONS_NAMES.get(self.reason, _CCR.DEFAULT)

    def getRequestID(self):
        return _CRT.COMMANDS.get(self.cmdID)

    def isInfinite(self):
        return self.expires is None

    def getExpiryTime(self):
        return self.expires

    def getExpiryTimeLeft(self):
        if not self.isInfinite():
            return self.expires - getCurrentTimestamp()
        else:
            return None

    def isExpired(self):
        expLeft = self.getExpiryTimeLeft()
        return expLeft is not None and expLeft <= 0

    def __repr__(self):
        return 'Restriction(cmdID = %s, reasonID = %s, reason = %s, expires = %s, object = %s)' % (self.cmdID,
         self.getReasonID(),
         self.getReasonString(),
         self.expires,
         self.object)


class RestrictionsCollection(object):

    def __init__(self, restrictions):
        self.__restrictions = defaultdict(list)
        for r in restrictions:
            restriction = _Restriction(*r)
            if restriction.object == RESTRICTION_OBJECT.SOURCE:
                self.__restrictions[restriction.getRequestID()].append(restriction)

    def getRestrictions(self):
        return self.__restrictions

    def isRequestValid(self, requestTypeID):
        if requestTypeID in self.__restrictions:
            return error(first(self.__restrictions[requestTypeID]).getReasonString())
        return success()

    def getRequestRestrictions(self, requestTypeID):
        return self.__restrictions[requestTypeID]

    def getNearestRestriction(self):
        valid = filter(lambda a: not a.isExpired(), chain(*self.__restrictions.values()))
        if len(valid):
            return min(valid, key=operator.methodcaller('getExpiryTime'))
        else:
            return None


class _AccountClubLimits(RestrictionsCollection, interfaces.IAccountClubLimits):
    pass


class DefaultAccountClubLimits(_AccountClubLimits):

    def __init__(self):
        super(DefaultAccountClubLimits, self).__init__([])

    def __repr__(self):
        return 'DefaultAccountClubLimits'


class AccountClubLimits(RestrictionsCollection, interfaces.IAccountClubLimits):

    def canCreateClub(self, profile):
        stateID = profile.getState().getStateID()
        if stateID == _CCB.HAS_CLUB:
            return error(_CCR.ACCOUNT_ALREADY_IN_TEAM)
        if stateID == _CCB.SENT_APP:
            return error(_CCR.APPLICATION_FOR_USER_EXCEEDED)
        return self._isAccountRequestValid(_CRT.CREATE_CLUB)

    def canAcceptInvite(self, profile, inviteID):
        if profile.getState().getStateID() == _CCB.HAS_CLUB:
            return error(_CCR.ACCOUNT_ALREADY_IN_TEAM)
        invite = profile.getInvite(inviteID)
        if not invite:
            return error(_CCR.INVITE_DOES_NOT_EXIST)
        if not invite.isActive():
            return error(_CCR.INVITE_IS_NOT_ACTIVE)
        return self._isAccountRequestValid(_CRT.ACCEPT_INVITE)

    def canDeclineInvite(self, profile, inviteID):
        invite = profile.getInvite(inviteID)
        if not invite:
            return error(_CCR.INVITE_DOES_NOT_EXIST)
        if not invite.isActive():
            return error(_CCR.INVITE_IS_NOT_ACTIVE)
        return self._isAccountRequestValid(_CRT.DECLINE_INVITE)

    def canSendApplication(self, profile, club = None):
        stateID = profile.getState().getStateID()
        if stateID == _CCB.HAS_CLUB:
            return error(_CCR.ACCOUNT_ALREADY_IN_TEAM)
        if stateID == _CCB.SENT_APP:
            return error(_CCR.APPLICATION_FOR_USER_EXCEEDED)
        if club:
            if club.getState().isClosed():
                return error(_CCR.CLUB_IS_CLOSED)
            for app in profile.getApplications().itervalues():
                if app.getClubDbID() == club.getClubDbID() and app.isDeclined() and app.getTimestamp() + THE_SAME_CLUB_SEND_APP_COOLDOWN > getCurrentTimestamp():
                    return error(_CCR.TEMPORARILY_RESTRICTED)

        return self._isClubRequestValid(_CRT.SEND_APPLICATION, club, 'canSendApplication')

    def canRevokeApplication(self, profile, club = None):
        stateID = profile.getState().getStateID()
        if stateID != _CCB.SENT_APP or club is not None and profile.getState().getClubDbID() != club.getClubDbID():
            return error(_CCR.NOT_IN_APPLICANTS)
        else:
            return self._isClubRequestValid(_CRT.REVOKE_APPLICATION, club, 'canRevokeApplication')

    def canSeeContenders(self, profile, club = None):
        if club and not club.getLadderInfo().isInLadder():
            return error(_CCR.CLUB_IS_NOT_IN_LADDER)
        return self._isClubRequestValid(_CRT.GET_CLUBS_CONTENDERS, club, 'canSeeContenders')

    def canSeeOtherPlayerInfo(self, profile, club = None, userDbID = None):
        return self._isAccountRequestValid(_CRT.GET_PLAYER_INFO)

    def canGetClubSeasons(self, profile, club = None):
        return self._isAccountRequestValid(_CRT.GET_SEASONS)

    def canDestroyClub(self, profile, club = None):
        stateID = profile.getState().getStateID()
        if stateID != _CCB.HAS_CLUB:
            return error(_CCR.HAS_NO_CLUB)
        return self._isClubRequestValid(_CRT.DESTROY_CLUB, club, 'canDestroyClub')

    def canLeaveClub(self, profile, club = None):
        stateID = profile.getState().getStateID()
        if stateID != _CCB.HAS_CLUB:
            return error(_CCR.HAS_NO_CLUB)
        else:
            if club is not None:
                if not club.hasMember(getAccountDatabaseID()):
                    return error(_CCR.NOT_A_CLUB_MEMBER)
            return self._isClubRequestValid(_CRT.LEAVE_CLUB, club, 'canLeaveClub')

    def canOpenClub(self, profile, club = None):
        stateID = profile.getState().getStateID()
        if stateID != _CCB.HAS_CLUB:
            return error(_CCR.HAS_NO_CLUB)
        return self._isClubRequestValid(_CRT.OPEN_CLUB, club, 'canOpenClub')

    def canCloseClub(self, profile, club = None):
        stateID = profile.getState().getStateID()
        if stateID != _CCB.HAS_CLUB:
            return error(_CCR.HAS_NO_CLUB)
        return self._isClubRequestValid(_CRT.CLOSE_CLUB, club, 'canCloseClub')

    def canSendInvite(self, profile, club = None, accountsToInvite = None):
        stateID = profile.getState().getStateID()
        if stateID != _CCB.HAS_CLUB:
            return error(_CCR.HAS_NO_CLUB)
        else:
            if accountsToInvite is not None:
                if len(accountsToInvite) > CLUB_LIMITS.MAX_INVITES_PER_CALL:
                    return error(_CCR.TOO_MANY_INVITES_PER_CALL)
                if club is not None:
                    available = MAX_CLUB_ACTIVE_INVITES - len(club.getInvites(onlyActive=True))
                    if available < len(accountsToInvite):
                        return error(_CCR.TOO_MANY_ACTIVE_INVITES)
            return self._isClubRequestValid(_CRT.SEND_INVITE, club, 'canSendInvite')

    def canRevokeInvite(self, profile, club = None):
        stateID = profile.getState().getStateID()
        if stateID != _CCB.HAS_CLUB:
            return error(_CCR.HAS_NO_CLUB)
        return self._isClubRequestValid(_CRT.REVOKE_INVITE, club, 'canRevokeInvite')

    def canAcceptApplication(self, profile, club = None):
        stateID = profile.getState().getStateID()
        if stateID != _CCB.HAS_CLUB:
            return error(_CCR.HAS_NO_CLUB)
        return self._isClubRequestValid(_CRT.ACCEPT_APPLICATION, club, 'canAcceptApplication')

    def canDeclineApplication(self, profile, club = None):
        stateID = profile.getState().getStateID()
        if stateID != _CCB.HAS_CLUB:
            return error(_CCR.HAS_NO_CLUB)
        return self._isClubRequestValid(_CRT.DECLINE_APPLICATION, club, 'canDeclineApplication')

    def canJoinUnit(self, profile, club = None):
        stateID = profile.getState().getStateID()
        if stateID != _CCB.HAS_CLUB:
            return error(_CCR.HAS_NO_CLUB)
        return self._isClubRequestValid(_CRT.JOIN_UNIT, club, 'canJoinUnit')

    def canCreateUnit(self, profile, club = None):
        stateID = profile.getState().getStateID()
        if stateID != _CCB.HAS_CLUB:
            return error(_CCR.HAS_NO_CLUB)
        if not club.canParticipateBattles():
            return error(_CCR.NOT_ENOUGH_MEMBERS)
        return self._isClubRequestValid(_CRT.JOIN_UNIT, club, 'canCreateUnit')

    def canSeeApplicants(self, profile, club = None):
        return self._isClubRequestValid(_CRT.GET_CLUB_APPLICANTS, club, 'canSeeApplicants')

    def canTransferOwnership(self, profile, club = None):
        return self._isClubRequestValid(_CRT.TRANSFER_OWNERSHIP, club, 'canTransferOwnership')

    def canAssignOfficer(self, profile, club = None):
        return self._isClubRequestValid(_CRT.ASSIGN_OFFICER, club, 'canAssignOfficer')

    def canAssignPrivate(self, profile, club = None):
        return self._isClubRequestValid(_CRT.ASSIGN_PRIVATE, club, 'canAssignPrivate')

    def canKickMember(self, profile, club = None, memberDbID = None):
        if club is not None:
            if memberDbID is not None:
                if not club.hasMember(memberDbID):
                    return error(_CCR.NOT_A_CLUB_MEMBER)
        return self._isClubRequestValid(_CRT.KICK_MEMBER, club, 'canKickMember')

    def canChangeClubRequirements(self, profile, club = None):
        return self._isClubRequestValid(_CRT.SET_APPLICANT_REQUIREMENTS, club, 'canChangeClubRequirements')

    def canChangeWebSettings(self, profile, club = None):
        url = GUI_SETTINGS.lookup('clubSettings')
        if not url:
            return error(_CCR.DEFAULT)
        elif club is not None:
            for rID in {_CRT.CHANGE_CLUB_NAME, _CRT.CHANGE_CLUB_EMBLEM}:
                result = self._isClubRequestValid(rID, club, 'canChangeWebSettings')
                if result.success:
                    return result

            return error(_CCR.NOT_ENOUGH_RATED_BATTLES)
        else:
            return success()

    def _isAccountRequestValid(self, requestTypeID):
        return self.isRequestValid(requestTypeID)

    def _isClubRequestValid(self, requestTypeID, club, permName):
        if club is not None:
            perms = club.getPermissions()
            if not getattr(perms, permName)():
                return error(_CCR.DEFAULT)
            isValid, reason = club.getRestrictions().isRequestValid(requestTypeID)
            if not isValid:
                return error(reason)
        else:
            LOG_WARNING('There is no club to check restrictions, skip', requestTypeID, club, permName)
        return self._isAccountRequestValid(requestTypeID)

    def __repr__(self):
        return 'AccountClubLimits'
