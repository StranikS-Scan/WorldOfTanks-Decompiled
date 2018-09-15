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
        """
        Ctr.
        
        :param intCompactDescr: item's int compact descriptor
        :param proxy: instance of ItemsRequester
        :param isBoughtForAltPrice: indicates whether the item has been bought for credits(alt price)
        """
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
        """
        Returns an alternative buy price.
        
        :param buyPrice: a buy price of the item
        :param proxy: an instance of ShopRequester
        
        :return: an alternative buy price in Money or MONEY_UNDEFINED (by default)
        """
        return MONEY_UNDEFINED

    @property
    def buyPrices(self):
        """
        Return available buy prices, including a regular price and alternative price.
        :return: ItemPrices object
        """
        return self._buyPrices

    @property
    def sellPrices(self):
        """
        Return available sell prices, including a regular sell price and alternative sell price.
        :return: ItemPrices object
        """
        return self._sellPrices

    @property
    def isForSale(self):
        """
        Some items can not be sold, they will have 'notForSale' tag in xml file.
        After moving to Money 2.0 concept this property can be removed and sellPrice.isDefined() will
        be used to replace this property.
        :return: bool, True if the item can be sold, False otherwise
        """
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
        """
        This property is set from g_CurrentVehicle
        """
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
        """
        Indicates whether the item can be removed from vehicle for free. Otherwise for gold or other currency
        differing from credits.
        
        :return: boolean
        """
        return True

    @property
    def minRentPrice(self):
        """
        Returns the min rent price.
        
        :return:  the min rent price in Money or None (by default)
        """
        return None

    @property
    def rentLeftTime(self):
        """
        Returns rent left time in seconds.
        
        :return:  int, rent left time in seconds
        """
        pass

    def isPreviewAllowed(self):
        return False

    @property
    def userType(self):
        """
        Returns item's type represented as user-friendly string.
        """
        return getTypeInfoByName(self.itemTypeName)['userString']

    @property
    def userName(self):
        """
        Returns item's name represented as user-friendly string.
        """
        return self.descriptor.userString

    @property
    def longUserName(self):
        """
        Returns item's long name represented as user-friendly string
        """
        return self.userType + ' ' + self.userName

    @property
    def shortUserName(self):
        """
        Returns item's short name represented as user-friendly string
        """
        return self.descriptor.shortUserString

    @property
    def shortDescription(self):
        """
        Return the first occurrence of short description from string.
        """
        return getShortDescr(self.descriptor.description)

    @property
    def fullDescription(self):
        """
        Returns short description tags from passed string and return full description body.
        :return: string
        """
        return stripShortDescrTags(self.descriptor.description)

    @property
    def name(self):
        """
        Returns item's tech-name as string.
        """
        return self.descriptor.name

    @property
    def level(self):
        """
        Returns item's level number value as int.
        """
        return self.descriptor.level

    @property
    def isInInventory(self):
        """
        Returns True if the item is in inventory, False otherwise.
        """
        return self.inventoryCount > 0

    def _getShortInfo(self, vehicle=None, expanded=False):
        """
        Returns string with item's parameters.
        
        :param vehicle: vehicle: vehicle which descriptor will be passed to the params_helper.getParameters
        :param expanded: indicates if it should be expanded.
        :return: formatted user-string
        """
        try:
            description = i18n.makeString('#menu:descriptions/' + self.itemTypeName + ('Full' if expanded else ''))
            vehicleDescr = vehicle.descriptor if vehicle is not None else None
            params = params_helper.getParameters(self, vehicleDescr)
            formattedParametersDict = dict(formatters.getFormattedParamsList(self.descriptor, params))
            if self.itemTypeName == vehicles._VEHICLE:
                formattedParametersDict['caliber'] = BigWorld.wg_getIntegralFormat(self.descriptor.gun.shots[0].shell.caliber)
            result = description % formattedParametersDict
            return result
        except Exception:
            LOG_CURRENT_EXCEPTION()
            return ''

        return

    def getShortInfo(self, vehicle=None, expanded=False):
        """
        Returns string with item's parameters or empty string if parameters is not available.
        """
        return '' if not GUI_SETTINGS.technicalInfo else self._getShortInfo(vehicle, expanded)

    def getParams(self, vehicle=None):
        """
        Returns dictionary of item's parameters to show in GUI
        """
        return dict(params_helper.get(self, vehicle.descriptor if vehicle is not None else None))

    def getRentPackage(self, days=None):
        return None

    def getGUIEmblemID(self):
        """
        Returns item's frame label as string. Should be overridden by derived classes.
        """
        pass

    @property
    def icon(self):
        """
        Returns item's icon path
        """
        return ICONS_MASK % {'type': self.itemTypeName,
         'subtype': '',
         'unicName': self.name.replace(':', '-')}

    @property
    def iconSmall(self):
        return ICONS_MASK % {'type': self.itemTypeName,
         'subtype': 'small/',
         'unicName': self.name.replace(':', '-')}

    def getBonusIcon(self, size='small'):
        return self.icon

    def getBuyPrice(self, preferred=True):
        """
        Returns the buy price in consideration of item's alternative price and player's preferences (only if the
        preferred argument is set to True).
        Be aware that for some items (shells and equipments right now) buying for alternative price (for credits
        for example) might be disabled on the server side. This method doesn't check it and always returns price
        as if the switch is off.
        
        :param preferred: bool, whether isBoughtForAltPrice should be checked.
        :return: ItemPrice
        """
        if self.buyPrices.hasAltPrice():
            if preferred:
                if self.isBoughtForAltPrice:
                    return self.buyPrices.itemAltPrice
            else:
                return self.buyPrices.itemAltPrice
        return self.buyPrices.itemPrice

    def getSellPrice(self, preferred=True):
        """
        The logic is similar to the previous method - getBuyPrice() but in terms of 'sell' price.
        At the moment we don't have cases to sell an item for alt price, but in future it can appear.
        :param preferred: bool, pass any value, in the future the flag can be used like 'isBoughtForAltPrice'
        :return: ItemPrice
        """
        return self.sellPrices.itemPrice

    def isInstalled(self, vehicle, slotIdx=None):
        """
        Item is installed on @vehicle. Can be overridden by inherited classes.
        :param vehicle: installation vehicle
        :param slotIdx: slot index to install. Used for equipments and optional devices.
        :return: is installed <bool>
        """
        return False

    def mayInstall(self, vehicle, slotIdx=None, position=0):
        """
        Item can be installed on @vehicle. Can be overridden by inherited classes.
        :param vehicle: installation vehicle
        :param slotIdx: slot index to install. Used for equipments and optional devices.
        :return: tuple(can be installed <bool>, error msg <str>)
        """
        return vehicle.descriptor.mayInstallComponent(self.intCD, position)

    def mayRemove(self, vehicle):
        """
        Item can be removed from @vehicle. Can be overridden by inherited classes.
        :param vehicle: removal vehicle
        :return: tuple(can be removed <bool>, error msg <str>)
        """
        return (True, '')

    def mayRent(self, money):
        """
        Item can be rented. Can be overridden by inherited classes.
        
        :param money: player money as Money
        :return: tuple(can be installed <bool>, error msg <str>)
        """
        return (False, GUI_ITEM_ECONOMY_CODE.UNDEFINED)

    def mayRestore(self, money):
        return (False, GUI_ITEM_ECONOMY_CODE.UNDEFINED)

    def mayRestoreWithExchange(self, money, exchangeRate):
        return False

    def mayObtainForMoney(self, money):
        """
        # Check if possible to buy or to restore or to rent item
        
        @param money: <Money>
        @return: <bool>
        """
        mayRent, rentReason = self.mayRent(money)
        if self.isRestoreAvailable():
            mayPurchase, reason = self.mayRestore(money)
        else:
            mayPurchase, reason = self.mayPurchase(money)
        if mayRent or mayPurchase:
            return (True, GUI_ITEM_ECONOMY_CODE.UNDEFINED)
        return (mayRent, rentReason) if self.isRentable and not mayRent else (mayPurchase, reason)

    def mayPurchaseWithExchange(self, money, exchangeRate):
        """
        Returns True if it is possible to exchange gold for credits to buy item.
        
        :param money: Money
        :param exchangeRate: gold to credits exchange rate
        :return: <bool>
        """
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
        """
        Check if possible to buy or to restore or to rent item with gold exchange.
        
        @param money: <Money>, available money
        @param exchangeRate: <int>, gold to credits exchange rate
        @return: <bool>
        """
        canRent, rentReason = self.mayRent(money)
        if canRent:
            return True
        return True if self.isRestoreAvailable() and self.mayRestoreWithExchange(money, exchangeRate) else self.mayPurchaseWithExchange(money, exchangeRate)

    def mayPurchase(self, money):
        """
        Item can be bought. If center is not available, than disables purchase for gold.
        We should check two prices: one is default price and other is alternative if it exists.
        Can be overridden by inherited classes.
        
        :param money: <Money>, player money
        :return: tuple(can be installed <bool>, error msg <str>)
        """
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
        """
        Returns the target for UI components.
        """
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
        currency = price.getCurrency(byWeight=False)
        wallet = BigWorld.player().serverSettings['wallet']
        useGold = bool(wallet[0])
        if currency == Currency.GOLD and useGold:
            if not self._mayConsumeWalletResources:
                return (False, GUI_ITEM_ECONOMY_CODE.WALLET_NOT_AVAILABLE)
        elif getattr(BigWorld.player(), 'isLongDisconnectedFromCenter', False):
            return (False, GUI_ITEM_ECONOMY_CODE.CENTER_UNAVAILABLE)
        if self.itemTypeID not in (GUI_ITEM_TYPE.EQUIPMENT,
         GUI_ITEM_TYPE.OPTIONALDEVICE,
         GUI_ITEM_TYPE.SHELL,
         GUI_ITEM_TYPE.BATTLE_BOOSTER) and not self.isUnlocked:
            return (False, GUI_ITEM_ECONOMY_CODE.UNLOCK_ERROR)
        return (False, GUI_ITEM_ECONOMY_CODE.ITEM_IS_HIDDEN) if self.isHidden else self._isEnoughMoney(price, money)

    @classmethod
    def _isEnoughMoney(cls, price, money):
        """
        Determines if the given money enough for buying/restoring an item with the given price. Note that the method
        should NOT check if the given price is defined and will return (True, '') if the price is undefined (see Money
        class, isDefined method).
        
        :param price: item price represented by Money
        :param money: money for buying, see Money
        :return: tuple(can be installed <bool>, error msg <str>), also see GUI_ITEM_ECONOMY_CODE
        """
        if not price.isDefined():
            return (False, GUI_ITEM_ECONOMY_CODE.ITEM_NO_PRICE)
        shortage = money.getShortage(price)
        if shortage:
            currency = shortage.getCurrency(byWeight=True)
            return (False, GUI_ITEM_ECONOMY_CODE.getMoneyError(currency))
        return (True, GUI_ITEM_ECONOMY_CODE.UNDEFINED)

    def _sortByType(self, other):
        pass

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
