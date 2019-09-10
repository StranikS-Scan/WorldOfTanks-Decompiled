# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/artefacts.py
from itertools import chain, imap
import nations
from debug_utils import LOG_CURRENT_EXCEPTION
from gui.Scaleform.genConsts.STORE_CONSTANTS import STORE_CONSTANTS
from gui.shared.gui_items import GUI_ITEM_ECONOMY_CODE, GUI_ITEM_TYPE_NAMES, GUI_ITEM_TYPE
from gui.shared.gui_items.fitting_item import FittingItem
from gui.shared.gui_items.Tankman import isSkillLearnt
from gui.shared.gui_items.gui_item_economics import ItemPrice, ITEM_PRICE_EMPTY
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.RES_SHOP_EXT import RES_SHOP_EXT
from gui.shared.money import Money, Currency, MONEY_UNDEFINED
from gui.shared.utils.functions import stripColorTagDescrTags
from items import artefacts, vehicles as vehicleItems, tankmen
from items.tankmen import PERKS
from gui.Scaleform.locale.ARTEFACTS import ARTEFACTS
from gui.Scaleform.locale.ITEM_TYPES import ITEM_TYPES
from helpers import i18n
from soft_exception import SoftException
from items.vehicles import ABILITY_SLOTS_BY_VEHICLE_CLASS, getVehicleClassFromVehicleType
_TAG_NOT_FOR_SALE = 'notForSale'
_TAG_TRIGGER = 'trigger'
_TAG_CREW_BATTLE_BOOSTER = 'crewSkillBattleBooster'
_TAG_EQUEPMENT_BUILTIN = 'builtin'
_TAG_OPT_DEVICE_DELUXE = 'deluxe'
_TOKEN_OPT_DEVICE_SIMPLE = 'simple'
_TOKEN_OPT_DEVICE_DELUXE = 'deluxe'
_TOKEN_CREW_PERK_REPLACE = 'perk'
_TOKEN_CREW_PERK_BOOST = 'boost'
_MAX_CAMOUFLAGE_NET_BONUS = None

def getMaxCamouflageNetBonus():
    global _MAX_CAMOUFLAGE_NET_BONUS
    if _MAX_CAMOUFLAGE_NET_BONUS is None:
        maxNetBonusDelta = max((vehicle.invisibilityDeltas['camouflageNetBonus'] for vehicle in chain.from_iterable((imap(lambda vehicleTypeID, n=n: vehicleItems.g_cache.vehicle(n, vehicleTypeID), vehicleItems.g_list.getList(n)) for n in nations.INDICES.itervalues()))))
        _MAX_CAMOUFLAGE_NET_BONUS = 1.0 + maxNetBonusDelta
    return _MAX_CAMOUFLAGE_NET_BONUS


class VehicleArtefact(FittingItem):
    __slots__ = ()

    @property
    def level(self):
        pass

    @property
    def icon(self):
        return self.descriptor.icon[0]

    def formattedShortDescription(self, formatter):
        description = super(VehicleArtefact, self).shortDescription
        return description.format(**formatter)

    def _getShortInfo(self, vehicle=None, expanded=False):
        return stripColorTagDescrTags(self.shortDescription)

    @property
    def isForSale(self):
        return _TAG_NOT_FOR_SALE not in self.tags

    @property
    def tags(self):
        return self.descriptor.tags

    @property
    def kpi(self):
        return self.descriptor.kpi

    @property
    def isStimulator(self):
        return isinstance(self.descriptor, artefacts.Stimulator)

    @property
    def crewLevelIncrease(self):
        return 0.0 if not self.isStimulator else self.descriptor.crewLevelIncrease

    @property
    def isRemovingStun(self):
        return False

    def getShopIcon(self, size=STORE_CONSTANTS.ICON_SIZE_MEDIUM):
        return RES_SHOP_EXT.getArtefactIcon(size, self.descriptor.iconName)


