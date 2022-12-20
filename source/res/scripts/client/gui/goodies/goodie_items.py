# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/goodies/goodie_items.py
import time
import weakref
import typing
import BigWorld
import nations
from constants import FORT_ORDER_TYPE
from goodies.goodie_constants import GOODIE_RESOURCE_TYPE, GOODIE_STATE, GOODIE_VARIETY, GOODIE_TARGET_TYPE, BoosterCategory
from goodies.goodie_helpers import GOODIE_TEXT_TO_RESOURCE
from gui import GUI_SETTINGS
from gui.Scaleform.genConsts.STORE_CONSTANTS import STORE_CONSTANTS
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.RES_SHOP_EXT import RES_SHOP_EXT
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.Scaleform.settings import ICONS_SIZES
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.common.personal_reserves.personal_reserves_shared_constants import PREMIUM_BOOSTER_IDS, MAX_ACTIVATED_BY_CATEGORY, UNATTAINABLE_BOOSTER_IDS
from gui.shared.economics import getActionPrc
from gui.shared.formatters import text_styles
from gui.shared.gui_items import GUI_ITEM_ECONOMY_CODE, KPI, GUI_ITEM_TYPE, GUI_ITEM_TYPE_NAMES
from gui.shared.gui_items.gui_item_economics import ItemPrices, ItemPrice, ITEM_PRICE_EMPTY, ITEM_PRICES_EMPTY
from gui.shared.money import Currency, MONEY_UNDEFINED
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import time_utils, dependency
from helpers.i18n import makeString as _ms
from shared_utils import CONST_CONTAINER, first
from skeletons.gui.game_control import IEpicBattleMetaGameController
if typing.TYPE_CHECKING:
    from typing import Any, Callable, Tuple, List, Union
    from gui.shared.money import Money
    from skeletons.gui.goodies import IGoodiesCache
    from gui.game_control.epic_meta_game_ctrl import EpicBattleMetaGameController
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
 GOODIE_RESOURCE_TYPE.FREE_XP: 'booster_free_xp',
 GOODIE_RESOURCE_TYPE.FL_XP: 'booster_fl_xp',
 GOODIE_RESOURCE_TYPE.FREE_XP_CREW_XP: 'booster_free_xp_and_crew_xp',
 GOODIE_RESOURCE_TYPE.FREE_XP_MAIN_XP: 'booster_free_xp_and_crew_xp'}
_BOOSTER_TYPE_TEXT = {v:k for k, v in GOODIE_TEXT_TO_RESOURCE.iteritems()}
BOOSTERS_ORDERS = {GOODIE_RESOURCE_TYPE.FL_XP: 0,
 GOODIE_RESOURCE_TYPE.XP: 1,
 GOODIE_RESOURCE_TYPE.CREW_XP: 2,
 GOODIE_RESOURCE_TYPE.FREE_XP: 3,
 GOODIE_RESOURCE_TYPE.FREE_XP_CREW_XP: 4,
 GOODIE_RESOURCE_TYPE.FREE_XP_MAIN_XP: 5,
 GOODIE_RESOURCE_TYPE.CREDITS: 6,
 GOODIE_RESOURCE_TYPE.GOLD: 7}
GOODIE_TYPE_TO_KPI_NAME_MAP = {GOODIE_RESOURCE_TYPE.XP: KPI.Name.GAME_XP,
 GOODIE_RESOURCE_TYPE.FREE_XP: KPI.Name.GAME_FREE_XP,
 GOODIE_RESOURCE_TYPE.CREW_XP: KPI.Name.GAME_CREW_XP,
 GOODIE_RESOURCE_TYPE.CREDITS: KPI.Name.GAME_CREDITS,
 GOODIE_RESOURCE_TYPE.FL_XP: KPI.Name.GAME_FL_XP}
