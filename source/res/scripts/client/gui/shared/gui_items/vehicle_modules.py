# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/vehicle_modules.py
import logging
import typing
from itertools import chain
import nations
from constants import SHELL_TYPES, SHELL_MECHANICS_TYPE
from gui.Scaleform.genConsts.FITTING_TYPES import FITTING_TYPES
from gui.Scaleform.genConsts.STORE_CONSTANTS import STORE_CONSTANTS
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.items_parameters import isDualAccuracy
from gui.shared.items_parameters.params_cache import g_paramsCache
from gui.shared.utils.functions import replaceHyphenToUnderscore
from gui.shared.gui_items.fitting_item import FittingItem, ICONS_MASK
from gui.shared.gui_items.vehicle_mechanics.factories import GunMechanicFactory, ChassisMechanicFactory, EngineMechanicFactory
from gui.shared.utils import GUN_CLIP, GUN_CAN_BE_CLIP, GUN_AUTO_RELOAD, GUN_CAN_BE_AUTO_RELOAD, GUN_DUAL_GUN, GUN_CAN_BE_DUAL_GUN, GUN_AUTO_SHOOT, GUN_CAN_BE_AUTO_SHOOT, GUN_CAN_BE_TWIN_GUN, GUN_TWIN_GUN
from gui.shared.money import Currency
from items import vehicles as veh_core
from shared_utils import CONST_CONTAINER, findFirst
if typing.TYPE_CHECKING:
    from gui.shared.gui_items.vehicle_mechanics.module_mechanic_item import ModuleMechanicItem
    from items.vehicles import VehicleDescr
    from vehicles.mechanics.mechanic_constants import VehicleMechanic
MODULE_TYPES_ORDER = ('vehicleGun', 'vehicleTurret', 'vehicleEngine', 'vehicleChassis', 'vehicleRadio', 'vehicleFuelTank')
MODULE_TYPES_ORDER_INDICES = dict(((n, i) for i, n in enumerate(MODULE_TYPES_ORDER)))
SHELL_TYPES_ORDER = (SHELL_TYPES.ARMOR_PIERCING,
 SHELL_TYPES.ARMOR_PIERCING_CR,
 SHELL_TYPES.HOLLOW_CHARGE,
 SHELL_TYPES.HIGH_EXPLOSIVE,
 SHELL_TYPES.SMOKE)
SHELL_TYPES_ORDER_INDICES = dict(((n, i) for i, n in enumerate(SHELL_TYPES_ORDER)))

class ModulesIconNames(CONST_CONTAINER):
    WHEELED_CHASSIS = 'wheeledChassis'
    CHASSIS = 'chassis'
    TURRET = 'tower'
    GUN = 'gun'
    ENGINE = 'engine'
    RADIO = 'radio'


_logger = logging.getLogger(__name__)

class VehicleModule(FittingItem):
    __slots__ = ('_vehicleModuleDescriptor',)
    _MECHANICS_FACTORY = ()

    def __init__(self, intCompactDescr, proxy=None, descriptor=None):
        super(VehicleModule, self).__init__(intCompactDescr, proxy)
        self._vehicleModuleDescriptor = descriptor

    @property
    def icon(self):
        return '' if not self.iconName else backport.image(R.images.gui.maps.icons.modules.dyn(self.iconName)())

    @property
    def iconName(self):
        pass

    @property
    def descriptor(self):
        return self._vehicleModuleDescriptor if self._vehicleModuleDescriptor is not None else super(VehicleModule, self).descriptor

    def getBonusIcon(self, size='small'):
        if size == 'small':
            return self.icon
        bigIconName = self.iconName + 'Big'
        return backport.image(R.images.gui.maps.icons.modules.dyn(bigIconName)())

    def getGUIEmblemID(self):
        return self.itemTypeName

    def getShopIcon(self, size=STORE_CONSTANTS.ICON_SIZE_MEDIUM):
        resID = R.images.gui.maps.shop.modules.num(size).dyn(replaceHyphenToUnderscore(self.itemTypeName))()
        return backport.image(resID) if resID != -1 else ''

    def getMechanics(self, vehDescr, withOverrides=False):
        return chain.from_iterable((factory.getMechanics(self, vehDescr, withOverrides=withOverrides) for factory in self._MECHANICS_FACTORY))

    def getModuleMechanicItems(self, vehDescr):
        mechanics = chain.from_iterable((factory.getMechanics(self, vehDescr, withOverrides=True) for factory in self._MECHANICS_FACTORY))
        return [ self.itemsFactory.createModuleMechanicItem(mechanic, self.itemTypeID) for mechanic in mechanics ]

    def getExtraIconInfo(self, vehDescr=None):
        status = findFirst(None, (item.getExtraStatuses(self) for item in self.getModuleMechanicItems(vehDescr)))
        return backport.image(R.images.gui.maps.icons.vehicle_hub.mechanics.x20x20.dyn(status)()) if status is not None else None

    def _sortByType(self, other):
        return MODULE_TYPES_ORDER_INDICES[self.itemTypeName] - MODULE_TYPES_ORDER_INDICES[other.itemTypeName]


