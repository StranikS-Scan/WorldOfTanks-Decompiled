# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/bootcamp_shared.py


class BOOTCAMP_BATTLE_ACTION(object):
    PLAYER_MOVE = 0
    PLAYER_SHOOT = 1
    PLAYER_SPOTTED = 2
    PLAYER_HIT_VEHICLE = 3
    PLAYER_OBSERVED_ACTION = 4
    SET_SCENERY_CONSTANT = 5


class BOOTCAMP_START_TYPE(object):
    AUTOMATICALLY = 0
    PLAYER_CHOICE = 1
    PLAYER_MANUAL = 2


class PLAYER_COHORT_TYPE(object):
    NEW_PLAYER = 0
    WOT_RETURN_PLAYER = 1
    WOT_PLAYER = 2
