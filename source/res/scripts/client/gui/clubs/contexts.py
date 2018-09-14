# Embedded file name: scripts/client/gui/clubs/contexts.py
from constants import PREBATTLE_TYPE, REQUEST_COOLDOWN
from club_shared import CLUB_LIMITS
from external_strings_utils import truncate_utf8
from gui.prb_control import settings as prb_settings
from gui.prb_control.context import PrbCtrlRequestCtx
from gui.clubs.settings import CLUB_REQUEST_TYPE, DEFAULT_COOLDOWN
from gui.shared.utils.decorators import ReprInjector
from gui.shared.utils.requesters import RequestCtx

@ReprInjector.withParent(('getConfirmID', 'confirmID'))

class CommonRequestCtx(RequestCtx):

    def __init__(self, waitingID = '', confirmID = ''):
        super(CommonRequestCtx, self).__init__(waitingID=waitingID)
        self._confirmID = confirmID

    def getConfirmID(self):
        return self._confirmID

    def getCooldown(self):
        return DEFAULT_COOLDOWN


@ReprInjector.withParent(('getClubDbID', 'clubDbID'))

class ClubRequestCtx(CommonRequestCtx):

    def __init__(self, clubDbID, waitingID = '', confirmID = ''):
        super(ClubRequestCtx, self).__init__(waitingID=waitingID, confirmID=confirmID)
        self.__clubDbID = clubDbID

    def getClubDbID(self):
        return self.__clubDbID

    def getCooldown(self):
        return DEFAULT_COOLDOWN


@ReprInjector.withParent(('getSubscriptionType', 'subscriptionType'), ('getUpdater', 'updater'))

class SubscribeCtx(ClubRequestCtx):

    def __init__(self, clubDbID, subscriptionType, updater = True, waitingID = '', confirmID = ''):
        super(SubscribeCtx, self).__init__(clubDbID, waitingID=waitingID, confirmID=confirmID)
        self.__subscriptionType = subscriptionType
        self.__updater = updater

    def getSubscriptionType(self):
        return self.__subscriptionType

    def getUpdater(self):
        return self.__updater

    def getRequestType(self):
        return CLUB_REQUEST_TYPE.SUBSCRIBE


@ReprInjector.withParent()

class UnsubscribeCtx(ClubRequestCtx):

    def getRequestType(self):
        return CLUB_REQUEST_TYPE.UNSUBSCRIBE


@ReprInjector.withParent()

class CreateClubCtx(CommonRequestCtx):

    def __init__(self, waitingID = '', confirmID = ''):
        super(CreateClubCtx, self).__init__(waitingID=waitingID, confirmID=confirmID)

    def getRequestType(self):
        return CLUB_REQUEST_TYPE.CREATE_CLUB


@ReprInjector.withParent()

class GetMyClubsCtx(CommonRequestCtx):

    def __init__(self, waitingID = '', confirmID = ''):
        super(GetMyClubsCtx, self).__init__(waitingID=waitingID, confirmID=confirmID)

    def getRequestType(self):
        return CLUB_REQUEST_TYPE.GET_MY_CLUBS


@ReprInjector.withParent()

class GetPrivateProfileCtx(CommonRequestCtx):

    def __init__(self, waitingID = '', confirmID = ''):
        super(GetPrivateProfileCtx, self).__init__(waitingID=waitingID, confirmID=confirmID)

    def getRequestType(self):
        return CLUB_REQUEST_TYPE.GET_PRIVATE_PROFILE


@ReprInjector.withParent()

class GetMyClubsHistoryCtx(CommonRequestCtx):

    def __init__(self, waitingID = '', confirmID = ''):
        super(GetMyClubsHistoryCtx, self).__init__(waitingID=waitingID, confirmID=confirmID)

    def getRequestType(self):
        return CLUB_REQUEST_TYPE.GET_MY_CLUBS_HISTORY


@ReprInjector.withParent()

