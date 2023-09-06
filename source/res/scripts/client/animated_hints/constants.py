# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/animated_hints/constants.py
import enum

class HintType(enum.IntEnum):
    Move = 1
    MoveTurret = 2
    Shoot = 3
    SniperOnDistance = 4
    SniperLevel0 = 5
    AdvancedSniper = 6
    WeakPoints = 7
    TargetLock = 8


class EventAction(enum.IntEnum):
    Show = 1
    Hide = 2
    Complete = 3
    Close = 4
    SetPenetration = 5


LOGGER_NAME = 'animated_hints'
