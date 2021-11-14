# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/artefacts.py
from constants import MIN_VEHICLE_LEVEL, MAX_VEHICLE_LEVEL
from debug_utils import LOG_CURRENT_EXCEPTION
from gui.Scaleform.genConsts.SLOT_HIGHLIGHT_TYPES import SLOT_HIGHLIGHT_TYPES
from gui.Scaleform.genConsts.STORE_CONSTANTS import STORE_CONSTANTS
from gui.Scaleform.locale.ARTEFACTS import ARTEFACTS
from gui.Scaleform.locale.ITEM_TYPES import ITEM_TYPES
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.RES_SHOP_EXT import RES_SHOP_EXT
from gui.shared.gui_items import GUI_ITEM_ECONOMY_CODE, GUI_ITEM_TYPE_NAMES, GUI_ITEM_TYPE, checkForTags, getKpiFormatDescription, KPI, collectKpi
from gui.shared.gui_items.Tankman import isSkillLearnt
from gui.shared.gui_items.fitting_item import FittingItem
from gui.shared.gui_items.gui_item_economics import ItemPrice, ITEM_PRICE_EMPTY
from gui.shared.money import Money, Currency, MONEY_UNDEFINED
from gui.shared.utils.functions import stripColorTagDescrTags
from helpers import i18n, dependency
from items import artefacts, tankmen, ITEM_OPERATION
from items.tankmen import PERKS
from skeletons.gui.game_control import IEpicBattleMetaGameController
from skeletons.gui.lobby_context import ILobbyContext
from soft_exception import SoftException
TAG_NOT_FOR_SALE = 'notForSale'
TAG_TRIGGER = 'trigger'
TAG_CREW_BATTLE_BOOSTER = 'crewSkillBattleBooster'
TAG_EQUEPMENT_BUILTIN = 'builtin'
TAG_OPT_DEVICE_DELUXE = 'deluxe'
TAG_OPT_DEVICE_TROPHY_BASIC = 'trophyBasic'
TAG_OPT_DEVICE_TROPHY_UPGRADED = 'trophyUpgraded'
TOKEN_OPT_DEVICE_SIMPLE = 'simple'
TOKEN_OPT_DEVICE_DELUXE = 'deluxe'
TOKEN_CREW_PERK_REPLACE = 'perk'
TOKEN_CREW_PERK_BOOST = 'boost'

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
        return TAG_NOT_FOR_SALE not in self.tags

    @property
    def tags(self):
        return self.descriptor.tags

    def getKpi(self, vehicle=None):
        return collectKpi(self.descriptor, vehicle)

    @property
    def isStimulator(self):
        return isinstance(self.descriptor, artefacts.Stimulator)

    @property
    def crewLevelIncrease(self):
        return 0.0 if not self.isStimulator else self.descriptor.crewLevelIncrease

    @property
    def isRemovingStun(self):
        return False

    @property
    def isUpgradable(self):
        return False

    def getShopIcon(self, size=STORE_CONSTANTS.ICON_SIZE_MEDIUM, store=RES_SHOP_EXT):
        return store.getArtefactIcon(size, self.descriptor.iconName)

    def getVehicleLevelRange(self):
        vehicleFilter = self.descriptor.getVehicleFilter()
        return vehicleFilter.getLevelRange() if vehicleFilter else (MIN_VEHICLE_LEVEL, MAX_VEHICLE_LEVEL)


class Equipment(VehicleArtefact):
    __slots__ = ()

    def _getAltPrice(self, buyPrice, proxy):
        return buyPrice.exchange(Currency.GOLD, Currency.CREDITS, proxy.exchangeRateForShellsAndEqs) if Currency.GOLD in buyPrice else super(Equipment, self)._getAltPrice(buyPrice, proxy)

    @property
    def icon(self):
        return '../maps/icons/artefact/%s.png' % super(Equipment, self).icon

    def getBonusIcon(self, size='small'):
        result = RES_ICONS.getBonusIcon(size, self.descriptor.iconName)
        if result is None:
            result = RES_ICONS.getBonusIcon(size, self.name.split('_')[0])
        return result

    @property
    def defaultLayoutValue(self):
        return (self.intCD if not self.isBoughtForAltPrice else -self.intCD, 1)

    @property
    def isRemovingStun(self):
        descr = self.descriptor
        return bool(descr.stunResistanceEffect or descr.stunResistanceDuration)

    @property
    def isBuiltIn(self):
        return TAG_EQUEPMENT_BUILTIN in self.tags

    def isInstalled(self, vehicle, slotIdx=None):
        return vehicle.consumables.installed.containsIntCD(self.intCD, slotIdx)

    def isInSetup(self, vehicle, setupIndex=None, slotIdx=None):
        return vehicle.consumables.setupLayouts.containsIntCD(self.intCD, setupIndex, slotIdx)

    def isInOtherLayout(self, vehicle):
        return vehicle.consumables.setupLayouts.isInOtherLayout(self)

    @property
    def isTrigger(self):
        return TAG_TRIGGER in self.tags

    def mayInstall(self, vehicle, slotIdx=None):
        for idx, eq in enumerate(vehicle.consumables.installed):
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
            if vehicle.consumables.setupLayouts.containsIntCD(self.intCD):
                result.add(vehicle)

        return result

    def getConflictedEquipments(self, vehicle):
        conflictEqs = list()
        if self in vehicle.consumables.installed:
            return conflictEqs
        for e in vehicle.consumables.installed.getItems():
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

    def isAffectsOnVehicle(self, vehicle, setupIdx=None):
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

    def getOptDeviceBoosterGainValue(self, vehicle):
        pass

    def getHighlightType(self, vehicle=None):
        return SLOT_HIGHLIGHT_TYPES.BUILT_IN_EQUIPMENT if self.isBuiltIn else SLOT_HIGHLIGHT_TYPES.NO_HIGHLIGHT