class VehicleChassis(VehicleModule):
    __slots__ = ()
    _MECHANICS_FACTORY = (ChassisMechanicFactory,)

    def isInstalled(self, vehicle, slotIdx=None):
        return self.intCD == vehicle.chassis.intCD

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

    def isHydraulicWheeledChassis(self):
        return g_paramsCache.isChassisHydraulic(self.intCD) and g_paramsCache.isChassisWheeled(self.intCD)

    def isWheeledOnSpotRotationChassis(self):
        return g_paramsCache.isChassisWheeledOnSpotRotation(self.intCD)

    def hasAutoSiege(self):
        return g_paramsCache.isChassisAutoSiege(self.intCD)

    def isTrackWithinTrack(self):
        return g_paramsCache.isTrackWithinTrack(self.intCD)

    @property
    def iconName(self):
        return ModulesIconNames.WHEELED_CHASSIS if self.isWheeledChassis() else ModulesIconNames.CHASSIS

    def getGUIEmblemID(self):
        return FITTING_TYPES.VEHICLE_WHEELED_CHASSIS if self.isWheeledChassis() else super(VehicleChassis, self).getGUIEmblemID()

    def getShopIcon(self, size=STORE_CONSTANTS.ICON_SIZE_MEDIUM):
        if self.isWheeledChassis():
            resID = R.images.gui.maps.shop.modules.num(size).dyn(FITTING_TYPES.VEHICLE_WHEELED_CHASSIS)()
            if resID != -1:
                return backport.image(resID)
            return ''
        return super(VehicleChassis, self).getShopIcon(size)

    def _getShortInfoKey(self):
        return '#menu:descriptions/{}'.format(FITTING_TYPES.VEHICLE_WHEELED_CHASSIS if self.isWheeledChassis() else self.itemTypeName)


class VehicleTurret(VehicleModule):
    __slots__ = ()

    def isInstalled(self, vehicle, slotIdx=None):
        return self.intCD == vehicle.turret.intCD

    def mayInstall(self, vehicle, slotIdx=None, gunCD=0):
        if vehicle is None:
            return (False, 'not for current vehicle')
        else:
            optDevicesLayouts = None
            if vehicle.optDevices.setupLayouts.capacity > 1:
                optDevicesLayouts = []
                for setup in vehicle.optDevices.setupLayouts.setups.itervalues():
                    optDevicesLayouts.append(setup.getIntCDs())

            installPossible, reason = vehicle.descriptor.mayInstallTurret(self.intCD, gunCD, optDevicesLayouts=optDevicesLayouts)
            return (False, 'need gun') if not installPossible and reason == 'not for this vehicle type' else (installPossible, reason)

    def getInstalledVehicles(self, vehicles):
        result = set()
        for vehicle in vehicles:
            if self.intCD == vehicle.turret.intCD:
                result.add(vehicle)

        return result

    @property
    def iconName(self):
        return ModulesIconNames.TURRET

    @property
    def isGunCarriage(self):
        return self.descriptor.isGunCarriage


