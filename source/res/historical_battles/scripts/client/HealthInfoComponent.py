# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/HealthInfoComponent.py
import BigWorld
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider

class HealthInfoComponent(BigWorld.DynamicScriptComponent):
    _sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def set_healthInfo(self, prev):
        battleField = self._sessionProvider.dynamic.battleField
        if self.healthInfo and battleField:
            for info in self.healthInfo:
                battleField.setVehicleHealth(info.vehicleID, info.health)
