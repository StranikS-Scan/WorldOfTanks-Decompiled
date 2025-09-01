# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/veh_mechanics/battle/updaters/updaters_common.py
import typing
import weakref
from events_handler import eventHandler
from gui.battle_control.controllers.vehicle_passenger import VehiclePassengerInfoWatcher
from vehicles.components.component_events import IComponentListener, ComponentListener
from vehicles.components.component_life_cycle import IComponentLifeCycleListenerLogic
from vehicles.mechanics.mechanic_constants import VehicleMechanic
from vehicles.mechanics.mechanic_helpers import getVehicleMechanic
if typing.TYPE_CHECKING:
    from Vehicle import Vehicle

class IViewUpdater(object):

    def initialize(self):
        pass

    def finalize(self):
        pass


class ViewUpdater(IViewUpdater):

    def __init__(self, view):
        super(ViewUpdater, self).__init__()
        self.__view = weakref.proxy(view)

    @property
    def view(self):
        return self.__view

    def finalize(self):
        self.__view = None
        return


class VehicleMechanicUpdater(ViewUpdater, ComponentListener, VehiclePassengerInfoWatcher, IComponentLifeCycleListenerLogic):

    def __init__(self, vehicleMechanic, view):
        super(VehicleMechanicUpdater, self).__init__(view)
        self.__vehicleMechanic = vehicleMechanic
        self.__mechanicComponent = None
        return

    @property
    def mechanicComponent(self):
        return self.__mechanicComponent

    def initialize(self):
        super(VehicleMechanicUpdater, self).initialize()
        self.startVehiclePassengerLateListening(self._onVehiclePassengerUpdate)

    def finalize(self):
        self.__releaseVehicleMechanicComponent()
        self.stopVehiclePassengerListening(self._onVehiclePassengerUpdate)
        super(VehicleMechanicUpdater, self).finalize()

    @eventHandler
    def onComponentDestroyed(self):
        self.__mechanicComponent = None
        super(VehicleMechanicUpdater, self).onComponentDestroyed()
        return

    def _onVehiclePassengerUpdate(self, vehicle):
        mechanicComponent = getVehicleMechanic(self.__vehicleMechanic, vehicle)
        if mechanicComponent is not self.__mechanicComponent:
            self.__releaseVehicleMechanicComponent()
            self.__catchVehicleMechanicComponent(mechanicComponent)

    def _subscribeToMechanicComponent(self, mechanicComponent):
        self.subscribeTo(mechanicComponent.lifeCycleEvents)

    def _unsubscribeFromMechanicComponent(self, mechanicComponent):
        self.unsubscribeFrom(mechanicComponent.lifeCycleEvents)

    def __catchVehicleMechanicComponent(self, mechanicComponent):
        if mechanicComponent is not None:
            self.__mechanicComponent = mechanicComponent
            self._subscribeToMechanicComponent(mechanicComponent)
        return

    def __releaseVehicleMechanicComponent(self):
        if self.__mechanicComponent is not None:
            self._unsubscribeFromMechanicComponent(self.__mechanicComponent)
            self.__mechanicComponent = None
        return