class Equipment(VehicleArtefact):
    __slots__ = ()

    def _getAltPrice(self, buyPrice, proxy):
        return buyPrice.exchange(Currency.GOLD, Currency.CREDITS, proxy.exchangeRateForShellsAndEqs) if Currency.GOLD in buyPrice else super(Equipment, self)._getAltPrice(buyPrice, proxy)

    @property
    def icon(self):
        return '../maps/icons/artefact/%s.png' % super(Equipment, self).icon

    def getBonusIcon(self, size='small'):
        return RES_ICONS.getBonusIcon(size, self.name)

    @property
    def defaultLayoutValue(self):
        return (self.intCD if not self.isBoughtForAltPrice else -self.intCD, 1)

    @property
    def isRemovingStun(self):
        descr = self.descriptor
        return bool(descr.stunResistanceEffect or descr.stunResistanceDuration)

    @property
    def isBuiltIn(self):
        return _TAG_EQUEPMENT_BUILTIN in self.tags

    def isInstalled(self, vehicle, slotIdx=None):
        return vehicle.equipment.regularConsumables.containsIntCD(self.intCD, slotIdx)

    @property
    def isTrigger(self):
        return _TAG_TRIGGER in self.tags

    def mayInstall(self, vehicle, slotIdx=None):
        for idx, eq in enumerate(vehicle.equipment.regularConsumables):
            if slotIdx is not None and idx == slotIdx or eq is None:
                continue
            if eq.intCD != self.intCD:
                installPossible = eq.descriptor.checkCompatibilityWithActiveEquipment(self.descriptor)
                if installPossible:
                    installPossible = self.descriptor.checkCompatibilityWithEquipment(eq.descriptor)
                if not installPossible:
                    return (False, 'not with installed equipment')

        return self.descriptor.checkCompatibilityWithVehicle(vehicle.descriptor)

    def getInstalledVehicles(self, vehicles):
        result = set()
        for vehicle in vehicles:
            if vehicle.equipment.regularConsumables.containsIntCD(self.intCD):
                result.add(vehicle)

        return result

    def getConflictedEquipments(self, vehicle):
        conflictEqs = list()
        if self in vehicle.equipment.regularConsumables:
            return conflictEqs
        for e in vehicle.equipment.regularConsumables.getInstalledItems():
            compatibility = e.descriptor.checkCompatibilityWithActiveEquipment(self.descriptor)
            if compatibility:
                compatibility = self.descriptor.checkCompatibilityWithEquipment(e.descriptor)
            if not compatibility:
                conflictEqs.append(e)

        return conflictEqs

    def getGUIEmblemID(self):
        return super(Equipment, self).icon

    def isCrewBooster(self):
        return False

    def isAffectsOnVehicle(self, vehicle):
        return False

    def isOptionalDeviceCompatible(self, optionalDevice):
        return True

    def getAffectedSkillName(self):
        pass

    def isAffectedSkillLearnt(self, vehicle=None):
        return False

    def getCrewBoosterDescription(self, isPerkReplace, formatter=None):
        pass

    def getCrewBoosterAction(self, isPerkReplace):
        pass

    def getOptDeviceBoosterDescription(self, vehicle, valueFormatter=None):
        pass


