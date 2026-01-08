# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/veh_mechanics/battle/updaters/mechanics/mechanics_common.py
from __future__ import absolute_import
import typing
from events_containers.common.containers import ContainersListener
from gui.battle_control.controllers.vehicles_tracking import VehiclesTrackingWatcher
from gui.veh_mechanics.battle.updaters.updaters_common import ViewUpdater
from vehicles.mechanics.mechanic_trackers import IVehicleMechanicsTrackerListenerLogic
if typing.TYPE_CHECKING:
    from events_containers.common.containers import IClientEventsContainerListener
    from vehicles.mechanics.mechanic_constants import VehicleMechanic

class VehicleMechanicUpdater(ViewUpdater, ContainersListener, VehiclesTrackingWatcher, IVehicleMechanicsTrackerListenerLogic):

    def __init__(self, vehicleMechanic, view):
        super(VehicleMechanicUpdater, self).__init__(view)
        self.__vehicleMechanic = vehicleMechanic

    def initialize(self):
        super(VehicleMechanicUpdater, self).initialize()
        self.startCurrentVehicleMechanicsTracking((self.__vehicleMechanic,), self)

    def finalize(self):
        self.stopCurrentVehicleMechanicsTracking((self.__vehicleMechanic,), self)
        super(VehicleMechanicUpdater, self).finalize()
