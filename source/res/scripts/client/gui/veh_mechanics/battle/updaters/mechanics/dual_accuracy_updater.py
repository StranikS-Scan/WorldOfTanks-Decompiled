# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/veh_mechanics/battle/updaters/mechanics/dual_accuracy_updater.py
from __future__ import absolute_import
import typing
from events_handler import eventHandler
from gui.veh_mechanics.battle.updaters.mechanics.mechanics_common import VehicleMechanicUpdater
from vehicles.mechanics.mechanic_constants import VehicleMechanic
if typing.TYPE_CHECKING:
    from DualAccuracy import DualAccuracy

class IDualAccuracyView(object):

    def setDualAccuracyState(self, isActive):
        raise NotImplementedError


class DualAccuracyUpdater(VehicleMechanicUpdater):

    def __init__(self, view):
        super(DualAccuracyUpdater, self).__init__(VehicleMechanic.DUAL_ACCURACY, view)
        self.__dualAccuracyComponent = None
        return

    @eventHandler
    def onMechanicComponentCatching(self, component):
        self.__dualAccuracyComponent = component
        component.onSetDualAccState += self.__onSetDualAccState
        self.__onSetDualAccState(component.isActive())

    @eventHandler
    def onMechanicComponentReleasing(self, component):
        component.onSetDualAccState -= self.__onSetDualAccState
        self.__dualAccuracyComponent = None
        return

    def destroy(self):
        self.__dualAccuracyComponent = None
        super(DualAccuracyUpdater, self).destroy()
        return

    def __onSetDualAccState(self, isActive):
        self.view.setDualAccuracyState(isActive)
