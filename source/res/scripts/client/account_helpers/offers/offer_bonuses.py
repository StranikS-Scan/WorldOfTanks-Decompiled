# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/account_helpers/offers/offer_bonuses.py
import typing
from constants import PREMIUM_ENTITLEMENTS, RentType
from gui.Scaleform.genConsts.SLOT_HIGHLIGHT_TYPES import SLOT_HIGHLIGHT_TYPES
from gui.Scaleform.genConsts.STORE_CONSTANTS import STORE_CONSTANTS
from gui.Scaleform.locale.RES_SHOP import RES_SHOP
from gui.impl import backport
from gui.impl.gen import R
from gui.server_events.bonuses import CreditsBonus, GoldBonus, CrystalBonus, FreeXpBonus, PlusPremiumDaysBonus, VehiclesBonus, CrewBooksBonus, ItemsBonus, CustomizationsBonus, CrewSkinsBonus, ItemsBonusFactory, CrewSkinsBonusFactory
from gui.server_events.formatters import tagText
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.Vehicle import getTypeUserName
from gui.shared.money import Currency
from helpers import int2roman, dependency
from skeletons.gui.customization import ICustomizationService

def _canCustomizationBeAdded(c11nItem, count):
    maxNumber = c11nItem.descriptor.maxNumber
    return False if maxNumber != 0 and c11nItem.inventoryCount + count > maxNumber else True


class OfferBonusMixin(object):
    CAN_BE_SHOWN = True

    @property
    def displayedItem(self):
        return None

    def getOfferName(self):
        return self.displayedItem.userName if self.displayedItem else ''

    def getOfferDescription(self):
        return self.displayedItem.shortDescriptionSpecial if self.displayedItem else ''

    def getOfferIcon(self):
        return self.displayedItem.getShopIcon(STORE_CONSTANTS.ICON_SIZE_SMALL) if self.displayedItem else ''

    def getOfferNationalFlag(self):
        pass

    def getOfferHighlight(self):
        return self.displayedItem.getOverlayType() if self.displayedItem else SLOT_HIGHLIGHT_TYPES.NO_HIGHLIGHT

    def getGiftCount(self):
        pass

    def getInventoryCount(self):
        if self.displayedItem and self.displayedItem.inventoryCount is not None:
            inventoryCount = self.displayedItem.inventoryCount
        else:
            inventoryCount = 0
        return inventoryCount

    def getRentInfo(self):
        return (RentType.NO_RENT, 0)

    def isMaxCountExceeded(self):
        return False

    @property
    def displayedBonusData(self):
        return {self.getName(): self.getValue()}

    def canBeShown(self):
        return self.CAN_BE_SHOWN


class OfferEconomyBonusMixin(OfferBonusMixin):
    DESCRIPTION_NAME = None
    ICON_NAME = None

    def getOfferName(self):
        return backport.text(R.strings.quests.bonuses.dyn(self.getName()).description(), value=tagText(self.formatValue(), 'neutral'))

    def getOfferDescription(self):
        typeName = self.DESCRIPTION_NAME or ''
        return backport.text(R.strings.tooltips.advanced.dyn(typeName)())

    def getOfferIcon(self):
        name = self.ICON_NAME or self.getName()
        return backport.image(self._getCurrencyResource(name))

    def getGiftCount(self):
        return self.getValue()

    @staticmethod
    def _getCurrencyResource(name, default=None):
        return R.images.gui.maps.shop.currency.c_180x135.dyn(name, default)()


class CreditsOfferBonus(OfferEconomyBonusMixin, CreditsBonus):
    DESCRIPTION_NAME = 'economyCredits'


class GoldOfferBonus(OfferEconomyBonusMixin, GoldBonus):
    DESCRIPTION_NAME = 'economyGold'

    def formatValue(self):
        return backport.getIntegralFormat(self._value) if self._value else None


class CrystalOfferBonus(OfferEconomyBonusMixin, CrystalBonus):
    DESCRIPTION_NAME = 'economyBonds'
    ICON_NAME = 'bon'


class FreeXpOfferBonus(OfferEconomyBonusMixin, FreeXpBonus):
    DESCRIPTION_NAME = 'economyConvertExp'


class PlusPremiumDaysOfferBonus(OfferEconomyBonusMixin, PlusPremiumDaysBonus):
    DESCRIPTION_NAME = 'economyPremium'

    def getOfferIcon(self):
        imgName = 'premium_icon_{}'
        resource = R.images.gui.maps.shop.premium.c_180x135.dyn(imgName.format(self.getValue()), R.images.gui.maps.shop.premium.c_180x135.dyn(imgName.format('wot')))()
        return backport.image(resource)


