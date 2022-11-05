# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/fitting_item.py
from collections import namedtuple
import BigWorld
from debug_utils import LOG_CURRENT_EXCEPTION
from gui import GUI_SETTINGS
from gui.Scaleform.genConsts.SLOT_HIGHLIGHT_TYPES import SLOT_HIGHLIGHT_TYPES
from gui.impl.gen.view_models.constants.item_highlight_types import ItemHighlightTypes
from gui.shared.gui_items import GUI_ITEM_TYPE, GUI_ITEM_ECONOMY_CODE
from gui.shared.gui_items.gui_item_economics import ItemPrice, ItemPrices, ITEM_PRICE_EMPTY, ITEM_PRICES_EMPTY
from gui.shared.gui_items.gui_item import GUIItem, HasIntCD
from gui.shared.items_parameters import params_helper, formatters
from gui.shared.money import Money, Currency, MONEY_UNDEFINED
from gui.shared.utils.functions import getShortDescr, stripColorTagDescrTags
from shared_utils import first
from skeletons.gui.game_control import ISeasonsController
from helpers import i18n, time_utils, dependency
from items import vehicles, getTypeInfoByName
from rent_common import SeasonRentDuration
from renewable_subscription_common.settings_constants import RENT_KEY as WOTPLUS_RENT_KEY
from telecom_rentals_common import TELECOM_RENTALS_RENT_KEY
ICONS_MASK = '../maps/icons/%(type)s/%(subtype)s%(unicName)s.png'
_RentalInfoProvider = namedtuple('RentalInfoProvider', ('rentExpiryTime', 'compensations', 'battlesLeft', 'winsLeft', 'seasonRent', 'isRented', 'isWotPlus', 'isTelecomRent'))
SeasonRentInfo = namedtuple('SeasonRentInfo', ('seasonType', 'seasonID', 'duration', 'expiryTime'))
_BIG_HIGHLIGHT_TYPES_MAP = {SLOT_HIGHLIGHT_TYPES.BATTLE_BOOSTER_CREW_REPLACE: SLOT_HIGHLIGHT_TYPES.BATTLE_BOOSTER_CREW_REPLACE_BIG,
 SLOT_HIGHLIGHT_TYPES.BATTLE_BOOSTER: SLOT_HIGHLIGHT_TYPES.BATTLE_BOOSTER_BIG,
 SLOT_HIGHLIGHT_TYPES.EQUIPMENT_PLUS: SLOT_HIGHLIGHT_TYPES.EQUIPMENT_PLUS_BIG,
 SLOT_HIGHLIGHT_TYPES.BUILT_IN_EQUIPMENT: SLOT_HIGHLIGHT_TYPES.BUILT_IN_EQUIPMENT_BIG,
 SLOT_HIGHLIGHT_TYPES.NO_HIGHLIGHT: SLOT_HIGHLIGHT_TYPES.NO_HIGHLIGHT,
 SLOT_HIGHLIGHT_TYPES.EQUIPMENT_TROPHY: SLOT_HIGHLIGHT_TYPES.EQUIPMENT_TROPHY_BIG,
 SLOT_HIGHLIGHT_TYPES.EQUIPMENT_TROPHY_BASIC: SLOT_HIGHLIGHT_TYPES.EQUIPMENT_TROPHY_BASIC_BIG,
 SLOT_HIGHLIGHT_TYPES.EQUIPMENT_TROPHY_UPGRADED: SLOT_HIGHLIGHT_TYPES.EQUIPMENT_TROPHY_UPGRADED_BIG,
 SLOT_HIGHLIGHT_TYPES.EQUIPMENT_MODERNIZED: SLOT_HIGHLIGHT_TYPES.EQUIPMENT_MODERNIZED_BIG}
