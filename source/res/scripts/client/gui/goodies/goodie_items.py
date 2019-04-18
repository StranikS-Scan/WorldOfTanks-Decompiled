# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/goodies/goodie_items.py
import time
import weakref
import typing
import BigWorld
from constants import FORT_ORDER_TYPE
from goodies.goodie_constants import GOODIE_RESOURCE_TYPE, GOODIE_STATE, GOODIE_VARIETY, GOODIE_TARGET_TYPE
from goodies.goodie_helpers import GOODIE_TEXT_TO_RESOURCE
from gui import GUI_SETTINGS
from gui.Scaleform.genConsts.STORE_CONSTANTS import STORE_CONSTANTS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.shared.gui_items import GUI_ITEM_ECONOMY_CODE, KPI
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.RES_SHOP_EXT import RES_SHOP_EXT
from gui.shared.economics import getActionPrc
from gui.shared.formatters import text_styles
from gui.shared.money import Currency, MONEY_UNDEFINED
from gui.shared.gui_items.gui_item_economics import ItemPrices, ItemPrice, ITEM_PRICE_EMPTY, ITEM_PRICES_EMPTY
from shared_utils import CONST_CONTAINER, first
from helpers import time_utils
from helpers.i18n import makeString as _ms
if typing.TYPE_CHECKING:
    from skeletons.gui.goodies import IGoodiesCache
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
_BOOSTER_TYPE_TEXT = {v:k for k, v in GOODIE_TEXT_TO_RESOURCE.iteritems()}
BOOSTERS_ORDERS = {GOODIE_RESOURCE_TYPE.XP: 0,
 GOODIE_RESOURCE_TYPE.CREW_XP: 1,
 GOODIE_RESOURCE_TYPE.FREE_XP: 2,
 GOODIE_RESOURCE_TYPE.CREDITS: 3,
 GOODIE_RESOURCE_TYPE.GOLD: 4}
GOODIE_TYPE_TO_KPI_NAME_MAP = {GOODIE_RESOURCE_TYPE.XP: KPI.Name.GAME_XP,
 GOODIE_RESOURCE_TYPE.FREE_XP: KPI.Name.GAME_FREE_XP,
 GOODIE_RESOURCE_TYPE.CREW_XP: KPI.Name.GAME_CREW_XP,
 GOODIE_RESOURCE_TYPE.CREDITS: KPI.Name.GAME_CREDITS}

class _Goodie(object):

    def __init__(self, goodieID, goodieDescription, stateProvider=None):
        self._goodieID = goodieID
        self._goodieDescription = goodieDescription
        self.__state = GOODIE_STATE.INACTIVE
        self.__count = 0
        self.__finishTime = None
        self._stateProvider = weakref.proxy(stateProvider) if stateProvider else None
        return

    @property
    def count(self):
        return self.__getStateAttribute('count', 0)

    @property
    def finishTime(self):
        return self.__getStateAttribute('finishTime', 0)

    @property
    def state(self):
        return self.__getStateAttribute('state', GOODIE_STATE.INACTIVE)

    @property
    def enabled(self):
        return self.__getDescrAttribute('enabled', False)

    @property
    def maxCount(self):
        return self.__getDescrAttribute('counter', 0)

    @property
    def expiryTime(self):
        return self.__getDescrAttribute('useby', 0)

    @property
    def effectTime(self):
        return self.__getDescrAttribute('lifetime', 0)

    @property
    def isInAccount(self):
        return self.count > 0

    @property
    def effectValue(self):
        return self._goodieDescription.resource.value if self._goodieDescription else 0

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

    def __getStateAttribute(self, attributeName, default=None):
        if self._stateProvider:
            goodie = self._stateProvider.personalGoodies.get(self._goodieID)
            if goodie:
                return getattr(goodie, attributeName, default)
        return default

    def __getDescrAttribute(self, attributeName, default=None):
        return getattr(self._goodieDescription, attributeName, default) if self._goodieDescription else default