class VehiclesOfferBonus(OfferBonusMixin, VehiclesBonus):
    c11n = dependency.descriptor(ICustomizationService)

    @property
    def displayedItem(self):
        vehItem, _ = self.getVehicles()[0]
        return vehItem

    def getOfferName(self):
        return ' '.join([getTypeUserName(self.displayedItem.type, False), tagText(int2roman(self.displayedItem.level), 'neutral'), self.displayedItem.shortUserName])

    def getOfferNationalFlag(self):
        return RES_SHOP.getNationFlagIcon(self.displayedItem.nationName)

    def getRentInfo(self):
        _, vehInfo = self.getVehicles()[0]
        if self.isRentVehicle(vehInfo):
            for rentType, getter in ((RentType.TIME_RENT, self.getRentDays), (RentType.BATTLES_RENT, self.getRentBattles), (RentType.WINS_RENT, self.getRentWins)):
                rentValue = getter(vehInfo)
                if rentValue:
                    return (rentType, rentValue)

        return (RentType.NO_RENT, 0)

    def getInventoryCount(self):
        return int(self.displayedItem.isInInventory)

    def isMaxCountExceeded(self):
        for vehicle, vehData in self.getVehicles():
            if vehicle.isInInventory and not vehicle.isRented:
                return True
            if 'customization' in vehData:
                styleId = vehData['customization'].get('styleId')
                if styleId is not None:
                    itemTypeID, count = GUI_ITEM_TYPE.STYLE, 1
                    c11nItem = self.c11n.getItemByID(itemTypeID, styleId)
                    if not _canCustomizationBeAdded(c11nItem, count):
                        return True

        return False

    @property
    def isWithCrew(self):
        return 'noCrew' not in self.displayedVehicleInfo

    @property
    def displayedVehicleInfo(self):
        for vehItem, vehInfo in self.getVehicles():
            if vehItem is self.displayedItem:
                return vehInfo

    @property
    def displayedBonusData(self):
        bonusData = {}
        for vehItem, vehInfo in self.getVehicles():
            if vehItem is self.displayedItem:
                bonusData = {self.getName(): {self.displayedItem.intCD: vehInfo}}
                break

        return bonusData


class OfferItemsBonusMixin(OfferBonusMixin):

    @property
    def displayedItem(self):
        return self._getItems()[0][0] if self._getItems else None

    def getGiftCount(self):
        giftCount = 0
        for item, count in self._getItems():
            if item is self.displayedItem:
                giftCount = count
                break

        return giftCount

    @property
    def displayedBonusData(self):
        bonusData = {}
        for item, count in self._getItems():
            if item is self.displayedItem:
                bonusData = {'items': {self.displayedItem.intCD: count}}
                break

        return bonusData

    def _getItems(self):
        return []


class CrewBooksOfferBonus(OfferItemsBonusMixin, CrewBooksBonus):

    def getOfferIcon(self):
        return self.displayedItem.getOldStyleIcon()

    def getOfferNationalFlag(self):
        nation = self.displayedItem.getNation()
        return RES_SHOP.getNationFlagIcon(self.displayedItem.getNation()) if nation is not None else None

    def getOfferDescription(self):
        return self.displayedItem.shortDescription

    def _getItems(self):
        return self.getItems()


class ItemsOfferBonus(OfferItemsBonusMixin, ItemsBonus):

    def getOfferDescription(self):
        return self.displayedItem.getOptDeviceBoosterDescription(None, None) if self.displayedItem.itemTypeID == GUI_ITEM_TYPE.BATTLE_BOOSTER and not self.displayedItem.isCrewBooster() else self.displayedItem.shortDescriptionSpecial

    def _getItems(self):
        return self.getItems().items()


class CustomizationsOfferBonus(OfferBonusMixin, CustomizationsBonus):
    CAN_BE_SHOWN = False

    def isMaxCountExceeded(self):
        for itemData in self.getCustomizations():
            count = itemData.get('value', 0)
            c11nItem = self.getC11nItem(itemData)
            return not _canCustomizationBeAdded(c11nItem, count)

        return False


class CrewSkinsOfferBonus(OfferBonusMixin, CrewSkinsBonus):
    CAN_BE_SHOWN = False

    def isMaxCountExceeded(self):
        crewSkinID = self.getValue().get('id', 0)
        count = self.getValue().get('count', 0)
        crewSkinItem = self.itemsCache.items.getCrewSkin(crewSkinID)
        return True if crewSkinItem.getFreeCount() + count > crewSkinItem.getMaxCount() else False


class ItemsOfferBonusFactory(ItemsBonusFactory):
    CREW_BOOKS_BONUS_CLASS = CrewBooksOfferBonus
    ITEMS_BONUS_CLASS = ItemsOfferBonus


class CrewSkinsOfferBonusFactory(CrewSkinsBonusFactory):
    CREW_SKINS_BONUS_CLASS = CrewSkinsOfferBonus


class OfferBonusAdapter(OfferBonusMixin):
    CAN_BE_SHOWN = False

    def __init__(self, bonus):
        self._bonus = bonus

    def __getattr__(self, item):
        return getattr(self._bonus, item)


OFFER_BONUSES = {Currency.CREDITS: CreditsOfferBonus,
 Currency.GOLD: GoldOfferBonus,
 Currency.CRYSTAL: CrystalOfferBonus,
 'freeXP': FreeXpOfferBonus,
 PREMIUM_ENTITLEMENTS.PLUS: PlusPremiumDaysOfferBonus,
 'vehicles': VehiclesOfferBonus,
 'items': ItemsOfferBonusFactory(),
 'customizations': CustomizationsOfferBonus,
 'crewSkins': CrewSkinsOfferBonusFactory()}