class VehicleGun(VehicleModule):
    __slots__ = ('_defaultAmmo', '_maxAmmo')
    _MECHANICS_FACTORY = (GunMechanicFactory,)

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

    def isAutoReloadableWithBoost(self, vehicleDescr=None):
        autoLoaderGunBoost = False
        if vehicleDescr:
            for gun in vehicleDescr.type.getGuns():
                if gun.compactDescr == self.intCD and gun.autoreloadHasBoost:
                    autoLoaderGunBoost = True

        return self.isAutoReloadable(vehicleDescr) and autoLoaderGunBoost

    def isAutoShoot(self, vehicleDescr=None):
        typeToCheck = GUN_AUTO_SHOOT if vehicleDescr is not None else GUN_CAN_BE_AUTO_SHOOT
        return self.getReloadingType(vehicleDescr) == typeToCheck

    def isDualGun(self, vehicleDescr=None):
        typeToCheck = GUN_DUAL_GUN if vehicleDescr is not None else GUN_CAN_BE_DUAL_GUN
        return self.getReloadingType(vehicleDescr) == typeToCheck

    def isTwinGun(self, vehicleDescr=None):
        typeToCheck = GUN_TWIN_GUN if vehicleDescr is not None else GUN_CAN_BE_TWIN_GUN
        return self.getReloadingType(vehicleDescr) == typeToCheck

    def isDamageMutable(self):
        return self.descriptor.isDamageMutable

    def isNonPiercingDamage(self):
        return any((shell.isNonPiercingDamageMechanics for shell in self.defaultAmmo))

    def hasDualAccuracy(self, vehicleDescr=None):
        return g_paramsCache.hasDualAccuracy(self.intCD, vehicleDescr.type.compactDescr) if vehicleDescr is not None else isDualAccuracy(self.descriptor)

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
    def iconName(self):
        return ModulesIconNames.GUN

    @property
    def userType(self):
        userType = super(VehicleGun, self).userType
        if self.isDualGun():
            return backport.text(R.strings.item_types.dualGun.name())
        return backport.text(R.strings.item_types.twinGun.name()) if self.isTwinGun() else userType

    def getGUIEmblemID(self):
        return FITTING_TYPES.VEHICLE_DUAL_GUN if self.isDualGun() else super(VehicleGun, self).getGUIEmblemID()

    def getDescriptor(self, vehDescr=None):
        vehicleGuns = vehDescr.type.getGuns() if vehDescr is not None else ()
        descriptor = findFirst(lambda gun: gun.compactDescr == self.intCD, vehicleGuns)
        return descriptor or self.descriptor

    def _getMaxAmmo(self):
        return self.descriptor.maxAmmo

    def _getDefaultAmmo(self, proxy):
        result = []
        shells = veh_core.getDefaultAmmoForGun(self.descriptor)
        for i in range(0, len(shells), 2):
            result.append(Shell(shells[i], count=shells[i + 1], proxy=proxy))

        return result

    def _getShortInfoKey(self, vehicleDescr=None):
        key = super(VehicleGun, self)._getShortInfoKey()
        if self.isAutoReloadable(vehicleDescr):
            return '/'.join((key, 'autoReload'))
        if self.isAutoShoot(vehicleDescr):
            return '/'.join((key, 'autoShoot'))
        if self.isDualGun(vehicleDescr):
            return '/'.join((key, 'dualGun'))
        return '/'.join((key, 'twinGun')) if self.isTwinGun(vehicleDescr) else key


class VehicleEngine(VehicleModule):
    __slots__ = ()
    _MECHANICS_FACTORY = (EngineMechanicFactory,)

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
        for eq in vehicle.consumables.installed.getItems():
            installPossible, _ = eq.descriptor.checkCompatibilityWithVehicle(vehicle.descriptor)
            if not installPossible:
                conflictEqs.append(eq)

        vehicle.descriptor.installComponent(oldModuleId)
        return conflictEqs

    def hasTurboshaftEngine(self, vehDescr=None):
        return vehDescr.hasTurboshaftEngine if vehDescr is not None else g_paramsCache.hasTurboshaftEngine(self.intCD)

    def hasRocketAcceleration(self, vehDescr=None):
        return vehDescr.hasRocketAcceleration if vehDescr is not None else g_paramsCache.hasRocketAcceleration(self.intCD)

    def hasRechargeableNitro(self):
        return g_paramsCache.hasRechargeableNitro(self.intCD)

    @property
    def iconName(self):
        return ModulesIconNames.ENGINE


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
    def iconName(self):
        return ModulesIconNames.RADIO


