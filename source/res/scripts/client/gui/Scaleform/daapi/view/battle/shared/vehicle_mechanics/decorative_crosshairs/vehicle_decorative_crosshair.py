# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/vehicle_mechanics/decorative_crosshairs/vehicle_decorative_crosshair.py
from __future__ import absolute_import
from gui.Scaleform.daapi.view.meta.BaseDecorativeCrosshairMeta import BaseDecorativeCrosshairMeta
from gui.veh_mechanics.battle.updaters.mechanics.mechanic_passenger_updater import IMechanicPassengerView

class VehicleDecorativeCrosshair(BaseDecorativeCrosshairMeta, IMechanicPassengerView):

    def setVisibleForPassenger(self, visibleForPassenger):
        self.as_setVisibleS(visibleForPassenger)