class _PersonalDiscount(_Goodie):

    def __init__(self, discountID, discountDescription, proxy):
        super(_PersonalDiscount, self).__init__(discountID, discountDescription, proxy)

    @property
    def discountID(self):
        return self._goodieID

    @property
    def targetType(self):
        return self._goodieDescription.target.targetType

    @property
    def targetValue(self):
        return self._goodieDescription.target.targetValue

    @property
    def limit(self):
        return self._goodieDescription.target.limit

    def getFormattedValue(self, formatter=None):
        value = '{}%'.format(self.effectValue)
        return formatter(value) if formatter is not None else value

    @property
    def targetName(self):
        raise NotImplementedError


class PersonalVehicleDiscount(_PersonalDiscount):

    def __init__(self, discountID, discountDescription, proxy):
        super(PersonalVehicleDiscount, self).__init__(discountID, discountDescription, proxy)
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
        resoruce = self._goodieDescription.resource
        if resoruce.isPercentage:
            return resoruce.value
        defaultCreditPrice = vehicle.buyPrices.itemPrice.defPrice.getSignValue(Currency.CREDITS)
        discountCreditPrice = defaultCreditPrice - resoruce.value
        return getActionPrc(discountCreditPrice, defaultCreditPrice)


class BoosterUICommon(_Goodie):

    @property
    def boosterID(self):
        return self._goodieID

    @property
    def boosterType(self):
        return self._goodieDescription.resource.resourceType

    @property
    def boosterGuiType(self):
        return _BOOSTER_TYPE_NAMES[self.boosterType]

    @property
    def icon(self):
        return RES_ICONS.boosterIconPath(self.boosterGuiType)

    @property
    def bigIcon(self):
        return RES_ICONS.boosterBigIconPath(self.boosterGuiType)

    @property
    def userName(self):
        return _ms(MENU.boosterTypeLocale(self.boosterGuiType))

    @property
    def description(self):
        return self.getDescription(valueFormatter=text_styles.neutral)

    @property
    def bigTooltipIcon(self):
        return RES_ICONS.boosterTTBigIconPath(self.boosterGuiType)

    def getCooldownAsPercent(self):
        percent = 0
        if self.finishTime is not None and self.effectTime is not None:
            leftTime = self.getUsageLeftTime()
            percent = float(max(self.effectTime - leftTime, 0)) / self.effectTime * 100
        return percent

    def getUsageLeftTime(self):
        return time_utils.getTimeDeltaFromNow(time_utils.makeLocalServerTime(self.finishTime)) if self.finishTime is not None else 0

    def getUsageLeftTimeStr(self):
        return time_utils.getTillTimeString(self.getUsageLeftTime(), MENU.BOOSTERS_TIMELEFT, removeLeadingZeros=True)

    def getEffectTimeStr(self, hoursOnly=False):
        return _ms(MENU.VEHICLEPREVIEW_TIMELEFTSHORT_HOURS, hour=str(time.gmtime(self.effectTime).tm_hour)) if hoursOnly else time_utils.getTillTimeString(self.effectTime, MENU.TIME_TIMEVALUE)

    def getFormattedValue(self, formatter=None):
        if self.effectValue > 0:
            value = '+{}%'.format(self.effectValue)
        else:
            value = '{}%'.format(self.effectValue)
        return formatter(value) if formatter is not None else value


