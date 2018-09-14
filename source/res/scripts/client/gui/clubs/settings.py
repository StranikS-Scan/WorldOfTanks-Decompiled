# Embedded file name: scripts/client/gui/clubs/settings.py
from collections import namedtuple
from club_shared import CLUB_SUBSCRIPTION_TYPE as _CST, CLIENT_CLUB_COMMANDS, CLUB_INVITE_STATE_NAMES
from shared_utils import CONST_CONTAINER
from helpers import time_utils
DEFAULT_COOLDOWN = 1.0
REQUEST_TIMEOUT = 60.0
MIN_BATTLES_FOR_STATS = 1
MIN_MEMBERS_COUNT = 4
CLUBS_COUNT = 1
APPLICATIONS_COUNT = 1
POINTS_PER_DIVISION = 100
MAX_POINTS_IN_DIVISION = 160
BROKEN_WEB_CHECK_PERIOD = 120.0
MAX_CLUB_ACTIVE_INVITES = 20
THE_SAME_CLUB_SEND_APP_COOLDOWN = time_utils.ONE_DAY
LEAGUES_COUNT = 6
DIVISIONS_IN_LEAGUE = 4
DIVISIONS_COUNT = LEAGUES_COUNT * DIVISIONS_IN_LEAGUE
TOP_DIVISION = DIVISIONS_COUNT - 1
MY_CLUB_SUBSCRIPTION = _CST.PUBLIC | _CST.UNIT | _CST.PRIVATE
UNIT_SUBSCRIPTION = _CST.UNIT
OTHER_CLUB_SUBSCRIPTION = _CST.PUBLIC
LADDER_CHEVRON_ICON_PATH = '../maps/icons/library/cybersport/ladder'
LEAGUE_RIBBONS_ICON_PATH = '../maps/icons/library/cybersport/leagueRibbons'
DEFAULT_EMBLEM_PATH = 'gui/maps/icons/library/cybersport/emblems'
DEFAULT_EMBLEM_NAME_PREFIX = 'default'
STUB_EMBLEM_NAME_PREFIX = 'stub'

class CLIENT_CLUB_RESTRICTIONS(CONST_CONTAINER):
    DEFAULT = 'HAVE_NO_RIGHTS'
    NOT_IN_APPLICANTS = 'NOT_IN_APPLICANTS'
    NOT_ENOUGH_MEMBERS = 'NOT_ENOUGH_MEMBERS'
    CLUB_IS_CLOSED = 'CLUB_IS_CLOSED'
    ACCOUNT_ALREADY_IN_TEAM = 'ACCOUNT_ALREADY_IN_TEAM'
    APPLICATION_FOR_USER_EXCEEDED = 'APPLICATION_FOR_USER_EXCEEDED'
    INVITE_DOES_NOT_EXIST = 'INVITE_DOES_NOT_EXIST'
    INVITE_IS_NOT_ACTIVE = 'INVITE_IS_NOT_ACTIVE'
    CLUB_IS_NOT_IN_LADDER = 'This club is not in the ladder.'
    NOT_A_CLUB_MEMBER = 'Account not a club member.'
    HAS_NO_CLUB = 'HAS_NO_CLUB'
    TOO_MANY_INVITES_PER_CALL = 'TOO_MANY_INVITES_PER_CALL'
    TOO_MANY_ACTIVE_INVITES = 'TEAM_ACTIVE_PROPOSALS_EXCEEDED'
    NOT_ENOUGH_RATED_BATTLES = 'NOT_ENOUGH_RATED_BATTLES'
    TEMPORARILY_RESTRICTED = 'This operation is restricted on web side'


class CLIENT_CLUB_STATE(CONST_CONTAINER):
    UNKNOWN = 1
    HAS_CLUB = 2
    NO_CLUB = 3
    SENT_APP = 4


class SUBSCRIPTION_STATE(CONST_CONTAINER):
    NOT_SUBSCRIBED = 1
    SUBSCRIBING = 2
    SUBSCRIBED = 3