class GetCompletedSeasonsCtx(CommonRequestCtx):

    def __init__(self, waitingID = '', confirmID = ''):
        super(GetCompletedSeasonsCtx, self).__init__(waitingID=waitingID, confirmID=confirmID)

    def getRequestType(self):
        return CLUB_REQUEST_TYPE.GET_COMPLETED_SEASONS


@ReprInjector.withParent(('getOffset', 'offset'), ('getCount', 'count'), ('isOnlyOpened', 'onlyOpened'))

class GetClubsCtx(CommonRequestCtx):

    def __init__(self, offset, count, onlyOpened = False, waitingID = '', confirmID = ''):
        super(GetClubsCtx, self).__init__(waitingID=waitingID, confirmID=confirmID)
        self.__offset = offset
        self.__count = count
        self.__onlyOpened = onlyOpened

    def getOffset(self):
        return self.__offset

    def getCount(self):
        return self.__count

    def isOnlyOpened(self):
        return self.__onlyOpened

    def getRequestType(self):
        return CLUB_REQUEST_TYPE.GET_CLUBS


@ReprInjector.withParent(('getPattern', 'pattern'), ('getOffset', 'offset'), ('getCount', 'count'))

class FindClubsCtx(CommonRequestCtx):

    def __init__(self, pattern, offset, count, waitingID = '', confirmID = ''):
        super(FindClubsCtx, self).__init__(waitingID=waitingID, confirmID=confirmID)
        self.__pattern = pattern
        self.__offset = offset
        self.__count = count

    def getPattern(self):
        return self.__pattern

    def getOffset(self):
        return self.__offset

    def getCount(self):
        return self.__count

    def getRequestType(self):
        return CLUB_REQUEST_TYPE.FIND_CLUBS

    def getCooldown(self):
        return 5.0


@ReprInjector.withParent()

class DestroyClubCtx(ClubRequestCtx):

    def getRequestType(self):
        return CLUB_REQUEST_TYPE.DESTROY_CLUB


@ReprInjector.withParent()

class LeaveClubCtx(ClubRequestCtx):

    def getRequestType(self):
        return CLUB_REQUEST_TYPE.LEAVE_CLUB


@ReprInjector.withParent()

class GetClubCtx(ClubRequestCtx):

    def getRequestType(self):
        return CLUB_REQUEST_TYPE.GET_CLUB


@ReprInjector.withParent()

class GetClubSeasonsCtx(ClubRequestCtx):

    def getRequestType(self):
        return CLUB_REQUEST_TYPE.GET_SEASONS


@ReprInjector.withParent()

class OpenCloseClubCtx(ClubRequestCtx):

    def __init__(self, isOpen, clubDbID, waitingID = '', confirmID = ''):
        super(OpenCloseClubCtx, self).__init__(clubDbID, waitingID=waitingID, confirmID=confirmID)
        self.__isOpen = isOpen

    def getRequestType(self):
        if self.__isOpen:
            return CLUB_REQUEST_TYPE.OPEN_CLUB
        else:
            return CLUB_REQUEST_TYPE.CLOSE_CLUB

    def isOpen(self):
        return self.__isOpen


@ReprInjector.withParent(('getName', 'name'))

class ChangeClubNameCtx(ClubRequestCtx):

    def __init__(self, clubDbID, name, waitingID = '', confirmID = ''):
        super(ChangeClubNameCtx, self).__init__(clubDbID, waitingID=waitingID, confirmID=confirmID)
        self.__name = name

    def getName(self):
        return self.__name

    def getRequestType(self):
        return CLUB_REQUEST_TYPE.CHANGE_CLUB_NAME


@ReprInjector.withParent(('getUserDbID', 'userDbID'))

class ClubUserCtx(ClubRequestCtx):

    def __init__(self, clubDbID, userDbID, waitingID = '', confirmID = ''):
        super(ClubUserCtx, self).__init__(clubDbID, waitingID=waitingID, confirmID=confirmID)
        self.__userDbID = userDbID

    def getUserDbID(self):
        return self.__userDbID


@ReprInjector.withParent(('getUserDbIDs', 'users'))