DEMOUNT_KIT_NAMES = {GOODIE_RESOURCE_TYPE.GOLD: 'common'}
_CLAN_RESERVE_TO_GUI_TYPE = {FORT_ORDER_TYPE.COMBAT_PAYMENTS: GOODIE_RESOURCE_TYPE.CREDITS,
 FORT_ORDER_TYPE.COMBAT_PAYMENTS_2_0: GOODIE_RESOURCE_TYPE.CREDITS,
 FORT_ORDER_TYPE.TACTICAL_TRAINING: GOODIE_RESOURCE_TYPE.XP,
 FORT_ORDER_TYPE.TACTICAL_TRAINING_2_0: GOODIE_RESOURCE_TYPE.XP,
 FORT_ORDER_TYPE.MILITARY_EXERCISES: GOODIE_RESOURCE_TYPE.FREE_XP,
 FORT_ORDER_TYPE.MILITARY_EXERCISES_2_0: GOODIE_RESOURCE_TYPE.FREE_XP,
 FORT_ORDER_TYPE.ADDITIONAL_BRIEFING: GOODIE_RESOURCE_TYPE.CREW_XP,
 FORT_ORDER_TYPE.ADDITIONAL_BRIEFING_2_0: GOODIE_RESOURCE_TYPE.CREW_XP}
_GUI_TYPE_TO_CLAN_RESERVE = {GOODIE_RESOURCE_TYPE.CREDITS: 'COMBAT_PAYMENTS_2_0',
 GOODIE_RESOURCE_TYPE.XP: 'TACTICAL_TRAINING_2_0',
 GOODIE_RESOURCE_TYPE.FREE_XP: 'MILITARY_EXERCISES_2_0',
 GOODIE_RESOURCE_TYPE.CREW_XP: 'ADDITIONAL_BRIEFING_2_0'}

def getBoosterGuiType(boosterType):
    return _BOOSTER_TYPE_NAMES[boosterType]


def getFullNameForBoosterIcon(boosterType, isPremium=False):
    return '{}{}'.format(getBoosterGuiType(boosterType), '_premium' if isPremium else '')


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
    def goodieID(self):
        return self._goodieID

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
        return getBoosterGuiType(self.boosterType)

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
        tooltipIconResId = R.images.gui.maps.icons.quests.bonuses.s180x135.dyn(self.getFullNameForResource())()
        return backport.image(tooltipIconResId)

    @property
    def category(self):
        raise NotImplementedError

    def getIsPremium(self):
        return self.boosterID in PREMIUM_BOOSTER_IDS

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

    def getFullNameForResource(self):
        return getFullNameForBoosterIcon(self.boosterType, self.getIsPremium())

    def getIsAttainable(self):
        return True


