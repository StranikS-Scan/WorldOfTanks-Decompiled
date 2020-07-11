# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/account_helpers/account_validator.py
import logging
from functools import partial
import constants
from gui.shared.gui_items import GUI_ITEM_TYPE
from helpers import dependency
from items import vehicles, tankmen, ITEM_TYPE_NAMES
from items.vehicles import isItemWithCompactDescrExist
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

    def validate(self):
        handlers = (partial(self.__validateInvItem, GUI_ITEM_TYPE.CHASSIS, ValidationCodes.CHASSIS_MISMATCH),
         partial(self.__validateInvItem, GUI_ITEM_TYPE.TURRET, ValidationCodes.TURRET_MISMATCH),
         partial(self.__validateInvItem, GUI_ITEM_TYPE.GUN, ValidationCodes.GUN_MISMATCH),
         partial(self.__validateInvItem, GUI_ITEM_TYPE.ENGINE, ValidationCodes.ENGINE_MISMATCH),
         partial(self.__validateInvItem, GUI_ITEM_TYPE.FUEL_TANK, ValidationCodes.FUEL_TANK_MISMATCH),
         partial(self.__validateInvItem, GUI_ITEM_TYPE.RADIO, ValidationCodes.RADIO_MISMATCH),
         partial(self.__validateInvItem, GUI_ITEM_TYPE.OPTIONALDEVICE, ValidationCodes.OPT_DEV_MISMATCH),
         partial(self.__validateInvItem, GUI_ITEM_TYPE.SHELL, ValidationCodes.SHELL_MISMATCH),
         partial(self.__validateInvItem, GUI_ITEM_TYPE.EQUIPMENT, ValidationCodes.EQ_MISMATCH),
         self.__validateUnlocks,
         self.__validateInventoryVehicles,
         self.__validateInventoryOutfit,
         self.__validateInventoryTankmen,
         self.__validateEliteVehicleCDs)
        for handler in handlers:
            try:
                handler()
            except ValidateException as e:
                _logger.error('There is exception while validating item %s', e.itemData)
                return e.code

        return ValidationCodes.OK

    def __validateEliteVehicleCDs(self):
        for vehicleCD in self.itemsCache.items.stats.eliteVehicles:
            try:
                self.itemsCache.items.getItemByCD(vehicleCD)
            except KeyError:
                _logger.error('No vehicle corresponding to compact descriptor: %s. Account data is inconsistent.', vehicleCD)

    def __validateInventoryVehicles(self):
        inventory = self.itemsCache.items.inventory
        vehsInvData = inventory.getCacheValue(GUI_ITEM_TYPE.VEHICLE, {})
        for invID, vehCompDescr in vehsInvData.get('compDescr', {}).iteritems():
            try:
                vehicles.VehicleDescr(vehCompDescr)
            except Exception as e:
                raise ValidateException(e.message, ValidationCodes.VEHICLE_MISMATCH, _packItemData(GUI_ITEM_TYPE.VEHICLE, (invID, vehCompDescr)))

        for invID, vehInvData in inventory.getItemsData(GUI_ITEM_TYPE.VEHICLE).iteritems():
            for idx, tankmanID in enumerate(vehInvData.crew):
                if idx >= len(vehInvData.descriptor.type.crewRoles):
                    raise ValidateException('Exceeded tankmen in tank', ValidationCodes.VEHICLE_CREW_MISMATCH, _packItemData(GUI_ITEM_TYPE.VEHICLE, vehInvData, tankmanID))

    def __validateInventoryTankmen(self):
        tmenInvData = self.itemsCache.items.inventory.getCacheValue(GUI_ITEM_TYPE.TANKMAN, {})
        for invID, tmanCompDescr in tmenInvData.get('compDescr', {}).iteritems():
            try:
                tankmen.TankmanDescr(tmanCompDescr)
            except Exception as e:
                raise ValidateException(e.message, ValidationCodes.TANKMEN_MISMATCH, _packItemData(GUI_ITEM_TYPE.TANKMAN, (invID, tmanCompDescr)))

    def __validateInventoryOutfit(self):
        c11nData = self.itemsCache.items.inventory.getCacheValue(GUI_ITEM_TYPE.CUSTOMIZATION, {})
        for vehIntCD, outfitsData in c11nData.get(constants.CustomizationInvData.OUTFITS, {}).iteritems():
            vehicleData = self.itemsCache.items.inventory.getItemData(vehIntCD)
            if vehicleData is not None:
                vehicleCD = vehicleData.compDescr
            else:
                _, nationID, vehicleTypeID = vehicles.parseIntCompactDescr(vehIntCD)
                vehicleDesc = vehicles.VehicleDescr(typeID=(nationID, vehicleTypeID))
                vehicleCD = vehicleDesc.makeCompactDescr()
            for outfitCD in outfitsData.itervalues():
                try:
                    self.itemsFactory.createOutfit(strCompactDescr=outfitCD, vehicleCD=vehicleCD)
                except Exception as e:
                    raise ValidateException(e.message, ValidationCodes.OUTFIT_MISMATCH, _packItemData(GUI_ITEM_TYPE.CUSTOMIZATION, (vehIntCD, outfitCD)))

        return

    def __validateInvItem(self, itemTypeID, errorCode):
        for intCompactDescr, itemData in self.itemsCache.items.inventory.getCacheValue(itemTypeID, {}).iteritems():
            try:
                item = vehicles.getItemByCompactDescr(abs(intCompactDescr))
                if item.typeID != itemTypeID:
                    raise SoftException('Expected {} to be of type {}, got {} instead'.format(intCompactDescr, itemTypeID, item.typeID))
            except Exception as e:
                raise ValidateException(e.message, errorCode, _packItemData(itemTypeID, itemData))

    def __validateUnlocks(self):
        try:
            unlocks = self.itemsCache.items.stats.unlocks
            for cd in unlocks:
                if not isItemWithCompactDescrExist(cd):
                    raise SoftException('Unknown cd {} in unlocks'.format(cd))

        except Exception as e:
            raise ValidateException(e.message, ValidationCodes.UNLOCKS_MISMATCH, ())