class SendInviteCtx(ClubRequestCtx):

    def __init__(self, clubDbID, userDbIDs, waitingID = '', confirmID = ''):
        super(SendInviteCtx, self).__init__(clubDbID, waitingID=waitingID, confirmID=confirmID)
        self.__userDbIDs = userDbIDs

    def getUserDbIDs(self):
        return self.__userDbIDs

    def getRequestType(self):
        return CLUB_REQUEST_TYPE.SEND_INVITE


@ReprInjector.withParent()

class RevokeInviteCtx(ClubUserCtx):

    def getRequestType(self):
        return CLUB_REQUEST_TYPE.REVOKE_INVITE


@ReprInjector.withParent()

class AcceptInviteCtx(ClubRequestCtx):

    def __init__(self, clubDbID, inviteID, waitingID = '', confirmID = ''):
        super(AcceptInviteCtx, self).__init__(clubDbID, waitingID=waitingID, confirmID=confirmID)
        self.__inviteID = inviteID

    def getInviteID(self):
        return self.__inviteID

    def getRequestType(self):
        return CLUB_REQUEST_TYPE.ACCEPT_INVITE


@ReprInjector.withParent()

class DeclineInviteCtx(ClubRequestCtx):

    def __init__(self, clubDbID, inviteID, waitingID = '', confirmID = ''):
        super(DeclineInviteCtx, self).__init__(clubDbID, waitingID=waitingID, confirmID=confirmID)
        self.__inviteID = inviteID

    def getInviteID(self):
        return self.__inviteID

    def getRequestType(self):
        return CLUB_REQUEST_TYPE.DECLINE_INVITE


@ReprInjector.withParent(('getComment', 'comment'))

class SendApplicationCtx(ClubRequestCtx):

    def __init__(self, clubDbID, comment, waitingID = '', confirmID = ''):
        super(SendApplicationCtx, self).__init__(clubDbID, waitingID=waitingID, confirmID=confirmID)
        self.__comment = comment

    def getComment(self):
        return self.__comment

    def getRequestType(self):
        return CLUB_REQUEST_TYPE.SEND_APPLICATION


@ReprInjector.withParent()

class RevokeApplicationCtx(ClubRequestCtx):

    def getRequestType(self):
        return CLUB_REQUEST_TYPE.REVOKE_APPLICATION


@ReprInjector.withParent()

class AcceptApplicationCtx(ClubUserCtx):

    def getRequestType(self):
        return CLUB_REQUEST_TYPE.ACCEPT_APPLICATION


@ReprInjector.withParent()

class DeclineApplicationCtx(ClubUserCtx):

    def getRequestType(self):
        return CLUB_REQUEST_TYPE.DECLINE_APPLICATION


@ReprInjector.withParent(('getTimestamp', 'time'))

class JoinUnitCtx(ClubRequestCtx):

    def __init__(self, clubDbID, joiningTime, waitingID = '', confirmID = ''):
        super(JoinUnitCtx, self).__init__(clubDbID, waitingID=waitingID, confirmID=confirmID)
        self.__joiningTime = joiningTime

    def getJoiningTime(self):
        return self.__joiningTime

    def getRequestType(self):
        return CLUB_REQUEST_TYPE.JOIN_UNIT


@ReprInjector.withParent()

class GetApplicationsCtx(CommonRequestCtx):

    def __init__(self, waitingID = '', confirmID = ''):
        super(GetApplicationsCtx, self).__init__(waitingID=waitingID, confirmID=confirmID)

    def getRequestType(self):
        return CLUB_REQUEST_TYPE.GET_APPLICATIONS


@ReprInjector.withParent()

class GetInvitesCtx(CommonRequestCtx):

    def __init__(self, waitingID = '', confirmID = ''):
        super(GetInvitesCtx, self).__init__(waitingID=waitingID, confirmID=confirmID)

    def getRequestType(self):
        return CLUB_REQUEST_TYPE.GET_INVITES


@ReprInjector.withParent()

class GetClubApplicants(ClubRequestCtx):

    def getRequestType(self):
        return CLUB_REQUEST_TYPE.GET_CLUB_APPLICANTS


@ReprInjector.withParent()

