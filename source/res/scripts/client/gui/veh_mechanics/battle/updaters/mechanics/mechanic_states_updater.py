# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/veh_mechanics/battle/updaters/mechanics/mechanic_states_updater.py
from __future__ import absolute_import
import typing
from events_handler import eventHandler
from gui.veh_mechanics.battle.updaters.mechanics.mechanics_common import VehicleMechanicUpdater

class VehicleMechanicStatesUpdater(VehicleMechanicUpdater):

    @eventHandler
    def onMechanicComponentCatching(self, component):
        component.statesEvents.lateSubscribe(self.view)

    @eventHandler
    def onMechanicComponentReleasing(self, component):
        self.view.unsubscribeFrom(component.statesEvents)
