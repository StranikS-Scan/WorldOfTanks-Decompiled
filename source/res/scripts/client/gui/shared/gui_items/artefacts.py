# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/artefacts.py
from debug_utils import LOG_CURRENT_EXCEPTION
from gui.shared.gui_items import GUI_ITEM_TYPE_NAMES, GUI_ITEM_TYPE
from gui.shared.gui_items.fitting_item import FittingItem
from gui.shared.gui_items.Tankman import isSkillLearnt
from gui.shared.gui_items.gui_item_economics import ItemPrice, ItemPrices, ITEM_PRICE_EMPTY, ITEM_PRICES_EMPTY
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.shared.money import Money, Currency, MONEY_UNDEFINED
from items import artefacts
from items.tankmen import PERKS
from gui.Scaleform.locale.ARTEFACTS import ARTEFACTS
from gui.Scaleform.locale.ITEM_TYPES import ITEM_TYPES
from helpers import i18n
_TAG_NOT_FOR_SALE = 'notForSale'
_TAG_CREW_BATTLE_BOOSTER = 'crewSkillBattleBooster'
_TAG_OPT_DEVICE_DELUXE = 'deluxe'
_TOKEN_OPT_DEVICE_SIMPLE = 'simple'
_TOKEN_OPT_DEVICE_DELUXE = 'deluxe'
_TOKEN_CREW_PERK_REPLACE = 'perk'
_TOKEN_CREW_PERK_BOOST = 'boost'

class VehicleArtefact(FittingItem):
    __slots__ = ()

    @property
    def level(self):
        """Return 0 because equipments and optional devices have no level."""
        pass

    @property
    def icon(self):
        return self.descriptor.icon[0]

    def formattedShortDescription(self, formatter):
        """
        Gets original description string and applies the formatter.
        :param formatter: dict containing colorTagOpen and colorTagClose
        :return: formatted description
        """
        description = super(VehicleArtefact, self).shortDescription
        return description.format(**formatter)

    def _getShortInfo(self, vehicle=None, expanded=False):
        return self.shortDescription

    @property
    def isForSale(self):
        """
        Some items can not be sold, they will have 'notForSale' tag in xml file.
        After moving to Money 2.0 concept this property can be removed and sellPrice.isDefined() will
        be used to replace this property.
        :return: True if the item can be sold, False otherwise
        """
        return _TAG_NOT_FOR_SALE not in self.tags

    @property
    def tags(self):
        """
        Returns list of tags, associated with this item.
        :return: frozenset of tags(strings), defined in the equipment.xml for the item.
        """
        return self.descriptor.tags

    @property
    def isStimulator(self):
        """ Is item stimulator which can increase crew role levels. """
        return isinstance(self.descriptor, artefacts.Stimulator)

    @property
    def crewLevelIncrease(self):
        """ Value of crew role levels increasing. """
        return 0 if not self.isStimulator else self.descriptor.crewLevelIncrease

    @property
    def isRemovingStun(self):
        return False