class TransferOwnershipCtx(ClubUserCtx):

    def getRequestType(self):
        return CLUB_REQUEST_TYPE.TRANSFER_OWNERSHIP


@ReprInjector.withParent()

class AssignOfficerCtx(ClubUserCtx):

    def getRequestType(self):
        return CLUB_REQUEST_TYPE.ASSIGN_OFFICER


@ReprInjector.withParent()

class AssignPrivateCtx(ClubUserCtx):

    def getRequestType(self):
        return CLUB_REQUEST_TYPE.ASSIGN_PRIVATE


@ReprInjector.withParent()

class KickMemberCtx(ClubUserCtx):

    def getRequestType(self):
        return CLUB_REQUEST_TYPE.KICK_MEMBER


@ReprInjector.withParent(('getMinWinRate', 'minWinRate'), ('getMinBattlesCount', 'minBattleCount'), ('getDescription', 'descr'))

class SetApplicantsRequirements(ClubRequestCtx):

    def __init__(self, clubDbID, minWinRate = 0, minBattleCount = 0, description = '', waitingID = '', confirmID = ''):
        super(SetApplicantsRequirements, self).__init__(clubDbID, waitingID=waitingID, confirmID=confirmID)
        self.__minWinRate = minWinRate
        self.__minBattleCount = minBattleCount
        self.__description = truncate_utf8(description, CLUB_LIMITS.MAX_SHORT_DESC_LENGTH)

    def getMinWinRate(self):
        return self.__minWinRate

    def getMinBattlesCount(self):
        return self.__minBattleCount

    def getDescription(self):
        return self.__description

    def getRequestType(self):
        return CLUB_REQUEST_TYPE.SET_APPLICANT_REQUIREMENTS


@ReprInjector.withParent()

class GetClubsContendersCtx(ClubRequestCtx):

    def __init__(self, clubDbID, waitingID = '', confirmID = ''):
        super(GetClubsContendersCtx, self).__init__(clubDbID, waitingID=waitingID, confirmID=confirmID)

    def getRequestType(self):
        return CLUB_REQUEST_TYPE.GET_CLUBS_CONTENDERS


@ReprInjector.withParent(('__battleID', 'battleID'), ('__slotIdx', 'slotIdx'))

class JoinClubBattleCtx(PrbCtrlRequestCtx):

    def __init__(self, clubDbID, joinTime, allowDelay = True, waitingID = '', isUpdateExpected = False):
        super(JoinClubBattleCtx, self).__init__(ctrlType=prb_settings.CTRL_ENTITY_TYPE.UNIT, entityType=PREBATTLE_TYPE.CLUBS, waitingID=waitingID, flags=prb_settings.FUNCTIONAL_FLAG.SWITCH)
        self.__clubDbID = clubDbID
        self.__joinTime = joinTime
        self.__isUpdateExpected = isUpdateExpected
        self.__allowDelay = allowDelay

    def getID(self):
        return self.__clubDbID

    def isUpdateExpected(self):
        return self.__isUpdateExpected

    def isAllowDelay(self):
        return self.__allowDelay

    def getCooldown(self):
        return REQUEST_COOLDOWN.CLUBS_ANY_CMD_COOLDOWN

    def getRequestType(self):
        return CLUB_REQUEST_TYPE.JOIN_UNIT

    def getClubDbID(self):
        return self.__clubDbID

    def getJoiningTime(self):
        return self.__joinTime

    def _setUpdateExpected(self, value):
        self.__isUpdateExpected = value


@ReprInjector.withParent(('getUserDbID', 'userDbID'))

class GetPlayerInfoCtx(CommonRequestCtx):

    def __init__(self, userDbID, waitingID = '', confirmID = ''):
        super(GetPlayerInfoCtx, self).__init__(waitingID=waitingID, confirmID=confirmID)
        self.__userDbID = userDbID

    def getRequestType(self):
        return CLUB_REQUEST_TYPE.GET_PLAYER_INFO

    def getUserDbID(self):
        return self.__userDbID

    def getCooldown(self):
        return DEFAULT_COOLDOWN
