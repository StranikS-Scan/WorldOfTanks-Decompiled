# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/artefacts.py
from debug_utils import LOG_CURRENT_EXCEPTION
from gui.shared.gui_items import GUI_ITEM_TYPE_NAMES, GUI_ITEM_TYPE
from gui.shared.gui_items.fitting_item import FittingItem
from gui.shared.gui_items.Tankman import isSkillLearnt
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.shared.money import Currency
from items import artefacts
from items.tankmen import PERKS
from gui.Scaleform.locale.ARTEFACTS import ARTEFACTS
from gui.Scaleform.locale.ITEM_TYPES import ITEM_TYPES
from helpers import i18n
_TAG_CREW_BATTLE_BOOSTER = 'crewSkillBattleBooster'
_TAG_OPT_DEVICE_DELUXE = 'deluxe'
_TOKEN_OPT_DEVICE_SIMPLE = 'simple'
_TOKEN_OPT_DEVICE_DELUXE = 'deluxe'
_TOKEN_CREW_PERK_REPLACE = 'perk'
_TOKEN_CREW_PERK_BOOST = 'boost'

class VehicleArtefact(FittingItem):

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
    def isStimulator(self):
        """ Is item stimulator which can increase crew role levels. """
        return isinstance(self.descriptor, artefacts.Stimulator)

    @property
    def crewLevelIncrease(self):
        """ Value of crew role levels increasing. """
        return 0 if not self.isStimulator else self.descriptor['crewLevelIncrease']

    @property
    def isRemovingStun(self):
        return False


class Equipment(VehicleArtefact):

    def _getAltPrice(self, buyPrice, proxy):
        """ Overridden method for receiving special action price value for shells
        @param buyPrice:
        @param proxy:
        @return: an instance of Money class
        """
        creditsPrice = buyPrice.exchange(Currency.GOLD, Currency.CREDITS, proxy.exchangeRateForShellsAndEqs)
        return buyPrice.replace(Currency.CREDITS, creditsPrice.credits)

    @property
    def icon(self):
        return '../maps/icons/artefact/%s.png' % super(Equipment, self).icon

    def getBonusIcon(self, size='small'):
        return RES_ICONS.getBonusIcon(size, self.name)

    @property
    def tags(self):
        return self.descriptor.tags

    @property
    def defaultLayoutValue(self):
        return (self.intCD if not self.isBoughtForCredits else -self.intCD, 1)

    @property
    def isRemovingStun(self):
        descr = self.descriptor
        return bool(descr.stunResistanceEffect or descr.stunResistanceDuration)

    def isInstalled(self, vehicle, slotIdx=None):
        for idx, eq in enumerate(vehicle.eqs):
            if eq is not None and self.intCD == eq.intCD:
                if slotIdx is None:
                    return True
                return idx == slotIdx

        return super(Equipment, self).isInstalled(vehicle, slotIdx)

    def mayInstall(self, vehicle, slotIdx=None):
        for idx, eq in enumerate(vehicle.eqs):
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
            installed = map(lambda x: x.intCD if x is not None else None, vehicle.eqs)
            if self.intCD in installed:
                result.add(vehicle)

        return result

    def getConflictedEquipments(self, vehicle):
        conflictEqs = list()
        if self in vehicle.eqs:
            return conflictEqs
        else:
            for e in vehicle.eqs:
                if e is not None:
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
    """
    This class represents BattleBooster entity. It is a kind of equipment.
    But it is not displayed in Technical Maintenance window, it has its own slot in hangar.
    For server we will always set this item in 4th position in equipment layout.
    """

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
        return _TAG_CREW_BATTLE_BOOSTER in self.descriptor.tags

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
        booster = vehicle.battleBooster
        return booster is not None and self.intCD == booster.intCD

    def getInstalledVehicles(self, vehicles):
        result = set()
        for vehicle in vehicles:
            if vehicle.battleBooster is not None and self.intCD == vehicle.battleBooster.intCD:
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

    def getAffectedSkillName(self):
        """
        Returns a skill name, for which booster has effect
        :return: string or None
        """
        return self.descriptor.skillName if self.isCrewBooster() else None

    def mayPurchaseWithExchange(self, money, exchangeRate):
        canBuy, reason = self.mayPurchase(money)
        return canBuy

    def isAffectedSkillLearnt(self, vehicle=None):
        """
        Check whether descriptor.skillName is learnt if vehicle is provided.
        :param vehicle: instance of gui_item.Vehicle
        :return: boolean result
        """
        if vehicle is not None:
            return isSkillLearnt(self.getAffectedSkillName(), vehicle)
        else:
            return False
            return

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


class OptionalDevice(VehicleArtefact):

    def __init__(self, intCompactDescr, proxy=None, isBoughtForCredits=False):
        super(OptionalDevice, self).__init__(intCompactDescr, proxy, isBoughtForCredits)
        splitIcon = self.icon.split('/')
        labelWithExtension = splitIcon[len(splitIcon) - 1]
        label = labelWithExtension.split('.')[0]
        self.GUIEmblemID = label

    @property
    def shortDescription(self):
        """
        By default return the string without value formatting. See artefacts.po
        """
        description = super(OptionalDevice, self).shortDescription
        return description.format(colorTagOpen='', colorTagClose='')

    @property
    def isRemovable(self):
        return self.descriptor['removable']

    def isDeluxe(self):
        return _TAG_OPT_DEVICE_DELUXE in self.descriptor.tags

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
        return self.GUIEmblemID
