# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fall_tanks/scripts/client/FallTanksArenaInfo.py
import math
import BigWorld
from gui.battle_control import avatar_getter
from fall_tanks.gui.battle_control.arena_info.arena_vos import FallTanksKeys

class FallTanksArenaInfo(BigWorld.DynamicScriptComponent):

    def __init__(self):
        self.__updateGameModeStats()

    def set_checkpoints(self, _=None):
        self.__updateGameModeStats()

    def set_positions(self, _=None):
        self.__updateGameModeStats()

    def set_finishTimes(self, _=None):
        self.__updateGameModeStats()

    def __updateGameModeStats(self):
        arena = avatar_getter.getArena()
        if arena is None:
            return
        else:
            stats = {vID:{FallTanksKeys.CHECKPOINT: checkpoint,
             FallTanksKeys.RACE_POSITION: position,
             FallTanksKeys.FINISH_TIME: max(finishTime, 0.0),
             FallTanksKeys.IS_LEAVER: math.copysign(1.0, finishTime) < 0.0} for vID, checkpoint, position, finishTime in zip(self.vehicleIDsOrder, self.checkpoints, self.positions, self.finishTimes)}
            arena.updateGameModeSpecificStats(isStatic=False, stats=stats)
            return