class BattleBooster(Equipment):
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        super(BattleBooster, self).__init__(*args, **kwargs)
        self.itemTypeID = GUI_ITEM_TYPE.BATTLE_BOOSTER

    @property
    def isForSale(self):
        return False

    @property
    def userType(self):
        return i18n.makeString(ITEM_TYPES.BATTLEBOOSTER_NAME)

    @property
    def itemTypeName(self):
        return GUI_ITEM_TYPE_NAMES[self.itemTypeID]

    def isCrewBooster(self):
        return _TAG_CREW_BATTLE_BOOSTER in self.tags

    def isAffectsOnVehicle(self, vehicle):
        if self.isCrewBooster():
            return True
        for device in vehicle.optDevices:
            if self.isOptionalDeviceCompatible(device):
                return True

        return False

    def isInstalled(self, vehicle, slotIdx=None):
        return vehicle.equipment.battleBoosterConsumables.containsIntCD(self.intCD, slotIdx)

    def getInstalledVehicles(self, vehicles):
        result = set()
        for vehicle in vehicles:
            if vehicle.equipment.battleBoosterConsumables.containsIntCD(self.intCD):
                result.add(vehicle)

        return result

    def mayInstall(self, vehicle, slotIdx=None):
        return (True, None)

    def isOptionalDeviceCompatible(self, optionalDevice):
        return not self.isCrewBooster() and optionalDevice is not None and self.descriptor.getLevelParamsForDevice(optionalDevice.descriptor) is not None

    def getCrewBonus(self, vehicle):
        if self.isCrewBooster():
            return 0
        else:
            for device in vehicle.optDevices:
                if device is not None:
                    levelParams = self.descriptor.getLevelParamsForDevice(device.descriptor)
                    if levelParams is not None and 'crewLevelIncrease' in levelParams:
                        return levelParams[1]

            return 0

    def getAffectedSkillName(self):
        return self.descriptor.skillName if self.isCrewBooster() else None

    def getAffectedSkillUserName(self):
        return tankmen.getSkillsConfig().getSkill(self.getAffectedSkillName()).userString if self.isCrewBooster() else ''

    def isAffectedSkillLearnt(self, vehicle=None):
        return isSkillLearnt(self.getAffectedSkillName(), vehicle) if vehicle is not None else False

    def getCrewBoosterDescription(self, isPerkReplace, formatter=None):
        if not self.isCrewBooster():
            raise SoftException('This description is only for Crew Booster!')
        action = i18n.makeString(ARTEFACTS.CREWBATTLEBOOSTER_DESCR_REPLACE if isPerkReplace else ARTEFACTS.CREWBATTLEBOOSTER_DESCR_BOOST)
        if self.getAffectedSkillName() in PERKS:
            skillOrPerk = i18n.makeString(ARTEFACTS.CREWBATTLEBOOSTER_DESCR_PERK)
        else:
            skillOrPerk = i18n.makeString(ARTEFACTS.CREWBATTLEBOOSTER_DESCR_SKILL)
        skillName = i18n.makeString(ITEM_TYPES.tankman_skills(self.getAffectedSkillName()))
        description = i18n.makeString(ARTEFACTS.CREWBATTLEBOOSTER_DESCR_COMMON)
        if formatter is None:
            formatted = description.format(action=action, skillOrPerk=skillOrPerk, name=skillName, colorTagOpen='', colorTagClose='')
        else:
            formatted = description.format(action=action, skillOrPerk=skillOrPerk, name=skillName, **formatter)
        return formatted

    def getCrewBoosterAction(self, isPerkReplace):
        if not self.isCrewBooster():
            raise SoftException('This action description is only for Crew Booster!')
        token = _TOKEN_CREW_PERK_REPLACE if isPerkReplace else _TOKEN_CREW_PERK_BOOST
        return i18n.makeString(ARTEFACTS.getCrewActionForBattleBooster(self.name, token))

    def getOptDeviceBoosterDescription(self, vehicle, valueFormatter=None):
        if self.isCrewBooster():
            raise SoftException('This description is only for Opt. Dev. Booster!')
        deviceType = _TOKEN_OPT_DEVICE_SIMPLE
        if vehicle is not None:
            for device in vehicle.optDevices:
                if self.isOptionalDeviceCompatible(device) and device.isDeluxe():
                    deviceType = _TOKEN_OPT_DEVICE_DELUXE
                    break

        gain = i18n.makeString(ARTEFACTS.getDeviceGainForBattleBooster(self.name, deviceType))
        formatted = valueFormatter(gain) if valueFormatter is not None else gain
        return self.shortDescription % formatted

    def _getShortInfo(self, vehicle=None, expanded=False):
        return self.getCrewBoosterDescription(isPerkReplace=False, formatter=None) if self.isCrewBooster() else self.getOptDeviceBoosterDescription(vehicle=None, valueFormatter=None)

    def _getAltPrice(self, buyPrice, proxy):
        return MONEY_UNDEFINED


