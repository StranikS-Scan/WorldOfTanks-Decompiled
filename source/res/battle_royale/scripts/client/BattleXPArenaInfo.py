# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/BattleXPArenaInfo.py
import BigWorld

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
