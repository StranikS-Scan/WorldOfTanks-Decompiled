# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/goodies/goodie_items.py
import BigWorld
from goodies.goodie_constants import GOODIE_RESOURCE_TYPE, GOODIE_STATE, GOODIE_VARIETY, GOODIE_TARGET_TYPE
from gui import GUI_SETTINGS
from gui.shared.gui_items import GUI_ITEM_ECONOMY_CODE
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.shared.economics import getActionPrc
from gui.shared.formatters import text_styles
from gui.shared.money import Currency, MONEY_UNDEFINED
from gui.shared.gui_items.gui_item_economics import ItemPrices, ItemPrice, ITEM_PRICE_EMPTY, ITEM_PRICES_EMPTY
from shared_utils import CONST_CONTAINER
from helpers import time_utils
from helpers.i18n import makeString as _ms
_BOOSTER_ICON_PATH = '../maps/icons/boosters/%s.png'
_BOOSTER_BIG_ICON_PATH = '../maps/icons/boosters/%s_big.png'
_BOOSTER_TT_BIG_ICON_PATH = '../maps/icons/boosters/%s_tt_big.png'
_BOOSTER_QUALITY_SOURCE_PATH = '../maps/icons/boosters/booster_quality_%s.png'
_BOOSTER_TYPE_LOCALE = '#menu:booster/userName/%s'
_BOOSTER_DESCRIPTION_LOCALE = '#menu:booster/description/%s'
_BOOSTER_QUALITY_LOCALE = '#menu:booster/quality/%s'
MAX_ACTIVE_BOOSTERS_COUNT = 3

class BOOSTER_QUALITY_NAMES(CONST_CONTAINER):
    BIG = 'big'
    MEDIUM = 'medium'
    SMALL = 'small'


_BOOSTER_QUALITY_VALUES = {BOOSTER_QUALITY_NAMES.BIG: 12.5,
 BOOSTER_QUALITY_NAMES.MEDIUM: 7.5}
_BOOSTER_TYPE_NAMES = {GOODIE_RESOURCE_TYPE.GOLD: 'booster_gold',
 GOODIE_RESOURCE_TYPE.CREDITS: 'booster_credits',
 GOODIE_RESOURCE_TYPE.XP: 'booster_xp',
 GOODIE_RESOURCE_TYPE.CREW_XP: 'booster_crew_xp',
 GOODIE_RESOURCE_TYPE.FREE_XP: 'booster_free_xp'}
BOOSTERS_ORDERS = {GOODIE_RESOURCE_TYPE.XP: 0,
 GOODIE_RESOURCE_TYPE.CREW_XP: 1,
 GOODIE_RESOURCE_TYPE.FREE_XP: 2,
 GOODIE_RESOURCE_TYPE.CREDITS: 3,
 GOODIE_RESOURCE_TYPE.GOLD: 4}

class _Goodie(object):
    """
    Base goodie class.
    """

    def __init__(self, goodieID, goodieDescription, proxy):
        self._goodieID = goodieID
        self._goodieDescription = goodieDescription
        self._goodieValues = proxy.personalGoodies.get(goodieID, None)
        self.__state = GOODIE_STATE.INACTIVE
        self.__count = 0
        self.__finishTime = None
        goodieValues = proxy.personalGoodies.get(goodieID, None)
        if goodieValues is not None:
            self.__state = goodieValues.state
            self.__count = goodieValues.count
            self.__finishTime = goodieValues.finishTime
        return

    @property
    def count(self):
        return self.__count

    @property
    def finishTime(self):
        return self.__finishTime

    @property
    def state(self):
        return self.__state

    @property
    def enabled(self):
        return self._goodieDescription.enabled

    @property
    def maxCount(self):
        return self._goodieDescription.counter

    @property
    def expiryTime(self):
        return self._goodieDescription.useby

    @property
    def effectTime(self):
        return self._goodieDescription.lifetime

    @property
    def isInAccount(self):
        return self.count > 0

    @property
    def effectValue(self):
        return self._goodieDescription.resource.value

    def getFormattedValue(self, formatter=None):
        raise NotImplementedError

    @property
    def icon(self):
        raise NotImplementedError

    @property
    def bigIcon(self):
        raise NotImplementedError

    @property
    def userName(self):
        raise NotImplementedError

    @property
    def description(self):
        raise NotImplementedError


class _PersonalDiscount(_Goodie):
    """
    Base personal discount class. Personal discounts effect on prices in game.
    """

    def __init__(self, discountID, discountDescription, proxy):
        super(_PersonalDiscount, self).__init__(discountID, discountDescription, proxy)
        assert discountDescription.variety == GOODIE_VARIETY.DISCOUNT

    @property
    def discountID(self):
        return self._goodieID

    @property
    def targetType(self):
        """
        One of GOODIE_TARGET_TYPE s.
        Target of discount applying (premimum days buying, or xp exchange rate, or vehicle buy price, etc)
        """
        return self._goodieDescription.target.targetType

    @property
    def targetValue(self):
        """
        The name of the target (for example premium packet name, or item intCD)
        """
        return self._goodieDescription.target.targetValue

    @property
    def limit(self):
        """
        Limits resource usage (for example 100% discount on free xp conversion, but no more than 20 gold)
        """
        return self._goodieDescription.target.limit

    def getFormattedValue(self, formatter=None):
        """
        Gets discount formatted value
        """
        value = '%s%%' % self.effectValue
        return formatter(value) if formatter is not None else value

    @property
    def targetName(self):
        """
        Gets localized target name
        """
        raise NotImplementedError


