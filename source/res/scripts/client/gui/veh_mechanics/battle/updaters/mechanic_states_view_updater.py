# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/veh_mechanics/battle/updaters/mechanic_states_view_updater.py
from gui.veh_mechanics.battle.updaters.updaters_common import VehicleMechanicUpdater

class VehicleMechanicStatesUpdater(VehicleMechanicUpdater):

    def _subscribeToMechanicComponent(self, mechanicComponent):
        super(VehicleMechanicStatesUpdater, self)._subscribeToMechanicComponent(mechanicComponent)
        mechanicComponent.statesEvents.lateSubscribe(self.view)

    def _unsubscribeFromMechanicComponent(self, mechanicComponent):
        self.view.unsubscribeFrom(mechanicComponent.statesEvents)
        super(VehicleMechanicStatesUpdater, self)._unsubscribeFromMechanicComponent(mechanicComponent)
