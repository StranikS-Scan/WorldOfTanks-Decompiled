# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/bob/bob_constants.py
from collections import namedtuple
from shared_utils import CONST_CONTAINER
BOB_TOKEN_PREFIX = 'bob3:'
BOB_TOKENS_DELIMITER = ':'
BOB_TEAM_ID_POS = 2

class AnnouncementType(CONST_CONTAINER):
    UNKNOWN = 0
    REGISTRATION_BEFORE_EVENT_START = 1
    REGISTRATION_AFTER_EVENT_START = 2
    REGISTRATION_LAST_TIME = 3
    WAITING_EVENT_START = 4
    WAITING_EVENT_FINISH = 5
    AVAILABLE_PRIME_TIME = 6
    NOT_AVAILABLE_PRIME_TIME = 7
    LAST_AVAILABLE_PRIME_TIME = 8
    ADD_TEAM_EXTRA_POINTS = 9
    TEAM_REWARD = 10
    EVENT_FINISH = 11


ANNOUNCEMENT_PRIORITY = {AnnouncementType.REGISTRATION_BEFORE_EVENT_START: 1,
 AnnouncementType.REGISTRATION_AFTER_EVENT_START: 2,
 AnnouncementType.REGISTRATION_LAST_TIME: 1,
 AnnouncementType.WAITING_EVENT_START: 1,
 AnnouncementType.WAITING_EVENT_FINISH: 1,
 AnnouncementType.AVAILABLE_PRIME_TIME: 4,
 AnnouncementType.NOT_AVAILABLE_PRIME_TIME: 4,
 AnnouncementType.LAST_AVAILABLE_PRIME_TIME: 3,
 AnnouncementType.ADD_TEAM_EXTRA_POINTS: 2,
 AnnouncementType.TEAM_REWARD: 1,
 AnnouncementType.EVENT_FINISH: 1}
EntryPointData = namedtuple('EntryPointData', ('header', 'body', 'footer', 'state', 'deltaFunc'))
EntryPointData.__new__.__defaults__ = ('', '', '', '', None)
