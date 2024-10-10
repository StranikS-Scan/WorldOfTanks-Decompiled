# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/auxiliary/vehicle_helper.py
import typing
from gui.shared.gui_items.Vehicle import VEHICLE_TAGS, getNationLessName
if typing.TYPE_CHECKING:
    from gui.impl.gen.view_models.common.vehicle_info_model import VehicleInfoModel
    from gui.shared.gui_items.Vehicle import Vehicle

def fillVehicleInfo(vehInfo, vehicle, separateIGRTag=False):
    isElite = not vehicle.getEliteStatusProgress().toUnlock or vehicle.isElite
    vehInfo.setIsElite(isElite)
    vehInfo.setVehicleLvl(vehicle.level)
    vehInfo.setIsPremiumIGR(vehicle.isPremiumIGR)
    vehInfo.setVehicleType(vehicle.type)
    vehInfo.setVehicleNation(vehicle.nationName)
    vehInfo.setVehicleShortName(vehicle.shortUserName)
    vehInfo.setVehicleTechName(getNationLessName(vehicle.name))
    if separateIGRTag:
        vehInfo.setVehicleName(vehicle.descriptor.type.userString)
        if vehicle.isPremiumIGR:
            vehInfo.getTags().addString(VEHICLE_TAGS.PREMIUM_IGR)
    else:
        vehInfo.setVehicleName(vehicle.descriptor.type.shortUserString)
    vehInfo.setVehicleCD(vehicle.intCD)
