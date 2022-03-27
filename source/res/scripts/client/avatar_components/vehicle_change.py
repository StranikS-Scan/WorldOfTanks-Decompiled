# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/avatar_components/vehicle_change.py
import BigWorld
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider

class VehicleChangeComponent(object):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    @property
    def currentVehicleID(self):
        ctrl = self.__getCtrl()
        if ctrl is None:
            if BigWorld.player():
                return BigWorld.player().playerVehicleID
            return
        else:
            return ctrl.currentVehicleID

    def onBecomePlayer(self):
        pass

    def onBecomeNonPlayer(self):
        pass

    def handleKey(self, isDown, key, mods):
        ctrl = self.__getCtrl()
        return False if ctrl is None else ctrl.handleKeyEvent(isDown, key, mods)

    def startVehicleControl(self, vehicleID):
        self.base.requestControlledVehicleState()

    def startVehicleControlAttempt(self, vehicleID):
        self.base.startVehicleControl(vehicleID)

    def stopVehicleControlAttempt(self):
        self.base.stopVehicleControl()

    def onStartVehicleControlFailed(self):
        ctrl = self.__getCtrl()
        if ctrl is not None:
            ctrl.onVehicleChangeFailed()
        return

    def stopVehicleControl(self):
        ctrl = self.__getCtrl()
        if ctrl is None:
            return
        else:
            ctrl.stopVehicleControl()
            return

    def canChangeVehicle(self):
        ctrl = self.__getCtrl()
        return True if ctrl is None else ctrl.canChangeVehicle(self.vehicle)

    def onVehicleChanged(self):
        vehicle = self.vehicle
        if vehicle is None:
            return
        else:
            ctrl = self.__getCtrl()
            if ctrl is not None:
                ctrl.onVehicleChanged(vehicle.id)
            return

    def isControlVehicleChanging(self):
        ctrl = self.__getCtrl()
        return False if ctrl is None else ctrl.isVehicleChanging

    def __getCtrl(self):
        return self.__sessionProvider.dynamic.vehicleChange
