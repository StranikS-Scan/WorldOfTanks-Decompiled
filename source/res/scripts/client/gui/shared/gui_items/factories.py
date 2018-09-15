# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/factories.py
from debug_utils import LOG_WARNING
from items import vehicles, EQUIPMENT_TYPES, getTypeOfCompactDescr
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.dossier import TankmanDossier, AccountDossier, VehicleDossier
from gui.shared.gui_items.vehicle_modules import Shell, VehicleGun, VehicleChassis, VehicleEngine, VehicleRadio, VehicleTurret, VehicleFuelTank
from gui.shared.gui_items.artefacts import Equipment, BattleBooster, OptionalDevice
from gui.shared.gui_items.Tankman import Tankman
from gui.shared.gui_items.Vehicle import Vehicle
from gui.shared.gui_items.badge import Badge
from skeletons.gui.shared.gui_items import IGuiItemsFactory
_NONE_GUI_ITEM_TYPE = 0

class GuiItemFactory(IGuiItemsFactory):

    def clear(self):
        """
        Clears the service. At the moment do nothing
        """
        pass

    def createGuiItem(self, itemTypeIdx, *args, **kwargs):
        """
        Creates a GUI item by the given GUI item type ID.
        
        :param itemTypeIdx: type of item in GUI list
        :param args: args to be passed in constructor
        :param kwargs: kwargs to be passed in constructor
        
        :return: An instance of GUI item or None if GUI item type ID is invalid.
        """
        item = None
        factoryMethod = _ITEM_TYPES_MAPPING.get(itemTypeIdx)
        if factoryMethod is not None:
            item = factoryMethod(self, *args, **kwargs)
        else:
            LOG_WARNING('Could not create GUI item with idx {}. There is no class associated with this idx.'.format(itemTypeIdx))
        return item

    def createGuiItemFromCompactDescr(self, compactDescr, *args, **kwargs):
        """
        Creates a GUI item by the item compact descriptor.
        
        :param compactDescr: item compact descriptor.
        :param args: args to be passed in constructor
        :param kwargs: kwargs to be passed in constructor
        
        :return: An instance of GUI item or None if the compactDescr is invalid.
        """
        return self.createGuiItem(getTypeOfCompactDescr(compactDescr), *args, **kwargs)

    def createShell(self, intCompactDescr, count=0, defaultCount=0, proxy=None, isBoughtForCredits=False):
        """
        Creates Shell item by the given arguments.
        
        :param intCompactDescr: item int compact descriptor
        :param count: count of shells in ammo bay
        :param defaultCount: count default shells in ammo bay
        :param proxy:  instance of ItemsRequester
        :param isBoughtForCredits: is item has been bought for credits
        :return: an instance of Shell class.
        """
        return Shell(intCompactDescr, count, defaultCount, proxy, isBoughtForCredits)

    def createEquipment(self, intCompactDescr, proxy=None, isBoughtForCredits=False):
        """
        Creates equipment (Equipment or BattleBooster) item by the given compact descriptor.
        
        :param intCompactDescr: item int compact descriptor
        :param proxy:  instance of ItemsRequester
        :param isBoughtForCredits: is item has been bought for credits
        :return: an instance of Equipment or BattleBooster class.
        """
        descriptor = vehicles.getItemByCompactDescr(intCompactDescr)
        if descriptor.equipmentType == EQUIPMENT_TYPES.battleBoosters:
            classType = BattleBooster
        else:
            classType = Equipment
        return classType(intCompactDescr, proxy, isBoughtForCredits)

    def createOptionalDevice(self, intCompactDescr, proxy=None):
        """
        Creates OptionalDevice item by the given arguments.
        
        :param intCompactDescr: item int compact descriptor
        :param proxy:  instance of ItemsRequester
        :param isBoughtForCredits: is item has been bought for credits
        :return: an instance of OptionalDevice class.
        """
        return OptionalDevice(intCompactDescr, proxy)

    def createVehicleGun(self, intCompactDescr, proxy=None, descriptor=None):
        """
        Creates OptionalDevice item by the given arguments.
        
        :param intCompactDescr: item int compact descriptor
        :param proxy:  instance of ItemsRequester
        :param descriptor: vehicle module descriptor
        :return: an instance of VehicleGun class.
        """
        return VehicleGun(intCompactDescr, proxy, descriptor)

    def createVehicleChassis(self, intCompactDescr, proxy=None, descriptor=None):
        """
        Creates VehicleChassis item by the given arguments.
        
        :param intCompactDescr: item int compact descriptor
        :param proxy:  instance of ItemsRequester
        :param descriptor: vehicle module descriptor
        :return: an instance of VehicleChassis class.
        """
        return VehicleChassis(intCompactDescr, proxy, descriptor)

    def createVehicleTurret(self, intCompactDescr, proxy=None, descriptor=None):
        """
        Creates VehicleTurret item by the given arguments.
        
        :param intCompactDescr: item int compact descriptor
        :param proxy:  instance of ItemsRequester
        :param descriptor: vehicle module descriptor
        :return: an instance of VehicleTurret class.
        """
        return VehicleTurret(intCompactDescr, proxy, descriptor)

    def createVehicleEngine(self, intCompactDescr, proxy=None, descriptor=None):
        """
        Creates VehicleEngine item by the given arguments.
        
        :param intCompactDescr: item int compact descriptor
        :param proxy:  instance of ItemsRequester
        :param descriptor: vehicle module descriptor
        :return: an instance of VehicleEngine class.
        """
        return VehicleEngine(intCompactDescr, proxy, descriptor)

    def createVehicleRadio(self, intCompactDescr, proxy=None, descriptor=None):
        """
        Creates VehicleRadio item by the given arguments.
        
        :param intCompactDescr: item int compact descriptor
        :param proxy:  instance of ItemsRequester
        :param descriptor: vehicle module descriptor
        :return: an instance of VehicleRadio class.
        """
        return VehicleRadio(intCompactDescr, proxy, descriptor)

    def createVehicleFuelTank(self, intCompactDescr, proxy=None, descriptor=None):
        """
        Creates VehicleFuelTank item by the given arguments.
        
        :param intCompactDescr: item int compact descriptor
        :param proxy:  instance of ItemsRequester
        :param descriptor: vehicle module descriptor
        :return: an instance of VehicleFuelTank class.
        """
        return VehicleFuelTank(intCompactDescr, proxy, descriptor)

    def createVehicle(self, strCompactDescr=None, inventoryID=-1, typeCompDescr=None, proxy=None):
        """
        Creates Vehicle item by the given arguments.
        
        :param strCompactDescr: vehicle string compact descriptor
        :param inventoryID:  inventory ID
        :param typeCompDescr: vehicle type descriptor
        :param proxy:  instance of ItemsRequester
        :return: an instance of Vehicle class.
        """
        return Vehicle(strCompactDescr, inventoryID, typeCompDescr, proxy)

    def createTankman(self, strCompactDescr, inventoryID=-1, vehicle=None, dismissedAt=None, proxy=None):
        """
        Creates Tankman item by the given arguments.
        
        :param strCompactDescr: vehicle string compact descriptor
        :param inventoryID:  tankman's inventory id
        :param vehicle: tankman's vehicle where it has been seat
        :param dismissedAt:
        :param proxy:  instance of ItemsRequester
        :return: an instance of Tankman class.
        """
        return Tankman(strCompactDescr, inventoryID, vehicle, dismissedAt, proxy)

    def createTankmanDossier(self, tmanDescr, tankmanDossierDescr, extDossier, playerDBID=None, currentVehicleItem=None):
        """
        Creates TankmanDossier item by the given arguments.
        
        :param tmanDescr: tankman descriptor
        :param tankmanDossierDescr: tankman dossier descriptor
        :param extDossier: account or vehicle dossier descriptor. Used for some calculations.
        :param playerDBID: player DB ID
        :param currentVehicleItem: references to object of Vehicle (Fitting Item).
        
        :return: an instance of TankmanDossier class.
        """
        return TankmanDossier(tmanDescr, tankmanDossierDescr, extDossier, playerDBID, currentVehicleItem)

    def createAccountDossier(self, dossier, playerDBID=None, rated7x7Seasons=None, rankedCurrentSeason=None):
        """
        Creates AccountDossier item by the given arguments.
        
        :param dossier: account descriptor
        :param playerDBID: player database ID
        :param rated7x7Seasons: is rated 7x7 season
        :param rankedCurrentSeason: current season of ranked battles
        
        :return: an instance of AccountDossier class.
        """
        return AccountDossier(dossier, playerDBID, rated7x7Seasons, rankedCurrentSeason)

    def createVehicleDossier(self, dossier, vehTypeCompDescr, playerDBID=None, rankedCurrentSeason=None):
        """
        Creates VehicleDossier item by the given arguments.
        
        :param dossier: vehicle descriptor
        :param vehTypeCompDescr: vehicle type compact descriptor
        :param playerDBID: player database ID
        :param rankedCurrentSeason: current season of ranked battles
        
        :return: an instance of VehicleDossier class.
        """
        return VehicleDossier(dossier, vehTypeCompDescr, playerDBID, rankedCurrentSeason)

    def createBadge(self, descriptor, proxy=None):
        """
        Creates Badge item by the given arguments.
        
        :param descriptor: badge dict descriptor
        :param proxy: instance of ItemsRequester
        
        :return: an instance of Badge class.
        """
        return Badge(descriptor, proxy)


