# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/BattleXPArenaInfo.py
import BigWorld
from debug_utils import LOG_WARNING
from shared_utils import nextTick
from AvatarInputHandler.control_modes import ArcadeControlMode

class BattleXPArenaInfo(BigWorld.DynamicScriptComponent):

    def __init__(self):
        self.__setAverageLevel()

    def set_vehiclesAverageBattleLevel(self, _):
        self.__setAverageLevel()

    def __setAverageLevel(self):
        progressionCtrl = self.entity.sessionProvider.dynamic.progression
        if progressionCtrl is not None:
            progressionCtrl.setAverageBattleLevel(self.vehiclesAverageBattleLevel)
        return