class BattleBooster(Equipment):
    __slots__ = ()
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, *args, **kwargs):
        super(BattleBooster, self).__init__(*args, **kwargs)
        self.itemTypeID = GUI_ITEM_TYPE.BATTLE_BOOSTER

    @property
    def userType(self):
        return i18n.makeString(ITEM_TYPES.BATTLEBOOSTER_NAME)

    @property
    def itemTypeName(self):
        return GUI_ITEM_TYPE_NAMES[self.itemTypeID]

    @property
    def isForSale(self):
        return self.__lobbyContext.getServerSettings().isBattleBoostersEnabled() and super(BattleBooster, self).isForSale

    def isCrewBooster(self):
        return TAG_CREW_BATTLE_BOOSTER in self.tags

    def isAffectsOnVehicle(self, vehicle, setupIdx=None):
        if self.isCrewBooster():
            return True
        else:
            if setupIdx is not None:
                for device in vehicle.optDevices.setupLayouts.setups[setupIdx]:
                    if self.isOptionalDeviceCompatible(device):
                        return True

            else:
                for device in vehicle.optDevices.installed:
                    if self.isOptionalDeviceCompatible(device):
                        return True

            return False

    def isInstalled(self, vehicle, slotIdx=None):
        return False if vehicle is None else vehicle.battleBoosters.installed.containsIntCD(self.intCD, slotIdx)

    def isInSetup(self, vehicle, setupIndex=None, slotIdx=None):
        return False if vehicle is None else vehicle.battleBoosters.setupLayouts.containsIntCD(self.intCD, setupIndex, slotIdx)

    def isInOtherLayout(self, vehicle):
        return vehicle.battleBoosters.setupLayouts.isInOtherLayout(self)

    def getInstalledVehicles(self, vehicles):
        result = set()
        for vehicle in vehicles:
            if vehicle.battleBoosters.setupLayouts.containsIntCD(self.intCD):
                result.add(vehicle)

        return result

    def mayInstall(self, vehicle, slotIdx=None):
        return (True, None)

    def getBonusIcon(self, size='small'):
        return RES_ICONS.getBonusIcon(size, self.name.split('_')[0])

    def isOptionalDeviceCompatible(self, optionalDevice):
        return not self.isCrewBooster() and optionalDevice is not None and self.descriptor.getLevelParamsForDevice(optionalDevice.descriptor) is not None

    def getCrewBonus(self, vehicle):
        if self.isCrewBooster():
            return 0
        else:
            for device in vehicle.optDevices.installed.getItems():
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
        token = TOKEN_CREW_PERK_REPLACE if isPerkReplace else TOKEN_CREW_PERK_BOOST
        return i18n.makeString(ARTEFACTS.getCrewActionForBattleBooster(self.name, token))

    def getOptDeviceBoosterDescription(self, vehicle, valueFormatter=None):
        if self.isCrewBooster():
            raise SoftException('This description is only for Opt. Dev. Booster!')
        gain = self.getOptDeviceBoosterGainValue(vehicle=vehicle)
        formatted = valueFormatter(gain) if valueFormatter is not None else gain
        return self.shortDescription % formatted

    def getOptDeviceBoosterGainValue(self, vehicle):
        if self.isCrewBooster():
            raise SoftException('This description is only for Opt. Dev. Booster!')
        deviceType = TOKEN_OPT_DEVICE_SIMPLE
        if vehicle is not None:
            for device in vehicle.optDevices.installed:
                if self.isOptionalDeviceCompatible(device) and device.isDeluxe:
                    deviceType = TOKEN_OPT_DEVICE_DELUXE
                    break

        gain = i18n.makeString(ARTEFACTS.getDeviceGainForBattleBooster(self.name, deviceType))
        return gain

    def _getShortInfo(self, vehicle=None, expanded=False):
        return self.getCrewBoosterDescription(isPerkReplace=False, formatter=None) if self.isCrewBooster() else self.getOptDeviceBoosterDescription(vehicle=None, valueFormatter=None)

    def _getAltPrice(self, buyPrice, proxy):
        return MONEY_UNDEFINED

    def getHighlightType(self, vehicle=None):
        if self.isCrewBooster():
            skillLearnt = self.isAffectedSkillLearnt(vehicle)
            if skillLearnt:
                return SLOT_HIGHLIGHT_TYPES.BATTLE_BOOSTER
            return SLOT_HIGHLIGHT_TYPES.BATTLE_BOOSTER_CREW_REPLACE
        return SLOT_HIGHLIGHT_TYPES.BATTLE_BOOSTER


