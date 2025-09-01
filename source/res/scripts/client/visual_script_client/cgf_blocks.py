# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/visual_script_client/cgf_blocks.py
import logging
import typing
import weakref
import BigWorld
from constants import IS_VS_EDITOR, ROCKET_ACCELERATION_STATE
from debug_utils import LOG_WARNING
from visual_script.block import Block
from visual_script.slot_types import SLOT_TYPE
from visual_script.misc import ASPECT, errorVScript
from visual_script.dependency import dependencyImporter
from visual_script.contexts.cgf_context import GameObjectWrapper
from visual_script.cgf_blocks import CGFMeta
Vehicle, CGF, tankStructure, RAC, SimulatedVehicle, cgf_helpers, battle_constants = dependencyImporter('Vehicle', 'CGF', 'vehicle_systems.tankStructure', 'cgf_components.rocket_acceleration_component', 'SimulatedVehicle', 'cgf_common.cgf_helpers', 'gui.battle_control.battle_constants')
if not IS_VS_EDITOR:
    from gui.battle_control.controllers.vehicle_passenger import hasVehiclePassengerCtrl, VehiclePassengerInfoWatcher
else:

    def hasVehiclePassengerCtrl(*_, **__):
        return lambda method: method


    class VehiclePassengerInfoWatcher(object):
        pass


if typing.TYPE_CHECKING:
    from gui.battle_control.controllers.vehicle_passenger import IVehiclePassengerController
_logger = logging.getLogger(__name__)

class CGFClientMeta(CGFMeta):

    @classmethod
    def blockAspects(cls):
        return [ASPECT.CLIENT, ASPECT.HANGAR]


class GetVehicleAppearanceGameObject(Block, CGFClientMeta):

    def __init__(self, *args, **kwargs):
        super(GetVehicleAppearanceGameObject, self).__init__(*args, **kwargs)
        self._object = self._makeDataInputSlot('gameObject', SLOT_TYPE.GAME_OBJECT)
        self._appObject = self._makeDataOutputSlot('appearanceObject', SLOT_TYPE.GAME_OBJECT, self._exec)

    def validate(self):
        return 'GameObject is required' if not self._object.hasValue() else super(GetVehicleAppearanceGameObject, self).validate()

    def _exec(self):
        currentGO = self._object.getValue()
        hierarchy = CGF.HierarchyManager(currentGO.spaceID)
        topGO = hierarchy.getTopMostParent(currentGO)
        currentGO = hierarchy.findFirstNode(topGO, tankStructure.CgfTankNodes.TANK_ROOT)
        if currentGO is not None:
            goWrapper = GameObjectWrapper(currentGO)
            self._appObject.setValue(weakref.proxy(goWrapper))
        else:
            self._appObject.setValue(None)
        return


class GetVehicleGameObject(Block, CGFClientMeta):

    def __init__(self, *args, **kwargs):
        super(GetVehicleGameObject, self).__init__(*args, **kwargs)
        self._object = self._makeDataInputSlot('gameObject', SLOT_TYPE.GAME_OBJECT)
        self._vehicleObject = self._makeDataOutputSlot('vehicleObject', SLOT_TYPE.GAME_OBJECT, self._exec)

    def validate(self):
        return 'GameObject is required' if not self._object.hasValue() else super(GetVehicleGameObject, self).validate()

    def _exec(self):
        currentGO = self._object.getValue()
        hierarchy = CGF.HierarchyManager(currentGO.spaceID)
        topGO = hierarchy.getTopMostParent(currentGO)
        isVehicle = topGO.findComponentByType(Vehicle.Vehicle) is not None
        if not isVehicle:
            isVehicle = topGO.findComponentByType(SimulatedVehicle.SimulatedVehicle) is not None
        if isVehicle:
            goWrapper = GameObjectWrapper(topGO)
            self._vehicleObject.setValue(weakref.proxy(goWrapper))
        else:
            self._vehicleObject.setValue(None)
        return