class CLUB_REQUEST_TYPE(CONST_CONTAINER):
    SUBSCRIBE = 1
    UNSUBSCRIBE = 2
    CREATE_CLUB = 3
    GET_MY_CLUBS = 4
    GET_MY_CLUBS_HISTORY = 5
    DESTROY_CLUB = 6
    LEAVE_CLUB = 7
    GET_CLUB = 8
    OPEN_CLUB = 9
    GET_CLUBS = 11
    CHANGE_CLUB_NAME = 12
    CHANGE_CLUB_EMBLEM = 13
    SEND_INVITE = 14
    REVOKE_INVITE = 15
    ACCEPT_INVITE = 16
    DECLINE_INVITE = 17
    SEND_APPLICATION = 18
    REVOKE_APPLICATION = 19
    ACCEPT_APPLICATION = 20
    DECLINE_APPLICATION = 21
    JOIN_UNIT = 22
    GET_APPLICATIONS = 23
    GET_CLUB_APPLICANTS = 24
    GET_INVITES = 25
    TRANSFER_OWNERSHIP = 26
    ASSIGN_OFFICER = 27
    ASSIGN_PRIVATE = 28
    KICK_MEMBER = 29
    SET_APPLICANT_REQUIREMENTS = 30
    GET_PRIVATE_PROFILE = 31
    GET_CLUBS_CONTENDERS = 32
    CLOSE_CLUB = 33
    FIND_CLUBS = 34
    GET_PLAYER_INFO = 35
    GET_SEASONS = 36
    GET_COMPLETED_SEASONS = 37
    COMMANDS = {CLIENT_CLUB_COMMANDS.SUBSCRIBE: SUBSCRIBE,
     CLIENT_CLUB_COMMANDS.CREATE: CREATE_CLUB,
     CLIENT_CLUB_COMMANDS.GET_MY_CLUBS: GET_MY_CLUBS,
     CLIENT_CLUB_COMMANDS.GET_MY_CLUBS_HISTORY: GET_MY_CLUBS_HISTORY,
     CLIENT_CLUB_COMMANDS.DISBAND: DESTROY_CLUB,
     CLIENT_CLUB_COMMANDS.LEAVE: LEAVE_CLUB,
     CLIENT_CLUB_COMMANDS.GET: GET_CLUB,
     CLIENT_CLUB_COMMANDS.OPEN_CLUB: OPEN_CLUB,
     CLIENT_CLUB_COMMANDS.CLOSE_CLUB: CLOSE_CLUB,
     CLIENT_CLUB_COMMANDS.GET_CLUBS: GET_CLUBS,
     CLIENT_CLUB_COMMANDS.CHANGE_CLUB_NAME: CHANGE_CLUB_NAME,
     CLIENT_CLUB_COMMANDS.CHANGE_CLUB_EMBLEM: CHANGE_CLUB_EMBLEM,
     CLIENT_CLUB_COMMANDS.SEND_INVITE: SEND_INVITE,
     CLIENT_CLUB_COMMANDS.REVOKE_INVITE: REVOKE_INVITE,
     CLIENT_CLUB_COMMANDS.ACCEPT_INVITE: ACCEPT_INVITE,
     CLIENT_CLUB_COMMANDS.DECLINE_INVITE: DECLINE_INVITE,
     CLIENT_CLUB_COMMANDS.SEND_APPLICATION: SEND_APPLICATION,
     CLIENT_CLUB_COMMANDS.REVOKE_APPLICATION: REVOKE_APPLICATION,
     CLIENT_CLUB_COMMANDS.ACCEPT_APPLICATION: ACCEPT_APPLICATION,
     CLIENT_CLUB_COMMANDS.DECLINE_APPLICATION: DECLINE_APPLICATION,
     CLIENT_CLUB_COMMANDS.JOIN_UNIT: JOIN_UNIT,
     CLIENT_CLUB_COMMANDS.GET_APPLICATIONS: GET_APPLICATIONS,
     CLIENT_CLUB_COMMANDS.GET_CLUB_APPLICANTS: GET_CLUB_APPLICANTS,
     CLIENT_CLUB_COMMANDS.GET_ACCOUNT_INVITES: GET_INVITES,
     CLIENT_CLUB_COMMANDS.TRANSFER_OWNERSHIP: TRANSFER_OWNERSHIP,
     CLIENT_CLUB_COMMANDS.ASSIGN_OFFICER: ASSIGN_OFFICER,
     CLIENT_CLUB_COMMANDS.ASSIGN_PRIVATE: ASSIGN_PRIVATE,
     CLIENT_CLUB_COMMANDS.EXPEL_MEMBER: KICK_MEMBER,
     CLIENT_CLUB_COMMANDS.GET_ACCOUNT_PROFILE: GET_PRIVATE_PROFILE,
     CLIENT_CLUB_COMMANDS.SET_CLUB_REQUIREMENTS: SET_APPLICANT_REQUIREMENTS,
     CLIENT_CLUB_COMMANDS.FIND_OPEN_CLUBS: FIND_CLUBS,
     CLIENT_CLUB_COMMANDS.GET_PLAYER_CLUBS: GET_PLAYER_INFO,
     CLIENT_CLUB_COMMANDS.GET_CLUB_BATTLE_STATS_HISTORY: GET_SEASONS,
     CLIENT_CLUB_COMMANDS.GET_COMPLETED_SEASONS: GET_COMPLETED_SEASONS}