class BattleAbility(Equipment):
    __slots__ = ('_level', '_unlocked')

    def __init__(self, *args, **kwargs):
        super(BattleAbility, self).__init__(*args, **kwargs)
        self.itemTypeID = GUI_ITEM_TYPE.BATTLE_ABILITY
        self._level = 0

    @property
    def level(self):
        return self._level

    @property
    def userType(self):
        return i18n.makeString(ITEM_TYPES.BATTLEABILITY_NAME)

    @property
    def itemTypeName(self):
        return GUI_ITEM_TYPE_NAMES[self.itemTypeID]

    @property
    def shortDescription(self):
        return self.descriptor.shortDescription

    @property
    def fullDescription(self):
        return self.descriptor.longDescription

    @property
    def shortFilterAlert(self):
        return self.descriptor.shortFilterAlert

    def getSubTypeName(self):
        return self.descriptor.__class__.__name__

    def setLevel(self, value):
        self._level = value

    def isInstalled(self, vehicle, slotIdx=None):
        return vehicle.equipment.battleAbilityConsumables.containsIntCD(self.intCD, slotIdx)

    def getInstalledVehicles(self, vehicles):
        result = set()
        for vehicle in vehicles:
            if self.isInstalled(vehicle):
                result.add(vehicle)

        return result

    def mayPurchase(self, money):
        return (False, GUI_ITEM_ECONOMY_CODE.ITEM_NO_PRICE)

    def mayInstall(self, vehicle, slotIdx=None):
        slotCheck = slotIdx < ABILITY_SLOTS_BY_VEHICLE_CLASS[getVehicleClassFromVehicleType(vehicle.descriptor.type)]
        return (False, 'slot index exceeds limit of vehicle class') if not slotCheck else self.descriptor.checkCompatibilityWithVehicle(vehicle.descriptor)

    def _getAltPrice(self, buyPrice, proxy):
        return MONEY_UNDEFINED


class RemovableDevice(VehicleArtefact):
    __slots__ = ()

    @property
    def isRemovable(self):
        return self.descriptor.removable

    def getRemovalPrice(self, proxy=None):
        return ITEM_PRICE_EMPTY


class OptionalDevice(RemovableDevice):
    __slots__ = ('_GUIEmblemID',)

    def __init__(self, intCompactDescr, proxy=None):
        super(OptionalDevice, self).__init__(intCompactDescr, proxy)
        splitIcon = self.icon.split('/')
        labelWithExtension = splitIcon[len(splitIcon) - 1]
        label = labelWithExtension.split('.')[0]
        self._GUIEmblemID = label

    @property
    def shortDescription(self):
        description = super(OptionalDevice, self).shortDescription
        return description.format(colorTagOpen='', colorTagClose='')

    def isDeluxe(self):
        return _TAG_OPT_DEVICE_DELUXE in self.tags

    def getRemovalPrice(self, proxy=None):
        if not self.isRemovable and proxy is not None:
            if self.isDeluxe():
                cost = proxy.shop.paidDeluxeRemovalCost
                defaultCost = proxy.shop.defaults.paidDeluxeRemovalCost
                return ItemPrice(price=cost, defPrice=defaultCost)
            cost = proxy.shop.paidRemovalCost
            defaultCost = proxy.shop.defaults.paidRemovalCost
            return ItemPrice(price=Money(gold=cost), defPrice=Money(gold=defaultCost))
        else:
            return super(OptionalDevice, self).getRemovalPrice(proxy)

    def getBonusIcon(self, size='small'):
        iconName = self.descriptor.icon[0].split('/')[-1].split('.')[0]
        result = RES_ICONS.getBonusIcon(size, iconName)
        if result is None:
            result = RES_ICONS.getBonusIcon(size, self.name.split('_')[0])
        return result

    def isInstalled(self, vehicle, slotIdx=None):
        for idx, op in enumerate(vehicle.optDevices):
            if op is not None and self.intCD == op.intCD:
                if slotIdx is None:
                    return True
                return idx == slotIdx

        return super(OptionalDevice, self).isInstalled(vehicle, slotIdx)

    def hasSimilarDevicesInstalled(self, vehicle):
        optDevs = vehicle.optDevices
        for device in optDevs:
            if device is not None and not self.descriptor.checkCompatibilityWithOther(device.descriptor):
                return True

        return False

    def isSimilarDevice(self, other):
        return not self.descriptor.checkCompatibilityWithOther(other) if other is not None else False

    def mayInstall(self, vehicle, slotIdx=None):
        return vehicle.descriptor.mayInstallOptionalDevice(self.intCD, slotIdx)

    def mayRemove(self, vehicle):
        try:
            slotIdx = vehicle.optDevices.index(self)
            return vehicle.descriptor.mayRemoveOptionalDevice(slotIdx)
        except Exception:
            LOG_CURRENT_EXCEPTION()
            return (False, 'not installed on vehicle')

    def getInstalledVehicles(self, vehicles):
        result = set()
        for vehicle in vehicles:
            installed = [ (x.intCD if x is not None else None) for x in vehicle.optDevices ]
            if self.intCD in installed:
                result.add(vehicle)

        return result

    def getGUIEmblemID(self):
        return self._GUIEmblemID
