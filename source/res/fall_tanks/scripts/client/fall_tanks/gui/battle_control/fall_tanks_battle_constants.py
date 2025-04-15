# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fall_tanks/scripts/client/fall_tanks/gui/battle_control/fall_tanks_battle_constants.py
from constants_utils import ConstInjector
from gui.battle_control import battle_constants
LAST_WIN_POSITION = 3

class VEHICLE_VIEW_STATE(battle_constants.VEHICLE_VIEW_STATE, ConstInjector):
    VEHICLE_EVACUATION = 19342813113834066795298816L


class WinStatus(battle_constants.WinStatus):

    @classmethod
    def fromPlayerPosition(cls, position, isFinished):
        if not isFinished:
            status = cls.LOSE
        elif 0 < position <= LAST_WIN_POSITION:
            status = cls.WIN
        else:
            status = cls.DRAW
        return cls(status=status)


def injectConsts(personality):
    VEHICLE_VIEW_STATE.inject(personality)
