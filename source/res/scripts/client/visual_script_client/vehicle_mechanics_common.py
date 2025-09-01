# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/visual_script_client/vehicle_mechanics_common.py
import typing
from constants import IS_VS_EDITOR
from events_handler import eventHandler
from vehicles.components.component_events import ComponentListener
from vehicles.mechanics.mechanic_constants import VehicleMechanic
from vehicles.mechanics.mechanic_helpers import getVehicleMechanic
from visual_script.block import Block, InitParam, buildStrKeysValue
from visual_script.dependency import dependencyImporter
from visual_script.misc import ASPECT, EDITOR_TYPE
from visual_script.slot_types import SLOT_TYPE
from visual_script.vehicle_mechanics_blocks import VehicleMechanicsMeta
if typing.TYPE_CHECKING:
    from _weakref import ReferenceType
    from vehicles.mechanics.mechanic_states import IMechanicStatesComponent
cgf_helpers = dependencyImporter('cgf_common.cgf_helpers')
if not IS_VS_EDITOR:
    from vehicles.components.component_life_cycle import IComponentLifeCycleListenerLogic
    from vehicles.mechanics.mechanic_states import IMechanicStatesListenerLogic
else:

    class IComponentLifeCycleListenerLogic(object):
        pass


    class IMechanicStatesListenerLogic(object):
        pass


if typing.TYPE_CHECKING:
    from CGF import GameObject
    from vehicles.mechanics.mechanic_states import IMechanicState

def getVehicleMechanicByVehicleGameObject(mechanic, vehicleGameObject):
    return getVehicleMechanic(mechanic, cgf_helpers.getVehicleEntityByVehicleGameObject(vehicleGameObject))


class VehicleMechanicEventsBlock(Block, VehicleMechanicsMeta, ComponentListener, IComponentLifeCycleListenerLogic):
    _EVENTS_NAME = ''

    def __init__(self, *args, **kwargs):
        super(VehicleMechanicEventsBlock, self).__init__(*args, **kwargs)
        self._vehicleMechanic = self._getVehicleMechanic(self._getInitParams())
        self.__mechanicComponent = None
        self._subscribe = self._makeEventInputSlot('subscribe', self.__subscribe)
        self._unsubscribe = self._makeEventInputSlot('unsubscribe', self.__unsubscribe)
        self._object = self._makeDataInputSlot('vehicleObject', SLOT_TYPE.GAME_OBJECT)
        self._subscribeOut = self._makeEventOutputSlot('subscribeOut')
        self._unsubscribeOut = self._makeEventOutputSlot('unsubscribeOut')
        return

    @classmethod
    def blockAspects(cls):
        return [ASPECT.CLIENT]

    def captionText(self):
        return 'On {} {}'.format(self._vehicleMechanic.value, self._EVENTS_NAME)

    @eventHandler
    def onComponentDestroyed(self):
        self.__mechanicComponent = None
        super(VehicleMechanicEventsBlock, self).onComponentDestroyed()
        return

    @classmethod
    def _getVehicleMechanic(cls, initParams):
        raise NotImplementedError

    def _subscribeToMechanicComponent(self, mechanicComponent):
        self.subscribeTo(mechanicComponent.lifeCycleEvents)

    def _unsubscribeFromMechanicComponent(self, mechanicComponent):
        self.unsubscribeFrom(mechanicComponent.lifeCycleEvents)

    def __subscribe(self):
        mechanicComponent = getVehicleMechanicByVehicleGameObject(self._vehicleMechanic, self._object.getValue())
        if mechanicComponent is not None:
            self.__mechanicComponent = mechanicComponent
            self._subscribeToMechanicComponent(mechanicComponent)
            self._subscribeOut.call()
        return

    def __unsubscribe(self):
        if self.__mechanicComponent is not None:
            self._unsubscribeFromMechanicComponent(self.__mechanicComponent)
            self.__mechanicComponent = None
        self._unsubscribeOut.call()
        return


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


class VehicleMechanicStateEventsBlock(VehicleMechanicEventsBlock, IMechanicStatesListenerLogic):
    _EVENTS_NAME = 'states'

    def __init__(self, *args, **kwargs):
        super(VehicleMechanicStateEventsBlock, self).__init__(*args, **kwargs)
        self._onStatePreparedSlot = self._makeEventOutputSlot('onStatePrepared')
        self._onStateObservationSlot = self._makeEventOutputSlot('onStateObservation')
        self._onStateTransitionSlot = self._makeEventOutputSlot('onStateTransition')

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

    def _subscribeToMechanicComponent(self, mechanicComponent):
        super(VehicleMechanicStateEventsBlock, self)._subscribeToMechanicComponent(mechanicComponent)
        mechanicComponent.statesEvents.lateSubscribe(self)

    def _unsubscribeFromMechanicComponent(self, mechanicComponent):
        self.unsubscribeFrom(mechanicComponent.statesEvents)
        super(VehicleMechanicStateEventsBlock, self)._unsubscribeFromMechanicComponent(mechanicComponent)


class VehicleMechanicLifeCycleEventsBlock(VehicleMechanicEventsBlock, IComponentLifeCycleListenerLogic):
    _EVENTS_NAME = 'lifeCycle'

    def __init__(self, *args, **kwargs):
        super(VehicleMechanicLifeCycleEventsBlock, self).__init__(*args, **kwargs)
        self._onComponentParamsCollectedSlot = self._makeEventOutputSlot('onComponentParamsCollected')
        self._onComponentDestroyedSlot = self._makeEventOutputSlot('onComponentDestroyed')

    @eventHandler
    def onComponentParamsCollected(self, component):
        super(VehicleMechanicLifeCycleEventsBlock, self).onComponentParamsCollected(component)
        self._onComponentParamsCollected(component)
        self._onComponentParamsCollectedSlot.call()

    @eventHandler
    def onComponentDestroyed(self):
        super(VehicleMechanicLifeCycleEventsBlock, self).onComponentDestroyed()
        self._onComponentDestroyed()
        self._onComponentDestroyedSlot.call()

    def _onComponentParamsCollected(self, component):
        pass

    def _onComponentDestroyed(self):
        pass

    def _subscribeToMechanicComponent(self, mechanicComponent):
        super(VehicleMechanicLifeCycleEventsBlock, self)._subscribeToMechanicComponent(mechanicComponent)
        mechanicComponent.lifeCycleEvents.lateSubscribe(self)

    def _unsubscribeFromMechanicComponent(self, mechanicComponent):
        self.unsubscribeFrom(mechanicComponent.lifeCycleEvents)
        super(VehicleMechanicLifeCycleEventsBlock, self)._unsubscribeFromMechanicComponent(mechanicComponent)
