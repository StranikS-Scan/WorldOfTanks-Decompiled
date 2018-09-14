# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/fitting_item.py
from collections import namedtuple
import BigWorld
from debug_utils import LOG_CURRENT_EXCEPTION
from helpers import i18n, time_utils
from items import vehicles, getTypeInfoByName
from gui import GUI_SETTINGS
from gui.shared.items_parameters import params_helper, formatters
from gui.shared.gui_items import GUI_ITEM_TYPE, GUI_ITEM_PURCHASE_CODE
from gui.shared.gui_items.gui_item import GUIItem, HasIntCD
from gui.shared.money import Money, ZERO_MONEY, Currency
from gui.shared.economics import getActionPrc
from gui.shared.utils.functions import getShortDescr, stripShortDescrTags
ICONS_MASK = '../maps/icons/%(type)s/%(subtype)s%(unicName)s.png'
_RentalInfoProvider = namedtuple('RentalInfoProvider', ('rentExpiryTime', 'compensations', 'battlesLeft', 'winsLeft', 'isRented'))

class RentalInfoProvider(_RentalInfoProvider):

    @staticmethod
    def __new__(cls, additionalData=None, time=0, battles=0, wins=0, isRented=False, *args, **kwargs):
        additionalData = additionalData or {}
        if 'compensation' in additionalData:
            compensations = Money(*additionalData['compensation'])
        else:
            compensations = ZERO_MONEY
        result = _RentalInfoProvider.__new__(cls, time, compensations, battles, wins, isRented)
        return result

    def getTimeLeft(self):
        return float(time_utils.getTimeDeltaFromNow(time_utils.makeLocalServerTime(self.rentExpiryTime))) if self.rentExpiryTime != float('inf') else float('inf')

    def getExpiryState(self):
        return self.rentExpiryTime != float('inf') and self.battlesLeft <= 0 and self.winsLeft <= 0 and self.getTimeLeft() <= 0


