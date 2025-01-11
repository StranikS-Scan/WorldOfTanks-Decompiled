# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/bob/bob_constants.py
from collections import namedtuple
from shared_utils import CONST_CONTAINER
BOB_TOKEN_PREFIX = 'bob4:'
BOB_TOKENS_DELIMITER = ':'
BOB_TEAM_ID_POS = 2

class AnnouncementType(CONST_CONTAINER):
    UNKNOWN = 0
    BEFORE_EVENT_START = 1
    PAUSED = 1
    REGISTRATION_AFTER_EVENT_START = 2
    AVAILABLE_PRIME_TIME = 3
    NOT_AVAILABLE_PRIME_TIME = 4
    EVENT_FINISH = 5


ANNOUNCEMENT_PRIORITY = {AnnouncementType.PAUSED: 0,
 AnnouncementType.BEFORE_EVENT_START: 1,
 AnnouncementType.REGISTRATION_AFTER_EVENT_START: 2,
 AnnouncementType.AVAILABLE_PRIME_TIME: 4,
 AnnouncementType.NOT_AVAILABLE_PRIME_TIME: 4,
 AnnouncementType.EVENT_FINISH: 1}
EntryPointData = namedtuple('EntryPointData', ('header', 'body', 'footer', 'state', 'deltaFunc'))
EntryPointData.__new__.__defaults__ = ('', '', '', '', None)
BOB_SEASON_MODIFIERS_DOMAIN = 'bobSeasonModifiers'