class PersonalVehicleDiscount(_PersonalDiscount):
    """
    Personal vehicle discount class.
    Represent GUI instance of personal vehicle discount.
    Effects on targeted vehicle buy price.
    Personal vehicle discount doesn't summ with SSE action.
    Its work only if personal discount value more than SSE discount value.
    """

    def __init__(self, discountID, discountDescription, proxy):
        super(PersonalVehicleDiscount, self).__init__(discountID, discountDescription, proxy)
        assert self.targetType == GOODIE_TARGET_TYPE.ON_BUY_VEHICLE
        vehicle = proxy.getItemByTargetValue(self.targetValue)
        self.__targetName = vehicle.userName
        self.__bigIcon = vehicle.icon
        self.__effectValue = self.__getEffectValue(vehicle)

    @property
    def effectValue(self):
        return self.__effectValue

    @property
    def icon(self):
        return RES_ICONS.MAPS_ICONS_LIBRARY_BONUSES_VEHICLEDISCOUNT

    @property
    def bigIcon(self):
        return self.__bigIcon

    @property
    def targetName(self):
        return self.__targetName

    @property
    def userName(self):
        return _ms(MENU.DISCOUNT_USERNAME_VEHICLE)

    @property
    def description(self):
        return _ms(MENU.DISCOUNT_DESCRIPTION_VEHICLE, effectValue=self.getFormattedValue(), targetName=self.targetName)

    def __getEffectValue(self, vehicle):
        """
        Calculates percent discount value for targeted vehicle
        """
        resoruce = self._goodieDescription.resource
        if resoruce.isPercentage:
            return resoruce.value
        else:
            defaultCreditPrice = vehicle.buyPrices.itemPrice.defPrice.getSignValue(Currency.CREDITS)
            discountCreditPrice = defaultCreditPrice - resoruce.value
            return getActionPrc(discountCreditPrice, defaultCreditPrice)


