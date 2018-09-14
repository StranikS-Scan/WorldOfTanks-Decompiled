# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/club_shared.py
from itertools import chain
SUBSCRIPTION_EXPIRY_TIME = 300

class CLUB_SUBSCRIPTION_TYPE:
    NONE = 0
    PUBLIC = 1
    PRIVATE = 2
    UNIT = 4


def _makeID(start=None, range=None):
    global _g_id
    id = _g_id = _g_id + 1 if start is None else start
    if range is not None:
        assert range > 0
        _g_id += range
    return id


class CLIENT_CLUB_COMMANDS:
    CREATE = _makeID(start=1)
    GET_MY_CLUBS = _makeID()
    GET_PLAYER_CLUBS = _makeID()
    GET_MY_CLUBS_HISTORY = _makeID()
    DISBAND = _makeID()
    LEAVE = _makeID()
    GET = _makeID()
    CHANGE_CLUB_NAME = _makeID()
    CHANGE_CLUB_EMBLEM = _makeID()
    SET_CLUB_REQUIREMENTS = _makeID()
    CLOSE_CLUB = _makeID()
    OPEN_CLUB = _makeID()
    GET_CLUBS = _makeID()
    GET_OPEN_CLUBS = _makeID()
    FIND_OPEN_CLUBS = _makeID()
    SUBSCRIBE = _makeID()
    GET_ACCOUNT_INVITES = _makeID()
    SEND_INVITE = _makeID()
    SEND_INVITES = _makeID()
    REVOKE_INVITE = _makeID()
    ACCEPT_INVITE = _makeID()
    DECLINE_INVITE = _makeID()
    GET_APPLICATIONS = _makeID()
    GET_CLUB_APPLICANTS = _makeID()
    SEND_APPLICATION = _makeID()
    REVOKE_APPLICATION = _makeID()
    ACCEPT_APPLICATION = _makeID()
    DECLINE_APPLICATION = _makeID()
    TRANSFER_OWNERSHIP = _makeID()
    ASSIGN_OFFICER = _makeID()
    ASSIGN_PRIVATE = _makeID()
    EXPEL_MEMBER = _makeID()
    JOIN_UNIT = _makeID()
    GET_ACCOUNT_PROFILE = _makeID()
    GET_CLUBS_CONTENDERS = _makeID()
    GET_CLUB_BATTLE_STATS_HISTORY = _makeID()
    GET_COMPLETED_SEASONS = _makeID()
    INT4_RANGE = {SET_CLUB_REQUIREMENTS}
    INT3_RANGE = {CREATE,
     DISBAND,
     LEAVE,
     GET,
     SUBSCRIBE,
     GET_MY_CLUBS,
     GET_MY_CLUBS_HISTORY,
     GET_CLUBS,
     GET_OPEN_CLUBS,
     OPEN_CLUB,
     CLOSE_CLUB,
     CHANGE_CLUB_EMBLEM,
     SEND_INVITE,
     REVOKE_INVITE,
     GET_ACCOUNT_INVITES,
     ACCEPT_INVITE,
     DECLINE_INVITE,
     TRANSFER_OWNERSHIP,
     ASSIGN_OFFICER,
     ASSIGN_PRIVATE,
     EXPEL_MEMBER,
     REVOKE_APPLICATION,
     ACCEPT_APPLICATION,
     DECLINE_APPLICATION,
     GET_APPLICATIONS,
     GET_CLUB_APPLICANTS,
     JOIN_UNIT,
     GET_ACCOUNT_PROFILE,
     ACCEPT_INVITE,
     DECLINE_INVITE,
     GET_CLUBS_CONTENDERS,
     GET_PLAYER_CLUBS,
     GET_COMPLETED_SEASONS,
     GET_CLUB_BATTLE_STATS_HISTORY}
    INTARR_STRARR_RANGE = {SEND_INVITES, SET_CLUB_REQUIREMENTS, FIND_OPEN_CLUBS}
    INT2_STR_RANGE = {CHANGE_CLUB_NAME, SEND_APPLICATION}
    RANGE = {CREATE,
     DISBAND,
     LEAVE,
     GET,
     SUBSCRIBE,
     GET_MY_CLUBS,
     GET_MY_CLUBS_HISTORY,
     SEND_INVITE,
     REVOKE_INVITE,
     GET_ACCOUNT_INVITES,
     ACCEPT_INVITE,
     DECLINE_INVITE,
     GET_CLUBS,
     GET_OPEN_CLUBS,
     OPEN_CLUB,
     CLOSE_CLUB,
     CHANGE_CLUB_NAME,
     CHANGE_CLUB_EMBLEM,
     TRANSFER_OWNERSHIP,
     ASSIGN_OFFICER,
     ASSIGN_PRIVATE,
     EXPEL_MEMBER,
     SEND_APPLICATION,
     REVOKE_APPLICATION,
     ACCEPT_APPLICATION,
     DECLINE_APPLICATION,
     GET_APPLICATIONS,
     GET_CLUB_APPLICANTS,
     JOIN_UNIT,
     ACCEPT_INVITE,
     DECLINE_INVITE,
     GET_ACCOUNT_PROFILE,
     SEND_INVITES,
     GET_CLUBS_CONTENDERS}
    TEST_RANGE = {}


