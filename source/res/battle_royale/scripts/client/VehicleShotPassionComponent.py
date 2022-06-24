# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/VehicleShotPassionComponent.py
from collections import namedtuple
import BigWorld
from battle_royale.gui.constants import BattleRoyaleEquipments
from Event import EventsSubscriber
from gui.battle_control.battle_constants import FEEDBACK_EVENT_ID
from gui.Scaleform.genConsts.BATTLE_MARKER_STATES import BATTLE_MARKER_STATES
ShotPassionInfo = namedtuple('ShotPassionInfo', ('endTime', 'stage'))

class VehicleShotPassionComponent(BigWorld.DynamicScriptComponent):
    EQUIPMENT_NAME = BattleRoyaleEquipments.SHOT_PASSION

    def __init__(self, *args):
        super(VehicleShotPassionComponent, self).__init__()
        self.__es = EventsSubscriber()
        self.__onUpdated()
        self.__es.subscribeToEvent(self.entity.guiSessionProvider.onUpdateObservedVehicleData, self.__onUpdateObservedVehicleData)
        player = BigWorld.player()
        if player is not None and player.inputHandler is not None:
            self.__es.subscribeToEvent(player.inputHandler.onCameraChanged, self.__onCameraChanged)
        return

    def getInfo(self):
        return ShotPassionInfo(self.endTime, self.stage)

    def set_endTime(self, prev):
        self.__onUpdated()

    def set_stage(self, prev):
        self.__onUpdated()

    def onDestroy(self):
        self.__destroy()

    def onLeaveWorld(self, *args):
        self.__destroy()

    def __destroy(self):
        self.__onUpdated(ShotPassionInfo(0.0, 0))
        self.__es.unsubscribeFromAllEvents()
        self.__es = None
        return

    def __onUpdateObservedVehicleData(self, *args, **kwargs):
        self.__onUpdated()

    def __onUpdated(self, info=None):
        self.entity.guiSessionProvider.shared.vehicleState.onEquipmentComponentUpdated(self.EQUIPMENT_NAME, self.entity.id, info or self.getInfo())

    def __onCameraChanged(self, cameraName, currentVehicleId=None):
        if cameraName == 'video':
            self.__elapsedTime = max(self.endTime - BigWorld.serverTime(), 0.0)
            self.__updateMarker(self.__elapsedTime)

    def __updateMarker(self, elapsedTime):
        feedback = self.entity.guiSessionProvider.shared.feedback
        data = {'isShown': bool(elapsedTime),
         'isSourceVehicle': False,
         'duration': elapsedTime,
         'animated': True,
         'markerID': BATTLE_MARKER_STATES.SHOT_PASSION_STATE}
        feedback.onVehicleFeedbackReceived(FEEDBACK_EVENT_ID.VEHICLE_CUSTOM_MARKER, self.entity.id, data)