class Booster(BoosterUICommon):
    __epicController = dependency.descriptor(IEpicBattleMetaGameController)

    def __init__(self, boosterID, boosterDescription, stateProvider):
        super(Booster, self).__init__(boosterID, boosterDescription, stateProvider)
        self.__buyPrices = ITEM_PRICES_EMPTY
        self.__sellPrices = ITEM_PRICES_EMPTY

    @property
    def isEventBooster(self):
        return self.boosterType == GOODIE_RESOURCE_TYPE.FL_XP

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
    def inCooldown(self):
        return self.state == GOODIE_STATE.ACTIVE

    @property
    def isReadyToActivate(self):
        return self.isReadyToUse or self.isReadyToUpdate

    @property
    def isAvailable(self):
        return self.__readyForEvent()

    @property
    def isReadyToUse(self):
        activeBoosterTypes = self.__getActiveBoosterTypes()
        return self.count > 0 and self.state == GOODIE_STATE.INACTIVE and len(self.__getActiveBoostersByCategory()) < MAX_ACTIVATED_BY_CATEGORY[self.category] and self.boosterType not in activeBoosterTypes and self.__readyForEvent() if self.enabled else False

    @property
    def isReadyToUpdate(self):
        if self.enabled:
            for aBoosterType, aEffectValue, _ in self.__getActiveResources():
                if self.boosterType == aBoosterType and self.count > 0 and self.__readyForEvent():
                    return self.effectValue > aEffectValue

        return False

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

    @property
    def category(self):
        return BoosterCategory.EVENT if self.isEventBooster else BoosterCategory.PERSONAL

    def getTypeAsString(self):
        return _BOOSTER_TYPE_TEXT[self.boosterType]

    def getDescription(self, valueFormatter=None):
        return _ms(MENU.boosterDescriptionLocale(self.boosterGuiType), effectValue=self.getFormattedValue(valueFormatter)) + _ms(MENU.BOOSTER_DESCRIPTION_EFFECTTIME, effectTime=self.getEffectTimeStr(True))

    def getBonusDescription(self, valueFormatter=None):
        return _ms(MENU.boosterBonusLocale(self.boosterGuiType), effectValue=self.getFormattedValue(valueFormatter), effectHours=self.getEffectTimeStr(hoursOnly=True))

    def getShortLeftTimeStr(self):
        return time_utils.getTillTimeString(self.getUsageLeftTime(), MENU.TIME_TIMEVALUESHORT)

    def getQualityIcon(self):
        return RES_ICONS.boosterQualitySourcePath(self.quality)

    def getShopIcon(self, size=STORE_CONSTANTS.ICON_SIZE_MEDIUM):
        return RES_SHOP_EXT.getBoosterIcon(size, self.getFullNameForResource())

    def getExpiryDate(self):
        return backport.getLongDateFormat(self.expiryTime) if self.expiryTime is not None else ''

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

    def getIsAttainable(self):
        return self.boosterID not in UNATTAINABLE_BOOSTER_IDS

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
            return (False, GUI_ITEM_ECONOMY_CODE.getCurrencyError(currency))
        return (False, GUI_ITEM_ECONOMY_CODE.ITEM_NO_PRICE)

    def __getActiveResources(self):
        return [] if not self._stateProvider else self._stateProvider.getActiveResources()

    def __getActiveBoosterTypes(self):
        return [] if not self._stateProvider else self._stateProvider.getActiveBoosterTypes()

    def __getActiveBoostersByCategory(self):
        criteria = REQ_CRITERIA.BOOSTER.ACTIVE | REQ_CRITERIA.BOOSTER.BOOSTER_CATEGORIES([self.category])
        return self._stateProvider.getBoosters(criteria=criteria).values()

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

    def __readyForEvent(self):
        return self.__epicController.isEnabled() and self.__epicController.isInPrimeTime() if self.isEventBooster else True

    def __repr__(self):
        stateStr = 'Inactive'
        if self.state == GOODIE_STATE.ACTIVE:
            stateStr = 'Activated'
        elif self.state == GOODIE_STATE.USED:
            stateStr = 'Used'
        return 'Booster(id={} ({}), state={}, count={})'.format(self.boosterID, self.getTypeAsString(), stateStr, self.count)


class ClanReservePresenter(BoosterUICommon):

    def __init__(self, reserveID, expirationTime, factors, duration):
        super(ClanReservePresenter, self).__init__(reserveID, None)
        self.__finishTime = expirationTime
        self.__factors = factors
        self.__duration = duration
        return

    @property
    def boosterType(self):
        return _CLAN_RESERVE_TO_GUI_TYPE[self.boosterID]

    @property
    def clanReserveType(self):
        return _GUI_TYPE_TO_CLAN_RESERVE[self.boosterType]

    @property
    def finishTime(self):
        return self.__finishTime

    @property
    def effectTime(self):
        return self.__duration

    @property
    def effectValue(self):
        return self.__factors.values()

    @property
    def state(self):
        return GOODIE_STATE.ACTIVE if self.__finishTime > BigWorld.serverTime() else GOODIE_STATE.INACTIVE

    @property
    def inCooldown(self):
        return self.state == GOODIE_STATE.ACTIVE

    @property
    def category(self):
        return BoosterCategory.CLAN

    def getFormattedValue(self, formatter=None):
        valuesSet = set(self.effectValue)
        if len(valuesSet) == 1:
            strValue = '{}%'.format(first(valuesSet))
        else:
            strValue = '{}%-{}%'.format(min(valuesSet), max(valuesSet))
        return formatter(strValue) if formatter is not None else strValue


