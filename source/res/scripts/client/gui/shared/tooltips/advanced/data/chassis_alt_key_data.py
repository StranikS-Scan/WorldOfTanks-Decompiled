# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/tooltips/advanced/data/chassis_alt_key_data.py
import typing
from gui.Scaleform.genConsts.FITTING_TYPES import FITTING_TYPES
from gui.shared.tooltips.advanced.data.default_alt_key_data import DefaultAltKeyData
if typing.TYPE_CHECKING:
    from typing import Tuple
    from gui.shared.gui_items.vehicle_modules import VehicleChassis

class ChassisAltKeyData(DefaultAltKeyData):
    CHASSIS_TRACK_WITHIN_TRACK = 'vehicleTrackWithinTrackChassis'
    MULTI_TRACK_CHASSIS = 'vehicleMultiTrackChassis'

    @classmethod
    def _getMechanicKeys(cls, item):
        if item.isTrackWithinTrack():
            return (ChassisAltKeyData.CHASSIS_TRACK_WITHIN_TRACK,)
        if item.isMultiTrack():
            return (ChassisAltKeyData.MULTI_TRACK_CHASSIS,)
        return (FITTING_TYPES.VEHICLE_WHEELED_CHASSIS,) if item.isWheeledChassis() else super(ChassisAltKeyData, cls)._getMechanicKeys(item)