CLIENT_CLUB_COMMAND_NAMES = {v:k for k, v in CLIENT_CLUB_COMMANDS.__dict__.iteritems() if isinstance(v, int)}

class CLUB_ROLE(object):
    PRIVATE = 2
    OFFICER = 4
    OWNER = 8
    DEFAULT = PRIVATE
    DEFAULT_CREATOR = OWNER | OFFICER
    DEFAULT_OWNER = OWNER | OFFICER


class CLUB_STATE(object):
    CREATED = 2
    OPENED = 4
    DELETED = 8
    INITIAL_STATE = CREATED


class ClubRolesHelper(object):

    @staticmethod
    def isOwner(mask):
        return mask & CLUB_ROLE.OWNER != 0

    @staticmethod
    def isPrivate(mask):
        return mask & CLUB_ROLE.PRIVATE != 0

    @staticmethod
    def isOfficer(mask):
        return mask & CLUB_ROLE.OFFICER != 0

    @staticmethod
    def canAppointOfficer(mask):
        return ClubRolesHelper.isOwner(mask)

    @staticmethod
    def canAppointPrivate(mask):
        return ClubRolesHelper.isOwner(mask)

    @staticmethod
    def canExpelMember(mask):
        return ClubRolesHelper.isOwner(mask)

    @staticmethod
    def deleteOfficer(mask):
        return mask & ~CLUB_ROLE.OFFICER

    @staticmethod
    def deleteOwner(mask):
        return mask & ~CLUB_ROLE.OWNER

    @staticmethod
    def assignOfficer():
        return CLUB_ROLE.OFFICER

    @staticmethod
    def assignPrivate():
        return CLUB_ROLE.PRIVATE

    @staticmethod
    def assignOwner(mask=None):
        return mask | CLUB_ROLE.DEFAULT_OWNER if mask else CLUB_ROLE.DEFAULT_OWNER


class ClubStateHelper(object):

    @staticmethod
    def isCloseForApplicants(state):
        return state & CLUB_STATE.OPENED == 0

    @staticmethod
    def isOpenForApplicants(state):
        return state & CLUB_STATE.OPENED != 0

    @staticmethod
    def isClubDisbanded(state):
        return state & CLUB_STATE.CREATED == 0

    @staticmethod
    def closeClub(state):
        return state & ~CLUB_STATE.OPENED

    @staticmethod
    def openClub(state):
        return state | CLUB_STATE.OPENED

    @staticmethod
    def disbandClub(state):
        return state & ~CLUB_STATE.CREATED

    @staticmethod
    def restoreClub(state):
        return state | CLUB_STATE.CREATED


def ladderRating(cr):
    return int(cr[0] - 3 * cr[1] + 0.5)


def ladderRatingLocal(cr, division):
    points = ladderRating(cr) if isinstance(cr, (tuple, list)) else int(cr)
    return points - 100 * division + 30