class DemountKit(_Goodie):

    def __init__(self, goodieID, goodieDescription, stateProvider=None):
        super(DemountKit, self).__init__(goodieID, goodieDescription, stateProvider)
        self.__sellPrices = ITEM_PRICES_EMPTY

    @property
    def userName(self):
        return backport.text(R.strings.demount_kit.userName.dyn(self.demountKitGuiType)())

    @property
    def description(self):
        pass

    def getIcon(self, size):
        return backport.image(R.images.gui.maps.icons.demountKit.dyn('{}_{}'.format(self.demountKitGuiType, size))())

    def getFormattedValue(self, formatter=None):
        pass

    @property
    def icon(self):
        return self.getIcon(STORE_CONSTANTS.ICON_SIZE_SMALL)

    @property
    def bigIcon(self):
        pass

    @property
    def iconInfo(self):
        return self.getIcon(ICONS_SIZES.X48)

    @property
    def itemTypeID(self):
        return GUI_ITEM_TYPE.DEMOUNT_KIT

    @property
    def itemTypeName(self):
        return GUI_ITEM_TYPE_NAMES[self.itemTypeID]

    def getOverlayType(self, vehicle=None):
        pass

    @property
    def nationID(self):
        return nations.NONE_INDEX

    @property
    def isForSale(self):
        return False

    def getSellPrice(self):
        return self.__sellPrices.itemPrice

    @property
    def intCD(self):
        return self._goodieID

    @property
    def shortDescription(self):
        return backport.text(R.strings.demount_kit.storage.description.dyn(self.demountKitGuiType)())

    @property
    def longDescription(self):
        return backport.text(R.strings.demount_kit.dialogue.description.dyn(self.demountKitGuiType)())

    def formattedShortDescription(self, formatter):
        description = self.shortDescription
        return description.format(**formatter)

    @property
    def inventoryCount(self):
        return self.count

    @property
    def demountKitType(self):
        return self._goodieDescription.resource.resourceType

    @property
    def demountKitGuiType(self):
        return DEMOUNT_KIT_NAMES[self.demountKitType]


class RecertificationForm(_Goodie):

    def __init__(self, goodieID, goodieDescription, stateProvider=None):
        super(RecertificationForm, self).__init__(goodieID, goodieDescription, stateProvider)
        self.__sellPrices = ITEM_PRICES_EMPTY

    @property
    def userName(self):
        return backport.text(R.strings.recertification_form.userName())

    @property
    def description(self):
        pass

    def getFormattedValue(self, formatter=None):
        pass

    @property
    def icon(self):
        return backport.image(R.images.gui.maps.shop.artefacts.c_180x135.recertification())

    @property
    def bigIcon(self):
        return backport.image(R.images.gui.maps.icons.recertification.common_80x80())

    @property
    def iconInfo(self):
        return backport.image(R.images.gui.maps.icons.recertification.common_48x48())

    @property
    def itemTypeID(self):
        return GUI_ITEM_TYPE.RECERTIFICATION_FORM

    @property
    def itemTypeName(self):
        return GUI_ITEM_TYPE_NAMES[self.itemTypeID]

    def getOverlayType(self, vehicle=None):
        pass

    @property
    def nationID(self):
        return nations.NONE_INDEX

    @property
    def isForSale(self):
        return False

    def getSellPrice(self):
        return self.__sellPrices.itemPrice

    @property
    def intCD(self):
        return self._goodieID

    @property
    def shortDescription(self):
        return backport.text(R.strings.recertification_form.storage.description())

    @property
    def longDescription(self):
        return backport.text(R.strings.recertification_form.dialogue.description())

    def formattedShortDescription(self, formatter):
        description = self.shortDescription
        return description.format(**formatter)

    @property
    def inventoryCount(self):
        return self.count


BoostersType = typing.TypeVar('BoostersType', bound=BoosterUICommon)
