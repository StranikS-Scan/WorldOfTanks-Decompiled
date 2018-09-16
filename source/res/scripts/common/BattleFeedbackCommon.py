# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/BattleFeedbackCommon.py
BATTLE_EVENTS_PROCESSING_TIMEOUT = 0.2
CAPTURE_POINTS_TO_REPORT = 10
NONE_SHELL_TYPE = 127

class BATTLE_EVENT_TYPE:
    SPOTTED = 0
    RADIO_ASSIST = 1
    TRACK_ASSIST = 2
    BASE_CAPTURE_POINTS = 3
    BASE_CAPTURE_DROPPED = 4
    TANKING = 5
    CRIT = 6
    DAMAGE = 7
    KILL = 8
    RECEIVED_CRIT = 9
    RECEIVED_DAMAGE = 10
    STUN_ASSIST = 11
    TARGET_VISIBILITY = 12
    HIDE_IF_TARGET_INVISIBLE = (CRIT, DAMAGE)
    DAMAGE_EVENTS = frozenset([RADIO_ASSIST,
     TRACK_ASSIST,
     STUN_ASSIST,
     TANKING,
     DAMAGE,
     RECEIVED_DAMAGE])
    CRITS_EVENTS = frozenset([CRIT, RECEIVED_CRIT])
    TARGET_EVENTS = frozenset([SPOTTED, KILL])
    POINTS_EVENTS = frozenset([BASE_CAPTURE_POINTS, BASE_CAPTURE_DROPPED])
    VISIBILITY_EVENTS = frozenset([TARGET_VISIBILITY])
    ALL = frozenset([SPOTTED,
     RADIO_ASSIST,
     TRACK_ASSIST,
     STUN_ASSIST,
     BASE_CAPTURE_POINTS,
     BASE_CAPTURE_DROPPED,
     TANKING,
     CRIT,
     DAMAGE,
     KILL,
     RECEIVED_CRIT,
     RECEIVED_DAMAGE,
     TARGET_VISIBILITY])

    @staticmethod
    def packDamage(damage, attackReasonID, isBurst=False, shellTypeID=NONE_SHELL_TYPE, shellIsGold=False):
        return (int(damage) & 65535) << 16 | (int(attackReasonID) & 127) << 9 | (1 if isBurst else 0) << 8 | (int(shellTypeID) & 127) << 1 | (1 if shellIsGold else 0)

    @staticmethod
    def unpackDamage(packedDamage):
        return (packedDamage >> 16 & 65535,
         packedDamage >> 9 & 127,
         packedDamage >> 8 & 1,
         packedDamage >> 1 & 127,
         packedDamage & 1)

    @staticmethod
    def packCrits(critsCount, attackReasonID, shellTypeID=NONE_SHELL_TYPE, shellIsGold=False):
        return (int(critsCount) & 65535) << 16 | (int(attackReasonID) & 255) << 8 | (int(shellTypeID) & 127) << 1 | (1 if shellIsGold else 0)

    @staticmethod
    def unpackCrits(packedCrits):
        return (packedCrits >> 16 & 65535,
         packedCrits >> 8 & 255,
         packedCrits >> 1 & 127,
         packedCrits & 1)

    @staticmethod
    def packVisibility(isVisible, isDirect):
        return (1 if isVisible else 0) | (2 if isDirect else 0)

    @staticmethod
    def unpackVisibility(packedVisibility):
        return (packedVisibility & 1, packedVisibility & 2)
