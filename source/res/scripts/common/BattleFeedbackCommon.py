# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/BattleFeedbackCommon.py
BATTLE_EVENTS_PROCESSING_TIMEOUT = 0.2
CAPTURE_POINTS_TO_REPORT = 10

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
    HIDE_IF_TARGET_INVISIBLE = (CRIT, DAMAGE)
    DAMAGE_EVENTS = frozenset([RADIO_ASSIST,
     TRACK_ASSIST,
     TANKING,
     DAMAGE])
    TARGET_EVENTS = frozenset([SPOTTED, CRIT, KILL])
    POINTS_EVENTS = frozenset([BASE_CAPTURE_POINTS, BASE_CAPTURE_DROPPED])
    ALL = frozenset([SPOTTED,
     RADIO_ASSIST,
     TRACK_ASSIST,
     BASE_CAPTURE_POINTS,
     BASE_CAPTURE_DROPPED,
     TANKING,
     CRIT,
     DAMAGE,
     KILL])
    assert ALL == DAMAGE_EVENTS | TARGET_EVENTS | POINTS_EVENTS

    @staticmethod
    def packDamage(damage, attackReasonID, isBurst=False):
        """
        Pack information about damage into 32 bits.
        [ 32 - 9 |      8 - 2       |       1       ]
        [ damage | attack reason id | is burst flag ]
        
        @param damage: value of damage
        @param attackReasonID: attack reason id. See ATTACK_REASON_INDICES
        @param isBurst: flag if damage has been made in burst of shots.
        @return: packed damage.
        """
        return (int(damage) & 16777215) << 8 | (int(attackReasonID) & 127) << 1 | (1 if isBurst else 0)

    @staticmethod
    def unpackDamage(packedDamage):
        """
        Unpack damage information that has been packed with packDamage.
        @param packedDamage: packed damage information.
        @return: tuple(damage, attackReasonID, isBurst)
        """
        return (packedDamage >> 8 & 16777215, packedDamage >> 1 & 127, packedDamage & 1)
