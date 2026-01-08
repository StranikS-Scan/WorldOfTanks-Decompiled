# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/visual_script_client/vehicle_mechanics_common.py
import typing
from constants import IS_VS_EDITOR, UNKNOWN_VEHICLE_ID
from events_containers.common.containers import ContainersListener
from events_handler import eventHandler
from vehicles.mechanics.mechanic_constants import VehicleMechanic
from visual_script.block import Block, InitParam, buildStrKeysValue
from visual_script.dependency import dependencyImporter
from visual_script.misc import ASPECT, EDITOR_TYPE
from visual_script.slot_types import SLOT_TYPE
from visual_script.vehicle_mechanics_blocks import VehicleMechanicsMeta
if typing.TYPE_CHECKING:
    from vehicles.mechanics.mechanic_states import IMechanicStatesComponent
    from _weakref import ProxyType
cgf_helpers, mechanic_trackers = dependencyImporter('cgf_common.cgf_helpers', 'vehicles.mechanics.mechanic_trackers')
if not IS_VS_EDITOR:
    from events_containers.components.life_cycle import IComponentLifeCycleListenerLogic
    from gui.battle_control.controllers.vehicles_tracking import VehiclesTrackingWatcher
    from vehicles.mechanics.mechanic_states import IMechanicStatesListenerLogic
    from vehicles.mechanics.mechanic_trackers import IVehicleMechanicsTrackerListenerLogic
else:

    class VehiclesTrackingWatcher(object):

        @classmethod
        def startVehicleMechanicsTracking(cls, vehicleID, mechanics, listener):
            pass

        @classmethod
        def stopVehicleMechanicsTracking(cls, vehicleID, mechanics, listener):
            pass


    class IVehicleMechanicsTrackerListenerLogic(object):
        pass


    class IComponentLifeCycleListenerLogic(object):
        pass


    class IMechanicStatesListenerLogic(object):
        pass


if typing.TYPE_CHECKING:
    from vehicles.mechanics.mechanic_states import IMechanicState

class VehicleMechanicEventsBlock(Block, VehicleMechanicsMeta, ContainersListener, VehiclesTrackingWatcher, IVehicleMechanicsTrackerListenerLogic):
    _EVENTS_NAME = ''

    def __init__(self, *args, **kwargs):
        super(VehicleMechanicEventsBlock, self).__init__(*args, **kwargs)
        self.__vehicleID = UNKNOWN_VEHICLE_ID
        self._vehicleMechanic = self._getVehicleMechanic(self._getInitParams())
        self._subscribe = self._makeEventInputSlot('subscribe', self.__subscribe)
        self._unsubscribe = self._makeEventInputSlot('unsubscribe', self.__unsubscribe)
        self._object = self._makeDataInputSlot('vehicleObject', SLOT_TYPE.GAME_OBJECT)
        self._subscribeOut = self._makeEventOutputSlot('subscribeOut')
        self._unsubscribeOut = self._makeEventOutputSlot('unsubscribeOut')

    @classmethod
    def blockAspects(cls):
        return [ASPECT.CLIENT]

    def captionText(self):
        return 'On {} {}'.format(self._vehicleMechanic.value, self._EVENTS_NAME)

    @classmethod
    def _getVehicleMechanic(cls, initParams):
        raise NotImplementedError

    def __subscribe(self):
        vehicleEntity = cgf_helpers.getVehicleEntityByVehicleGameObject(self._object.getValue())
        self.__vehicleID = vehicleEntity.id if vehicleEntity is not None else UNKNOWN_VEHICLE_ID
        self.startVehicleMechanicsTracking(self.__vehicleID, (self._vehicleMechanic,), self)
        self._subscribeOut.call()
        return

    def __unsubscribe(self):
        self.stopVehicleMechanicsTracking(self.__vehicleID, (self._vehicleMechanic,), self)
        self.__vehicleID = UNKNOWN_VEHICLE_ID
        self._unsubscribeOut.call()


class VehicleSelectableMechanicEventsBlock(VehicleMechanicEventsBlock):

    @classmethod
    def initParams(cls):
        return [InitParam('Vehicle Mechanic', SLOT_TYPE.STR, buildStrKeysValue(*cls._getInitParamMechanics()), EDITOR_TYPE.STR_KEY_SELECTOR)]

    @classmethod
    def _getInitParamMechanics(cls):
        raise NotImplementedError

    @classmethod
    def _getVehicleMechanic(cls, initParams):
        return VehicleMechanic(initParams[0])


class VehicleMechanicLifeCycleEventsBlock(VehicleMechanicEventsBlock, IComponentLifeCycleListenerLogic):
    _EVENTS_NAME = 'lifeCycle'

    def __init__(self, *args, **kwargs):
        super(VehicleMechanicLifeCycleEventsBlock, self).__init__(*args, **kwargs)
        self._onComponentParamsCollectedSlot = self._makeEventOutputSlot('onComponentParamsCollected')
        self._onComponentDestroyedSlot = self._makeEventOutputSlot('onComponentDestroyed')

    @eventHandler
    def onMechanicComponentCatching(self, component):
        component.lifeCycleEvents.lateSubscribe(self)

    @eventHandler
    def onMechanicComponentReleasing(self, component):
        self.unsubscribeFrom(component.lifeCycleEvents)

    @eventHandler
    def onComponentParamsCollected(self, params):
        self._onComponentParamsCollected(params)
        self._onComponentParamsCollectedSlot.call()

    @eventHandler
    def onComponentDestroyed(self, component):
        self._onComponentDestroyed(component)
        self._onComponentDestroyedSlot.call()

    def _onComponentParamsCollected(self, params):
        pass

    def _onComponentDestroyed(self, component):
        pass


class VehicleMechanicStateEventsBlock(VehicleMechanicEventsBlock, IMechanicStatesListenerLogic):
    _EVENTS_NAME = 'states'

    def __init__(self, *args, **kwargs):
        super(VehicleMechanicStateEventsBlock, self).__init__(*args, **kwargs)
        self._onStatePreparedSlot = self._makeEventOutputSlot('onStatePrepared')
        self._onStateObservationSlot = self._makeEventOutputSlot('onStateObservation')
        self._onStateTransitionSlot = self._makeEventOutputSlot('onStateTransition')

    @eventHandler
    def onMechanicComponentCatching(self, component):
        component.statesEvents.lateSubscribe(self)

    @eventHandler
    def onMechanicComponentReleasing(self, component):
        self.unsubscribeFrom(component.statesEvents)

    @eventHandler
    def onStatePrepared(self, state):
        self._onStatePrepared(state)
        self._onStatePreparedSlot.call()

    @eventHandler
    def onStateObservation(self, state):
        self._onStateObservation(state)
        self._onStateObservationSlot.call()

    @eventHandler
    def onStateTransition(self, prevState, newState):
        self._onStateTransition(prevState, newState)
        self._onStateTransitionSlot.call()

    def _onStatePrepared(self, state):
        pass

    def _onStateObservation(self, state):
        pass

    def _onStateTransition(self, prevState, newState):
        pass