SLOT_HIGHLIGHT_TO_ITEM_HIGHLIGHT_TYPES = {SLOT_HIGHLIGHT_TYPES.EQUIPMENT_TROPHY: ItemHighlightTypes.TROPHY,
 SLOT_HIGHLIGHT_TYPES.EQUIPMENT_TROPHY_BASIC: ItemHighlightTypes.TROPHY_BASIC,
 SLOT_HIGHLIGHT_TYPES.EQUIPMENT_TROPHY_UPGRADED: ItemHighlightTypes.TROPHY_UPGRADED,
 SLOT_HIGHLIGHT_TYPES.BATTLE_BOOSTER: ItemHighlightTypes.BATTLE_BOOSTER,
 SLOT_HIGHLIGHT_TYPES.BATTLE_BOOSTER_CREW_REPLACE: ItemHighlightTypes.BATTLE_BOOSTER_REPLACE,
 SLOT_HIGHLIGHT_TYPES.EQUIPMENT_PLUS: ItemHighlightTypes.EQUIPMENT_PLUS,
 SLOT_HIGHLIGHT_TYPES.BUILT_IN_EQUIPMENT: ItemHighlightTypes.BUILT_IN_EQUIPMENT,
 SLOT_HIGHLIGHT_TYPES.EQUIPMENT_MODERNIZED: ItemHighlightTypes.MODERNIZED}

def canBuyWithGoldExchange(price, money, exchangeRate):
    money = money.exchange(Currency.GOLD, Currency.CREDITS, exchangeRate, default=0)
    return FittingItem._isEnoughMoney(price, money)[0]


