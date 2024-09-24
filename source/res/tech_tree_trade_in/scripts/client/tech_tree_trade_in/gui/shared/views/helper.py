# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: tech_tree_trade_in/scripts/client/tech_tree_trade_in/gui/shared/views/helper.py
import nations
from gui.impl.auxiliary.vehicle_helper import fillVehicleInfo
from helpers import dependency
from items import vehicles
from skeletons.gui.shared import IItemsCache
from tech_tree_trade_in.gui.impl.gen.view_models.views.lobby.branch_vehicle_info_model import BranchVehicleInfoModel

def packVehicleIconUpperCase(vehicle):
    vehInfo = vehicle.name.split(':')
    return vehInfo[1].replace('-', '_')


def packVehicleIconLowerCase(vehicle):
    vehInfo = vehicle.name.split(':')
    return vehInfo[1].lower().replace('-', '_')


def packVehicleIconSmall(vehicle):
    return vehicle.iconSmall


def packVehicleIconBig(vehicle):
    return vehicle.icon


def fillVehiclesList(vehArray, vehCDs, smallIconPacker=packVehicleIconSmall, bigIconPacker=packVehicleIconBig):
    itemsCache = dependency.instance(IItemsCache)
    vehArray.clear()
    for vehCD in vehCDs:
        vehicle = itemsCache.items.getItemByCD(vehCD)
        if vehicle:
            vehInfo = BranchVehicleInfoModel()
            fillVehicleInfo(vehInfo, vehicle)
            vehInfo.setIconSmall(smallIconPacker(vehicle))
            vehInfo.setIcon(bigIconPacker(vehicle))
            vehInfo.setUnlocked(vehicle.isUnlocked)
            vehInfo.setObtained(vehicle.isInInventory and not vehicle.isRented)
            vehInfo.setId(vehCD)
            vehArray.addViewModel(vehInfo)

    vehArray.invalidate()


def getNationIDByVehCD(vehCD):
    return vehicles.parseIntCompactDescr(vehCD)[1]


def getNationNameByVehCD(vehCD):
    return nations.MAP[getNationIDByVehCD(vehCD)]