class CLUB_LIMITS(object):
    MAX_SHORT_DESC_LENGTH = 120
    MAX_INVITES_PER_CALL = 20
    MAX_PREVIOUS_CLUBS = 5
    MAX_NAME_LENGTH = 32
    MAX_PAGE_SIZE = 100
    MAX_APPLICANTS = 30
    MAX_MEMBERS = 12
    MAX_COMMENT_LENGTH = 250
    MIN_BATTLES_COUNT_TO_CHANGE_NAME = 20


class RESTRICTION_REASONS(object):
    TEAM_DOES_NOT_EXIST = 301
    TEAM_IS_FULL = 302
    TEAM_IS_NOT_ACTIVE = 303
    TEAM_ALREADY_EXIST = 304
    TEAM_MEMBERS_COUNT_ERROR = 306
    TEAM_DOES_NOT_HAVE_OWNER = 307
    TEAM_DOSSIER_WAS_LOCKED = 308
    TEAM_ALREADY_UNLOCKED = 309
    TEAM_LOCK_TOKEN_ERROR = 310
    EMBLEM_DOES_NOT_EXIST = 311
    MIXED_FIELDS_UPDATE_DURING_UNLOCK = 311
    EMBLEM_FOR_CURRENT_TEAM_ALREADY_EXIST = 312
    TEAM_CHECKOUT_ACCOUNT_ERROR = 312
    PRIVATE_PROFILE_UNKNOWN = 313
    WGESTB_COOLDOWN = 701
    CHANGE_TEAM_NAME_COOLDOWN = 70101
    CHANGE_TEAM_TAG_COOLDOWN = 70102
    TEAM_LEAVE_COOLDOWN = 70103
    CANCEL_APPLICATION_COOLDOWN = 70104
    CREATE_TEAM_AFTER_LEAVE_COOLDOWN = 70105
    CREATE_TEAM_AFTER_DEACTIVATION_COOLDOWN = 70106
    JOIN_TEAM_AFTER_DEACTIVATION_COOLDOWN = 70107
    SAME_TEAM_APPLICATION_COOLDOWN = 70108
    WGL_CUSTOM_ERROR = 702
    MEMBERSHIP_APPLICATION_NOT_NEEDED = 801
    APPLICATION_FOR_USER_EXCEEDED = 803
    SPA_ATTRIBUTE_EXISTS = 111
    ACCOUNT_DOES_NOT_EXIST = 401
    ACCOUNT_BANNED = 402
    ACCOUNT_NOT_IN_TEAM = 501
    ACCOUNT_ALREADY_IN_TEAM = 502
    ACCOUNT_TEAMS_LIMIT_EXCEEDED = 503
    ACCOUNT_IS_TEAM_OWNER = 504
    OWNER_TEAMS_LIMIT_EXCEEDED = 505
    MEMBERSHIP_PROPOSAL_NOT_NEEDED = 901
    TEAM_ACTIVE_PROPOSALS_EXCEEDED = 906


RESTRICTION_REASONS_NAMES = dict(((v, k) for k, v in RESTRICTION_REASONS.__dict__.iteritems() if not k.startswith('_')))

class CLUB_INVITE_STATE(object):
    ACTIVE = 1
    ACCEPTED = 2
    DECLINED = 3
    CANCELLED = 4


CLUB_INVITE_STATE_NAMES = dict([ (v, k) for k, v in CLUB_INVITE_STATE.__dict__.iteritems() if not k.startswith('_') ])