class RentalInfoProvider(_RentalInfoProvider):
    seasonsController = dependency.descriptor(ISeasonsController)

    @staticmethod
    def __new__(cls, additionalData=None, time=0, battles=0, wins=0, seasonRent=None, isRented=False, *args, **kwargs):
        additionalData = additionalData or {}
        if 'compensation' in additionalData:
            compensations = Money.makeFromMoneyTuple(additionalData['compensation'])
        else:
            compensations = MONEY_UNDEFINED
        isWotPlus = WOTPLUS_RENT_KEY in additionalData
        isTelecomRent = TELECOM_RENTALS_RENT_KEY in additionalData
        result = _RentalInfoProvider.__new__(cls, time, compensations, battles, wins, seasonRent or {}, isRented, isWotPlus, isTelecomRent)
        return result

    def canRentRenewForSeason(self, seasonType):
        currentSeason = self.seasonsController.getCurrentSeason(seasonType)
        return currentSeason and currentSeason.getCycleInfo()

    def getLastCycleRentInfo(self, seasonType):
        currentSeason = self.seasonsController.getCurrentSeason(seasonType)
        if currentSeason:
            rents = self.seasonRent.get(seasonType, [])
            if rents:
                cyclesIDs = [ cycleID for cycleID, duration in rents if duration == SeasonRentDuration.SEASON_CYCLE ]
                cycles = [ currentSeason.getCycleInfo(cycleID) for cycleID in cyclesIDs if currentSeason.getCycleInfo(cycleID) ]
                if cycles:
                    return sorted(cycles, key=lambda c: c.ordinalNumber)[-1]
        return None

    def getActiveSeasonRent(self):
        for seasonType, rentTypes in self.seasonRent.iteritems():
            seasonRents = [ item for item in rentTypes if item[1] == SeasonRentDuration.ENTIRE_SEASON ]
            if seasonRents:
                for rentType in seasonRents:
                    rentID, duration = rentType
                    if self.seasonsController.isWithinSeasonTime(rentID, seasonType):
                        seasonByID = self.seasonsController.getSeason(seasonType, rentID)
                        if seasonByID is not None:
                            return SeasonRentInfo(seasonType, rentID, duration, seasonByID.getEndDate())

            cycleRents = [ item for item in rentTypes if item[1] == SeasonRentDuration.SEASON_CYCLE ]
            if cycleRents:
                for rentType in cycleRents:
                    rentID, duration = rentType
                    currentSeason = self.seasonsController.getCurrentSeason(seasonType)
                    if currentSeason is not None:
                        if currentSeason.getCycleID() == rentID:
                            return SeasonRentInfo(seasonType, rentID, duration, currentSeason.getCycleEndDate())
                        now = time_utils.getCurrentLocalServerTimestamp()
                        nextCycle = currentSeason.getNextCycleInfo(now) or currentSeason.getNextByTimeCycle(now)
                        if nextCycle and nextCycle.ID == rentID:
                            return SeasonRentInfo(seasonType, rentID, duration, nextCycle.endDate)

        return

    def getTimeLeft(self):
        if self.rentExpiryTime != float('inf'):
            expiryTime = max(self.rentExpiryTime, self._getSeasonExpiryTime())
            return float(time_utils.getTimeDeltaFromNow(time_utils.makeLocalServerTime(expiryTime)))
        return float('inf')

    def getExpiryState(self):
        return self.rentExpiryTime != float('inf') and self.battlesLeft <= 0 and self.winsLeft <= 0 and self.getTimeLeft() <= 0 and not self.getActiveSeasonRent()

    def getRentalPeriodInCycles(self):
        activeSeasonRentInfo = self.getActiveSeasonRent()
        if not activeSeasonRentInfo:
            return
        else:
            seasonType, rentID, duration, _ = activeSeasonRentInfo
            currentSeason = self.seasonsController.getCurrentSeason(seasonType)
            if currentSeason:
                if duration == SeasonRentDuration.ENTIRE_SEASON:
                    if self.seasonsController.isWithinSeasonTime(rentID, seasonType):
                        curCycle = currentSeason.getCycleInfo()
                        lastCycle = currentSeason.getLastCycleInfo()
                        if curCycle is None or lastCycle is None:
                            return
                        if curCycle == lastCycle:
                            return (curCycle,)
                        return (curCycle, lastCycle)
                elif duration == SeasonRentDuration.SEASON_CYCLE:
                    now = time_utils.getCurrentLocalServerTimestamp()
                    curCycle = currentSeason.getCycleInfo() or currentSeason.getNextByTimeCycle(now)
                    if curCycle:
                        lastFutureCycleInfo = self._getLastFutureCycleRentInfo()
                        if lastFutureCycleInfo and lastFutureCycleInfo.seasonID != curCycle.ID:
                            lastCycle = currentSeason.getCycleInfo(lastFutureCycleInfo.seasonID)
                            return (curCycle, lastCycle)
                        return (curCycle,)
            return

    def _getLastFutureCycleRentInfo(self):
        now = time_utils.getCurrentLocalServerTimestamp()
        for seasonType, rentTypes in self.seasonRent.iteritems():
            currentSeason = self.seasonsController.getCurrentSeason(seasonType)
            if currentSeason:
                currentCycleID = currentSeason.getCycleID() or currentSeason.getLastActiveCycleID(now)
                futureCycleRents = first(sorted([ item[0] for item in rentTypes if item[1] == SeasonRentDuration.SEASON_CYCLE and item[0] > currentCycleID ], reverse=True))
                if futureCycleRents:
                    lastFutureCycleRentID = futureCycleRents
                    cycleInfo = currentSeason.getCycleInfo(lastFutureCycleRentID)
                    if cycleInfo:
                        return SeasonRentInfo(seasonType, lastFutureCycleRentID, SeasonRentDuration.SEASON_CYCLE, cycleInfo.endDate)

        return None

    def _getSeasonExpiryTime(self):
        activeSeasonRent = self.getActiveSeasonRent()
        if activeSeasonRent:
            lastFutureCycleRent = self._getLastFutureCycleRentInfo()
            if lastFutureCycleRent:
                return lastFutureCycleRent.expiryTime
            return activeSeasonRent.expiryTime


