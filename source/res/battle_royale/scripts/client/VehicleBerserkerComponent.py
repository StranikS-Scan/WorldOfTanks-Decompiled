# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/VehicleBerserkerComponent.py
import BigWorld
from battle_royale.gui.constants import BattleRoyaleEquipments
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE, FEEDBACK_EVENT_ID
from gui.Scaleform.genConsts.BATTLE_MARKER_STATES import BATTLE_MARKER_STATES

class VehicleBerserkerComponent(BigWorld.DynamicScriptComponent):
    __EQUIPMENT_NAME = BattleRoyaleEquipments.BERSERKER

    def __init__(self, *args):
        super(VehicleBerserkerComponent, self).__init__()
        self.__subscribeEvents()
        self.__updateVisuals()

    def set_endTime(self, prev):
        self.__updateVisuals()

    def onLeaveWorld(self, *args):
        self.__destroy()

    def onDestroy(self):
        self.__destroy()

    def __destroy(self):
        self.__unSubscribeEvents()
        self.__elapsedTime = 0.0
        if self.entity.id == BigWorld.player().getObservedVehicleID():
            self.__hideTimer()
        self.__updateMarker(self.__elapsedTime)

    def __subscribeEvents(self):
        self.entity.guiSessionProvider.onUpdateObservedVehicleData += self.__onUpdateObservedVehicleData
        player = BigWorld.player()
        if player is not None and player.inputHandler is not None:
            player.inputHandler.onCameraChanged += self.__onCameraChanged
        return

    def __unSubscribeEvents(self):
        self.entity.guiSessionProvider.onUpdateObservedVehicleData -= self.__onUpdateObservedVehicleData
        player = BigWorld.player()
        if player is not None and player.inputHandler is not None:
            player.inputHandler.onCameraChanged -= self.__onCameraChanged
        return

    def __updateVisuals(self):
        self.__elapsedTime = max(self.endTime - BigWorld.serverTime(), 0.0)
        self.entity.guiSessionProvider.shared.vehicleState.onEquipmentComponentUpdated(self.__EQUIPMENT_NAME, self.entity.id, self.__getData())
        if self.entity.id == BigWorld.player().getObservedVehicleID():
            self.__showTimer()
        else:
            self.__updateMarker(self.__elapsedTime)

    def __showTimer(self):
        self.entity.guiSessionProvider.invalidateVehicleState(VEHICLE_VIEW_STATE.BERSERKER, self.__getData())
        self.__updateMarker(0.0)

    def __hideTimer(self):
        self.entity.guiSessionProvider.invalidateVehicleState(VEHICLE_VIEW_STATE.BERSERKER, self.__getData(isReset=True))

    def __updateMarker(self, elapsedTime):
        feedback = self.entity.guiSessionProvider.shared.feedback
        data = {'isShown': bool(elapsedTime),
         'isSourceVehicle': False,
         'duration': elapsedTime,
         'animated': True,
         'markerID': BATTLE_MARKER_STATES.BERSERKER_STATE}
        feedback.onVehicleFeedbackReceived(FEEDBACK_EVENT_ID.VEHICLE_CUSTOM_MARKER, self.entity.id, data)

    def __onUpdateObservedVehicleData(self, *args, **kwargs):
        self.__updateVisuals()

    def __getData(self, isReset=False):
        elapsed = max(self.endTime - BigWorld.serverTime(), 0.0) if not isReset else 0.0
        endTime = self.endTime if not isReset else BigWorld.serverTime()
        data = {'duration': elapsed,
         'endTime': endTime,
         'tickInterval': self.tickInterval}
        return data

    def __onCameraChanged(self, cameraName, currentVehicleId=None):
        if cameraName == 'video':
            self.__elapsedTime = max(self.endTime - BigWorld.serverTime(), 0.0)
            self.__updateMarker(self.__elapsedTime)