class RocketAcceleratorEvents(Block, CGFClientMeta):

    def __init__(self, *args, **kwargs):
        super(RocketAcceleratorEvents, self).__init__(*args, **kwargs)
        self._activate = self._makeEventInputSlot('activate', self.__activate)
        self._deactivate = self._makeEventInputSlot('deactivate', self.__deactivate)
        self._object = self._makeDataInputSlot('vehicleObject', SLOT_TYPE.GAME_OBJECT)
        self._activateOut = self._makeEventOutputSlot('activateOut')
        self._deactivateOut = self._makeEventOutputSlot('deactivateOut')
        self._failure = self._makeEventOutputSlot('failure')
        self._deploying = self._makeEventOutputSlot(ROCKET_ACCELERATION_STATE.toString(ROCKET_ACCELERATION_STATE.DEPLOYING))
        self._preparing = self._makeEventOutputSlot(ROCKET_ACCELERATION_STATE.toString(ROCKET_ACCELERATION_STATE.PREPARING))
        self._empty = self._makeEventOutputSlot(ROCKET_ACCELERATION_STATE.toString(ROCKET_ACCELERATION_STATE.EMPTY))
        self._ready = self._makeEventOutputSlot(ROCKET_ACCELERATION_STATE.toString(ROCKET_ACCELERATION_STATE.READY))
        self._active = self._makeEventOutputSlot(ROCKET_ACCELERATION_STATE.toString(ROCKET_ACCELERATION_STATE.ACTIVE))
        self._disabled = self._makeEventOutputSlot(ROCKET_ACCELERATION_STATE.toString(ROCKET_ACCELERATION_STATE.DISABLED))
        self._tryActivate = self._makeEventOutputSlot('tryActivate')
        self._duration = self._makeDataOutputSlot('duration', SLOT_TYPE.FLOAT, None)
        self.__switcher = {}
        self.__controllerLink = None
        return

    def __activate(self):
        go, provider, errorMsg = _extractRACComponent(self._object)
        if errorMsg:
            LOG_WARNING('[VScript] RocketAcceleratorEvents:', errorMsg)
            self._writeLog(errorMsg)
            self._failure.call()
            return
        self.__switcher = {ROCKET_ACCELERATION_STATE.NOT_RUNNING: lambda *args: None,
         ROCKET_ACCELERATION_STATE.DEPLOYING: lambda status: self._deploying.call(),
         ROCKET_ACCELERATION_STATE.PREPARING: lambda status: self._preparing.call(),
         ROCKET_ACCELERATION_STATE.READY: lambda status: self._ready.call(),
         ROCKET_ACCELERATION_STATE.ACTIVE: lambda status: self._active.call(),
         ROCKET_ACCELERATION_STATE.DISABLED: lambda status: self._disabled.call(),
         ROCKET_ACCELERATION_STATE.EMPTY: lambda status: self._empty.call()}
        provider.subscribe(self.__onStateChange, self.__onTryActivate)
        self.__controllerLink = CGF.ComponentLink(go, RAC.RocketAccelerationController)
        self._activateOut.call()

    def __deactivate(self):
        self.__switcher = None
        if self.__controllerLink:
            controller = self.__controllerLink() if self.__controllerLink else None
            if controller:
                controller.unsubscribe(self.__onStateChange, self.__onTryActivate)
            self.__controllerLink = None
        self._deactivateOut.call()
        return

    def __onStateChange(self, status, _):
        self._duration.setValue(status.endTime - BigWorld.serverTime())
        self.__switcher.get(status.status, self.__onWrongState)(status)

    def __onTryActivate(self):
        self._tryActivate.call()

    def __onWrongState(self, *args, **kwargs):
        errorVScript(self, 'RocketAcceleratorEvents: Set state called with undefined value')

    @classmethod
    def blockAspects(cls):
        return [ASPECT.CLIENT]


