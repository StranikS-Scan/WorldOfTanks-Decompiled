# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/factories.py
import logging
import typing
from debug_utils import LOG_WARNING
from items import vehicles, EQUIPMENT_TYPES, getTypeOfCompactDescr
from items.components.c11n_constants import CustomizationType, DecalType
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.customization.c11n_items import Customization, Paint, Camouflage, Modification, Insignia, Decal, Emblem, Inscription, Style, ProjectionDecal, PersonalNumber, Sequence, Attachment
from vehicle_outfit.outfit import Outfit
from gui.shared.gui_items.dossier import TankmanDossier, AccountDossier, VehicleDossier
from gui.shared.gui_items.vehicle_modules import Shell, VehicleGun, VehicleChassis, VehicleEngine, VehicleRadio, VehicleTurret, VehicleFuelTank
from gui.shared.gui_items.artefacts import Equipment, BattleBooster, BattleAbility, OptionalDevice
from gui.shared.gui_items.Tankman import Tankman
from gui.shared.gui_items.Vehicle import Vehicle
import gui.shared.gui_items.badge as badges
from gui.shared.gui_items.loot_box import LootBox
from gui.shared.gui_items.crew_skin import CrewSkin
from gui.shared.gui_items.crew_book import CrewBook
from gui.veh_post_progression.models.progression import PostProgressionItem
from skeletons.gui.shared.gui_items import IGuiItemsFactory
if typing.TYPE_CHECKING:
    from items.vehicles import VehicleType
    from post_progression_common import VehicleState
_logger = logging.getLogger(__name__)
_NONE_GUI_ITEM_TYPE = 0

class GuiItemFactory(IGuiItemsFactory):

    def clear(self):
        pass

    def createGuiItem(self, itemTypeIdx, *args, **kwargs):
        item = None
        if itemTypeIdx in _ITEM_TYPES_MAPPING:
            item = _ITEM_TYPES_MAPPING[itemTypeIdx](self, *args, **kwargs)
        else:
            LOG_WARNING('Could not create GUI item with idx {}. There is no class associated with this idx.'.format(itemTypeIdx))
        return item

    def createGuiItemFromCompactDescr(self, compactDescr, *args, **kwargs):
        return self.createGuiItem(getTypeOfCompactDescr(compactDescr), *args, **kwargs)

    def createShell(self, intCompactDescr, count=0, proxy=None, isBoughtForCredits=False):
        return Shell(intCompactDescr, count, proxy, isBoughtForCredits)

    def createEquipment(self, intCompactDescr, proxy=None, isBoughtForCredits=False):
        descriptor = vehicles.getItemByCompactDescr(intCompactDescr)
        if descriptor.equipmentType == EQUIPMENT_TYPES.battleBoosters:
            cls = BattleBooster
        elif descriptor.equipmentType == EQUIPMENT_TYPES.battleAbilities:
            cls = BattleAbility
        else:
            cls = Equipment
        return cls(intCompactDescr, proxy, isBoughtForCredits)

    def createOptionalDevice(self, intCompactDescr, proxy=None):
        return OptionalDevice(intCompactDescr, proxy)

    def createVehicleGun(self, intCompactDescr, proxy=None, descriptor=None):
        return VehicleGun(intCompactDescr, proxy, descriptor)

    def createVehicleChassis(self, intCompactDescr, proxy=None, descriptor=None):
        return VehicleChassis(intCompactDescr, proxy, descriptor)

    def createVehicleTurret(self, intCompactDescr, proxy=None, descriptor=None):
        return VehicleTurret(intCompactDescr, proxy, descriptor)

    def createVehicleEngine(self, intCompactDescr, proxy=None, descriptor=None):
        return VehicleEngine(intCompactDescr, proxy, descriptor)

    def createVehicleRadio(self, intCompactDescr, proxy=None, descriptor=None):
        return VehicleRadio(intCompactDescr, proxy, descriptor)

    def createVehicleFuelTank(self, intCompactDescr, proxy=None, descriptor=None):
        return VehicleFuelTank(intCompactDescr, proxy, descriptor)

    def createVehicle(self, strCompactDescr=None, inventoryID=-1, typeCompDescr=None, proxy=None, extData=None, invData=None):
        return Vehicle(strCompactDescr, inventoryID, typeCompDescr, proxy, extData, invData)

    def createTankman(self, strCompactDescr, inventoryID=-1, vehicle=None, dismissedAt=None, proxy=None, vehicleSlotIdx=-1):
        return Tankman(strCompactDescr, inventoryID, vehicle, dismissedAt, proxy, vehicleSlotIdx)

    def createTankmanDossier(self, tmanDescr, tankmanDossierDescr, extDossier, playerDBID=None, currentVehicleItem=None):
        return TankmanDossier(tmanDescr, tankmanDossierDescr, extDossier, playerDBID, currentVehicleItem)

    def createAccountDossier(self, dossier, playerDBID=None, rated7x7Seasons=None):
        return AccountDossier(dossier, playerDBID, rated7x7Seasons)

    def createVehicleDossier(self, dossier, vehTypeCompDescr, playerDBID=None):
        return VehicleDossier(dossier, vehTypeCompDescr, playerDBID)

    def createBadge(self, descriptor, proxy=None, extraData=None):
        badgeData = descriptor.copy()
        if badges.CUSTOM_LOGIC_KEY in badgeData:
            className = badgeData.pop(badges.CUSTOM_LOGIC_KEY)
            cls = getattr(badges, className, None)
            if cls:
                return cls(badgeData, proxy=proxy, extraData=extraData)
            _logger.error('Wrong name of custom badge class %r', className)
        return badges.Badge(badgeData, proxy=proxy)

    def createLootBox(self, lootBoxID, lootBoxConfig, count):
        return LootBox(lootBoxID, lootBoxConfig, count)

    def createCustomization(self, intCompactDescr, proxy=None):
        descriptor = vehicles.getItemByCompactDescr(intCompactDescr)
        if descriptor.itemType == CustomizationType.CAMOUFLAGE:
            cls = Camouflage
        elif descriptor.itemType == CustomizationType.PAINT:
            cls = Paint
        elif descriptor.itemType == CustomizationType.MODIFICATION:
            cls = Modification
        elif descriptor.itemType == CustomizationType.STYLE:
            cls = Style
        elif descriptor.itemType == CustomizationType.DECAL:
            if descriptor.type == DecalType.EMBLEM:
                cls = Emblem
            elif descriptor.type == DecalType.INSCRIPTION:
                cls = Inscription
            else:
                LOG_WARNING('Unknown decal type', descriptor.type)
                cls = Decal
        elif descriptor.itemType == CustomizationType.PERSONAL_NUMBER:
            cls = PersonalNumber
        elif descriptor.itemType == CustomizationType.PROJECTION_DECAL:
            cls = ProjectionDecal
        elif descriptor.itemType == CustomizationType.INSIGNIA:
            cls = Insignia
        elif descriptor.itemType == CustomizationType.SEQUENCE:
            cls = Sequence
        elif descriptor.itemType == CustomizationType.ATTACHMENT:
            cls = Attachment
        else:
            LOG_WARNING('Unknown customization type', descriptor.itemType)
            cls = Customization
        return cls(intCompactDescr, proxy)

    def createOutfit(self, strCompactDescr=None, component=None, vehicleCD=''):
        if strCompactDescr is not None and component is not None:
            _logger.error("'strCompactDescr' and 'component' arguments are mutually exclusive!")
            return
        else:
            return Outfit(strCompactDescr=strCompactDescr, component=component, vehicleCD=vehicleCD)

    def createCrewSkin(self, intCompactDescr, proxy=None):
        return CrewSkin(intCompactDescr, proxy)

    def createCrewBook(self, intCompactDescr, proxy=None):
        return CrewBook(intCompactDescr, proxy)

    def createVehPostProgression(self, vehIntCD, state, vehType):
        if vehType is None:
            _, vehNationID, vehID = vehicles.parseIntCompactDescr(vehIntCD)
            vehType = vehicles.g_cache.vehicle(vehNationID, vehID)
        return PostProgressionItem(state, vehType)


