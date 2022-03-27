# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/account_helpers/account_validator.py
import logging
import BigWorld
import async
import constants
from gui.shared.gui_items import GUI_ITEM_TYPE
from helpers import dependency
from items import vehicles, tankmen, ITEM_TYPE_NAMES
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.gui_items import IGuiItemsFactory
from soft_exception import SoftException
_logger = logging.getLogger(__name__)

class ValidateException(SoftException):

    def __init__(self, msg, code, itemData):
        super(ValidateException, self).__init__(msg)
        self.code = code
        self.itemData = itemData


class ValidationCodes(object):
    OK = 0
    VEHICLE_MISMATCH = 1001
    CHASSIS_MISMATCH = 1002
    TURRET_MISMATCH = 1003
    GUN_MISMATCH = 1004
    ENGINE_MISMATCH = 1005
    FUEL_TANK_MISMATCH = 1006
    RADIO_MISMATCH = 1007
    TANKMEN_MISMATCH = 1008
    OPT_DEV_MISMATCH = 1009
    SHELL_MISMATCH = 1010
    EQ_MISMATCH = 1011
    VEHICLE_CREW_MISMATCH = 1012
    OUTFIT_MISMATCH = 1013
    UNLOCKS_MISMATCH = 1014


def _packItemData(itemTypeID, itemData, *args):
    return (ITEM_TYPE_NAMES[itemTypeID], itemData) + args


class AccountValidator(object):
    itemsCache = dependency.descriptor(IItemsCache)
    itemsFactory = dependency.descriptor(IGuiItemsFactory)

    @async.async
    def validate(self, callback=None):
        handlers = self._getHandlers()
        for handler in handlers:
            try:
                yield async.await(handler())
            except ValidateException as e:
                _logger.error('There is exception while validating item %s', e.itemData)
                callback(e.code)
                return

        callback(ValidationCodes.OK)

    def _getHandlers(self):
        raise NotImplementedError


class InventoryVehiclesValidator(AccountValidator):

    def _getHandlers(self):
        return (self.__validateInventoryVehicles,)

    @async.async
    def __validateInventoryVehicles(self):
        inventory = self.itemsCache.items.inventory
        vehsInvData = inventory.getCacheValue(GUI_ITEM_TYPE.VEHICLE, {})

        def createVehicleDescrAsync():
            for invID, vehCompDescr in vehsInvData.get('compDescr', {}).iteritems():
                try:
                    yield vehicles.VehicleDescr(vehCompDescr)
                except Exception as e:
                    raise ValidateException(e.message, ValidationCodes.VEHICLE_MISMATCH, _packItemData(GUI_ITEM_TYPE.VEHICLE, (invID, vehCompDescr)))

        yield async.await(async.distributeLoopOverTicks(createVehicleDescrAsync(), minPerTick=10, maxPerTick=100, logID='createVehicleDescrAsync', tickLength=0.0))

        def validateTankmanAsync():
            for vehInvData in inventory.getItemsData(GUI_ITEM_TYPE.VEHICLE).itervalues():
                for idx, tankmanID in enumerate(vehInvData.crew):
                    if BigWorld.player() is None:
                        return
                    yield idx
                    if idx >= len(vehInvData.descriptor.type.crewRoles):
                        raise ValidateException('Exceeded tankmen in tank', ValidationCodes.VEHICLE_CREW_MISMATCH, _packItemData(GUI_ITEM_TYPE.VEHICLE, vehInvData, tankmanID))

            return

        yield async.await(async.distributeLoopOverTicks(validateTankmanAsync(), minPerTick=10, maxPerTick=100, logID='validateTankmanAsync', tickLength=0.0))


class InventoryOutfitValidator(AccountValidator):

    def _getHandlers(self):
        return (self.__validateInventoryOutfit,)

    @async.async
    def __validateInventoryOutfit(self):
        c11nData = self.itemsCache.items.inventory.getCacheValue(GUI_ITEM_TYPE.CUSTOMIZATION, {})

        def validateOutfitsAsync():
            for vehIntCD, outfitsData in c11nData.get(constants.CustomizationInvData.OUTFITS, {}).iteritems():
                vehicleData = self.itemsCache.items.inventory.getItemData(vehIntCD)
                if vehicleData is not None:
                    vehicleCD = vehicleData.compDescr
                else:
                    _, nationID, vehicleTypeID = vehicles.parseIntCompactDescr(vehIntCD)
                    vehicleDesc = vehicles.VehicleDescr(typeID=(nationID, vehicleTypeID))
                    vehicleCD = vehicleDesc.makeCompactDescr()
                for outfitCD in outfitsData.itervalues():
                    if BigWorld.player() is None:
                        return
                    try:
                        yield self.itemsFactory.createOutfit(strCompactDescr=outfitCD, vehicleCD=vehicleCD)
                    except Exception as e:
                        raise ValidateException(e.message, ValidationCodes.OUTFIT_MISMATCH, _packItemData(GUI_ITEM_TYPE.CUSTOMIZATION, (vehIntCD, outfitCD)))

            return

        yield async.await(async.distributeLoopOverTicks(validateOutfitsAsync(), minPerTick=10, maxPerTick=100, logID='validateOutfitsAsync', tickLength=0.0))


class InventoryTankmenValidator(AccountValidator):

    def _getHandlers(self):
        return (self.__validateInventoryTankmen,)

    @async.async
    def __validateInventoryTankmen(self):
        tmenInvData = self.itemsCache.items.inventory.getCacheValue(GUI_ITEM_TYPE.TANKMAN, {})

        def validateInventoryTankmenAsync():
            for invID, tmanCompDescr in tmenInvData.get('compDescr', {}).iteritems():
                if BigWorld.player() is None:
                    return
                try:
                    yield tankmen.TankmanDescr(tmanCompDescr)
                except Exception as e:
                    raise ValidateException(e.message, ValidationCodes.TANKMEN_MISMATCH, _packItemData(GUI_ITEM_TYPE.TANKMAN, (invID, tmanCompDescr)))

            return

        yield async.await(async.distributeLoopOverTicks(validateInventoryTankmenAsync(), minPerTick=10, maxPerTick=100, logID='validateOutfitsAsync', tickLength=0.0))