class ACCOUNT_NOTIFICATION_TYPE(object):
    APPLICATION_ADDED = 1
    APPLICATION_ACCEPTED = 2
    APPLICATION_DECLINED = 3
    APPLICATION_REVOKED = 4
    APPLICATION_TERMINATED = 5
    INVITE_ADDED = 11
    INVITE_ACCEPTED = 12
    INVITE_DECLINED = 13
    INVITE_REVOKED = 14
    INVITE_TERMINATED = 15
    CLUB_CREATED = 21
    CLUB_ATTRIBUTES_CHANGED = 22
    CLUB_MEMBER_ROLE_UPDATE = 23
    CLUB_MEMBER_EXPELLED = 24
    CLUB_DISBANDED = 25
    RESTRICTION_ADDED = 31
    RESTRICTION_REMOVED = 32
    WEB_AVAILABLE = 66
    WEB_UNAVAILABLE = 67
    SEASON_ACTIVE = 70
    SEASON_SUSPENDED = 71
    SEASON_INACTIVE = 72
    SEASON = {SEASON_ACTIVE, SEASON_SUSPENDED, SEASON_INACTIVE}
    WEB = {WEB_AVAILABLE, WEB_UNAVAILABLE}
    CLUB = {CLUB_CREATED,
     CLUB_ATTRIBUTES_CHANGED,
     CLUB_MEMBER_ROLE_UPDATE,
     CLUB_MEMBER_EXPELLED,
     CLUB_DISBANDED}
    INVITE = {INVITE_ADDED,
     INVITE_ACCEPTED,
     INVITE_DECLINED,
     INVITE_REVOKED,
     INVITE_TERMINATED}
    APPLICATION = {APPLICATION_ADDED,
     APPLICATION_ACCEPTED,
     APPLICATION_DECLINED,
     APPLICATION_REVOKED,
     APPLICATION_TERMINATED}
    RESTRICTION = {RESTRICTION_ADDED, RESTRICTION_REMOVED}
    REQUIRES_PROFILE_UPDATE = CLUB | INVITE | APPLICATION | RESTRICTION | {WEB_AVAILABLE}


class EMBLEM_TYPE(object):
    SIZE_16x16 = '16x16'
    SIZE_24x24 = '24x24'
    SIZE_32x32 = '32x32'
    SIZE_64x64 = '64x64'
    SIZE_195x195 = '195x195'
    SIZE_256x256 = '256x256'
    ALL = {SIZE_16x16,
     SIZE_24x24,
     SIZE_32x32,
     SIZE_64x64,
     SIZE_195x195,
     SIZE_256x256}


class RESTRICTION_OBJECT(object):
    TARGET = 0
    SOURCE = 1


