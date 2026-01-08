# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/veh_mechanics/battle/updaters/mechanics/tracked_mechanics_updater.py
from __future__ import absolute_import
import typing
from future.utils import viewkeys
from events_containers.common.containers import ContainersListener
from events_handler import eventHandler
from gui.battle_control.controllers.vehicles_tracking import VehiclesTrackingWatcher
from gui.veh_mechanics.battle.updaters.updaters_common import ViewUpdater
from vehicles.mechanics.mechanic_trackers import IVehicleMechanicsTrackerListenerLogic
if typing.TYPE_CHECKING:
    from vehicles.mechanics.mechanic_constants import VehicleMechanic

class IVehicleTrackedMechanicsView(object):

    def onTrackedMechanicsUpdate(self, mechanics):
        raise NotImplementedError


class VehicleTrackedMechanicsUpdater(ViewUpdater, ContainersListener, VehiclesTrackingWatcher, IVehicleMechanicsTrackerListenerLogic):

    def initialize(self):
        super(VehicleTrackedMechanicsUpdater, self).initialize()
        self.startCurrentVehicleMechanicsTracking((), self)

    def finalize(self):
        self.stopCurrentVehicleMechanicsTracking((), self)
        super(VehicleTrackedMechanicsUpdater, self).finalize()

    @eventHandler
    def onMechanicComponentsUpdate(self, components):
        self.view.onTrackedMechanicsUpdate(viewkeys(components))
