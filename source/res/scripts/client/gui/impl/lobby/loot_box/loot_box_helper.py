# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/loot_box/loot_box_helper.py
import hashlib
import typing
import BigWorld
from gui import SystemMessages
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.common.vehicle_model import NationType, VehicleType
from gui.shared.gui_items.Vehicle import getNationLessName, getIconResourceName
from gui.shared.notifications import NotificationPriorityLevel
from gui.shared.utils.requesters.ItemsRequester import REQ_CRITERIA
from helpers import dependency
from items.utils import getItemDescrByCompactDescr
from items.vehicles import getVehicleClass
from nations import NAMES
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from gui.shared.gui_items.loot_box import LootBox

def showRestrictedSysMessage():

    def _showRestrictedSysMessage():
        SystemMessages.pushMessage(text=backport.text(R.strings.lootboxes.restrictedMessage.body()), type=SystemMessages.SM_TYPE.ErrorHeader, priority=NotificationPriorityLevel.HIGH, messageData={'header': backport.text(R.strings.lootboxes.restrictedMessage.header())})

    BigWorld.callback(0.0, _showRestrictedSysMessage)


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def getObtainableVehicles(lootbox, itemsCache=None):
    vehsInPossession = itemsCache.items.getVehicles(REQ_CRITERIA.INVENTORY)
    vehsInPossession.update(itemsCache.items.getVehicles(REQ_CRITERIA.VEHICLE.IS_RESTORE_POSSIBLE))
    return [ veh for veh in lootbox.getBonusVehicles() if veh not in vehsInPossession ]


def setVehicleDataToModel(vehicleCD, vehicleModel):
    vehicle = getItemDescrByCompactDescr(vehicleCD)
    vehicleModel.setVehicleId(vehicleCD)
    vehicleModel.setName(vehicle.userString)
    vehicleModel.setLevel(vehicle.level)
    nationId, _ = vehicle.id
    vehicleModel.setNation(NationType(NAMES[nationId]))
    vehicleModel.setType(VehicleType(getVehicleClass(vehicleCD)))
    vehicleModel.setVehicleTechName(getIconResourceName(getNationLessName(vehicle.name)))
    vehicleModel.setImageName(hashlib.md5(vehicle.name).hexdigest())
