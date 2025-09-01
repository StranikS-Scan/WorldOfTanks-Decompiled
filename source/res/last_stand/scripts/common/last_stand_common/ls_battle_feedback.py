# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/common/last_stand_common/ls_battle_feedback.py
from collections import namedtuple
LSGameplayAction = namedtuple('LSGameplayAction', ('value', 'targetID', 'id'))

class LSGameplayActionID(object):
    UNKNOWN = 0
    VEHICLE_REPAIR_INCOMING = 1
    VEHICLE_REPAIR_OUTCOMING = 2
    MODULES_DAMAGE_BLOCKED = 3
    HEALTH_DRAINED_BY_PASSIVE_VAMPIRE = 4
    EQUIPMENT_ACTIVATED = 5
    HEAL_BY_SELF_SITUATIONAL = 6


def packGameplayActionFeedback(action):
    return (int(action.targetID) & 4294967295L) << 32 | (int(action.value) & 65535) << 16 | action.id & 65535


def unpackGameplayActionFeedback(packedData):
    return LSGameplayAction(targetID=packedData >> 32 & 4294967295L, value=packedData >> 16 & 65535, id=packedData & 65535)