class FittingItem(GUIItem, HasIntCD):
    """
    Root item which can be bought and installed.
    """

    class TARGETS(object):
        CURRENT = 1
        IN_INVENTORY = 2
        OTHER = 3

    def __init__(self, intCompactDescr, proxy=None, isBoughtForCredits=False):
        """
        Ctr.
        
        :param intCompactDescr: item's int compact descriptor
        :param proxy: instance of ItemsRequester
        :param isBoughtForCredits: indicates whether the item has been bought for credits
        """
        GUIItem.__init__(self, proxy)
        HasIntCD.__init__(self, intCompactDescr)
        self.defaultPrice = ZERO_MONEY
        self._buyPrice = ZERO_MONEY
        self.sellPrice = ZERO_MONEY
        self.defaultSellPrice = ZERO_MONEY
        self.altPrice = None
        self.defaultAltPrice = None
        self.sellActionPrc = 0
        self.isHidden = False
        self.inventoryCount = 0
        self.sellForGold = False
        self.isUnlocked = False
        self.isBoughtForCredits = isBoughtForCredits
        self.rentInfo = RentalInfoProvider()
        self.restoreInfo = None
        self.fullyConfigured = False
        self._personalDiscountPrice = None
        if proxy is not None and proxy.isSynced():
            self.defaultPrice = proxy.shop.defaults.getItemPrice(self.intCompactDescr)
            if self.defaultPrice is None:
                self.defaultPrice = ZERO_MONEY
            self._buyPrice, self.isHidden, self.sellForGold = proxy.shop.getItem(self.intCompactDescr)
            if self._buyPrice is None:
                self._buyPrice = ZERO_MONEY
            self.defaultSellPrice = Money(*BigWorld.player().shop.getSellPrice(self.defaultPrice, proxy.shop.defaults.sellPriceModifiers(intCompactDescr), self.itemTypeID))
            self.sellPrice = Money(*BigWorld.player().shop.getSellPrice(self._buyPrice, proxy.shop.sellPriceModifiers(intCompactDescr), self.itemTypeID))
            self.inventoryCount = proxy.inventory.getItems(self.itemTypeID, self.intCompactDescr)
            if self.inventoryCount is None:
                self.inventoryCount = 0
            self.isUnlocked = self.intCD in proxy.stats.unlocks
            self.isInitiallyUnlocked = self.intCD in proxy.stats.initialUnlocks
            self.altPrice = self._getAltPrice(self._buyPrice, proxy.shop)
            self.defaultAltPrice = self._getAltPrice(self.defaultPrice, proxy.shop.defaults)
            self.sellActionPrc = -1 * getActionPrc(self.sellPrice, self.defaultSellPrice)
            self.fullyConfigured = True
        return

    def _getAltPrice(self, buyPrice, proxy):
        """
        Returns an alternative buy price.
        
        :param buyPrice: a buy price of the item
        :param proxy: an instance of ShopRequester
        
        :return: an alternative buy price in Money or None (by default)
        """
        return None

    @property
    def buyPrice(self):
        """
        Returns the current buy price.
        
        :return: the current buy price in Money or None (by default)
        """
        return self._buyPrice

    @property
    def actionPrc(self):
        """
        Returns the buy price with discount.
        
        :return: action buy price in Money or None (by default)
        """
        return getActionPrc(self.altPrice or self.buyPrice, self.defaultAltPrice or self.defaultPrice)

    @property
    def isSecret(self):
        return False

    @property
    def isPremium(self):
        return self.buyPrice.isSet(Currency.GOLD)

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
        return vehicles.getDictDescr(self.intCompactDescr)

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
        return self.descriptor.get('userString', '')

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
        return self.descriptor.get('shortUserString', '')

    @property
    def shortDescription(self):
        """
        Return the first occurrence of short description from string.
        """
        return getShortDescr(self.descriptor.get('description', ''))

    @property
    def fullDescription(self):
        """
        Returns short description tags from passed string and return full description body.
        :return: string
        """
        return stripShortDescrTags(self.descriptor.get('description', ''))

    @property
    def name(self):
        """
        Returns item's tech-name as string.
        """
        return self.descriptor.get('name', '')

    @property
    def level(self):
        """
        Returns item's level number value as int.
        """
        return self.descriptor.get('level', 0)

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
                formattedParametersDict['caliber'] = BigWorld.wg_getIntegralFormat(self.descriptor.gun['shots'][0]['shell']['caliber'])
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

    def getBuyPriceCurrency(self):
        """
        Returns the currency of the buy price. If the item has been bought for credits and the item has an
        alternative price, returns Currency.CREDITS even if the original currency differs from it.
        
        :return: string, see Currency enum.
        """
        if self.altPrice is not None:
            currency = self.altPrice.getCurrency(byWeight=True)
            if currency != Currency.CREDITS and self.isBoughtForCredits:
                return Currency.CREDITS
        return self.buyPrice.getCurrency(byWeight=True)

    def getBuyPrice(self):
        """
        Returns the buy price in consideration of item's alternative price and player's preferences (
        isBoughtForCredits property). Be aware that for some items (shells and equipments right now) buying for
        alternative price (for credits for example) might be disabled on the server side. This method doesn't check it
        and always returns price as if the switch is off.
        
        :return: Money
        """
        if self.altPrice is not None:
            currency = self.altPrice.getCurrency(byWeight=True)
            if currency != Currency.CREDITS and self.isBoughtForCredits:
                currency = Currency.CREDITS
            return Money.makeFrom(currency, self.altPrice.get(currency))
        else:
            return self.buyPrice

    def getSellPriceCurrency(self):
        """
        Returns the currency of the sell price.
        
        :return: string, see Currency enum.
        """
        return self.sellPrice.getCurrency(byWeight=True)

    def isInstalled(self, vehicle, slotIdx=None):
        """
        Item is installed on @vehicle. Can be overridden by inherited classes.
        :param vehicle: installation vehicle
        :param slotIdx: slot index to install. Used for equipments and optional devices.
        :return: is installed <bool>
        """
        return False

    def mayInstall(self, vehicle, slotIdx=None):
        """
        Item can be installed on @vehicle. Can be overridden by inherited classes.
        :param vehicle: installation vehicle
        :param slotIdx: slot index to install. Used for equipments and optional devices.
        :return: tuple(can be installed <bool>, error msg <str>)
        """
        return vehicle.descriptor.mayInstallComponent(self.intCD)

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
        return (False, '')

    def mayRestore(self, money):
        return (False, '')

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
            return (True, '')
        elif self.isRentable and not mayRent:
            return (mayRent, rentReason)
        else:
            return (mayPurchase, reason)

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
        elif reason == GUI_ITEM_PURCHASE_CODE.NOT_ENOUGH_CREDITS:
            price = self.altPrice or self.buyPrice
            money = money.exchange(Currency.GOLD, Currency.CREDITS, exchangeRate)
            return price <= money
        else:
            return False

    def mayObtainWithMoneyExchange(self, money, exchangeRate):
        """
        Check if possible to buy or to restore or to rent item with gold exchange.
        
        @param money: <Money>, available money
        @param exchangeRate: <int>, gold to credits exchange rate
        @return: <bool>
        """
        canRent, rentReason = self.mayRent(money)
        if self.isRestoreAvailable():
            mayPurchase = self.mayRestoreWithExchange(money, exchangeRate)
        else:
            mayPurchase = self.mayPurchaseWithExchange(money, exchangeRate)
        return canRent or mayPurchase

    def mayPurchase(self, money):
        """
        Item can be bought. If center is not available, than disables purchase.
        Can be overridden by inherited classes.
        
        :param money: <Money>, player money
        :return: tuple(can be installed <bool>, error msg <str>)
        """
        if getattr(BigWorld.player(), 'isLongDisconnectedFromCenter', False):
            return (False, GUI_ITEM_PURCHASE_CODE.CENTER_UNAVAILABLE)
        if self.itemTypeID not in (GUI_ITEM_TYPE.EQUIPMENT,
         GUI_ITEM_TYPE.OPTIONALDEVICE,
         GUI_ITEM_TYPE.SHELL,
         GUI_ITEM_TYPE.BATTLE_BOOSTER) and not self.isUnlocked:
            return (False, GUI_ITEM_PURCHASE_CODE.UNLOCK_ERROR)
        if self.isHidden:
            return (False, GUI_ITEM_PURCHASE_CODE.ITEM_IS_HIDDEN)
        price = self.altPrice or self.buyPrice
        if not price:
            return (True, GUI_ITEM_PURCHASE_CODE.OK)
        for c in price.getSetCurrencies():
            if money.get(c) >= price.get(c):
                return (True, GUI_ITEM_PURCHASE_CODE.OK)

        shortage = money.getShortage(price)
        if shortage:
            currency, _ = shortage.pop()
            return (False, '%s_error' % currency)
        return (True, GUI_ITEM_PURCHASE_CODE.OK)

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
            for currency in Currency.BY_WEIGHT:
                res = self.buyPrice.get(currency) - other.buyPrice.get(currency)
                if res:
                    return res

            return cmp(self.userName, other.userName)

    def __eq__(self, other):
        return False if other is None else self.intCompactDescr == other.intCompactDescr

    def __repr__(self):
        return '%s<intCD:%d, type:%s, nation:%d>' % (self.__class__.__name__,
         self.intCD,
         self.itemTypeName,
         self.nationID)
