# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/avatar_components/event_abilities_controller.py
from constants import ARENA_BONUS_TYPE
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE

class EventAbilitiesController(object):

    def __init__(self):
        self.__enabled = False

    def handleKey(self, isDown, key, mods):
        pass

    def onBecomePlayer(self):
        self.__enabled = self.arenaBonusType == ARENA_BONUS_TYPE.EVENT_BATTLES

    def onBecomeNonPlayer(self):
        self.__enabled = False

    def setLastStandActive(self, isStarted, destructionDelay):
        if not self.__enabled:
            return
        if isStarted:
            data = {'destructionDelay': destructionDelay}
            self.guiSessionProvider.invalidateVehicleState(VEHICLE_VIEW_STATE.LAST_STAND, data)

    def displayLastStandOnVehicle(self, isStarted, vehID):
        if not self.__enabled:
            return
        else:
            ctrl = self.guiSessionProvider.shared.feedback
            if isStarted and ctrl is not None:
                ctrl.setVehicleNewHealth(vehID, 0)
            fireExtra = self.vehicleTypeDescriptor.extrasDict['fire']
            for vehicle in self.vehicles:
                if vehicle.id == vehID and fireExtra:
                    if isStarted:
                        fireExtra.startFor(vehicle)
                    elif not isStarted:
                        fireExtra.stopFor(vehicle)

            return
