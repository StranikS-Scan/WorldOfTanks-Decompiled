# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/BattleFeedbackCommon.py
from constants import ATTACK_REASON, ATTACK_REASON_INDICES
BATTLE_EVENTS_PROCESSING_TIMEOUT = 0.2
CAPTURE_POINTS_TO_REPORT = 10
CAPTURE_BLOCKED_SESSION_TIMEOUT = 3
CAPTURE_BLOCKED_POINTS_TO_REPORT = 10
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
    ENEMY_SECTOR_CAPTURED = 13
    DESTRUCTIBLE_DAMAGED = 14
    DESTRUCTIBLE_DESTROYED = 15
    DESTRUCTIBLES_DEFENDED = 16
    DEFENDER_BONUS = 17
    SMOKE_ASSIST = 18
    INSPIRE_ASSIST = 19
    BASE_CAPTURE_BLOCKED = 20
    MULTI_STUN = 21
    DETECTED = 22
    EQUIPMENT_TIMER_EXPIRED = 23
    SUPPLY_DAMAGE = 24
    SUPPLY_DESTROYED = 25
    HIDE_IF_TARGET_INVISIBLE = (CRIT,
     DAMAGE,
     TRACK_ASSIST,
     STUN_ASSIST,
     RADIO_ASSIST,
     MULTI_STUN,
     SUPPLY_DAMAGE)
    DISCLOSED_ATTACK_REASON_IDS = (ATTACK_REASON_INDICES[ATTACK_REASON.MINEFIELD_EQ],)
    DAMAGE_EVENTS = frozenset([RADIO_ASSIST,
     TRACK_ASSIST,
     STUN_ASSIST,
     TANKING,
     DAMAGE,
     RECEIVED_DAMAGE,
     SMOKE_ASSIST,
     INSPIRE_ASSIST,
     SUPPLY_DAMAGE])
    CRITS_EVENTS = frozenset([CRIT, RECEIVED_CRIT])
    TARGET_EVENTS = frozenset([SPOTTED,
     KILL,
     DETECTED,
     SUPPLY_DESTROYED])
    POINTS_EVENTS = frozenset([BASE_CAPTURE_POINTS, BASE_CAPTURE_DROPPED, BASE_CAPTURE_BLOCKED])
    VISIBILITY_EVENTS = frozenset([TARGET_VISIBILITY])
    STUN_EVENTS = frozenset([MULTI_STUN])
    TARGET_POINTS_EVENTS = frozenset([DESTRUCTIBLE_DAMAGED,
     DESTRUCTIBLE_DESTROYED,
     DESTRUCTIBLES_DEFENDED,
     ENEMY_SECTOR_CAPTURED,
     DEFENDER_BONUS])
    EQUIPMENT_EVENTS = frozenset([EQUIPMENT_TIMER_EXPIRED])
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
     TARGET_VISIBILITY,
     ENEMY_SECTOR_CAPTURED,
     DESTRUCTIBLE_DAMAGED,
     DESTRUCTIBLE_DESTROYED,
     DESTRUCTIBLES_DEFENDED,
     DEFENDER_BONUS,
     SMOKE_ASSIST,
     INSPIRE_ASSIST,
     BASE_CAPTURE_BLOCKED,
     MULTI_STUN,
     DETECTED,
     EQUIPMENT_TIMER_EXPIRED,
     SUPPLY_DAMAGE,
     SUPPLY_DESTROYED])

    @staticmethod
    def packDamage(damage, attackReasonID, isBurst=False, shellTypeID=NONE_SHELL_TYPE, shellIsGold=False, secondaryAttackReasonID=ATTACK_REASON_INDICES[ATTACK_REASON.NONE], isRoleAction=False):
        return (int(damage) & 65535) << 25 | (int(attackReasonID) & 255) << 17 | (1 if isBurst else 0) << 16 | (int(shellTypeID) & 127) << 9 | (1 if shellIsGold else 0) << 8 | int(secondaryAttackReasonID) & 255 | (1 if isRoleAction else 0) << 41

    @staticmethod
    def unpackDamage(packedDamage):
        return (packedDamage >> 25 & 65535,
         packedDamage >> 17 & 255,
         packedDamage >> 16 & 1,
         packedDamage >> 9 & 127,
         packedDamage >> 8 & 1,
         packedDamage & 255,
         packedDamage >> 41 & 1)

    @staticmethod
    def unpackAttackReason(packedDamage):
        return packedDamage >> 17 & 255

    @staticmethod
    def packCrits(critsCount, attackReasonID, shellTypeID=NONE_SHELL_TYPE, shellIsGold=False, secondaryAttackReasonID=ATTACK_REASON_INDICES[ATTACK_REASON.NONE]):
        return (int(critsCount) & 65535) << 24 | (int(attackReasonID) & 255) << 16 | (int(shellTypeID) & 127) << 9 | (1 if shellIsGold else 0) << 8 | int(secondaryAttackReasonID) & 255

    @staticmethod
    def unpackCrits(packedCrits):
        return (packedCrits >> 24 & 65535,
         packedCrits >> 16 & 255,
         packedCrits >> 9 & 127,
         packedCrits >> 8 & 1,
         packedCrits & 255)

    @staticmethod
    def packVisibility(isVisible, isDirect, isRoleAction):
        return (1 if isVisible else 0) | (2 if isDirect else 0) | (4 if isRoleAction else 0)

    @staticmethod
    def unpackVisibility(packedVisibility):
        return (packedVisibility & 1, packedVisibility & 2, packedVisibility & 4)
