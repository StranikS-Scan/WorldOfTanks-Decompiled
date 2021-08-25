# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/marathon/marathon_reward_helper.py
from collections import namedtuple
from gui.shared.gui_items import Vehicle
from helpers import dependency, int2roman
from skeletons.gui.shared import IItemsCache
SpecialRewardData = namedtuple('SpecialRewardData', ('sourceName', 'congratsSourceId', 'vehicleName', 'vehicleLvl', 'vehicleIsElite', 'vehicleType', 'goToVehicleBtn', 'videoShownKey'))

def getVehicleStrID(vehicleName):
    return vehicleName.split(':')[1]


def formatEliteVehicle(isElite, typeName):
    ubFormattedTypeName = Vehicle.getIconResourceName(typeName)
    return '{}_elite'.format(ubFormattedTypeName) if isElite else ubFormattedTypeName


def showMarathonReward(vehicleCD, videoShownKey):
    from gui.impl.lobby.marathon.marathon_reward_view import MarathonRewardViewWindow
    itemsCache = dependency.instance(IItemsCache)
    vehicle = itemsCache.items.getItemByCD(vehicleCD)
    if vehicle is not None:
        vehicleType = formatEliteVehicle(vehicle.isElite, vehicle.type)
        congratsSourceId = str(vehicle.intCD)
        sourceName = Vehicle.getIconResourceName(getVehicleStrID(vehicle.name))
        if sourceName and congratsSourceId is not None:
            specialRewardData = SpecialRewardData(sourceName=sourceName, congratsSourceId=congratsSourceId, vehicleName=vehicle.userName, vehicleIsElite=vehicle.isElite, vehicleLvl=int2roman(vehicle.level), vehicleType=vehicleType, goToVehicleBtn=vehicle.isInInventory, videoShownKey=videoShownKey)
            if MarathonRewardViewWindow.getInstances():
                return
            window = MarathonRewardViewWindow(specialRewardData)
            window.load()
    return
