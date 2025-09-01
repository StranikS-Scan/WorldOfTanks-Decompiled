# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/vehicle_mechanics/decorative_crosshairs/vehicle_decorative_crosshair.py
from gui.Scaleform.daapi.view.meta.BaseDecorativeCrosshairMeta import BaseDecorativeCrosshairMeta
from gui.veh_mechanics.battle.updaters.mechanic_passenger_view_updater import IMechanicPassengerView

class VehicleDecorativeCrosshair(BaseDecorativeCrosshairMeta, IMechanicPassengerView):

    def setVisible(self, visible):
        self.as_setVisibleS(visible)