class Shell(FittingItem):
    __slots__ = ('_count',)

    def __init__(self, intCompactDescr, count=0, proxy=None, isBoughtForCredits=False):
        FittingItem.__init__(self, intCompactDescr, proxy, isBoughtForCredits)
        self._count = count

    @property
    def level(self):
        pass

    @property
    def count(self):
        return self._count

    @count.setter
    def count(self, value):
        self._count = value

    @property
    def type(self):
        return self.descriptor.kind

    @property
    def mechanics(self):
        return self.descriptor.type.mechanics

    @property
    def isModernMechanics(self):
        return self.type == SHELL_TYPES.HIGH_EXPLOSIVE and self.mechanics == SHELL_MECHANICS_TYPE.MODERN

    @property
    def isNonPiercingDamageMechanics(self):
        return self.mechanics == SHELL_MECHANICS_TYPE.NON_PIERCING_DAMAGE

    @property
    def longUserName(self):
        return self._getFormatLongUserName('kinds')

    @property
    def longUserNameAbbr(self):
        return self._getFormatLongUserName('kindsAbbreviation')

    @property
    def icon(self):
        return ICONS_MASK[:-4] % {'type': self.itemTypeName,
         'subtype': 'small/',
         'unicName': self.descriptor.icon[0]}

    @property
    def defaultLayoutValue(self):
        return (self.intCD if not self.isBoughtForAltPrice else -self.intCD, self.count)

    def isDamageMutable(self):
        return self.descriptor.isDamageMutable

    def getAdvancedTooltipKey(self):
        return (self.type,
         self.isModernMechanics,
         self.isNonPiercingDamageMechanics,
         self.isDamageMutable())

    def getBonusIcon(self, size='small'):
        sizeFldr = R.images.gui.maps.icons.shell.dyn(size)
        if not sizeFldr:
            _logger.warn('Shell %s icon for size %s doesnt exists!', self.descriptor.iconName, size)
            return ''
        return backport.image(sizeFldr.dyn(self.descriptor.iconName)())

    def getGUIEmblemID(self):
        return self.descriptor.iconName

    def getShopIcon(self, size=STORE_CONSTANTS.ICON_SIZE_MEDIUM):
        resID = R.images.gui.maps.shop.shells.num(size).dyn(replaceHyphenToUnderscore(self.descriptor.iconName))()
        return backport.image(resID) if resID != -1 else ''

    def isInstalled(self, vehicle, slotIdx=None):
        for shell in vehicle.shells.installed.getItems():
            if self.intCD == shell.intCD:
                return True

        return super(Shell, self).isInstalled(vehicle, slotIdx)

    def isInSetup(self, vehicle, setupIndex=None, slotIdx=None):
        return vehicle.shells.setupLayouts.containsIntCD(self.intCD, setupIndex, slotIdx)

    def isInOtherLayout(self, vehicle):
        return vehicle.shells.setupLayouts.isInOtherLayout(self)

    def _getAltPrice(self, buyPrice, proxy):
        return buyPrice.exchange(Currency.GOLD, Currency.CREDITS, proxy.exchangeRateForShellsAndEqs, useDiscounts=False) if Currency.GOLD in buyPrice else super(Shell, self)._getAltPrice(buyPrice, proxy)

    def _getFormatLongUserName(self, kind):
        if self.nationID == nations.INDICES['germany']:
            caliber = float(self.descriptor.caliber) / 10
            dimension = backport.text(R.strings.item_types.shell.dimension.sm())
        elif self.nationID == nations.INDICES['usa']:
            caliber = float(self.descriptor.caliber) / 25.4
            dimension = backport.text(R.strings.item_types.shell.dimension.inch())
        else:
            caliber = self.descriptor.caliber
            dimension = backport.text(R.strings.item_types.shell.dimension.mm())
        return backport.text(R.strings.item_types.shell.name(), kind=backport.text(R.strings.item_types.shell.dyn(kind).dyn(self.descriptor.kind)()), name=self.userName, caliber=backport.getNiceNumberFormat(caliber), dimension=dimension)

    def _getShortInfoKey(self):
        return '#menu:descriptions/mutableDamageShell' if self.isDamageMutable() else super(Shell, self)._getShortInfoKey()

    def _sortByType(self, other):
        return SHELL_TYPES_ORDER_INDICES[self.type] - SHELL_TYPES_ORDER_INDICES[other.type]
