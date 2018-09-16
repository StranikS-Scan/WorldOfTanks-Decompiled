# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/fitting_item.py
from collections import namedtuple
import BigWorld
from debug_utils import LOG_CURRENT_EXCEPTION
from gui import GUI_SETTINGS
from gui.shared.gui_items import GUI_ITEM_TYPE, GUI_ITEM_ECONOMY_CODE
from gui.shared.gui_items.gui_item_economics import ItemPrice, ItemPrices, ITEM_PRICE_EMPTY, ITEM_PRICES_EMPTY
from gui.shared.gui_items.gui_item import GUIItem, HasIntCD
from gui.shared.items_parameters import params_helper, formatters
from gui.shared.money import Money, Currency, MONEY_UNDEFINED
from gui.shared.utils.functions import getShortDescr, stripShortDescrTags
from helpers import i18n, time_utils
from items import vehicles, getTypeInfoByName
ICONS_MASK = '../maps/icons/%(type)s/%(subtype)s%(unicName)s.png'
_RentalInfoProvider = namedtuple('RentalInfoProvider', ('rentExpiryTime', 'compensations', 'battlesLeft', 'winsLeft', 'isRented'))

class RentalInfoProvider(_RentalInfoProvider):

    @staticmethod
    def __new__(cls, additionalData=None, time=0, battles=0, wins=0, isRented=False, *args, **kwargs):
        additionalData = additionalData or {}
        if 'compensation' in additionalData:
            compensations = Money.makeFromMoneyTuple(additionalData['compensation'])
        else:
            compensations = MONEY_UNDEFINED
        result = _RentalInfoProvider.__new__(cls, time, compensations, battles, wins, isRented)
        return result

    def getTimeLeft(self):
        return float(time_utils.getTimeDeltaFromNow(time_utils.makeLocalServerTime(self.rentExpiryTime))) if self.rentExpiryTime != float('inf') else float('inf')

    def getExpiryState(self):
        return self.rentExpiryTime != float('inf') and self.battlesLeft <= 0 and self.winsLeft <= 0 and self.getTimeLeft() <= 0


class FittingItem(GUIItem, HasIntCD):
    __slots__ = ('_buyPrices', '_sellPrices', '_mayConsumeWalletResources', '_personalDiscountPrice', '_isHidden', '_inventoryCount', '_isUnlocked', '_isBoughtForAltPrice', '_rentInfo', '_restoreInfo', '_fullyConfigured', '_isInitiallyUnlocked')

    class TARGETS(object):
        CURRENT = 1
        IN_INVENTORY = 2
        OTHER = 3

    def __init__(self, intCompactDescr, proxy=None, isBoughtForAltPrice=False):
        GUIItem.__init__(self, proxy)
        HasIntCD.__init__(self, intCompactDescr)
        self._isBoughtForAltPrice = isBoughtForAltPrice
        self._rentInfo = RentalInfoProvider()
        self._restoreInfo = None
        self._personalDiscountPrice = None
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
        return vehicles.getItemByCompactDescr(self.intCD)

    @property
    def isRemovable(self):
        return True

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
        return stripShortDescrTags(self.descriptor.description)

    @property
    def name(self):
        return self.descriptor.name

    @property
    def level(self):
        return self.descriptor.level

    @property
    def isInInventory(self):
        return self.inventoryCount > 0

    @property
    def isFootball(self):
        return False

    def getShortInfo(self, vehicle=None, expanded=False):
        return '' if not GUI_SETTINGS.technicalInfo else self._getShortInfo(vehicle, expanded)

    def getParams(self, vehicle=None):
        return dict(params_helper.get(self, vehicle.descriptor if vehicle is not None else None))

    def getRentPackage(self, days=None):
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

    def isInstalled(self, vehicle, slotIdx=None):
        return False

    def mayInstall(self, vehicle, slotIdx=None):
        return vehicle.descriptor.mayInstallComponent(self.intCD)

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
         GUI_ITEM_TYPE.BATTLE_BOOSTER) and not self.isUnlocked:
            return (False, GUI_ITEM_ECONOMY_CODE.UNLOCK_ERROR)
        return (False, GUI_ITEM_ECONOMY_CODE.ITEM_IS_HIDDEN) if self.isHidden else self._isEnoughMoney(price, money)

    @classmethod
    def _isEnoughMoney(cls, price, money):
        if not price.isDefined():
            return (False, GUI_ITEM_ECONOMY_CODE.ITEM_NO_PRICE)
        shortage = money.getShortage(price)
        if shortage:
            currency = shortage.getCurrency(byWeight=True)
            return (False, GUI_ITEM_ECONOMY_CODE.getMoneyError(currency))
        return (True, GUI_ITEM_ECONOMY_CODE.UNDEFINED)

    def _sortByType(self, other):
        pass

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
            res = HasIntCD.__cmp__(self, other)
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
