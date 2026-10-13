# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/advanced/data/turret_alt_key_data.py
import typing
from gui.shared.tooltips.advanced.data.default_alt_key_data import DefaultAltKeyData
if typing.TYPE_CHECKING:
    from typing import Tuple
    from gui.shared.gui_items.vehicle_modules import VehicleTurret

class TurretAltKeyData(DefaultAltKeyData):
    THERMAL_VISION = 'vehicleThermalVision'

    @classmethod
    def _getMechanicKeys(cls, item):
        return (TurretAltKeyData.THERMAL_VISION,) if item.hasThermalVision() else super(TurretAltKeyData, cls)._getMechanicKeys(item)