_ITEM_TYPES_MAPPING = {_NONE_GUI_ITEM_TYPE: lambda *args, **kwargs: None,
 GUI_ITEM_TYPE.SHELL: GuiItemFactory.createShell,
 GUI_ITEM_TYPE.EQUIPMENT: GuiItemFactory.createEquipment,
 GUI_ITEM_TYPE.BATTLE_BOOSTER: GuiItemFactory.createEquipment,
 GUI_ITEM_TYPE.OPTIONALDEVICE: GuiItemFactory.createOptionalDevice,
 GUI_ITEM_TYPE.GUN: GuiItemFactory.createVehicleGun,
 GUI_ITEM_TYPE.CHASSIS: GuiItemFactory.createVehicleChassis,
 GUI_ITEM_TYPE.TURRET: GuiItemFactory.createVehicleTurret,
 GUI_ITEM_TYPE.ENGINE: GuiItemFactory.createVehicleEngine,
 GUI_ITEM_TYPE.RADIO: GuiItemFactory.createVehicleRadio,
 GUI_ITEM_TYPE.FUEL_TANK: GuiItemFactory.createVehicleFuelTank,
 GUI_ITEM_TYPE.VEHICLE: GuiItemFactory.createVehicle,
 GUI_ITEM_TYPE.TANKMAN: GuiItemFactory.createTankman,
 GUI_ITEM_TYPE.TANKMAN_DOSSIER: GuiItemFactory.createTankmanDossier,
 GUI_ITEM_TYPE.ACCOUNT_DOSSIER: GuiItemFactory.createAccountDossier,
 GUI_ITEM_TYPE.VEHICLE_DOSSIER: GuiItemFactory.createVehicleDossier,
 GUI_ITEM_TYPE.BADGE: GuiItemFactory.createBadge}