class Booster(_Goodie):
    """
    Booster class. Represent GUI instance of booster.
    Booster effects on game params such as earned xp, free xp, crew xp and credits in battle.
    Boosters gradates by effects value and effects types.
    Boosters can be activated by player and has time-limited period of work
    """

    def __init__(self, boosterID, boosterDescription, proxy):
        super(Booster, self).__init__(boosterID, boosterDescription, proxy)
        assert boosterDescription.variety == GOODIE_VARIETY.BOOSTER
        buyPrice, defaultPrice, altPrice, defaultAltPrice, self.isHidden = proxy.getBoosterPriceData(boosterID)
        buyPrice = ItemPrice(price=buyPrice, defPrice=defaultPrice)
        if altPrice is not None:
            altPrice = ItemPrice(price=altPrice, defPrice=defaultAltPrice)
        else:
            altPrice = ITEM_PRICE_EMPTY
        self.__buyPrices = ItemPrices(itemPrice=buyPrice, itemAltPrice=altPrice)
        self.__sellPrices = ITEM_PRICES_EMPTY
        self.__activeBoostersValues = proxy.getActiveBoostersTypes()
        return

    @property
    def buyPrices(self):
        return self.__buyPrices

    @property
    def sellPrices(self):
        return self.__sellPrices

    @property
    def boosterID(self):
        return self._goodieID

    @property
    def boosterType(self):
        return self._goodieDescription.resource.resourceType

    @property
    def icon(self):
        return _BOOSTER_ICON_PATH % self.boosterGuiType

    @property
    def bigIcon(self):
        return _BOOSTER_BIG_ICON_PATH % self.boosterGuiType

    @property
    def bigTooltipIcon(self):
        return _BOOSTER_TT_BIG_ICON_PATH % self.boosterGuiType

    @property
    def boosterGuiType(self):
        return _BOOSTER_TYPE_NAMES[self.boosterType]

    @property
    def quality(self):
        boosterQualityValues = GUI_SETTINGS.lookup(self.boosterGuiType) or _BOOSTER_QUALITY_VALUES
        if self.effectValue >= boosterQualityValues[BOOSTER_QUALITY_NAMES.BIG]:
            return BOOSTER_QUALITY_NAMES.BIG
        elif self.effectValue >= boosterQualityValues[BOOSTER_QUALITY_NAMES.MEDIUM]:
            return BOOSTER_QUALITY_NAMES.MEDIUM
        else:
            return BOOSTER_QUALITY_NAMES.SMALL

    @property
    def qualityStr(self):
        return _ms(_BOOSTER_QUALITY_LOCALE % self.quality)

    @property
    def inCooldown(self):
        return self.state == GOODIE_STATE.ACTIVE

    @property
    def isReadyToActivate(self):
        return self.isReadyToUse or self.isReadyToUpdate

    @property
    def isReadyToUse(self):
        activeBoosterTypes = [ boosterType for boosterType, _, _ in self.__activeBoostersValues ]
        return self.count > 0 and self.state == GOODIE_STATE.INACTIVE and len(self.__activeBoostersValues) < MAX_ACTIVE_BOOSTERS_COUNT and self.boosterType not in activeBoosterTypes if self.enabled else False

    @property
    def isReadyToUpdate(self):
        if self.enabled:
            for aBoosterType, aEffectValue, _ in self.__activeBoostersValues:
                if self.boosterType == aBoosterType and self.count > 0:
                    return self.effectValue > aEffectValue

        return False

    @property
    def userName(self):
        return _ms(_BOOSTER_TYPE_LOCALE % self.boosterGuiType)

    @property
    def fullUserName(self):
        return _ms(MENU.BOOSTERSWINDOW_BOOSTERSTABLERENDERER_HEADER, boosterName=self.userName, quality=self.qualityStr)

    @property
    def description(self):
        return _ms(_BOOSTER_DESCRIPTION_LOCALE % self.boosterGuiType, effectValue=self.getFormattedValue(text_styles.neutral)) + _ms(MENU.BOOSTER_DESCRIPTION_EFFECTTIME, effectTime=self.getEffectTimeStr())

    def getCooldownAsPercent(self):
        percent = 0
        if self.finishTime is not None and self.effectTime is not None:
            leftTime = self.getUsageLeftTime()
            percent = float(max(self.effectTime - leftTime, 0)) / self.effectTime * 100
        return percent

    def getUsageLeftTime(self):
        return time_utils.getTimeDeltaFromNow(time_utils.makeLocalServerTime(self.finishTime)) if self.finishTime is not None else 0

    def getUsageLeftTimeStr(self):
        return time_utils.getTillTimeString(self.getUsageLeftTime(), MENU.TIME_TIMEVALUE)

    def getShortLeftTimeStr(self):
        return time_utils.getTillTimeString(self.getUsageLeftTime(), MENU.TIME_TIMEVALUESHORT)

    def getEffectTimeStr(self):
        return time_utils.getTillTimeString(self.effectTime, MENU.TIME_TIMEVALUE)

    def getQualityIcon(self):
        return _BOOSTER_QUALITY_SOURCE_PATH % self.quality

    def getExpiryDate(self):
        return BigWorld.wg_getLongDateFormat(self.expiryTime) if self.expiryTime is not None else ''

    def getExpiryDateStr(self):
        if self.expiryTime:
            text = _ms(MENU.BOOSTERSWINDOW_BOOSTERSTABLERENDERER_TIME, tillTime=self.getExpiryDate())
        else:
            text = _ms(MENU.BOOSTERSWINDOW_BOOSTERSTABLERENDERER_UNDEFINETIME)
        return text_styles.standard(text)

    def getBuyPrice(self, preferred=True):
        """
        For goodie item - return always item's regular buy price
        :param preferred: bool - this flag is necessary to match FittingItem's signature
        :return: ItemPrice
        """
        return self.buyPrices.itemPrice

    def getSellPrice(self, preferred=True):
        """
        For goodie item - return always item's regular sell price
        :param preferred: bool - this flag is necessary to match FittingItem's signature
        :return: ItemPrice
        """
        return self.sellPrices.itemPrice

    def mayPurchase(self, money):
        """
        Checks booster purchasing possibility.
        if center is not available, than disables purchase.
        Return True and empty str if booster can be purchased,
        else return False and error msg.
        """
        if getattr(BigWorld.player(), 'isLongDisconnectedFromCenter', False):
            return (False, GUI_ITEM_ECONOMY_CODE.CENTER_UNAVAILABLE)
        return (False, GUI_ITEM_ECONOMY_CODE.ITEM_IS_HIDDEN) if self.isHidden else self._isEnoughMoney(self.buyPrices, money)

    def getFormattedValue(self, formatter=None):
        """
        Gets booster formatted value
        """
        if self.effectValue > 0:
            value = '+%s%%' % self.effectValue
        else:
            value = '%s%%' % self.effectValue
        return formatter(value) if formatter is not None else value

    @classmethod
    def _isEnoughMoney(cls, prices, money):
        """
        Determines if the given money enough for buying the booster for a price.
        
        :param prices: item prices represented by ItemPrices
        :param money: money for buying, see Money
        :return: tuple(can be installed <bool>, error msg <str>), also see GUI_ITEM_ECONOMY_CODE
        """
        shortage = MONEY_UNDEFINED
        for itemPrice in prices:
            need = money.getShortage(itemPrice.price)
            if need:
                shortage += need
            return (True, GUI_ITEM_ECONOMY_CODE.UNDEFINED)

        if shortage:
            currency = shortage.getCurrency(byWeight=True)
            return (False, GUI_ITEM_ECONOMY_CODE.getMoneyError(currency))
        return (False, GUI_ITEM_ECONOMY_CODE.ITEM_NO_PRICE)
