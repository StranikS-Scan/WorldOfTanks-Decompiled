# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/VehicleCorrodingShotComponent.py
import BigWorld
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE
from script_component.DynamicScriptComponent import DynamicScriptComponent

class VehicleCorrodingShotComponent(DynamicScriptComponent):

    def __init__(self, *args):
        super(VehicleCorrodingShotComponent, self).__init__()
        self.__updateTimer()
        self.__subscribeEvents()

    def _onAvatarReady(self):
        self.set_finishTime()

    def set_finishTime(self, _=None):
        self.__updateTimer()

    def onDestroy(self):
        self.__unSubscribeEvents()
        if self.entity.id == BigWorld.player().getObservedVehicleID():
            self.__updateTimer(isShow=False)

    def __subscribeEvents(self):
        self.entity.guiSessionProvider.onUpdateObservedVehicleData += self.__onUpdateObservedVehicleData

    def __unSubscribeEvents(self):
        self.entity.guiSessionProvider.onUpdateObservedVehicleData -= self.__onUpdateObservedVehicleData

    def __onUpdateObservedVehicleData(self, *args, **kwargs):
        self.__updateTimer()

    def __updateTimer(self, isShow=True):
        if self.entity.id == BigWorld.player().getObservedVehicleID():
            elapsedTime = max(self.finishTime - BigWorld.serverTime(), 0.0) if isShow else 0.0
            self.entity.guiSessionProvider.invalidateVehicleState(VEHICLE_VIEW_STATE.CORRODING_SHOT, elapsedTime)
