# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/visual_script_client/cgf_blocks.py
import weakref
import BigWorld
import logging
from debug_utils import LOG_WARNING
from visual_script.block import Block, Meta
from visual_script.slot_types import SLOT_TYPE
from visual_script.misc import ASPECT, errorVScript
from visual_script.dependency import dependencyImporter
from contexts.cgf_context import GameObjectWrapper
from constants import ROCKET_ACCELERATION_STATE
Vehicle, CGF, tankStructure, RAC = dependencyImporter('Vehicle', 'CGF', 'vehicle_systems.tankStructure', 'cgf_components.rocket_acceleration_component')
_logger = logging.getLogger(__name__)

class CGFMeta(Meta):

    @classmethod
    def blockColor(cls):
        pass

    @classmethod
    def blockCategory(cls):
        pass

    @classmethod
    def blockIcon(cls):
        pass

    @classmethod
    def blockAspects(cls):
        return [ASPECT.CLIENT, ASPECT.HANGAR]


class GetVehicleAppearanceGameObject(Block, CGFMeta):

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


class GetVehicleGameObject(Block, CGFMeta):

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
        if topGO.findComponentByType(Vehicle.Vehicle) is not None:
            goWrapper = GameObjectWrapper(topGO)
            self._vehicleObject.setValue(weakref.proxy(goWrapper))
        else:
            self._vehicleObject.setValue(None)
        return


class RocketAcceleratorEvents(Block, CGFMeta):

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
        else:
            LOG_WARNING('')
        self._deactivateOut.call()
        return

    def __onStateChange(self, status):
        self._duration.setValue(status.endTime - BigWorld.serverTime())
        self.__switcher.get(status.status, self.__onWrongState)(status)

    def __onTryActivate(self):
        self._tryActivate.call()

    def __onWrongState(self, *args, **kwargs):
        errorVScript(self, 'RocketAcceleratorEvents: Set state called with undefined value')

    @classmethod
    def blockAspects(cls):
        return [ASPECT.CLIENT]


class RocketAcceleratorSettings(Block, CGFMeta):

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
