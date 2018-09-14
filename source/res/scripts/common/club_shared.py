# Embedded file name: scripts/common/club_shared.py
SUBSCRIPTION_EXPIRY_TIME = 300

class CLUB_SUBSCRIPTION_TYPE:
    NONE = 0
    PUBLIC = 1
    PRIVATE = 2
    UNIT = 4


def _makeID(start = None, range = None):
    global _g_id
    id = _g_id = _g_id + 1 if start is None else start
    if not (range is not None and range > 0):
        raise AssertionError
        _g_id += range
    return id


class CLIENT_CLUB_COMMANDS:
    CREATE = _makeID(start=1)
    GET_MY_CLUBS = _makeID()
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
    SUBSCRIBE = _makeID()
    GET_ACCOUNT_INVITES = _makeID()
    SEND_INVITE = _makeID()
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
    INT4_RANGE = {SET_CLUB_REQUIREMENTS}
    INT3_RANGE = {CREATE,
     DISBAND,
     LEAVE,
     GET,
     SUBSCRIBE,
     GET_MY_CLUBS,
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
     SEND_APPLICATION,
     REVOKE_APPLICATION,
     ACCEPT_APPLICATION,
     DECLINE_APPLICATION,
     GET_APPLICATIONS,
     GET_CLUB_APPLICANTS,
     JOIN_UNIT,
     ACCEPT_INVITE,
     DECLINE_INVITE}
    INT2_STR_RANGE = {CHANGE_CLUB_NAME}
    RANGE = {CREATE,
     DISBAND,
     LEAVE,
     GET,
     SUBSCRIBE,
     GET_MY_CLUBS,
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
     SET_CLUB_REQUIREMENTS,
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
     DECLINE_INVITE}
    TEST_RANGE = {}


CLIENT_CLUB_COMMAND_NAMES = {v:k for k, v in CLIENT_CLUB_COMMANDS.__dict__.iteritems() if isinstance(v, int)}