class RocketAcceleratorSettings(Block, CGFClientMeta):

    def __init__(self, *args, **kwargs):
        super(RocketAcceleratorSettings, self).__init__(*args, **kwargs)
        self._activate = self._makeEventInputSlot('in', self.__execute)
        self._object = self._makeDataInputSlot('vehicleObject', SLOT_TYPE.GAME_OBJECT)
        self._out = self._makeEventOutputSlot('out')
        self._failure = self._makeEventOutputSlot('failure')
        self._isPlayer = self._makeDataOutputSlot('isPlayer', SLOT_TYPE.BOOL, None)
        return

    def __execute(self):
        _, provider, errorMsg = _extractRACComponent(self._object)
        if errorMsg:
            LOG_WARNING('[VScript]: RocketAcceleratorSettings', errorMsg)
            self._failure.call()
            self._writeLog(errorMsg)
        else:
            self._isPlayer.setValue(provider.entity.isPlayerVehicle)
            self._out.call()

    @classmethod
    def blockAspects(cls):
        return [ASPECT.CLIENT]


def _extractRACComponent(gameObjectLink):
    go = gameObjectLink.getValue()
    if not go.isValid:
        return (None, None, 'Input game object is not valid')
    else:
        provider = go.findComponentByType(RAC.RocketAccelerationController)
        return (None, None, 'No RocketAccelerationController can be found') if provider is None else (go, provider, None)


class OnVehiclePassengerInfo(Block, CGFClientMeta, VehiclePassengerInfoWatcher):

    def __init__(self, *args, **kwargs):
        super(OnVehiclePassengerInfo, self).__init__(*args, **kwargs)
        self._vehicleID = battle_constants.UNKNOWN_VEHICLE_ID
        self._subscribe = self._makeEventInputSlot('subscribe', self.__subscribe)
        self._unsubscribe = self._makeEventInputSlot('unsubscribe', self.__unsubscribe)
        self._object = self._makeDataInputSlot('vehicleObject', SLOT_TYPE.GAME_OBJECT)
        self._subscribeOut = self._makeEventOutputSlot('subscribeOut')
        self._unsubscribeOut = self._makeEventOutputSlot('unsubscribeOut')
        self._onVehicleInfoUpdating = self._makeEventOutputSlot('onVehicleInfoUpdating')
        self._onVehicleInfoUpdate = self._makeEventOutputSlot('onVehicleInfoUpdate')
        self._isPlayerVehicle = self._makeDataOutputSlot('isPlayerVehicle', SLOT_TYPE.BOOL, None)
        self._isCurrentVehicle = self._makeDataOutputSlot('isCurrentVehicle', SLOT_TYPE.BOOL, None)
        self._isCurrentVehicleFPV = self._makeDataOutputSlot('isCurrentVehicleFPV', SLOT_TYPE.BOOL, None)
        return

    @classmethod
    def blockAspects(cls):
        return [ASPECT.CLIENT]

    def __subscribe(self):
        vehicle = cgf_helpers.getVehicleEntityByVehicleGameObject(self._object.getValue())
        if vehicle is not None:
            self.__subscribeVehicle(vehicle)
        return

    def __subscribeVehicle(self, vehicle):
        self._vehicleID = vehicle.id
        self.startVehiclePassengerLateListening(self.__onVehiclePassengerUpdate, self.__onVehiclePassengerUpdating)
        self._subscribeOut.call()

    def __unsubscribe(self):
        self._vehicleID = battle_constants.UNKNOWN_VEHICLE_ID
        self.stopVehiclePassengerListening(self.__onVehiclePassengerUpdate, self.__onVehiclePassengerUpdating)
        self._unsubscribeOut.call()

    def __onVehiclePassengerUpdating(self, _):
        self.__updateVehicleInfoByPassenger()
        self._onVehicleInfoUpdating.call()

    def __onVehiclePassengerUpdate(self, _):
        self.__updateVehicleInfoByPassenger()
        self._onVehicleInfoUpdate.call()

    @hasVehiclePassengerCtrl()
    def __updateVehicleInfoByPassenger(self, passengerCtrl=None):
        isCurrentVehicle = self._vehicleID == passengerCtrl.currentVehicleID
        self._isCurrentVehicle.setValue(isCurrentVehicle)
        self._isCurrentVehicleFPV.setValue(isCurrentVehicle and passengerCtrl.isCurrentVehicleFPV)
        self._isPlayerVehicle.setValue(self._vehicleID == passengerCtrl.playerVehicleID)