class Booster(BoosterUICommon):

    def __init__(self, boosterID, boosterDescription, stateProvider):
        super(Booster, self).__init__(boosterID, boosterDescription, stateProvider)
        self.__buyPrices = ITEM_PRICES_EMPTY
        self.__sellPrices = ITEM_PRICES_EMPTY

    @property
    def buyPrices(self):
        if not self.__buyPrices:
            self.__buildPrice()
        return self.__buyPrices

    @property
    def sellPrices(self):
        if not self.__sellPrices:
            self.__buildPrice()
        return self.__sellPrices

    @property
    def quality(self):
        boosterQualityValues = GUI_SETTINGS.lookup(self.boosterGuiType) or _BOOSTER_QUALITY_VALUES
        if self.effectValue >= boosterQualityValues[BOOSTER_QUALITY_NAMES.BIG]:
            return BOOSTER_QUALITY_NAMES.BIG
        return BOOSTER_QUALITY_NAMES.MEDIUM if self.effectValue >= boosterQualityValues[BOOSTER_QUALITY_NAMES.MEDIUM] else BOOSTER_QUALITY_NAMES.SMALL

    @property
    def qualityStr(self):
        return _ms(MENU.boosterQualityLocale(self.quality))

    @property
    def inCooldown(self):
        return self.state == GOODIE_STATE.ACTIVE

    @property
    def isReadyToActivate(self):
        return self.isReadyToUse or self.isReadyToUpdate

    @property
    def isReadyToUse(self):
        activeBoosterTypes = [ boosterType for boosterType, _, _ in self.__getActiveBoosters() ]
        return self.count > 0 and self.state == GOODIE_STATE.INACTIVE and len(self.__getActiveBoosters()) < MAX_ACTIVE_BOOSTERS_COUNT and self.boosterType not in activeBoosterTypes if self.enabled else False

    @property
    def isReadyToUpdate(self):
        if self.enabled:
            for aBoosterType, aEffectValue, _ in self.__getActiveBoosters():
                if self.boosterType == aBoosterType and self.count > 0:
                    return self.effectValue > aEffectValue

        return False

    @property
    def fullUserName(self):
        return _ms(MENU.BOOSTERSWINDOW_BOOSTERSTABLERENDERER_HEADER, boosterName=self.userName, quality=self.qualityStr)

    @property
    def shortDescriptionSpecial(self):
        return _ms(TOOLTIPS.BOOSTERSWINDOW_BOOSTER_SHORTDESCRIPTIONSPECIAL)

    @property
    def longDescriptionSpecial(self):
        return _ms(TOOLTIPS.BOOSTERSWINDOW_BOOSTER_LONGDESCRIPTIONSPECIAL)

    @property
    def isHidden(self):
        return self._stateProvider.isBoosterHidden(self.boosterID) if self._stateProvider else False

    @property
    def kpi(self):
        kpiList = []
        name = GOODIE_TYPE_TO_KPI_NAME_MAP.get(self.boosterType)
        if name is not None:
            kpiList.append(KPI(name, 1.0 + self.effectValue / 100.0, KPI.Type.MUL))
        return kpiList

    def getTypeAsString(self):
        return _BOOSTER_TYPE_TEXT[self.boosterType]

    def getDescription(self, valueFormatter=None):
        return _ms(MENU.boosterDescriptionLocale(self.boosterGuiType), effectValue=self.getFormattedValue(valueFormatter)) + _ms(MENU.BOOSTER_DESCRIPTION_EFFECTTIME, effectTime=self.getEffectTimeStr())

    def getBonusDescription(self, valueFormatter=None):
        return _ms(MENU.boosterBonusLocale(self.boosterGuiType), effectValue=self.getFormattedValue(valueFormatter), effectHours=self.getEffectTimeStr(hoursOnly=True))

    def getShortLeftTimeStr(self):
        return time_utils.getTillTimeString(self.getUsageLeftTime(), MENU.TIME_TIMEVALUESHORT)

    def getQualityIcon(self):
        return RES_ICONS.boosterQualitySourcePath(self.quality)

    def getShopIcon(self, size=STORE_CONSTANTS.ICON_SIZE_MEDIUM):
        return RES_SHOP_EXT.getBoosterIcon(size, self.boosterGuiType)

    def getExpiryDate(self):
        return BigWorld.wg_getLongDateFormat(self.expiryTime) if self.expiryTime is not None else ''

    def getExpiryDateStr(self):
        if self.expiryTime:
            text = _ms(MENU.BOOSTERSWINDOW_BOOSTERSTABLERENDERER_TIME, tillTime=self.getExpiryDate())
        else:
            text = _ms(MENU.BOOSTERSWINDOW_BOOSTERSTABLERENDERER_UNDEFINETIME)
        return text_styles.standard(text)

    def getBuyPrice(self, preferred=True):
        return self.buyPrices.itemPrice

    def getSellPrice(self, preferred=True):
        return self.sellPrices.itemPrice

    def mayPurchase(self, money):
        if getattr(BigWorld.player(), 'isLongDisconnectedFromCenter', False):
            return (False, GUI_ITEM_ECONOMY_CODE.CENTER_UNAVAILABLE)
        return (False, GUI_ITEM_ECONOMY_CODE.ITEM_IS_HIDDEN) if self.isHidden else self._isEnoughMoney(self.buyPrices, money)

    @classmethod
    def _isEnoughMoney(cls, prices, money):
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

    def __getActiveBoosters(self):
        return [] if not self._stateProvider else self._stateProvider.getActiveBoostersTypes()

    def __buildPrice(self):
        if not self._stateProvider:
            return
        else:
            priceData = self._stateProvider.getBoosterPriceData(self.boosterID)
            buyPrice, defaultPrice, altPrice, defaultAltPrice = priceData
            buyPrice = ItemPrice(price=buyPrice, defPrice=defaultPrice)
            if altPrice is not None:
                altPrice = ItemPrice(price=altPrice, defPrice=defaultAltPrice)
            else:
                altPrice = ITEM_PRICE_EMPTY
            self.__buyPrices = ItemPrices(itemPrice=buyPrice, itemAltPrice=altPrice)
            return


