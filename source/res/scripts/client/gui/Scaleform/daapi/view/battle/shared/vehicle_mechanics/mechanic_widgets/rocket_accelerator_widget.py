# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/vehicle_mechanics/mechanic_widgets/rocket_accelerator_widget.py
from __future__ import absolute_import
import typing
from gui.Scaleform.daapi.view.meta.RocketAcceleratorIndicatorMeta import RocketAcceleratorIndicatorMeta
from gui.veh_mechanics.battle.updaters.mechanics.mechanic_passenger_updater import VehicleMechanicPassengerUpdater
from gui.veh_mechanics.battle.updaters.mechanics.rocket_accelerator_updater import IRocketAcceleratorView, RocketAcceleratorUpdater
from vehicles.mechanics.mechanic_constants import VehicleMechanic
if typing.TYPE_CHECKING:
    from gui.veh_mechanics.battle.updaters.updaters_common import IViewUpdater

class RocketAcceleratorMechanicIndicator(RocketAcceleratorIndicatorMeta, IRocketAcceleratorView):

    def setCount(self, count):
        self.as_setCountS(count)

    def setProgress(self, progress):
        self.as_setProgressS(progress)

    def setState(self, state, isInstantly=False):
        self.as_setStateS(state, isInstantly=isInstantly)

    def setTime(self, time):
        self.as_setTimeS(time)

    def _getViewUpdaters(self):
        return [VehicleMechanicPassengerUpdater(VehicleMechanic.ROCKET_ACCELERATION, self), RocketAcceleratorUpdater(self)]
