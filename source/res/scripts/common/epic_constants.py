# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/epic_constants.py
from constants import IS_CLIENT

class EPIC_BATTLE_TEAM_ID(object):
    TEAM_ATTACKER = 1
    TEAM_DEFENDER = 2


class IN_BATTLE_RESERVE_EVENTS:
    PASS = 0
    SLOT_EVENT = 1
    NAMES = {PASS: 'pass',
     SLOT_EVENT: 'slotEvent'}
    EVENT_BY_NAME = {d:k for k, d in NAMES.iteritems()}

    class SLOT_EVENT_ACTIONS:
        UNLOCKED = 0
        UPGRADED = 1
        NAMES = {UNLOCKED: 'unlocked',
         UPGRADED: 'upgraded'}
        EVENT_BY_NAME = {d:k for k, d in NAMES.iteritems()}


if IS_CLIENT:
    from shared_utils import CONST_CONTAINER

    class SECTOR_EDGE_STATE(CONST_CONTAINER):
        NONE = 0
        SAFE = 1
        DANGER = 2
