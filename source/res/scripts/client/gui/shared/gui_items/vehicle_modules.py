# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/vehicle_modules.py
import BigWorld
from constants import SHELL_TYPES
from gui.Scaleform.genConsts.FITTING_TYPES import FITTING_TYPES
from gui.Scaleform.genConsts.STORE_CONSTANTS import STORE_CONSTANTS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.RES_SHOP_EXT import RES_SHOP_EXT
from gui.shared.items_parameters.params_cache import g_paramsCache
import nations
from helpers import i18n
from items import vehicles as veh_core
from gui.shared.gui_items.fitting_item import FittingItem, ICONS_MASK
from gui.shared.utils import GUN_CLIP, GUN_CAN_BE_CLIP, GUN_AUTO_RELOAD, GUN_CAN_BE_AUTO_RELOAD
from gui.shared.money import Currency
MODULE_TYPES_ORDER = ('vehicleGun', 'vehicleTurret', 'vehicleEngine', 'vehicleChassis', 'vehicleRadio', 'vehicleFuelTank')
MODULE_TYPES_ORDER_INDICES = dict(((n, i) for i, n in enumerate(MODULE_TYPES_ORDER)))
SHELL_TYPES_ORDER = (SHELL_TYPES.ARMOR_PIERCING,
 SHELL_TYPES.ARMOR_PIERCING_CR,
 SHELL_TYPES.HOLLOW_CHARGE,
 SHELL_TYPES.HIGH_EXPLOSIVE)
SHELL_TYPES_ORDER_INDICES = dict(((n, i) for i, n in enumerate(SHELL_TYPES_ORDER)))

class VehicleModule(FittingItem):
    __slots__ = ('_vehicleModuleDescriptor',)

    def __init__(self, intCompactDescr, proxy=None, descriptor=None):
        super(VehicleModule, self).__init__(intCompactDescr, proxy)
        self._vehicleModuleDescriptor = descriptor

    @property
    def icon(self):
        pass

    @property
    def descriptor(self):
        return self._vehicleModuleDescriptor if self._vehicleModuleDescriptor is not None else super(VehicleModule, self).descriptor

    def _sortByType(self, other):
        return MODULE_TYPES_ORDER_INDICES[self.itemTypeName] - MODULE_TYPES_ORDER_INDICES[other.itemTypeName]

    def getGUIEmblemID(self):
        return self.itemTypeName

    def getShopIcon(self, size=STORE_CONSTANTS.ICON_SIZE_MEDIUM):
        return RES_SHOP_EXT.getModuleIcon(size, self.itemTypeName)


class VehicleChassis(VehicleModule):
    __slots__ = ()

    def isInstalled(self, vehicle, slotIdx=None):
        return self.intCD == vehicle.chassis.intCD

    def mayInstall(self, vehicle, slotIdx=None):
        installPossible, reason = FittingItem.mayInstall(self, vehicle, slotIdx)
        return (False, 'too heavy chassis') if not installPossible and reason == 'too heavy' else (installPossible, reason)

    def getInstalledVehicles(self, vehicles):
        result = set()
        for vehicle in vehicles:
            if self.intCD == vehicle.chassis.intCD:
                result.add(vehicle)

        return result

    def isHydraulicChassis(self):
        return g_paramsCache.isChassisHydraulic(self.intCD)

    def isWheeledChassis(self):
        return g_paramsCache.isChassisWheeled(self.intCD)

    @property
    def icon(self):
        return RES_ICONS.MAPS_ICONS_MODULES_WHEELEDCHASSIS if self.isWheeledChassis() else RES_ICONS.MAPS_ICONS_MODULES_CHASSIS

    def getExtraIconInfo(self, _=None):
        if self.isHydraulicChassis():
            if self.isWheeledChassis():
                return RES_ICONS.MAPS_ICONS_MODULES_HYDRAULICWHEELEDCHASSISICON
            return RES_ICONS.MAPS_ICONS_MODULES_HYDRAULICCHASSISICON
        else:
            return None

    def getGUIEmblemID(self):
        return FITTING_TYPES.VEHICLE_WHEELED_CHASSIS if self.isWheeledChassis() else super(VehicleChassis, self).getGUIEmblemID()

    def getShopIcon(self, size=STORE_CONSTANTS.ICON_SIZE_MEDIUM):
        return RES_SHOP_EXT.getModuleIcon(size, FITTING_TYPES.VEHICLE_WHEELED_CHASSIS) if self.isWheeledChassis() else super(VehicleChassis, self).getShopIcon(size)

    def _getShortInfoKey(self):
        return '#menu:descriptions/{}'.format(FITTING_TYPES.VEHICLE_WHEELED_CHASSIS if self.isWheeledChassis() else self.itemTypeName)


