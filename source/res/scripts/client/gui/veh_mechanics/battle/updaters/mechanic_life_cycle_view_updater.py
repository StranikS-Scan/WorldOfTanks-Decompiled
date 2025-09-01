# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/veh_mechanics/battle/updaters/mechanic_life_cycle_view_updater.py
from gui.veh_mechanics.battle.updaters.updaters_common import VehicleMechanicUpdater

class VehicleMechanicLifeCycleUpdater(VehicleMechanicUpdater):

    def _subscribeToMechanicComponent(self, mechanicComponent):
        super(VehicleMechanicLifeCycleUpdater, self)._subscribeToMechanicComponent(mechanicComponent)
        mechanicComponent.lifeCycleEvents.lateSubscribe(self.view)

    def _unsubscribeFromMechanicComponent(self, mechanicComponent):
        self.view.unsubscribeFrom(mechanicComponent.lifeCycleEvents)
        super(VehicleMechanicLifeCycleUpdater, self)._unsubscribeFromMechanicComponent(mechanicComponent)
