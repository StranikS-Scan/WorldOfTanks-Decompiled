# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/HWVehiclesPositionArenaInfo.py
import BigWorld
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider

class HWVehiclesPositionArenaInfo(BigWorld.DynamicScriptComponent):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def onEnterWorld(self):
        self._setVehiclesPositionParams()

    def onLeaveWorld(self):
        pass

    def set_vehiclesPositionParams(self, _):
        self._setVehiclesPositionParams()

    def _setVehiclesPositionParams(self):
        vehiclesPositionCtrl = self.sessionProvider.dynamic.vehiclesPositionCtrl
        if self.vehiclesPositionParams is not None and vehiclesPositionCtrl:
            vehiclesPositionCtrl.setPositionParams(self.vehiclesPositionParams)
        return