_ITEM_TYPES_MAPPING = {_NONE_GUI_ITEM_TYPE: lambda *args, **kwargs: None,
 GUI_ITEM_TYPE.SHELL: GuiItemFactory.createShell,
 GUI_ITEM_TYPE.EQUIPMENT: GuiItemFactory.createEquipment,
 GUI_ITEM_TYPE.BATTLE_BOOSTER: GuiItemFactory.createEquipment,
 GUI_ITEM_TYPE.BATTLE_ABILITY: GuiItemFactory.createEquipment,
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
 GUI_ITEM_TYPE.BADGE: GuiItemFactory.createBadge,
 GUI_ITEM_TYPE.LOOT_BOX: GuiItemFactory.createLootBox,
 GUI_ITEM_TYPE.CUSTOMIZATION: GuiItemFactory.createCustomization,
 GUI_ITEM_TYPE.PAINT: GuiItemFactory.createCustomization,
 GUI_ITEM_TYPE.CAMOUFLAGE: GuiItemFactory.createCustomization,
 GUI_ITEM_TYPE.MODIFICATION: GuiItemFactory.createCustomization,
 GUI_ITEM_TYPE.DECAL: GuiItemFactory.createCustomization,
 GUI_ITEM_TYPE.STYLE: GuiItemFactory.createCustomization,
 GUI_ITEM_TYPE.PROJECTION_DECAL: GuiItemFactory.createCustomization,
 GUI_ITEM_TYPE.SEQUENCE: GuiItemFactory.createCustomization,
 GUI_ITEM_TYPE.ATTACHMENT: GuiItemFactory.createCustomization,
 GUI_ITEM_TYPE.OUTFIT: GuiItemFactory.createOutfit,
 GUI_ITEM_TYPE.CREW_SKINS: GuiItemFactory.createCrewSkin,
 GUI_ITEM_TYPE.CREW_BOOKS: GuiItemFactory.createCrewBook,
 GUI_ITEM_TYPE.VEH_POST_PROGRESSION: GuiItemFactory.createVehPostProgression}