class WEB_CMD_RESULT(object):
    OK = 0
    TIMEOUT = 1
    ALREADY_CLUB_OWNER = 10
    ALREADY_CLUB_MEMBER = 11
    CLUB_NOT_FOUND = 12
    NOT_A_CLUB_MEMBER = 13
    NON_EMPTY_CLUB = 14
    FORBIDDEN_FOR_CLUB_OWNER = 15
    CLUB_IS_CLOSED = 16
    INACTIVE_CLUB = 17
    CLUB_IS_LOCKED = 18
    CLUB_NOT_IN_LADDER = 19
    CLUB_IS_UNLOCKED = 20
    MEMBERS_LIMIT_REACHED = 21
    CANT_CHANGE_ROLE = 22
    NOT_REGISTERED_EMBLEM = 23
    EMBLEM_ALREADY_EXISTS = 24
    APPLICATION_ALREADY_EXISTS = 50
    APPLICANTS_LIMIT_REACHED = 51
    NOT_A_CLUB_APPLICANT = 52
    INACTIVE_APPLICATION = 53
    INVITE_ALREADY_SENT = 54
    INVITE_NOT_FOUND = 55
    INVITES_LIMIT_REACHED = 56
    INACTIVE_INVITE = 57
    INCORRECT_PARAMS = 60
    RESPONSE_NOT_REGISTERED = 61
    SPA_ACCOUNT_NOT_REGISTERED = 62
    WEB_ACCOUNT_NOT_REGISTERED = 63
    ACCOUNT_IS_BANNED = 64
    SPA_ERROR = 65
    FORBIDDEN_FOR_ACCOUNT = 66
    MAX_PENDING_REQUESTS = 67
    NAME_ALREADY_TAKEN = 68
    INCORRECT_TOKEN = 69
    INCORRECT_URL = 70
    WRONG_WEB_FORMAT = 71
    WEB_RESTRICTION = 72
    WEB_UNAVAILABLE = 73
    COMPOSITE_REQUEST_FAILED = 74
    UNIT_ERROR = 75
    ESTB_SERVER_ERROR = 76
    UNKNOWN = 42
    WEB_UNAVAILABLE_ERRORS = (UNKNOWN,
     WEB_UNAVAILABLE,
     SPA_ERROR,
     ESTB_SERVER_ERROR)
    UNEXPECTED_ISSUES = {ESTB_SERVER_ERROR,
     TIMEOUT,
     INCORRECT_PARAMS,
     RESPONSE_NOT_REGISTERED,
     UNKNOWN,
     SPA_ACCOUNT_NOT_REGISTERED,
     SPA_ERROR,
     MAX_PENDING_REQUESTS,
     INCORRECT_TOKEN,
     INCORRECT_URL,
     WRONG_WEB_FORMAT,
     WEB_UNAVAILABLE,
     CLUB_IS_UNLOCKED,
     CLUB_IS_LOCKED}
    MSG = {OK: 'Command finished successfully.',
     ALREADY_CLUB_OWNER: 'Account already owns the club.',
     ALREADY_CLUB_MEMBER: 'Account already a club member.',
     CLUB_NOT_FOUND: 'No club found.',
     NOT_A_CLUB_MEMBER: 'Account not a club member.',
     NON_EMPTY_CLUB: 'Forbidden operation for non-empty club.',
     FORBIDDEN_FOR_CLUB_OWNER: 'This operation is forbidden for club owner.',
     APPLICANTS_LIMIT_REACHED: 'Forbidden operation because applicants limit reached.',
     MEMBERS_LIMIT_REACHED: 'Forbidden operation because members limit reached.',
     INVITE_ALREADY_SENT: 'Invite to the club already sent to this player.',
     INVITE_NOT_FOUND: 'Invite to the club not found for this player.',
     NOT_A_CLUB_APPLICANT: 'Account not a club applicant.',
     INCORRECT_PARAMS: 'Incorrect params passed to the handler.',
     RESPONSE_NOT_REGISTERED: 'Handler response not registered.',
     CLUB_IS_CLOSED: 'Applications to the closed club are forbidden.',
     NOT_REGISTERED_EMBLEM: 'This emblem not registered in emulator.',
     TIMEOUT: 'Command failed by timeout.',
     UNKNOWN: 'Unknown or unexpected error.',
     ACCOUNT_IS_BANNED: 'Account for given ID is banned.',
     SPA_ERROR: 'Internal error in SPA .',
     FORBIDDEN_FOR_ACCOUNT: 'Forbidden operation for this account.',
     INACTIVE_CLUB: 'Inactive club.',
     INACTIVE_APPLICATION: 'Inactive application.',
     INACTIVE_INVITE: 'Inactive invite.',
     MAX_PENDING_REQUESTS: 'Too many requests are in the pending state.',
     NAME_ALREADY_TAKEN: 'This club name is already taken.',
     INCORRECT_TOKEN: 'Incorrect checkout token.',
     CLUB_IS_LOCKED: 'Club is locked',
     CLUB_IS_UNLOCKED: 'Club is already unlocked',
     INCORRECT_URL: 'Attempt to access to the incorrect url.',
     WRONG_WEB_FORMAT: 'Wrong obtained web data format. Please see server logs.',
     WEB_RESTRICTION: 'This operation is restricted on web side.',
     WEB_UNAVAILABLE: 'Web API is not available at this moment.',
     COMPOSITE_REQUEST_FAILED: 'None of the sub-requests was not completed successfully.',
     CLUB_NOT_IN_LADDER: 'This club is not in the ladder.',
     INVITES_LIMIT_REACHED: 'Too many invites sent to that player.',
     APPLICATION_ALREADY_EXISTS: 'Application from this account already exists.',
     WEB_ACCOUNT_NOT_REGISTERED: 'Account not registered for given ID.',
     ESTB_SERVER_ERROR: 'Some error on estb side. See server log for details.',
     EMBLEM_ALREADY_EXISTS: 'Emblem already exists.',
     CANT_CHANGE_ROLE: 'Cannot change club member role.'}


class CLUBS_SEASON_STATE(object):
    INACTIVE = 1
    SUSPENDED = 2
    ACTIVE = 3
    TO_TEXT = {ACTIVE: 'ACTIVE',
     SUSPENDED: 'SUSPENDED',
     INACTIVE: 'INACTIVE'}
    ALL = {INACTIVE, SUSPENDED, ACTIVE}
