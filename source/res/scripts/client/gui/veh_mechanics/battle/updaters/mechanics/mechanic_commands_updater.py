# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/veh_mechanics/battle/updaters/mechanics/mechanic_commands_updater.py
from __future__ import absolute_import
import typing
from events_handler import eventHandler
from gui.veh_mechanics.battle.updaters.mechanics.mechanics_common import VehicleMechanicUpdater

class VehicleMechanicCommandsUpdater(VehicleMechanicUpdater):

    @eventHandler
    def onMechanicComponentCatching(self, component):
        self.view.subscribeTo(component.commandsEvents)

    @eventHandler
    def onMechanicComponentReleasing(self, component):
        self.view.unsubscribeFrom(component.commandsEvents)
