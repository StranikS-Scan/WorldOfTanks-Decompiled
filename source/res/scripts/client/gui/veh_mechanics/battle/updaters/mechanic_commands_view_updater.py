# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/veh_mechanics/battle/updaters/mechanic_commands_view_updater.py
import typing
from gui.veh_mechanics.battle.updaters.updaters_common import VehicleMechanicUpdater
if typing.TYPE_CHECKING:
    from vehicles.mechanics.mechanic_commands import IMechanicCommandsComponent

class MechanicsCommandsUpdater(VehicleMechanicUpdater):

    def _subscribeToMechanicComponent(self, mechanicComponent):
        super(MechanicsCommandsUpdater, self)._subscribeToMechanicComponent(mechanicComponent)
        self.subscribeTo(mechanicComponent.commandsEvents)
        self.view.subscribeTo(mechanicComponent.commandsEvents)

    def _unsubscribeFromMechanicComponent(self, mechanicComponent):
        super(MechanicsCommandsUpdater, self)._unsubscribeFromMechanicComponent(mechanicComponent)
        self.unsubscribeFrom(mechanicComponent.commandsEvents)
        self.view.unsubscribeFrom(mechanicComponent.commandsEvents)
