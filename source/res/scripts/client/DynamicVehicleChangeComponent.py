# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/DynamicVehicleChangeComponent.py
import BigWorld
import aih_constants
from Event import Event
from arena_bonus_type_caps import ARENA_BONUS_TYPE_CAPS
from helpers import dependency
from script_component.ScriptComponent import ScriptComponent
from skeletons.gui.battle_session import IBattleSessionProvider

class DynamicVehicleChangeComponent(ScriptComponent):
    REQUIRED_BONUS_CAP = ARENA_BONUS_TYPE_CAPS.DYNAMIC_VEHICLE_CHANGE
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    _DEFAULT_ARCADE_CAMERA_DISTANCE = 15

    def __init__(self):
        super(DynamicVehicleChangeComponent, self).__init__()
        self.onStartVehicleControl = Event()
        self.onStopVehicleControl = Event()

    def isActive(self):
        return ARENA_BONUS_TYPE_CAPS.checkAny(self.entity.arenaBonusType, self.REQUIRED_BONUS_CAP)

    def onOriginalVehicleDeath(self):
        self.__onVehicleChanged(self.originalVehicleID)

    def set_newVehicleID(self, prev):
        self.entity.onVehicleChangeFinished += self.__onVehicleChanged

    @property
    def avatar(self):
        return self.entity

    def __onVehicleChanged(self, vehicleID):
        if not self.isActive():
            return
        else:
            newVehicle = BigWorld.entity(vehicleID)
            if newVehicle is None:
                return
            originalVehicle = BigWorld.entity(self.originalVehicleID)
            if not originalVehicle.isAlive():
                self.avatar.inputHandler.onControlModeChanged(aih_constants.CTRL_MODE_NAME.POSTMORTEM)
                self.__sessionProvider.shared.viewPoints.selectVehicle(self.originalVehicleID)
            else:
                self.__changeControlMode(aih_constants.CTRL_MODE_NAME.ARCADE)
            oldVehicle = BigWorld.entity(self.oldVehicleID)
            if oldVehicle is not None:
                oldVehicle.isPlayerVehicle = False
                self.__sessionProvider.startVehicleVisual(oldVehicle, True)
                oldVehicle.show(True)
                oldVehicle.targetCaps = [1]
                oldVehicle.appearance.highlighter.setVehicleOwnership()
            gunRotator = self.avatar.gunRotator
            if gunRotator is not None:
                gunRotator.clientMode = True
                gunRotator.stop()
                gunRotator.reset()
            BigWorld.player().autoAim(None)
            self.entity._PlayerAvatar__deviceStates = {}
            self.__sessionProvider.shared.vehicleState.switchToOther(None)
            newVehicle.isPlayerVehicle = True
            self.__sessionProvider.switchVehicle(vehicleID)
            self.__sessionProvider.stopVehicleVisual(vehicleID, False)
            self.avatar.updateObservedVehicleData()
            self.avatar.vehicleTypeDescriptor = newVehicle.typeDescriptor
            newVehicle.targetCaps = [0]
            newVehicle.appearance.highlighter.setVehicleOwnership()
            self.__onStartVehicleControlSuccess(vehicleID)
            return

    def __onStartVehicleControlSuccess(self, vehicleID):
        vehicle = BigWorld.entity(vehicleID)
        if vehicle is None:
            return
        else:
            vehicle.resetProperties()
            if hasattr(vehicle.filter, 'enableStabilisedMatrix'):
                vehicle.filter.enableStabilisedMatrix(True)
            if self.isControllingVehicle:
                self.__currentControlledVehicleID = vehicleID
                self.onStartVehicleControl(vehicleID)
                self.__sessionProvider.shared.vehicleState.setPossessedVehicleID(vehicleID)
            else:
                self.__currentControlledVehicleID = self.originalVehicleID
                self.onStopVehicleControl(self.isControlInterrupted)
                self.__sessionProvider.shared.vehicleState.setPossessedVehicleID(None)
            self.__sessionProvider.shared.vehicleState.switchToOther(vehicleID)
            self.entity.onVehicleChangeFinished -= self.__onVehicleChanged
            return

    def __changeControlMode(self, ctrlModeName, **kwargs):
        if self.avatar.inputHandler is not None:
            self.avatar.inputHandler.onCameraChanged += self.__onCameraChanged
            self.avatar.inputHandler.onControlModeChanged(ctrlModeName, **kwargs)
            self.avatar.inputHandler.refreshGunMarkers()
        return

    def __onCameraChanged(self, eMode, _=None):
        if eMode == aih_constants.CTRL_MODE_NAME.ARCADE:
            self.avatar.inputHandler.ctrl.camera.setCameraDistance(self._DEFAULT_ARCADE_CAMERA_DISTANCE)
            self.avatar.inputHandler.onCameraChanged -= self.__onCameraChanged
