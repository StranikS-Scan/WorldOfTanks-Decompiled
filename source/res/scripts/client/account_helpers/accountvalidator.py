# Embedded file name: scripts/client/account_helpers/AccountValidator.py
import BigWorld
import constants
from adisp import process, async
from items import vehicles, tankmen, ITEM_TYPE_NAMES
from debug_utils import *
from gui.shared import g_itemsCache
from gui.shared.gui_items import GUI_ITEM_TYPE

class ValidateException(Exception):

    def __init__(self, msg, code, itemData):
        super(ValidateException, self).__init__(msg)
        self.code = code
        self.itemData = itemData


class AccountValidator(object):

    class CODES:
        OK = 0
        INVENTORY_VEHICLE_MISMATCH = 1001
        INVENTORY_CHASSIS_MISMATCH = 1002
        INVENTORY_TURRET_MISMATCH = 1003
        INVENTORY_GUN_MISMATCH = 1004
        INVENTORY_ENGINE_MISMATCH = 1005
        INVENTORY_FUEL_TANK_MISMATCH = 1006
        INVENTORY_RADIO_MISMATCH = 1007
        INVENTORY_TANKMEN_MISMATCH = 1008
        INVENTORY_OPT_DEV_MISMATCH = 1009
        INVENTORY_SHELL_MISMATCH = 1010
        INVENTORY_EQ_MISMATCH = 1011
        INVENTORY_VEHICLE_CREW_MISMATCH = 1012

    @classmethod
    def __packItemData(cls, itemTypeID, itemData, *args):
        return (ITEM_TYPE_NAMES[itemTypeID], itemData) + args

    @async
    def __devSellInvalidVehicle(self, vehInvID, callback):

        def response(code):
            LOG_WARNING('Invalid vehicle selling result', vehInvID, code)
            callback(code >= 0)

        BigWorld.player().inventory.sellVehicle(vehInvID, True, [], [], response)

    @async
    def __devDismissInvalidTankmen(self, tmanInvID, callback):

        def response(code):
            LOG_WARNING('Invalid tankman dismissing result', tmanInvID, code)
            callback(code >= 0)

        BigWorld.player().inventory.dismissTankman(tmanInvID, response)

    def __validateEliteVehicleCDs(self):
        for vehicleCD in g_itemsCache.items.stats.eliteVehicles:
            try:
                g_itemsCache.items.getItemByCD(vehicleCD)
            except KeyError:
                LOG_ERROR('No vehicle corresponding to compact descriptor: {0}. Account data is inconsistent.'.format(vehicleCD))

    def __validateInventoryVehicles(self):
        inventory = g_itemsCache.items.inventory
        vehsInvData = g_itemsCache.items.inventory.getCacheValue(GUI_ITEM_TYPE.VEHICLE, {})
        for invID, vehCompDescr in vehsInvData.get('compDescr', {}).iteritems():
            try:
                vehicles.VehicleDescr(vehCompDescr)
            except Exception as e:
                raise ValidateException(e.message, self.CODES.INVENTORY_VEHICLE_MISMATCH, self.__packItemData(GUI_ITEM_TYPE.VEHICLE, (invID, vehCompDescr)))

        for invID, vehInvData in inventory.getItemsData(GUI_ITEM_TYPE.VEHICLE).iteritems():
            for idx, tankmanID in enumerate(vehInvData.crew):
                if idx >= len(vehInvData.descriptor.type.crewRoles):
                    raise ValidateException('Exceeded tankmen in tank', self.CODES.INVENTORY_VEHICLE_CREW_MISMATCH, self.__packItemData(GUI_ITEM_TYPE.VEHICLE, vehInvData, tankmanID))

    def __validateInventoryTankmen(self):
        tmenInvData = g_itemsCache.items.inventory.getCacheValue(GUI_ITEM_TYPE.TANKMAN, {})
        for invID, tmanCompDescr in tmenInvData.get('compDescr', {}).iteritems():
            try:
                tankmen.TankmanDescr(tmanCompDescr)
            except Exception as e:
                raise ValidateException(e.message, self.CODES.INVENTORY_TANKMEN_MISMATCH, self.__packItemData(GUI_ITEM_TYPE.TANKMAN, (invID, tmanCompDescr)))

    def __validateInvItem(self, itemTypeID, errorCode):
        for intCompactDescr, itemData in g_itemsCache.items.inventory.getItemsData(itemTypeID).iteritems():
            try:
                vehicles.getDictDescr(abs(intCompactDescr))
            except Exception as e:
                raise ValidateException(e.message, errorCode, self.__packItemData(itemTypeID, itemData))

    @async
    @process
    def validate(self, callback):
        yield lambda callback: callback(True)
        handlers = [lambda : self.__validateInvItem(GUI_ITEM_TYPE.CHASSIS, self.CODES.INVENTORY_CHASSIS_MISMATCH),
         lambda : self.__validateInvItem(GUI_ITEM_TYPE.TURRET, self.CODES.INVENTORY_TURRET_MISMATCH),
         lambda : self.__validateInvItem(GUI_ITEM_TYPE.GUI, self.CODES.INVENTORY_GUN_MISMATCH),
         lambda : self.__validateInvItem(GUI_ITEM_TYPE.ENGINE, self.CODES.INVENTORY_ENGINE_MISMATCH),
         lambda : self.__validateInvItem(GUI_ITEM_TYPE.FUEL_TANK, self.CODES.INVENTORY_FUEL_TANK_MISMATCH),
         lambda : self.__validateInvItem(GUI_ITEM_TYPE.RADIO, self.CODES.INVENTORY_RADIO_MISMATCH),
         lambda : self.__validateInvItem(GUI_ITEM_TYPE.OPTIONALDEVICE, self.CODES.INVENTORY_OPT_DEV_MISMATCH),
         lambda : self.__validateInvItem(GUI_ITEM_TYPE.SHELL, self.CODES.INVENTORY_SHELL_MISMATCH),
         lambda : self.__validateInvItem(GUI_ITEM_TYPE.EQUIPMENT, self.CODES.INVENTORY_EQ_MISMATCH),
         self.__validateEliteVehicleCDs,
         self.__validateInventoryTankmen,
         self.__validateInventoryVehicles]
        for handler in handlers:
            try:
                handler()
            except ValidateException as e:
                processed = False
                if constants.IS_DEVELOPMENT:
                    itemData = e.itemData[1]
                    if e.code == self.CODES.INVENTORY_TANKMEN_MISMATCH:
                        tmanInvID, _ = itemData
                        processed = yield self.__devDismissInvalidTankmen(tmanInvID)
                    elif e.code == self.CODES.INVENTORY_VEHICLE_CREW_MISMATCH:
                        processed = yield self.__devSellInvalidVehicle(itemData.invID)
                    elif e.code == self.CODES.INVENTORY_VEHICLE_MISMATCH:
                        venInvID, _ = itemData
                        processed = yield self.__devSellInvalidVehicle(venInvID)
                if not processed:
                    LOG_ERROR('There is exception while validating item', e.itemData)
                    LOG_ERROR(e.message)
                    callback(e.code)
                    return

        callback(self.CODES.OK)