class Equipment(VehicleArtefact):
    __slots__ = ()

    def _getAltPrice(self, buyPrice, proxy):
        """
        Returns an alternative price (right now in Currency.CREDITS) based on the original buy price and equipments
        gold-credits exchange rate defined in the shop.
        
        @param buyPrice: buy price in Money
        @param proxy: shop stats proxy, see IShopCommonStats
        @return: alternative price in Money (right now in credits)
        """
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

    def isInstalled(self, vehicle, slotIdx=None):
        return vehicle.equipment.regularConsumables.containsIntCD(self.intCD, slotIdx)

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
    def userType(self):
        return i18n.makeString(ITEM_TYPES.BATTLEBOOSTER_NAME)

    @property
    def itemTypeName(self):
        return GUI_ITEM_TYPE_NAMES[self.itemTypeID]

    def isCrewBooster(self):
        """
        Check whether it crew or opt.dev battle booster
        :return: boolean result
        """
        return _TAG_CREW_BATTLE_BOOSTER in self.tags

    def isAffectsOnVehicle(self, vehicle):
        """
        Determines if the vehicle has optional devices for which this booster has effects.
        :param vehicle: vehicle to get optional devices
        """
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
        """
        Check if the provided opt. device is suitable for this booster(it means the booster affects this device).
        :param optionalDevice: instance of OptionalDevice Gui item
        :return True if suitable, False otherwise
        """
        return not self.isCrewBooster() and optionalDevice is not None and self.descriptor.getLevelParamsForDevice(optionalDevice.descriptor) is not None

    def getCrewBonus(self, vehicle):
        """
        Calculates crew bonus percent. For battle booster it is necessary to check each optional device on vehicle,
        due to this percent can depend on type of opt. device.
        :param vehicle: gui_items.Vehicle instances
        :return: float value
        """
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
        """
        Returns a skill name, for which booster has effect
        :return: string or None
        """
        return self.descriptor.skillName if self.isCrewBooster() else None

    def isAffectedSkillLearnt(self, vehicle=None):
        """
        Check whether descriptor.skillName is learnt if vehicle is provided.
        :param vehicle: instance of gui_item.Vehicle
        :return: boolean result
        """
        return isSkillLearnt(self.getAffectedSkillName(), vehicle) if vehicle is not None else False

    def getCrewBoosterDescription(self, isPerkReplace, formatter=None):
        """
        Constructs crew booster description. There can be perk replace or perk boost text.
        :param isPerkReplace: should 'perk replace' or 'perk boost' text be returned
        :param formatter: pass function to format the result, None - without formatting
        :return: formatted string
        """
        assert self.isCrewBooster(), 'This description is only for Crew Booster!'
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
        """
        Constructs 'action' description for crew booster. It is used in tooltip and booster
        buy window. The text is little bit different than in 'getCrewBoosterDescription' method
        :param isPerkReplace: should 'perk replace' or 'perk boost' text be returned
        :return: string without formatting
        """
        assert self.isCrewBooster(), 'This action description is only for Crew Booster!'
        token = _TOKEN_CREW_PERK_REPLACE if isPerkReplace else _TOKEN_CREW_PERK_BOOST
        return i18n.makeString(ARTEFACTS.getCrewActionForBattleBooster(self.name, token))

    def getOptDeviceBoosterDescription(self, vehicle, valueFormatter=None):
        """
        Constructs booster description for an optional device.
        The gain value is depending on type of opt. device: regular or deluxe
        :param vehicle: information is gathered from this object.
        :param valueFormatter: pass function to format the result, None - without formatting
        :return: formatted string
        """
        assert not self.isCrewBooster(), 'This description is only for Opt. Dev. Booster!'
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
        """
        Returns an alternative price based on the original buy price and equipments exchange rate defined in the shop.
        Right now BattleBooster are not available for alternative price and can be bought only for Currency.CRYSTAL.
        
        @param buyPrice: buy price in Money
        @param proxy: shop stats proxy, see IShopCommonStats
        @return: alternative price in Money (right now in credits)
        """
        return MONEY_UNDEFINED


class RemovableDevice(VehicleArtefact):
    __slots__ = ()

    @property
    def isRemovable(self):
        """
        Indicates whether the item can be removed from vehicle for free.
        :return: bool
        """
        return self.descriptor.removable

    def getRemovalPrice(self, proxy=None):
        """
        The price to remove this device from vehicle, by default - empty price (remove for free)
        :param proxy: instance of ItemsRequester
        :return: ItemPrice
        """
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
        """
        By default return the string without value formatting. See artefacts.po
        """
        description = super(OptionalDevice, self).shortDescription
        return description.format(colorTagOpen='', colorTagClose='')

    def isDeluxe(self):
        return _TAG_OPT_DEVICE_DELUXE in self.tags

    def getRemovalPrice(self, proxy=None):
        """
        The price to remove this device from vehicle
        :param proxy: instance of ItemsRequester
        :return: ItemPrice
        """
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
        """
        Check if similar(duplicated) device is already installed on the vehicle.
        Deluxe(device+) optional device has the same effect as regular opt.Device
        and they can not be installed together.
        :param vehicle: instance of gui_item.Vehicle
        :return: boolean value
        """
        optDevs = vehicle.optDevices
        for device in optDevs:
            if device is not None and not self.descriptor.checkCompatibilityWithOther(device.descriptor):
                return True

        return False

    def isSimilarDevice(self, other):
        """
        Check if 'other' device is similar this, i.e. has the same effect as this device.
        :param other: optional device
        :return: boolean value
        """
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
            installed = map(lambda x: x.intCD if x is not None else None, vehicle.optDevices)
            if self.intCD in installed:
                result.add(vehicle)

        return result

    def getGUIEmblemID(self):
        return self._GUIEmblemID