class BattleAbility(Equipment):
    __slots__ = ('_level', '_unlocked', '__weakref__')
    __epicMetaGameCtrl = dependency.descriptor(IEpicBattleMetaGameController)

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
        return vehicle.battleAbilities.installed.containsIntCD(self.intCD, slotIdx)

    def isInSetup(self, vehicle, setupIndex=None, slotIdx=None):
        return vehicle.battleAbilities.setupLayouts.containsIntCD(self.intCD, setupIndex, slotIdx)

    def isInOtherLayout(self, vehicle):
        return vehicle.battleAbilities.setupLayouts.isInOtherLayout(self)

    def getInstalledVehicles(self, vehicles):
        result = set()
        for vehicle in vehicles:
            if vehicle.battleAbilities.setupLayouts.containsIntCD(self.intCD):
                result.add(vehicle)

        return result

    def mayPurchase(self, money):
        return (False, GUI_ITEM_ECONOMY_CODE.ITEM_NO_PRICE)

    def mayInstall(self, vehicle, slotIdx=None):
        slotCheck = slotIdx < self.__epicMetaGameCtrl.getNumAbilitySlots(vehicle.descriptor.type)
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

    def __cmp__(self, other):
        if other is None:
            return 1
        else:
            if isinstance(other, OptionalDevice):
                if self.isTrophy != other.isTrophy:
                    if self.isTrophy:
                        return 1
                    return -1
                if self.isTrophy:
                    if self.isUpgraded != other.isUpgraded:
                        if self.isSimilarDevice(other):
                            if self.isUpgraded:
                                return 1
                            return -1
                if self.isDeluxe != other.isDeluxe:
                    if self.isDeluxe:
                        return 1
                    return -1
            return super(OptionalDevice, self).__cmp__(other)

    @property
    def shortDescription(self):
        description = super(OptionalDevice, self).shortDescription
        return description.format(colorTagOpen='', colorTagClose='')

    @property
    def isUpgradable(self):
        return checkForTags(self.tags, TAG_OPT_DEVICE_TROPHY_BASIC)

    @property
    def isUpgraded(self):
        return checkForTags(self.tags, TAG_OPT_DEVICE_TROPHY_UPGRADED)

    @property
    def isDeluxe(self):
        return checkForTags(self.tags, TAG_OPT_DEVICE_DELUXE)

    @property
    def isTrophy(self):
        return checkForTags(self.tags, (TAG_OPT_DEVICE_TROPHY_BASIC, TAG_OPT_DEVICE_TROPHY_UPGRADED))

    @property
    def isRegular(self):
        return not checkForTags(self.tags, (TAG_OPT_DEVICE_TROPHY_BASIC, TAG_OPT_DEVICE_TROPHY_UPGRADED, TAG_OPT_DEVICE_DELUXE))

    def getRemovalPrice(self, proxy=None):
        if not self.isRemovable and proxy is not None:
            if self.isDeluxe:
                cost = proxy.shop.paidDeluxeRemovalCost
                defaultCost = proxy.shop.defaults.paidDeluxeRemovalCost
                return ItemPrice(price=cost, defPrice=defaultCost)
            if self.isUpgradable:
                cost = proxy.shop.paidTrophyBasicRemovalCost
                defaultCost = proxy.shop.defaults.paidTrophyBasicRemovalCost
                return ItemPrice(price=cost, defPrice=defaultCost)
            if self.isUpgraded:
                cost = proxy.shop.paidTrophyUpgradedRemovalCost
                defaultCost = proxy.shop.defaults.paidTrophyUpgradedRemovalCost
                return ItemPrice(price=cost, defPrice=defaultCost)
            cost = proxy.shop.paidRemovalCost
            defaultCost = proxy.shop.defaults.paidRemovalCost
            return ItemPrice(price=Money(gold=cost), defPrice=Money(gold=defaultCost))
        else:
            return super(OptionalDevice, self).getRemovalPrice(proxy)

    def getBonusIcon(self, size='small'):
        result = RES_ICONS.getBonusIcon(size, self.descriptor.iconName)
        if result is None:
            result = RES_ICONS.getBonusIcon(size, self.name.split('_')[0])
        return result

    def isInstalled(self, vehicle, slotIdx=None):
        for idx, op in enumerate(vehicle.optDevices.installed):
            if op is not None and self.intCD == op.intCD:
                if slotIdx is None:
                    return True
                return idx == slotIdx

        return super(OptionalDevice, self).isInstalled(vehicle, slotIdx)

    def isInSetup(self, vehicle, setupIndex=None, slotIdx=None):
        return vehicle.optDevices.setupLayouts.containsIntCD(self.intCD, setupIndex, slotIdx)

    def isInOtherLayout(self, vehicle):
        return vehicle.optDevices.setupLayouts.isInOtherLayout(self)

    def hasSimilarDevicesInstalled(self, vehicle):
        for device in vehicle.optDevices.installed.getItems():
            if not self.descriptor.checkCompatibilityWithOther(device.descriptor):
                return True

        return False

    def isSimilarDevice(self, other):
        return not self.descriptor.checkCompatibilityWithOther(other) if other is not None else False

    def mayInstall(self, vehicle, slotIdx=None):
        return vehicle.descriptor.mayInstallOptionalDevice(self.intCD, slotIdx)

    def mayRemove(self, vehicle):
        try:
            slotIdx = vehicle.optDevices.layout.index(self)
            return vehicle.descriptor.mayRemoveOptionalDevice(slotIdx)
        except Exception:
            LOG_CURRENT_EXCEPTION()
            return (False, 'not installed on vehicle')

    def getInstalledVehicles(self, vehicles):
        result = set()
        for vehicle in vehicles:
            if vehicle.optDevices.setupLayouts.containsIntCD(self.intCD):
                result.add(vehicle)

        return result

    def getGUIEmblemID(self):
        return self._GUIEmblemID

    def getHighlightType(self, vehicle=None):
        if self.isDeluxe:
            return SLOT_HIGHLIGHT_TYPES.EQUIPMENT_PLUS
        return SLOT_HIGHLIGHT_TYPES.EQUIPMENT_TROPHY if self.isUpgradable or self.isUpgraded else SLOT_HIGHLIGHT_TYPES.NO_HIGHLIGHT

    def getOverlayType(self, vehicle=None):
        if self.isDeluxe:
            return SLOT_HIGHLIGHT_TYPES.EQUIPMENT_PLUS
        if self.isUpgradable:
            return SLOT_HIGHLIGHT_TYPES.EQUIPMENT_TROPHY_BASIC
        return SLOT_HIGHLIGHT_TYPES.EQUIPMENT_TROPHY_UPGRADED if self.isUpgraded else SLOT_HIGHLIGHT_TYPES.NO_HIGHLIGHT

    def getUpgradePrice(self, proxy=None):
        if self.isUpgradable and proxy is not None:
            price = proxy.shop.getOperationPrices().get(ITEM_OPERATION.UPGRADE, {}).get((self.intCD, self.descriptor.upgradeInfo.upgradedCompDescr), None)
            defaultPrice = proxy.shop.defaults.getOperationPrices().get(ITEM_OPERATION.UPGRADE, {}).get((self.intCD, self.descriptor.upgradeInfo.upgradedCompDescr), None)
            if price is not None and defaultPrice is not None:
                return ItemPrice(price=Money(**price), defPrice=Money(**defaultPrice))
        return ITEM_PRICE_EMPTY

    def mayPurchaseUpgrade(self, proxy):
        canBuy, _ = self._isEnoughMoney(self.getUpgradePrice(proxy).price, proxy.stats.money)
        return canBuy

    def mayPurchaseUpgradeWithExchange(self, proxy):
        money = proxy.stats.money
        if not money.isSet(Currency.GOLD):
            return False
        money = money.exchange(Currency.GOLD, Currency.CREDITS, proxy.shop.exchangeRate, default=0)
        canBuy, _ = self._isEnoughMoney(self.getUpgradePrice(proxy).price, money)
        return canBuy

    def _getShortInfo(self, vehicle=None, expanded=False):
        kpi = self.getKpi()
        return stripColorTagDescrTags(self.shortDescriptionSpecial) if not kpi or len(kpi) >= 2 or any((bonus.type == KPI.Type.AGGREGATE_MUL for bonus in kpi)) else getKpiFormatDescription(kpi[0])
