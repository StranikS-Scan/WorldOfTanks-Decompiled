# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/VehicleSelfBuffComponent.py
from collections import namedtuple
import BigWorld
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE, FEEDBACK_EVENT_ID
from battle_royale.gui.constants import BattleRoyaleEquipments
from gui.Scaleform.genConsts.BATTLE_MARKER_STATES import BATTLE_MARKER_STATES
SelfBuffInfo = namedtuple('SelfBuffInfo', 'endTime')

class VehicleSelfBuffComponent(BigWorld.DynamicScriptComponent):
    __EQUIPMENT_NAME = BattleRoyaleEquipments.SELF_BUFF

    def __init__(self, *args):
        super(VehicleSelfBuffComponent, self).__init__()
        self.entity.guiSessionProvider.shared.vehicleState.onEquipmentComponentUpdated(self.__EQUIPMENT_NAME, self.entity.id, SelfBuffInfo(self.endTime))
        self.__updateState(self.__getInspireArgs())
        self.entity.guiSessionProvider.onUpdateObservedVehicleData += self.__onUpdateObservedVehicleData

    def set_endTime(self, prev):
        self.entity.guiSessionProvider.shared.vehicleState.onEquipmentComponentUpdated(self.__EQUIPMENT_NAME, self.entity.id, SelfBuffInfo(self.endTime))
        self.__updateState(self.__getInspireArgs())

    def onDestroy(self):
        self.entity.guiSessionProvider.onUpdateObservedVehicleData -= self.__onUpdateObservedVehicleData
        self.entity.guiSessionProvider.shared.vehicleState.onEquipmentComponentUpdated(self.__EQUIPMENT_NAME, self.entity.id, SelfBuffInfo(0.0))
        self.__updateState({'endTime': 0.0,
         'isInactivation': None,
         'isSourceVehicle': True,
         'duration': 0})
        return

    def __onUpdateObservedVehicleData(self, *args, **kwargs):
        self.__updateState(self.__getInspireArgs())

    def __updateState(self, inspireArgs):
        if self.entity.id == BigWorld.player().getObservedVehicleID():
            self.entity.guiSessionProvider.invalidateVehicleState(VEHICLE_VIEW_STATE.INSPIRE, inspireArgs)
            self.__updateMarker(0.0)
        else:
            ctrl = self.entity.guiSessionProvider.shared.feedback
            if ctrl is not None:
                ctrl.invalidateBuffEffect(FEEDBACK_EVENT_ID.VEHICLE_INSPIRE, self.entity.id, inspireArgs)
        return

    def __getInspireArgs(self):
        duration = self.endTime - BigWorld.serverTime()
        return {'endTime': self.endTime,
         'isInactivation': duration > 0,
         'isSourceVehicle': True,
         'duration': duration}

    def __updateMarker(self, elapsedTime):
        feedback = self.entity.guiSessionProvider.shared.feedback
        data = {'isShown': bool(elapsedTime),
         'isSourceVehicle': False,
         'duration': elapsedTime,
         'animated': True,
         'markerID': BATTLE_MARKER_STATES.INSPIRING_STATE}
        feedback.onVehicleFeedbackReceived(FEEDBACK_EVENT_ID.VEHICLE_CUSTOM_MARKER, self.entity.id, data)