class FittingItem(GUIItem):
    __slots__ = ('_buyPrices', '_sellPrices', '_mayConsumeWalletResources', '_personalDiscountPrice', '_isHidden', '_inventoryCount', '_isUnlocked', '_isBoughtForAltPrice', '_rentInfo', '_restoreInfo', '_fullyConfigured', '_isInitiallyUnlocked', '_descriptor')

    class TARGETS(object):
        CURRENT = 1
        IN_INVENTORY = 2
        OTHER = 3

    def __init__(self, intCompactDescr, proxy=None, isBoughtForAltPrice=False, strCD=None):
        super(FittingItem, self).__init__(intCD=HasIntCD(intCompactDescr), strCD=strCD)
        self._isBoughtForAltPrice = isBoughtForAltPrice
        self._rentInfo = RentalInfoProvider(None, None, None, None, None, None)
        self._restoreInfo = None
        self._personalDiscountPrice = None
        self._descriptor = self._getDescriptor()
        if proxy is not None and proxy.inventory.isSynced() and proxy.stats.isSynced() and proxy.shop.isSynced():
            self._mayConsumeWalletResources = proxy.stats.mayConsumeWalletResources
            defaultPrice = proxy.shop.defaults.getItemPrice(self.intCD)
            if defaultPrice is None:
                defaultPrice = MONEY_UNDEFINED
            buyPrice, self._isHidden = proxy.shop.getItem(self.intCD)
            if buyPrice is None:
                buyPrice = MONEY_UNDEFINED
            altPrice = self._getAltPrice(buyPrice, proxy.shop)
            defaultAltPrice = self._getAltPrice(defaultPrice, proxy.shop.defaults)
            self._buyPrices = ItemPrices(itemPrice=ItemPrice(price=buyPrice, defPrice=defaultPrice), itemAltPrice=ItemPrice(price=altPrice, defPrice=defaultAltPrice))
            defaultSellPrice = Money.makeFromMoneyTuple(BigWorld.player().shop.getSellPrice(defaultPrice, proxy.shop.defaults.sellPriceModifiers(intCompactDescr), self.itemTypeID))
            sellPrice = Money.makeFromMoneyTuple(BigWorld.player().shop.getSellPrice(buyPrice, proxy.shop.sellPriceModifiers(intCompactDescr), self.itemTypeID))
            self._sellPrices = ItemPrices(itemPrice=ItemPrice(price=sellPrice, defPrice=defaultSellPrice), itemAltPrice=ITEM_PRICE_EMPTY)
            self._inventoryCount = proxy.inventory.getItems(self.itemTypeID, self.intCD)
            if self._inventoryCount is None:
                self._inventoryCount = 0
            self._isUnlocked = self.intCD in proxy.stats.unlocks
            self._isInitiallyUnlocked = self.intCD in proxy.stats.initialUnlocks
            self._fullyConfigured = True
        else:
            self._buyPrices = ITEM_PRICES_EMPTY
            self._sellPrices = ITEM_PRICES_EMPTY
            self._isHidden = False
            self._inventoryCount = 0
            self._isUnlocked = False
            self._mayConsumeWalletResources = False
            self._isInitiallyUnlocked = False
            self._fullyConfigured = False
        return

    def _getAltPrice(self, buyPrice, proxy):
        return MONEY_UNDEFINED

    @property
    def buyPrices(self):
        return self._buyPrices

    @property
    def sellPrices(self):
        return self._sellPrices

    @property
    def isForSale(self):
        return True

    @property
    def inventoryCount(self):
        return self._inventoryCount

    @property
    def isHidden(self):
        return self._isHidden

    @property
    def isUnlocked(self):
        return self._isUnlocked

    @isUnlocked.setter
    def isUnlocked(self, value):
        self._isUnlocked = value

    @property
    def isBoughtForAltPrice(self):
        return self._isBoughtForAltPrice

    @property
    def rentInfo(self):
        return self._rentInfo

    @property
    def restoreInfo(self):
        return self._restoreInfo

    @property
    def fullyConfigured(self):
        return self._fullyConfigured

    @property
    def isInitiallyUnlocked(self):
        return self._isInitiallyUnlocked

    @property
    def isSecret(self):
        return False

    @property
    def isCollectible(self):
        return False

    @property
    def isPremium(self):
        return self.buyPrices.hasPriceIn(Currency.GOLD)

    @property
    def isPremiumIGR(self):
        return False

    @property
    def isRentable(self):
        return False

    @property
    def isRented(self):
        return False

    @property
    def descriptor(self):
        return self._descriptor

    @property
    def isRemovable(self):
        return True

    @property
    def isRentPromotion(self):
        return False

    @property
    def minRentPrice(self):
        return None

    @property
    def rentLeftTime(self):
        pass

    def isPreviewAllowed(self):
        return False

    @property
    def userType(self):
        return getTypeInfoByName(self.itemTypeName)['userString']

    @property
    def userName(self):
        return self.descriptor.userString

    @property
    def longUserName(self):
        return self.userType + ' ' + self.userName

    @property
    def shortUserName(self):
        return self.descriptor.shortUserString

    @property
    def shortDescription(self):
        return getShortDescr(self.descriptor.description)

    @property
    def fullDescription(self):
        return stripColorTagDescrTags(self.descriptor.description)

    @property
    def shortDescriptionSpecial(self):
        return self.descriptor.shortDescriptionSpecial

    @property
    def longDescriptionSpecial(self):
        return self.descriptor.longDescriptionSpecial

    @property
    def name(self):
        return self.descriptor.name

    @property
    def level(self):
        return self.descriptor.level

    @property
    def isInInventory(self):
        return self.inventoryCount > 0

    def getShortInfo(self, vehicle=None, expanded=False):
        return '' if not GUI_SETTINGS.technicalInfo else self._getShortInfo(vehicle, expanded)

    def getParams(self, vehicle=None):
        return dict(params_helper.get(self, vehicle.descriptor if vehicle is not None else None))

    def getRentPackage(self, rentID=None):
        return None

    def getGUIEmblemID(self):
        pass

    @property
    def icon(self):
        return ICONS_MASK % {'type': self.itemTypeName,
         'subtype': '',
         'unicName': self.name.replace(':', '-')}

    def getExtraIconInfo(self, _=None):
        return None

    @property
    def iconSmall(self):
        return ICONS_MASK % {'type': self.itemTypeName,
         'subtype': 'small/',
         'unicName': self.name.replace(':', '-')}

    def getBonusIcon(self, size='small'):
        return self.icon

    def getShopIcon(self, size):
        pass

    def getBuyPrice(self, preferred=True):
        if self.buyPrices.hasAltPrice():
            if preferred:
                if self.isBoughtForAltPrice:
                    return self.buyPrices.itemAltPrice
            else:
                return self.buyPrices.itemAltPrice
        return self.buyPrices.itemPrice

    def getSellPrice(self, preferred=True):
        return self.sellPrices.itemPrice

    def getHighlightType(self, vehicle=None):
        return SLOT_HIGHLIGHT_TYPES.NO_HIGHLIGHT

    def getBigHighlightType(self, vehicle=None):
        return _BIG_HIGHLIGHT_TYPES_MAP[self.getHighlightType(vehicle)]

    def getOverlayType(self, vehicle=None):
        return self.getHighlightType(vehicle)

    def getBigOverlayType(self, vehicle=None):
        return _BIG_HIGHLIGHT_TYPES_MAP[self.getOverlayType(vehicle)]

    def isInstalled(self, vehicle, slotIdx=None):
        return False

    def isInSetup(self, vehicle, setupIndex=None, slotIdx=None):
        return False

    def isInOtherLayout(self, vehicle):
        return False

    def mayInstall(self, vehicle, slotIdx=None):
        optDevicesLayouts = None
        if vehicle.optDevices.setupLayouts.capacity > 1:
            optDevicesLayouts = []
            for setup in vehicle.optDevices.setupLayouts.setups.itervalues():
                optDevicesLayouts.append(setup.getIntCDs())

        return vehicle.descriptor.mayInstallComponent(self.intCD, optDevicesLayouts=optDevicesLayouts)

    def mayRemove(self, vehicle):
        return (True, '')

    def mayRent(self, money):
        return (False, GUI_ITEM_ECONOMY_CODE.UNDEFINED)

    def mayRestore(self, money):
        return (False, GUI_ITEM_ECONOMY_CODE.UNDEFINED)

    def mayRestoreWithExchange(self, money, exchangeRate):
        return False

    def mayObtainForMoney(self, money):
        mayRent, rentReason = self.mayRent(money)
        if self.isRestoreAvailable():
            mayPurchase, reason = self.mayRestore(money)
        else:
            mayPurchase, reason = self.mayPurchase(money)
        if mayRent or mayPurchase:
            return (True, GUI_ITEM_ECONOMY_CODE.UNDEFINED)
        return (mayRent, rentReason) if self.isRentable and not mayRent else (mayPurchase, reason)

    def mayPurchaseWithExchange(self, money, exchangeRate):
        canBuy, reason = self.mayPurchase(money)
        if canBuy:
            return canBuy
        if reason == GUI_ITEM_ECONOMY_CODE.NOT_ENOUGH_CREDITS and money.isSet(Currency.GOLD):
            money = money.exchange(Currency.GOLD, Currency.CREDITS, exchangeRate, default=0)
            price = self.getBuyPrice().price
            canBuy, reason = self._isEnoughMoney(price, money)
            return canBuy
        return False

    def mayObtainWithMoneyExchange(self, money, exchangeRate):
        canRent, _ = self.mayRent(money)
        if canRent:
            return True
        return True if self.isRestoreAvailable() and self.mayRestoreWithExchange(money, exchangeRate) else self.mayPurchaseWithExchange(money, exchangeRate)

    def mayPurchase(self, money):
        buyPrice = self.getBuyPrice(preferred=True).price
        result, code = self._mayPurchase(buyPrice, money)
        if not result:
            altPrice = self.getBuyPrice(preferred=False).price
            if buyPrice != altPrice:
                altResult, altCode = self._mayPurchase(altPrice, money)
                if altResult:
                    result, code = altResult, altCode
        return (result, code)

    def getTarget(self, vehicle):
        if self.isInstalled(vehicle):
            return self.TARGETS.CURRENT
        return self.TARGETS.IN_INVENTORY if self.isInInventory else self.TARGETS.OTHER

    def getConflictedEquipments(self, vehicle):
        pass

    def getInstalledVehicles(self, vehs):
        return set()

    def isRestorePossible(self):
        return False

    def isRestoreAvailable(self):
        return False

    def _mayPurchase(self, price, money):
        if self.itemTypeID not in (GUI_ITEM_TYPE.EQUIPMENT,
         GUI_ITEM_TYPE.OPTIONALDEVICE,
         GUI_ITEM_TYPE.SHELL,
         GUI_ITEM_TYPE.BATTLE_BOOSTER,
         GUI_ITEM_TYPE.CREW_BOOKS) and not self.isUnlocked and not self.isCollectible:
            return (False, GUI_ITEM_ECONOMY_CODE.UNLOCK_ERROR)
        return (False, GUI_ITEM_ECONOMY_CODE.ITEM_IS_HIDDEN) if self.isHidden else self._isEnoughMoney(price, money)

    @classmethod
    def _isEnoughMoney(cls, price, money):
        if not price.isDefined():
            return (False, GUI_ITEM_ECONOMY_CODE.ITEM_NO_PRICE)
        shortage = money.getShortage(price)
        if shortage:
            currency = shortage.getCurrency(byWeight=True)
            return (False, GUI_ITEM_ECONOMY_CODE.getCurrencyError(currency))
        return (True, GUI_ITEM_ECONOMY_CODE.UNDEFINED)

    def _sortByType(self, other):
        pass

    def _getDescriptor(self):
        return vehicles.getItemByCompactDescr(self.intCD)

    def _getShortInfo(self, vehicle=None, expanded=False):
        try:
            description = i18n.makeString(self._getShortInfoKey() + ('Full' if expanded else ''))
            vehicleDescr = vehicle.descriptor if vehicle is not None else None
            params = params_helper.getParameters(self, vehicleDescr)
            formattedParametersDict = dict(formatters.getFormattedParamsList(self.descriptor, params))
            result = description % formattedParametersDict
            return result
        except Exception:
            LOG_CURRENT_EXCEPTION()
            return ''

        return

    def _getShortInfoKey(self):
        return '#menu:descriptions/' + self.itemTypeName

    def __cmp__(self, other):
        if other is None:
            return 1
        else:
            res = cmp(self._intCD, other.intCDO)
            if res:
                return res
            res = self._sortByType(other)
            if res:
                return res
            res = self.level - other.level
            if res:
                return res
            buyMaxValues = self.buyPrices.getMaxValuesAsMoney()
            otherMaxValues = other.buyPrices.getMaxValuesAsMoney()
            for currency in Currency.BY_WEIGHT:
                res = buyMaxValues.get(currency, 0) - otherMaxValues.get(currency, 0)
                if res:
                    return res

            return cmp(self.userName, other.userName)

    def __eq__(self, other):
        return False if other is None else self.intCD == other.intCD

    def __repr__(self):
        return '%s<intCD:%d, type:%s, nation:%d>' % (self.__class__.__name__,
         self.intCD,
         self.itemTypeName,
         self.nationID)
