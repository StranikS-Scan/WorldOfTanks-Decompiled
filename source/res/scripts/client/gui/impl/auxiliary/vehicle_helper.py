# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/auxiliary/vehicle_helper.py
import typing
if typing.TYPE_CHECKING:
    from gui.shared.gui_items.Vehicle import Vehicle

def fillVehicleInfo(vehInfo, vehicle):
    vehInfo.setIsElite(vehicle.isElite)
    vehInfo.setVehicleLvl(vehicle.level)
    vehInfo.setVehicleName(vehicle.userName)
    vehInfo.setVehicleType(vehicle.type)
