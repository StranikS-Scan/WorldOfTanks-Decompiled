# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/common/halloween_common/hw_battle_feedback.py


class HWGameplayActionID(object):
    VEHICLE_REPAIR = 0


def packGameplayActionFeedback(vehID, effectValue, actionID):
    return (int(vehID) & 65535) << 24 | (int(effectValue) & 4095) << 12 | actionID & 255


def unpackGameplayActionFeedback(packedData):
    return (packedData >> 24 & 65535, packedData >> 12 & 4095, packedData & 255)