def getLeagueByDivision(division):
    return int(DIVISIONS_COUNT - division - 1) / DIVISIONS_IN_LEAGUE


def getDivisionWithinLeague(division):
    return int(DIVISIONS_COUNT - division - 1) % DIVISIONS_IN_LEAGUE


def getDefaultEmblem16x16():
    return _getDefaultEmblemPath(16)


def getDefaultEmblem24x24():
    return _getDefaultEmblemPath(24)


def getDefaultEmblem32x32():
    return _getDefaultEmblemPath(32)


def getDefaultEmblem64x64():
    return _getDefaultEmblemPath(64)


def getDefaultEmblem256x256():
    return _getDefaultEmblemPath(256)


def getStubEmblem24x24():
    return _getStubEmblemPath(24)


def getStubEmblem32x32():
    return _getStubEmblemPath(32)


def getStubEmblem64x64():
    return _getStubEmblemPath(64)


def getLadderBackground(division = None):
    if division is not None:
        imgFileName = '%d' % (getLeagueByDivision(division) + 1)
    else:
        imgFileName = 'no_ladder'
    return '%s/%s.png' % (LEAGUE_RIBBONS_ICON_PATH, imgFileName)


def getInviteStatusString(state):
    return CLUB_INVITE_STATE_NAMES.get(state, 'N/A')


def getLadderChevron16x16(division = None):
    return _getLadderChevronIcon(16, division)


def getLadderChevron64x64(division = None):
    return _getLadderChevronIcon(64, division)


def getLadderChevron128x128(division = None):
    return _getLadderChevronIcon(128, division)


def getLadderChevron256x256(division = None):
    return _getLadderChevronIcon(256, division)


def getLadderChevronIconName(division = None):
    from gui.clubs.formatters import getDivisionString
    if division is not None:
        return '%d%s' % (getLeagueByDivision(division) + 1, getDivisionString(division))
    else:
        return 'no_ladder'
        return


def getPointsToNextDivision(localRating):
    return MAX_POINTS_IN_DIVISION - localRating


def _getDefaultEmblemPath(size):
    return '%s/%s_%dx%d.png' % (DEFAULT_EMBLEM_PATH,
     DEFAULT_EMBLEM_NAME_PREFIX,
     size,
     size)


def _getStubEmblemPath(size):
    return '%s/%s_%dx%d.png' % (DEFAULT_EMBLEM_PATH,
     STUB_EMBLEM_NAME_PREFIX,
     size,
     size)


def _getLadderChevronIcon(iconSize, division = None):
    return '%s/%d/%s.png' % (LADDER_CHEVRON_ICON_PATH, iconSize, getLadderChevronIconName(division))


_RestrResult = namedtuple('_RestrResult', 'success reason')

def error(reason):
    return _RestrResult(False, reason)


def success():
    return _RestrResult(True, '')