class VehicleTurret(VehicleModule):
    __slots__ = ()

    def isInstalled(self, vehicle, slotIdx=None):
        return self.intCD == vehicle.turret.intCD

    def mayInstall(self, vehicle, slotIdx=None, gunCD=0):
        installPossible, reason = vehicle.descriptor.mayInstallTurret(self.intCD, gunCD)
        return (False, 'need gun') if not installPossible and reason == 'not for this vehicle type' else (installPossible, reason)

    def getInstalledVehicles(self, vehicles):
        result = set()
        for vehicle in vehicles:
            if self.intCD == vehicle.turret.intCD:
                result.add(vehicle)

        return result

    @property
    def icon(self):
        return RES_ICONS.MAPS_ICONS_MODULES_TOWER

    @property
    def isGunCarriage(self):
        return self.descriptor.isGunCarriage


class VehicleGun(VehicleModule):
    __slots__ = ('_defaultAmmo', '_maxAmmo')

    def __init__(self, intCompactDescr, proxy=None, descriptor=None):
        super(VehicleGun, self).__init__(intCompactDescr, proxy, descriptor)
        self._defaultAmmo = self._getDefaultAmmo(proxy)
        self._maxAmmo = self._getMaxAmmo()

    def isInstalled(self, vehicle, slotIdx=None):
        return self.intCD == vehicle.gun.intCD

    def mayInstall(self, vehicle, slotIdx=None):
        installPossible, reason = FittingItem.mayInstall(self, vehicle)
        return (False, 'need turret') if not installPossible and reason == 'not for current vehicle' else (installPossible, reason)

    def getReloadingType(self, vehicleDescr=None):
        return g_paramsCache.getGunReloadingSystemType(self.intCD, vehicleDescr.type.compactDescr if vehicleDescr is not None else None)

    def isClipGun(self, vehicleDescr=None):
        typeToCheck = GUN_CLIP if vehicleDescr is not None else GUN_CAN_BE_CLIP
        return self.getReloadingType(vehicleDescr) == typeToCheck

    def isAutoReloadable(self, vehicleDescr=None):
        typeToCheck = GUN_AUTO_RELOAD if vehicleDescr is not None else GUN_CAN_BE_AUTO_RELOAD
        return self.getReloadingType(vehicleDescr) == typeToCheck

    def getInstalledVehicles(self, vehicles):
        result = set()
        for vehicle in vehicles:
            if self.intCD == vehicle.gun.intCD:
                result.add(vehicle)

        return result

    @property
    def defaultAmmo(self):
        return self._defaultAmmo

    @property
    def maxAmmo(self):
        return self._maxAmmo

    @property
    def icon(self):
        return RES_ICONS.MAPS_ICONS_MODULES_GUN

    def getExtraIconInfo(self, vehDescr=None):
        if self.isClipGun(vehDescr):
            return RES_ICONS.MAPS_ICONS_MODULES_MAGAZINEGUNICON
        else:
            return RES_ICONS.MAPS_ICONS_MODULES_AUTOLOADERGUN if self.isAutoReloadable(vehDescr) else None

    def _getMaxAmmo(self):
        return self.descriptor.maxAmmo

    def _getDefaultAmmo(self, proxy):
        result = []
        shells = veh_core.getDefaultAmmoForGun(self.descriptor)
        for i in range(0, len(shells), 2):
            result.append(Shell(shells[i], defaultCount=shells[i + 1], proxy=proxy))

        return result

    def _getShortInfoKey(self, vehicleDescr=None):
        key = super(VehicleGun, self)._getShortInfoKey()
        return '/'.join((key, 'autoReload')) if self.isAutoReloadable(vehicleDescr) else key