class ClanReservePresenter(BoosterUICommon):
    _CLAN_RESERVE_TO_GUI_TYPE = {FORT_ORDER_TYPE.COMBAT_PAYMENTS: GOODIE_RESOURCE_TYPE.CREDITS,
     FORT_ORDER_TYPE.COMBAT_PAYMENTS_2_0: GOODIE_RESOURCE_TYPE.CREDITS,
     FORT_ORDER_TYPE.TACTICAL_TRAINING: GOODIE_RESOURCE_TYPE.XP,
     FORT_ORDER_TYPE.TACTICAL_TRAINING_2_0: GOODIE_RESOURCE_TYPE.XP,
     FORT_ORDER_TYPE.MILITARY_EXERCISES: GOODIE_RESOURCE_TYPE.FREE_XP,
     FORT_ORDER_TYPE.MILITARY_EXERCISES_2_0: GOODIE_RESOURCE_TYPE.FREE_XP,
     FORT_ORDER_TYPE.ADDITIONAL_BRIEFING: GOODIE_RESOURCE_TYPE.CREW_XP,
     FORT_ORDER_TYPE.ADDITIONAL_BRIEFING_2_0: GOODIE_RESOURCE_TYPE.CREW_XP}

    def __init__(self, reserveID, expirationTime, factors, duration):
        super(ClanReservePresenter, self).__init__(reserveID, None)
        self.__finishTime = expirationTime
        self.__factors = factors
        self.__duration = duration
        return

    @property
    def boosterType(self):
        return self._CLAN_RESERVE_TO_GUI_TYPE[self.boosterID]

    @property
    def finishTime(self):
        return self.__finishTime

    @property
    def effectTime(self):
        return self.__duration

    @property
    def effectValue(self):
        return self.__factors.values()

    def getFormattedValue(self, formatter=None):
        valuesSet = set(self.effectValue)
        if len(valuesSet) == 1:
            strValue = '{}%'.format(first(valuesSet))
        else:
            strValue = '{}%-{}%'.format(min(valuesSet), max(valuesSet))
        return formatter(strValue) if formatter is not None else strValue
