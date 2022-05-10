# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/VehicleHealingComponent.py
import BigWorld
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE, FEEDBACK_EVENT_ID

class VehicleHealingComponent(BigWorld.DynamicScriptComponent):

    def __init__(self, *args):
        super(VehicleHealingComponent, self).__init__()
        self.__updateState(self.__getHealingArgs())
        self.entity.guiSessionProvider.onUpdateObservedVehicleData += self.__onUpdateObservedVehicleData

    def set_endTime(self, prev):
        self.__updateState(self.__getHealingArgs())

    def set_isInactivation(self, prev):
        self.__updateState(self.__getHealingArgs())

    def onDestroy(self):
        self.entity.guiSessionProvider.onUpdateObservedVehicleData -= self.__onUpdateObservedVehicleData
        self.__updateState({key:None for key in ('isSourceVehicle', 'isInactivation', 'endTime', 'duration', 'senderKey')})

    def __updateState(self, healingArgs):
        if BigWorld.player().getObservedVehicleID() == self.entity.id:
            self.entity.guiSessionProvider.invalidateVehicleState(VEHICLE_VIEW_STATE.HEALING, healingArgs)
        else:
            ctrl = self.entity.guiSessionProvider.shared.feedback
            if ctrl is not None:
                ctrl.invalidateBuffEffect(FEEDBACK_EVENT_ID.VEHICLE_HEAL_POINT, self.entity.id, healingArgs)
        return

    def __getHealingArgs(self):
        return {'isSourceVehicle': self.isSourceVehicle,
         'isInactivation': self.isInactivation,
         'endTime': self.endTime,
         'duration': round(self.endTime - BigWorld.serverTime()),
         'senderKey': None}

    def __onUpdateObservedVehicleData(self, *args, **kwargs):
        self.__updateState(self.__getHealingArgs())
