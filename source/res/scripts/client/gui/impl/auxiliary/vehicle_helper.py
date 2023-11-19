# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/auxiliary/vehicle_helper.py
import typing
from gui.shared.gui_items.Vehicle import VEHICLE_TAGS
if typing.TYPE_CHECKING:
    from typing import Optional, Iterable
    from gui.impl.gen.view_models.common.vehicle_info_model import VehicleInfoModel
    from gui.shared.gui_items.Vehicle import Vehicle

def fillVehicleInfo(vehInfo, vehicle, separateIGRTag=False, tags=None):
    isElite = not vehicle.getEliteStatusProgress().toUnlock or vehicle.isElite
    vehInfo.setIsElite(isElite)
    vehInfo.setVehicleLvl(vehicle.level)
    vehInfo.setVehicleType(vehicle.type)
    vehInfo.setVehicleNation(vehicle.nationName)
    vehInfo.setVehicleShortName(vehicle.descriptor.type.shortUserString)
    vehicleTags = set(tags or [])
    vehicleTags.add(VEHICLE_TAGS.PREMIUM_IGR)
    vehInfo.setTags(','.join(vehicleTags & vehicle.tags))
    if separateIGRTag:
        vehInfo.setVehicleName(vehicle.descriptor.type.userString)
    else:
        vehInfo.setVehicleName(vehicle.descriptor.type.shortUserString)