class VehicleEngine(VehicleModule):
    __slots__ = ()

    def isInstalled(self, vehicle, slotIdx=None):
        return self.intCD == vehicle.engine.intCD

    def getInstalledVehicles(self, vehicles):
        result = set()
        for vehicle in vehicles:
            if self.intCD == vehicle.engine.intCD:
                result.add(vehicle)

        return result

    def getConflictedEquipments(self, vehicle):
        conflictEqs = list()
        oldModuleId = vehicle.engine.intCD
        vehicle.descriptor.installComponent(self.intCD)
        for eq in vehicle.equipment.regularConsumables.getInstalledItems():
            installPossible, _ = eq.descriptor.checkCompatibilityWithVehicle(vehicle.descriptor)
            if not installPossible:
                conflictEqs.append(eq)

        vehicle.descriptor.installComponent(oldModuleId)
        return conflictEqs

    @property
    def icon(self):
        return RES_ICONS.MAPS_ICONS_MODULES_ENGINE


class VehicleFuelTank(VehicleModule):
    __slots__ = ()

    def isInstalled(self, vehicle, slotIdx=None):
        return self.intCD == vehicle.fuelTank.intCD

    def getInstalledVehicles(self, vehicles):
        result = set()
        for vehicle in vehicles:
            if self.intCD == vehicle.fuelTank.intCD:
                result.add(vehicle)

        return result


class VehicleRadio(VehicleModule):
    __slots__ = ()

    def isInstalled(self, vehicle, slotIdx=None):
        return self.intCD == vehicle.radio.intCD

    def getInstalledVehicles(self, vehicles):
        result = set()
        for vehicle in vehicles:
            if self.intCD == vehicle.radio.intCD:
                result.add(vehicle)

        return result

    @property
    def icon(self):
        return RES_ICONS.MAPS_ICONS_MODULES_RADIO


class Shell(FittingItem):
    __slots__ = ('_count', '_defaultCount')

    def __init__(self, intCompactDescr, count=0, defaultCount=0, proxy=None, isBoughtForCredits=False):
        FittingItem.__init__(self, intCompactDescr, proxy, isBoughtForCredits)
        self._count = count
        self._defaultCount = defaultCount

    @property
    def level(self):
        pass

    def _getAltPrice(self, buyPrice, proxy):
        return buyPrice.exchange(Currency.GOLD, Currency.CREDITS, proxy.exchangeRateForShellsAndEqs) if Currency.GOLD in buyPrice else super(Shell, self)._getAltPrice(buyPrice, proxy)

    def _getFormatLongUserName(self, kind):
        if self.nationID == nations.INDICES['germany']:
            caliber = float(self.descriptor.caliber) / 10
            dimension = i18n.makeString('#item_types:shell/dimension/sm')
        elif self.nationID == nations.INDICES['usa']:
            caliber = float(self.descriptor.caliber) / 25.4
            dimension = i18n.makeString('#item_types:shell/dimension/inch')
        else:
            caliber = self.descriptor.caliber
            dimension = i18n.makeString('#item_types:shell/dimension/mm')
        return i18n.makeString('#item_types:shell/name') % {'kind': i18n.makeString('#item_types:shell/%s/%s' % (kind, self.descriptor.kind)),
         'name': self.userName,
         'caliber': BigWorld.wg_getNiceNumberFormat(caliber),
         'dimension': dimension}

    @property
    def count(self):
        return self._count

    @property
    def defaultCount(self):
        return self._defaultCount

    @property
    def type(self):
        return self.descriptor.kind

    @property
    def longUserName(self):
        return self._getFormatLongUserName('kinds')

    @property
    def longUserNameAbbr(self):
        return self._getFormatLongUserName('kindsAbbreviation')

    @property
    def icon(self):
        return ICONS_MASK[:-4] % {'type': self.itemTypeName,
         'subtype': '',
         'unicName': self.descriptor.icon[0]}

    def getShopIcon(self, size=STORE_CONSTANTS.ICON_SIZE_MEDIUM):
        return RES_SHOP_EXT.getShellIcon(size, self.descriptor.iconName)

    def getGUIEmblemID(self):
        return self.type

    @property
    def defaultLayoutValue(self):
        return (self.intCD if not self.isBoughtForAltPrice else -self.intCD, self.defaultCount)

    def isInstalled(self, vehicle, slotIdx=None):
        for shell in vehicle.shells:
            if self.intCD == shell.intCD:
                return True

        return super(Shell, self).isInstalled(vehicle, slotIdx)

    def _sortByType(self, other):
        return SHELL_TYPES_ORDER_INDICES[self.type] - SHELL_TYPES_ORDER_INDICES[other.type]
