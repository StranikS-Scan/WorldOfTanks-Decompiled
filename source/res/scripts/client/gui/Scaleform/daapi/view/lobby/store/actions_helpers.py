# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/store/actions_helpers.py
import BigWorld
import operator
import time
import constants
import nations
from gui.Scaleform.locale.QUESTS import QUESTS
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.server_events.event_items import ActionData
from gui.server_events.events_helpers import EventInfoModel
from gui.server_events.formatters import formatStrDiscount, formatPercentValue, formatMultiplierValue, DECORATION_SIZES, formatGoldPrice, formatGoldPriceBig, formatCreditPrice, formatCreditPriceBig, formatVehicleLevel, DISCOUNT_TYPE
from gui.shared.formatters import icons
from gui.server_events import settings as quest_settings
from helpers import i18n, dependency, time_utils
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.shared.gui_items.Vehicle import getTypeBigIconPath, VEHICLE_CLASS_NAME
from gui.shared.money import MONEY_UNDEFINED, Currency, Money
from gui.shared.tooltips.common import CURRENCY_SETTINGS, _getCurrencySetting
from gui.Scaleform.genConsts.SLOT_HIGHLIGHT_TYPES import SLOT_HIGHLIGHT_TYPES
from gui.shared.tooltips import formatters, contexts
from gui.shared.formatters import text_styles
from helpers.i18n import makeString as _ms
from gui.shared.items_parameters import formatters as param_formatter, params_helper
_DT = DISCOUNT_TYPE
_VEHICLE_NATION_ICON_PATH = '../maps/icons/filters/nations/%s.png'
_MAX_ITEMS_IN_TABLE = 3
_PRIORITY_FOR_FUTURE_ACTION = 4
_MULTIPLIER = 'Multiplier'
_PREMIUM_PACKET = 'premiumPacket'
_gold_bonus_list = ('slotsPrices',
 'berthsPrices',
 'premiumPacket1Cost',
 'premiumPacket3Cost',
 'premiumPacket7Cost',
 'premiumPacket14Cost',
 'premiumPacket30Cost',
 'premiumPacket90Cost',
 'premiumPacket180Cost',
 'premiumPacket360Cost')

class ActionInfo(EventInfoModel):
    """Data model for action card on action store view
    """

    def __init__(self, event, actionData):
        super(ActionInfo, self).__init__(event)
        self.discount = actionData.discountObj
        self.priority = actionData.priority
        self.uiDecoration = actionData.uiDecoration
        self._compositionType = None
        self._id = ''
        self._maxDiscount = None
        self._packedDiscounts = None
        return

    @property
    def visualPriority(self):
        """Visual priority for view
        :return: int (1 - hero, 2 - normal, 3 - small)
        """
        return self.priority

    @visualPriority.setter
    def visualPriority(self, value):
        """Visual priority for view
        """
        self.priority = value

    def getID(self):
        """Unique id for action card
        """
        if not self._id:
            self._id = '{}/{}/{}'.format(self.event.getID(), self.discount.getName(), self.discount.getParamName())
        return self._id

    def isAvailable(self):
        """Dump method, used for self.getIsNew()
        """
        return (True, None)

    def isCompleted(self):
        """Dump method, used for self.getIsNew()
        """
        return False

    def isOutOfDate(self):
        """Dump method, used for self.getIsNew()
        """
        return False

    def getStartTime(self):
        """Return action start time
        """
        return self.event.getStartTime()

    def getFinishTime(self):
        """Return action finish time
        """
        return self.event.getFinishTime()

    def getTitle(self):
        """Return card title
        """
        return self.event.getUserName()

    def getIsNew(self):
        """Is card viewed before
        """
        return quest_settings.isNewCommonEvent(self)

    def getAutoDescription(self, useBigIco=False):
        """Automatic description for all cards
        :param useBigIco: use big or small currency icons
        :return: i18n formatted text
        """
        discountValue = self._getAutoDescriptionData(useBigIco)
        return self._getShortDescription(self.discount.getParamName(), discount=discountValue)

    def getAdditionalDescription(self, useBigIco=False, forHeroCard=False):
        """Additional description, automatically showed for hero card
        on hover show for normal cards
        """
        discount = self._getAdditionalDescriptionData(useBigIco)
        return self._getFullDescription(self.discount.getParamName(), discount, forHeroCard=forHeroCard)

    def getComingSoonDescription(self):
        pass

    def getTooltipInfo(self):
        """Get str for card tooltip
        """
        return self.event.getDescription()

    def isDiscountVisible(self):
        discount = self._getMaxDiscount()
        if discount:
            if discount.discountType == _DT.MULTIPLIER:
                return not (discount.discountValue == 0 or discount.discountValue == 1)
            return discount.discountValue > 0
        return False

    def getDiscount(self):
        """Returns string with discount or empty string if can't calculate
        Is used on red label on action cards
        """
        discount = self._getMaxDiscount()
        return formatStrDiscount(discount) if discount else ''

    def getBattleQuestsInfo(self):
        """Get linked quests and format button text
        """
        linkedQuests = self.event.linkedQuests
        return i18n.makeString(QUESTS.ACTION_LABEL_BATTLEQUESTS, count=len(linkedQuests)) if linkedQuests else ''

    def getLinkBtnLabel(self):
        """Formatted web link text
        """
        pass

    def getActionBtnLabel(self):
        """Get formatted button text
        """
        return self._getButtonName(self.discount.getParamName())

    def getPicture(self):
        """Get img for action
        """
        picture = getDecoration(self.uiDecoration)
        if picture:
            return {'isWeb': True,
             'src': picture}
        paramName = self.discount.getParamName()
        if paramName.endswith(_MULTIPLIER):
            paramName = paramName[:-len(_MULTIPLIER)]
        return {'isWeb': False,
         'src': _PARAM_TO_IMG_DICT.get(paramName, '')}

    def getTriggerChainID(self):
        """Gets chapter ID to run tutorial system for sales
        :return: str
        """
        raise NotImplementedError

    def getTableData(self):
        """If card contains tabled data, format and return data
        """
        return []

    def getActionTime(self):
        return {'id': self.getID(),
         'isTimeOver': not self.event.isAvailable()[0],
         'timeLeft': self._getActiveTimeDateText(),
         'isShowTimeIco': self._showTimerIco()}

    def setComposition(self, compositionType):
        self._compositionType = compositionType

    def getMaxDiscountValue(self):
        """
        Always returns int, if maxDiscount is None, 0 is returned
        """
        maxDiscount = self._getMaxDiscount()
        return maxDiscount.discountValue if maxDiscount is not None else 0

    def getExtraData(self):
        return None

    def _showTimerIco(self):
        """Show timer icon when action comes to end
        :return:
        """
        return self.event.getFinishTimeLeft() <= time_utils.ONE_DAY

    def _getActiveTimeDateText(self):
        """
        Gets formatted mission's active time
        """
        timeStr = self._getActiveDateTimeString()
        return text_styles.stats(timeStr)

    def _getAutoDescription(self, stepName):
        """Card description text
        Used only for coming soon cards
        :param stepName: step name
        :return: i18n description string
        """
        formatter = 'auto/{}'.format(self.__modifyName(stepName))
        return i18n.makeString(QUESTS.getActionDescription(formatter))

    def _getFullDescription(self, stepName, discount=None, forHeroCard=False):
        modifiedStepName = self.__modifyName(stepName)
        locKey = None
        if forHeroCard:
            locKey = QUESTS.getActionDescription('hero/full/{}'.format(modifiedStepName))
        if locKey is None:
            locKey = QUESTS.getActionDescription('full/{}'.format(modifiedStepName))
        return i18n.makeString(locKey, discount=discount)

    def _getShortDescription(self, stepName, **kwargs):
        """Card description text
        Used for small cards
        :param stepName: step name
        :param kwargs: dict params for text
        :return: i18n description string
        """
        formatter = 'short/{}'.format(self.__modifyName(stepName))
        return i18n.makeString(QUESTS.getActionDescription(formatter), **kwargs)

    @classmethod
    def _getButtonName(cls, stepName):
        """Button text
        :param stepName: step name
        :return: i18n button text
        """
        formatter = 'button/{}'.format(stepName)
        return i18n.makeString(QUESTS.getActionDescription(formatter))

    @classmethod
    def _formatPriceIcon(cls, item, useBigIco):
        """Convert price to text with currency icon
        :param item: vehicle, camuflage, etc...
        :param useBigIco: show small or big icon format
        :return: formatted price
        """
        if hasattr(item, 'buyPrices'):
            sellGold = item.buyPrices.itemPrice.price.gold
            sellCredits = item.buyPrices.itemPrice.price.credits
            if sellGold:
                if useBigIco:
                    return formatGoldPriceBig(sellGold)
                return formatGoldPrice(sellGold)
            if sellCredits:
                if useBigIco:
                    return formatCreditPriceBig(sellCredits)
                return formatCreditPrice(sellCredits)

    @classmethod
    def _formatRentPriceIcon(cls, item, useBigIco):
        """Convert price to text with currency icon
        :param item: vehicle, camuflage, etc...
        :param useBigIco: show small or big icon format
        :return: formatted price
        """
        if hasattr(item, 'minRentPrice'):
            rentPrice = item.minRentPrice.toDict()
            if rentPrice[Currency.GOLD]:
                if useBigIco:
                    return formatGoldPriceBig(rentPrice[Currency.GOLD])
                return formatGoldPrice(rentPrice[Currency.GOLD])
            if rentPrice[Currency.CREDITS]:
                if useBigIco:
                    return formatCreditPriceBig(rentPrice[Currency.CREDITS])
                return formatCreditPrice(rentPrice[Currency.CREDITS])

    def _getPackedDiscounts(self, sorting=False):
        """Gather info about all discounts for card
        :param sorting: if value equals True than list should be sorted,
            otherwise - do not sort list of discounts. For example, if user finds
            max discount, sorting is pointless.
        :return: list of discounts
        """
        if not self._packedDiscounts:
            self._packedDiscounts = self.discount.packDiscounts(sorting=sorting)
        return self._packedDiscounts

    def _getMaxDiscount(self):
        """Get best discount value for action
        :return: discount with max value
        """
        if not self._maxDiscount:
            discounts = self._getPackedDiscounts(sorting=False)
            if discounts:
                self._maxDiscount = max(discounts.values(), key=operator.itemgetter(1))
        return self._maxDiscount

    def _getAutoDescriptionData(self, useBigIco=False):
        """format string with auto description about action
        :param useBigIco: big/small icon in text
        :return: i18n string
        """
        return self._getAdditionalDescriptionData(useBigIco)

    def _getAdditionalDescriptionData(self, useBigIco=False):
        """format string with short description about action
        :param useBigIco: big/small icon in text
        :return: i18n string
        """
        discount = self._getMaxDiscount()
        return formatPercentValue(discount.discountValue) if discount else None

    def _formatFinishTime(self):
        """Format string with finish time for action
        """
        return '{} {}'.format(text_styles.main(i18n.makeString(QUESTS.ACTION_TIME_FINISH)), BigWorld.wg_getShortDateFormat(self.getFinishTime()))

    def _getActiveDateTimeString(self):
        """Format time in 'hh mm' format
        """
        if self.event.getFinishTimeLeft() <= time_utils.ONE_DAY:
            gmtime = time.gmtime(self.event.getFinishTimeLeft())
            if gmtime.tm_hour > 0:
                fmt = i18n.makeString(QUESTS.ITEM_TIMER_TILLFINISH_LONGFORMAT)
            else:
                fmt = i18n.makeString(QUESTS.ITEM_TIMER_TILLFINISH_SHORTFORMAT)
            fmt %= {'hours': time.strftime('%H', gmtime),
             'min': time.strftime('%M', gmtime)}
            return '{} {}'.format(text_styles.main(i18n.makeString(QUESTS.ACTION_TIME_LEFT)), fmt)
        return self._formatFinishTime()

    def __modifyName(self, stepName):
        return self._compositionType or stepName


class EconomicsActionsInfo(ActionInfo):
    """Economics actions
    """

    def getTriggerChainID(self):
        """Gets chapter ID to run tutorial system for sales
        :return: str
        """
        return 'winXPFactorMode' if 'winXPFactorMode' in self.discount.getParamName() else self.discount.getParamName()

    def getDiscount(self):
        paramName = self.discount.getParamName()
        if 'winXPFactorMode' in paramName:
            discount = self.__handleWinXPFactorMode()
        else:
            discounts = self._getPackedDiscounts()
            discount = discounts.get(paramName) if discounts else None
        return formatStrDiscount(discount) if discount else ''

    def getActionBtnLabel(self):
        """Get formatted button text
        """
        discountParamName = self.discount.getParamName()
        if discountParamName in ('clanCreationCost',):
            return ''
        if _PREMIUM_PACKET in discountParamName:
            isPremium = getEconomicalStatsDict().get('isPremium', False)
            if isPremium:
                return self._getButtonName('{}/continue'.format(_PREMIUM_PACKET))
            return self._getButtonName('{}/new'.format(_PREMIUM_PACKET))
        return super(EconomicsActionsInfo, self).getActionBtnLabel()

    def getLinkBtnLabel(self):
        """Formatted web link text
        """
        return self._getButtonName(self.discount.getParamName()) if self.discount.getParamName() == 'clanCreationCost' else ''

    def _getAutoDescriptionData(self, useBigIco=False):
        """format string with auto description about action
        :param useBigIco: big/small icon in text
        :return: i18n string
        """
        paramName = self.discount.getParamName()
        if 'exchangeRate' in paramName:
            discountValue = self.__getExchangeRateBonusIco(useBigIco)
        elif paramName in ('freeXPConversionDiscrecity', 'freeXPToTManXPRate'):
            discount = self._getMaxDiscount()
            discountValue = formatMultiplierValue(discount.discountValue)
        else:
            discountValue = self._getAdditionalDescriptionData(useBigIco)
        return discountValue

    def _getAdditionalDescriptionData(self, useBigIco=False):
        """format string with short description about action
        :param useBigIco: big/small icon in text
        :return: i18n string
        """
        paramName = self.discount.getParamName()
        if paramName.endswith(_MULTIPLIER):
            paramName = paramName[:-len(_MULTIPLIER)]
        if 'winXPFactorMode' in paramName:
            discountValue = getEconomicalStatsDict().get('dailyXPFactor', None)
        elif 'exchangeRate' in paramName:
            discountValue = self.__getExchangeRateBonusIco()
        else:
            discountValue = getEconomicalStatsDict().get(paramName, None)
        if paramName in _gold_bonus_list:
            if useBigIco:
                discountValue = formatGoldPriceBig(discountValue)
            else:
                discountValue = formatGoldPrice(discountValue)
        if not discountValue:
            discount = self._getMaxDiscount()
            discountValue = formatPercentValue(discount.discountValue) if discount else None
        return discountValue

    def isDiscountVisible(self):
        paramName = self.discount.getParamName()
        if 'winXPFactorMode' in paramName:
            discount = self.__handleWinXPFactorMode()
        else:
            discount = self._getMaxDiscount()
        if discount:
            if discount.discountType == _DT.MULTIPLIER:
                return not (discount.discountValue == 0 or discount.discountValue == 1)
            return discount.discountValue > 0
        return False

    def __handleWinXPFactorMode(self):
        return self.discount.handlerWinXPFactorMode()

    def __getExchangeRateBonusIco(self, useBigIco=False):
        credits = getEconomicalStatsDict().get('exchangeRate')
        if useBigIco:
            goldIcon = formatGoldPriceBig(1)
            creditsIcon = formatCreditPriceBig(credits)
        else:
            goldIcon = formatGoldPrice(1)
            creditsIcon = formatCreditPrice(credits)
        return i18n.makeString(QUESTS.ACTION_EXCHANGERATE_GOLD2CREDIT, gold=goldIcon, credits=creditsIcon)


class VehPriceActionInfo(ActionInfo):
    _DEFAULT_MARGIN_AFTER_BLOCK = 10
    _DEFAULT_MARGIN_AFTER_SEPARATOR = 17

    def getTriggerChainID(self):
        """Gets chapter ID to run tutorial system for sales
        :return: str
        """
        pass

    def getAutoDescription(self, useBigIco=False):
        """Return card description
        :param useBigIco: use big or small currency icon
        :return: formatted text
        """
        vehs = self._getAdditionalDescriptionData(useBigIco)
        vehsLen = len(vehs)
        if vehsLen > 1:
            paramKey = 'two' if vehsLen == 2 else 'more'
            paramName = '{}/{}'.format(self.discount.getParamName(), paramKey)
            values = {'vehicles': '{}, {}'.format(vehs[0]['title'], vehs[1]['title']),
             'discount': formatPercentValue(vehs[0]['discount'])}
            return self._getShortDescription(paramName, **values)

    def getAdditionalDescription(self, useBigIco=False, forHeroCard=False):
        """Format table description
        :return: formatted text
        """
        vehiclesCount = len(self._getPackedDiscounts())
        return i18n.makeString(QUESTS.ACTION_DISCOUNT_MORE, deviceName=i18n.makeString(QUESTS.ACTION_MORE_TYPE_VEHICLES), count=vehiclesCount - _MAX_ITEMS_IN_TABLE) if vehiclesCount > _MAX_ITEMS_IN_TABLE else ''

    def getTableData(self):
        """If card contains tabled data, format and return data
        """
        result = []
        for item in self._sortVehicles():
            veh = item.discountName
            if veh.isPremium or veh.isElite:
                iconFunc = RES_ICONS.maps_icons_vehicletypes_elite
            else:
                iconFunc = RES_ICONS.maps_icons_vehicletypes
            item = {'icon': _VEHICLE_NATION_ICON_PATH % nations.NAMES[veh.nationID],
             'additionalIcon': iconFunc(veh.type + '.png'),
             'title': '{} {}'.format(i18n.makeString(TOOLTIPS.level(veh.level)), veh.shortUserName),
             'discount': formatStrDiscount(item),
             'price': self._getPrice(veh, False)}
            result.append(item)

        return result

    def getExtraData(self):
        items = self._getAdditionalDescriptionData(useBigIco=True, addVehInfo=True)
        return self.__getCardWithTTCForVehicle(items[0]) if len(items) == 1 else None

    def _getAdditionalDescriptionData(self, useBigIco=False, addVehInfo=False):
        """format string with short description about action
        :param useBigIco: big/small icon in text
        :return: i18n string
        """
        result = []
        for item in self._sortVehicles():
            veh = item.discountName
            level = formatVehicleLevel(i18n.makeString(TOOLTIPS.level(veh.level)))
            item = {'title': '{} {}'.format(level, veh.shortUserName),
             'discount': item.discountValue,
             'price': self._getPrice(veh, useBigIco)}
            if addVehInfo:
                item.update({'veh': veh})
            result.append(item)

        return result

    def _getPrice(self, veh, useBigIco):
        return self._formatPriceIcon(veh, useBigIco)

    def _sortVehicles(self):

        def __sortByNameFunc(item):
            return item.discountName.shortUserName

        def __sortByVehicleParams(item):
            veh = item.discountName
            dscnt = item.discountValue
            return (dscnt, (veh.buyPrices.itemPrice.price.gold, veh.buyPrices.itemPrice.price.credits), veh.level)

        discountItems = self._getPackedDiscounts()
        return sorted(sorted(discountItems.values(), key=__sortByNameFunc), key=__sortByVehicleParams, reverse=True)[:3]

    def __getCardWithTTCForVehicle(self, vehItemDict):
        result = {}
        items = []
        context = contexts.ToolTipContext(None)
        statsConfig = context.getStatsConfiguration(vehItemDict['veh'])
        leftPadding = 20
        rightPadding = 20
        blockTopPadding = -4
        leftRightPadding = formatters.packPadding(left=leftPadding, right=rightPadding)
        blockPadding = formatters.packPadding(left=leftPadding, right=rightPadding, top=blockTopPadding)
        valueWidth = 75
        textGap = -2
        items.append(formatters.packBuildUpBlockData(self.__getHeaderBlock(vehItemDict), padding=leftRightPadding))
        items.append(formatters.packBuildUpBlockData(self._getPriceBlock(vehItemDict['veh'], statsConfig, valueWidth), gap=textGap, padding=blockPadding))
        items.append(formatters.packBuildUpBlockData(self.__getCommonStatsBlock(vehItemDict['veh']), gap=textGap, padding=blockPadding))
        result.update({'blocksData': items,
         'marginAfterBlock': self._DEFAULT_MARGIN_AFTER_BLOCK,
         'marginAfterSeparator': self._DEFAULT_MARGIN_AFTER_SEPARATOR,
         'width': 600,
         'highlightType': SLOT_HIGHLIGHT_TYPES.NO_HIGHLIGHT})
        return result

    def __getHeaderBlock(self, vehItemDict):
        block = []
        icon = getTypeBigIconPath(vehItemDict['veh'].type, vehItemDict['veh'].isElite)
        paramName = '{}/{}'.format(self.discount.getParamName(), 'one')
        values = {'vehicles': vehItemDict['title'],
         'discount': vehItemDict['price']}
        titleDescr = text_styles.superPromoTitle(self._getShortDescription(paramName, **values))
        block.append(formatters.packImageTextBlockData(title=titleDescr, img=icon, imgPadding=formatters.packPadding(left=10, top=-15), txtGap=-6, txtOffset=84, padding=formatters.packPadding(top=15, bottom=-17)))
        return block

    def __getCommonStatsBlock(self, vehicle):
        PARAMS = {VEHICLE_CLASS_NAME.LIGHT_TANK: ('enginePowerPerTon', 'speedLimits', 'chassisRotationSpeed', 'circularVisionRadius'),
         VEHICLE_CLASS_NAME.MEDIUM_TANK: ('avgDamagePerMinute', 'enginePowerPerTon', 'speedLimits', 'chassisRotationSpeed'),
         VEHICLE_CLASS_NAME.HEAVY_TANK: ('avgDamage', 'avgPiercingPower', 'hullArmor', 'turretArmor'),
         VEHICLE_CLASS_NAME.SPG: ('avgDamage', 'stunMinDuration', 'stunMaxDuration', 'reloadTimeSecs', 'aimingTime', 'explosionRadius'),
         VEHICLE_CLASS_NAME.AT_SPG: ('avgPiercingPower', 'shotDispersionAngle', 'avgDamagePerMinute', 'speedLimits', 'chassisRotationSpeed', 'switchOnTime', 'switchOffTime'),
         'default': ('speedLimits', 'enginePower', 'chassisRotationSpeed')}
        block = []
        paramsDict = params_helper.getParameters(vehicle)
        comparator = params_helper.idealCrewComparator(vehicle)
        for paramName in PARAMS.get(vehicle.type, 'default'):
            if paramName in paramsDict:
                paramInfo = comparator.getExtendedData(paramName)
                fmtValue = param_formatter.colorizedFormatParameter(paramInfo, param_formatter.BASE_SCHEME)
                if fmtValue is not None:
                    block.append(formatters.packTextParameterBlockData(name=param_formatter.formatVehicleParamName(paramName), value=fmtValue, valueWidth=80, padding=formatters.packPadding(left=-1)))

        return block

    def _getPriceBlock(self, vehicle, configuration, valueWidth):
        block = []
        buyPrice = configuration.buyPrice
        if buyPrice:
            itemPrice = vehicle.buyPrices.itemPrice
            price = itemPrice.price
            actionPrc = itemPrice.getActionPrc()
            defaultPrice = itemPrice.defPrice
            currency = price.getCurrency()
            buyPriceValue = price.get(currency)
            oldPriceValue = defaultPrice.get(currency)
            block.append(self.__makePriceBlock(oldPriceValue, CURRENCY_SETTINGS.getBuySetting(currency), valueWidth=valueWidth))
            block.append(self.__makePriceBlock(buyPriceValue, CURRENCY_SETTINGS.getBuySetting(currency), percent=actionPrc, valueWidth=valueWidth))
        return [formatters.packBuildUpBlockData(block, gap=2, padding=formatters.packPadding(top=-2))]

    def __makePriceBlock(self, price, currencySetting, percent=0, valueWidth=-1):
        _int = BigWorld.wg_getIntegralFormat
        hasAction = percent != 0
        settings = _getCurrencySetting(currencySetting)
        if settings is None:
            return
        else:
            valueFormatted = settings.textStyle(_int(price))
            if hasAction:
                settingsFrame = settings.frame
                if settingsFrame in Currency.ALL:
                    newPrice = MONEY_UNDEFINED.replace(settingsFrame, price)
                else:
                    newPrice = Money(credits=price)
                return formatters.packActionTextParameterBlockData(name=text_styles.main(_ms(TOOLTIPS.ACTIONPRICE_BUYPRICE_ACTIONPRICE, value=text_styles.expText(percent))), value=valueFormatted, icon=_getCurrencySetting(currencySetting).frame, padding=formatters.packPadding(left=20, bottom=-20), currency=newPrice.getCurrency())
            return formatters.packTextParameterWithIconBlockData(name=text_styles.main(_ms(TOOLTIPS.ACTIONPRICE_BUYPRICE_DEFAULTPRICE)), value=valueFormatted, icon=settings.frame, valueWidth=valueWidth)
            return


class VehRentActionInfo(VehPriceActionInfo):

    def getTriggerChainID(self):
        """Gets chapter ID to run tutorial system for sales
        :return: str
        """
        pass

    def getAdditionalDescription(self, useBigIco=False, forHeroCard=False):
        """Format table description
        :return: formatted text
        """
        return self._getFullDescription(self.discount.getParamName(), forHeroCard=forHeroCard)

    def getTableData(self):
        """If card contains tabled data, format and return data
        """
        return None

    def _getPrice(self, veh, useBigIco):
        return self._formatRentPriceIcon(veh, useBigIco)

    def _calcDiscountValue(self, value, default):
        discount = float(value) / default * 100
        return int(discount)

    def _getPriceBlock(self, vehicle, configuration, valueWidth):
        block = []
        if vehicle.isRentAvailable and vehicle.isRentable:
            buyPrice = vehicle.buyPrices
            rentPackages = vehicle.rentPackages
            if buyPrice and rentPackages:
                itemPrice = vehicle.buyPrices.itemPrice
                price = itemPrice.price
                currency = price.getCurrency()
                buyPriceValue = price.get(currency)
                block.append(self.__makePriceBlock(buyPriceValue, CURRENCY_SETTINGS.getBuySetting(currency), valueWidth=valueWidth))
                for rent in rentPackages:
                    defaultPrice = rent.get('defaultRentPrice')
                    defaultPriceValue = defaultPrice.get(defaultPrice.getCurrency())
                    days = rent.get('days')
                    rentPrice = rent.get('rentPrice')
                    currency = rentPrice.getCurrency()
                    rentPriceValue = rentPrice.get(currency)
                    block.append(self.__makeRentBlock(rentPriceValue, CURRENCY_SETTINGS.getBuySetting(currency), days, percent=self._calcDiscountValue(rentPriceValue, defaultPriceValue)))

        return [formatters.packBuildUpBlockData(block, gap=2, padding=formatters.packPadding(top=-2))]

    def _sortVehicles(self):

        def __sortByNameFunc(item):
            return item.discountName.shortUserName

        def __sortByVehicleParams(item):
            veh = item.discountName
            dscnt = item.discountValue
            return (dscnt, (veh.minRentPrice.gold, veh.minRentPrice.credits), veh.level)

        res = {}
        for (intCD, rentDays), vehicle in self._getPackedDiscounts().items():
            res[intCD] = vehicle

        return sorted(sorted(res.values(), key=__sortByNameFunc), key=__sortByVehicleParams, reverse=True)[:3]

    def __makeRentBlock(self, price, currencySetting, days, percent=0):
        _int = BigWorld.wg_getIntegralFormat
        settings = _getCurrencySetting(currencySetting)
        if settings is None:
            return
        else:
            valueFormatted = settings.textStyle(_int(price))
            settingsFrame = settings.frame
            if settingsFrame in Currency.ALL:
                newPrice = MONEY_UNDEFINED.replace(settingsFrame, price)
            else:
                newPrice = Money(credits=price)
            if days == 1:
                text = text_styles.main(_ms(TOOLTIPS.ACTIONPRICE_RENTPRICE_1DAY, value=text_styles.expText(percent)))
            elif days == 3:
                text = text_styles.main(_ms(TOOLTIPS.ACTIONPRICE_RENTPRICE_3DAY, value=text_styles.expText(percent)))
            else:
                text = text_styles.main(_ms(TOOLTIPS.ACTIONPRICE_RENTPRICE_DAYS, days=days, value=text_styles.expText(percent)))
            return formatters.packActionTextParameterBlockData(name=text, value=valueFormatted, icon=_getCurrencySetting(currencySetting).frame, padding=formatters.packPadding(left=20, bottom=-20), currency=newPrice.getCurrency())

    def __makePriceBlock(self, price, currencySetting, percent=0, valueWidth=-1):
        _int = BigWorld.wg_getIntegralFormat
        settings = _getCurrencySetting(currencySetting)
        if settings is None:
            return
        else:
            valueFormatted = settings.textStyle(_int(price))
            return formatters.packTextParameterWithIconBlockData(name=text_styles.main(_ms(TOOLTIPS.ACTIONPRICE_RENTPRICE_DEFAULTPRICE)), value=valueFormatted, icon=settings.frame, valueWidth=valueWidth)


class EquipmentActionInfo(ActionInfo):

    def getTriggerChainID(self):
        """Gets chapter ID to run tutorial system for sales
        :return: str
        """
        pass

    def getAdditionalDescription(self, useBigIco=False, forHeroCard=False):
        """Format table description
        """
        equipCount = len(self._getPackedDiscounts())
        return i18n.makeString(QUESTS.ACTION_DISCOUNT_MORE, deviceName=i18n.makeString(QUESTS.ACTION_MORE_TYPE_EQUIPMENT), count=equipCount - _MAX_ITEMS_IN_TABLE) if equipCount > _MAX_ITEMS_IN_TABLE else ''

    def getTableData(self):
        """If card contains tabled data, format and return data
        """
        items = self._getPackedDiscounts()
        res = []
        for intCD, data in items.iteritems():
            equip = data.discountName
            item = {'icon': '',
             'additionalIcon': '',
             'title': '{} {}'.format(icons.makeImageTag(equip.icon, vSpace=-3), equip.userName),
             'discount': formatStrDiscount(data),
             'price': self._formatPriceIcon(equip, False)}
            res.append(item)

        return res[:3]


class OptDeviceActionInfo(ActionInfo):

    def getTriggerChainID(self):
        """Gets chapter ID to run tutorial system for sales
        :return: str
        """
        pass

    def getAdditionalDescription(self, useBigIco=False, forHeroCard=False):
        """Format table description
        :return: formatted text
        """
        optDeviceCount = len(self._getPackedDiscounts())
        return i18n.makeString(QUESTS.ACTION_DISCOUNT_MORE, deviceName=i18n.makeString(QUESTS.ACTION_MORE_TYPE_OPTIONALDEVICES), count=optDeviceCount - _MAX_ITEMS_IN_TABLE) if optDeviceCount > _MAX_ITEMS_IN_TABLE else ''

    def getTableData(self):
        """If card contains tabled data, format and return data
        """
        items = self._getPackedDiscounts()
        res = []
        for intCD, data in items.iteritems():
            optDevice = data.discountName
            item = {'icon': '',
             'additionalIcon': '',
             'title': '{} {}'.format(icons.makeImageTag(optDevice.icon, vSpace=-3), optDevice.userName),
             'discount': formatStrDiscount(data),
             'price': self._formatPriceIcon(optDevice, False)}
            res.append(item)

        return sorted(res, key=lambda x: x['discount'], reverse=True)[:3]


class ShellPriceActionInfo(ActionInfo):

    def getTriggerChainID(self):
        """Gets chapter ID to run tutorial system for sales
        :return: str
        """
        pass


class BoosterPriceActionInfo(ActionInfo):

    def getTriggerChainID(self):
        """Gets chapter ID to run tutorial system for sales
        :return: str
        """
        pass

    def getAdditionalDescription(self, useBigIco=False, forHeroCard=False):
        """Format table description
        """
        boostersCount = len(self._getPackedDiscounts())
        return i18n.makeString(QUESTS.ACTION_DISCOUNT_MORE, deviceName=i18n.makeString(QUESTS.ACTION_MORE_TYPE_GOODIES), count=boostersCount - _MAX_ITEMS_IN_TABLE) if boostersCount > _MAX_ITEMS_IN_TABLE else ''

    def getTableData(self):
        """If card contains tabled data, format and return data
        """
        res = []
        for data in self.__sortBoosters():
            booster = data.discountName
            guiType = booster.boosterGuiType
            formatter = 'booster/{}'.format(guiType)
            busterName = i18n.makeString(QUESTS.getActionDescription(formatter))
            busterSmallIcon = RES_ICONS.getBusterSmallIcon(guiType)
            item = {'icon': busterSmallIcon,
             'additionalIcon': '',
             'title': busterName,
             'discount': formatStrDiscount(data),
             'price': self._formatPriceIcon(booster, False)}
            res.append(item)

        return res

    def __sortBoosters(self):

        def __sortByNameFunc(item):
            return item.discountName.userName

        def __sortByParams(item):
            booster = item.discountName
            maxValues = booster.buyPrices.getMaxValuesAsMoney()
            discount = item.discountValue
            return (discount, tuple(maxValues.iterallitems(byWeight=True)))

        discountItems = self._getPackedDiscounts()
        return sorted(sorted(discountItems.values(), key=__sortByNameFunc), key=__sortByParams, reverse=True)[:3]


class C11nPriceGroupPriceActionInfo(ActionInfo):
    """Action info for customization items
    """

    def getTriggerChainID(self):
        """Gets chapter ID to run tutorial system for sales
        :return: str
        """
        pass

    def getAdditionalDescription(self, useBigIco=False, forHeroCard=False):
        """Format table description
        """
        itemsCount = len(self._getPackedDiscounts())
        return i18n.makeString(QUESTS.ACTION_DISCOUNT_MORE, deviceName=i18n.makeString(QUESTS.ACTION_MORE_TYPE_CUSTOMIZATIONS), count=itemsCount - _MAX_ITEMS_IN_TABLE) if itemsCount > _MAX_ITEMS_IN_TABLE else ''

    def getTableData(self):
        """If card contains tabled data, format and return data
        """
        items = self._getPackedDiscounts()
        res = []
        for intCD, data in items.iteritems():
            c11n = data.discountName
            item = {'icon': '',
             'additionalIcon': '',
             'title': '{} {}'.format(c11n.userType, c11n.userName),
             'discount': formatStrDiscount(data),
             'price': self._formatPriceIcon(c11n, False)}
            res.append(item)

        return sorted(res, key=lambda x: x['discount'], reverse=True)[:3]


class ComingSoonActionInfo(ActionInfo):
    """Future actions with limited fields to show
    """

    def __init__(self, info):
        self.__name = info['name']
        self.__startTime = info['startTime']
        self.__announceTime = info['announceTime']
        self.__params = info['params']
        super(ComingSoonActionInfo, self).__init__(object, ActionData(object, _PRIORITY_FOR_FUTURE_ACTION, 0))

    def getID(self):
        return '{}/{}/{}'.format(self.__announceTime, self.__startTime, self._getParamName())

    def getStartTime(self):
        return self.__startTime

    def getFinishTime(self):
        pass

    def getActionTime(self):
        return {'id': self.getID(),
         'isTimeOver': False,
         'timeLeft': self._getStartTime(),
         'isShowTimeIco': False}

    def getTriggerChainID(self):
        pass

    def getPicture(self):
        picture = getDecoration(self.uiDecoration)
        return {'isWeb': True,
         'src': picture} if picture else {'isWeb': False,
         'src': _PARAM_TO_IMG_DICT.get(self._getParamName(), '')}

    def getTitle(self):
        return i18n.makeString(QUESTS.ACTION_COMINGSOON_LABEL)

    def getIsNew(self):
        return False

    def getAutoDescription(self, useBigIco=False):
        pass

    def getAdditionalDescription(self, useBigIco=False, forHeroCard=False):
        pass

    def getComingSoonDescription(self):
        return self._getAutoDescription(self._getParamName())

    def getTooltipInfo(self):
        pass

    def getDiscount(self):
        pass

    def getBattleQuestsInfo(self):
        pass

    def getLinkBtnLabel(self):
        pass

    def getActionBtnLabel(self):
        pass

    def _getStartTime(self):
        startTimeStr = BigWorld.wg_getShortDateFormat(self.__startTime)
        return text_styles.main(i18n.makeString(QUESTS.ACTION_COMINGSOON_TIME, startTime=startTimeStr)) if startTimeStr is not None else ''

    def _getParamName(self):
        """Get step name for images, texts...
        :return: str
        """
        paramName = self.__name
        if 'Economics' in paramName or 'set_TradeInParams' in paramName:
            paramName = self.__params[0] if self.__params else ''
        if paramName.endswith(_MULTIPLIER):
            paramName = paramName[:-len(_MULTIPLIER)]
        return paramName


class CalendarActionInfo(ActionInfo):

    def isDiscountVisible(self):
        return True

    def getTitle(self):
        return i18n.makeString(QUESTS.ACTION_SHORT_CALENDAR)

    def getTriggerChainID(self):
        pass


class NyBoxBuyingActionInfo(ActionInfo):

    def isDiscountVisible(self):
        return True

    def getTitle(self):
        return i18n.makeString(QUESTS.ACTION_SHORT_BOXBUYING)

    def getTriggerChainID(self):
        pass


def getEconomicalStatsDict():
    itemsCache = dependency.instance(IItemsCache)
    shop = itemsCache.items.shop
    return {'exchangeRate': shop.exchangeRate,
     'slotsPrices': shop.slotsPrices[1][0],
     'berthsPrices': shop.berthsPrices[2][0],
     'premiumPacket1Cost': shop.getPremiumPacketCost(1),
     'premiumPacket3Cost': shop.getPremiumPacketCost(3),
     'premiumPacket7Cost': shop.getPremiumPacketCost(7),
     'premiumPacket14Cost': shop.getPremiumPacketCost(14),
     'premiumPacket30Cost': shop.getPremiumPacketCost(30),
     'premiumPacket90Cost': shop.getPremiumPacketCost(90),
     'premiumPacket180Cost': shop.getPremiumPacketCost(180),
     'premiumPacket360Cost': shop.getPremiumPacketCost(360),
     'winXPFactorMode': shop.winXPFactorMode,
     'freeXPToTManXPRate': shop.freeXPToTManXPRate,
     'dailyXPFactor': shop.dailyXPFactor,
     'freeXPConversionDiscrecity': shop.freeXPConversion[0],
     'isPremium': itemsCache.items.stats.isPremium}


def getDecoration(uiDecoration):
    """ Get external decoration for the discount.
    """
    eventsCache = dependency.instance(IEventsCache)
    prefetcher = eventsCache.prefetcher
    return prefetcher.getMissionDecoration(uiDecoration, DECORATION_SIZES.DISCOUNT)


_PARAM_TO_IMG_DICT = {'exchangeRate': RES_ICONS.MAPS_ICONS_ACTIONS_480X280_CONVERT_GOLD,
 'paidRemovalCost': RES_ICONS.MAPS_ICONS_ACTIONS_480X280_REMOVE_EQUIPMENT,
 'changeRoleCost': RES_ICONS.MAPS_ICONS_ACTIONS_480X280_CREW_CHANGE_MAIN_SKILL,
 'freeXPConversionDiscrecity': RES_ICONS.MAPS_ICONS_ACTIONS_480X280_CONVERT_EXP,
 'slotsPrices': RES_ICONS.MAPS_ICONS_ACTIONS_480X280_SLOT,
 'berthsPrices': RES_ICONS.MAPS_ICONS_ACTIONS_480X280_PLACE_IN_BARRACKS,
 'goldTankmanCost': RES_ICONS.MAPS_ICONS_ACTIONS_480X280_CREW_EDUCATION,
 'creditsTankmanCost': RES_ICONS.MAPS_ICONS_ACTIONS_480X280_CREW_EDUCATION,
 'creditsDropSkillsCost': RES_ICONS.MAPS_ICONS_ACTIONS_480X280_CREW_SKILL_RESET,
 'goldDropSkillsCost': RES_ICONS.MAPS_ICONS_ACTIONS_480X280_CREW_SKILL_RESET,
 'passportChangeCost': RES_ICONS.MAPS_ICONS_ACTIONS_480X280_CREW_CHANGE_PROFILE,
 'femalePassportChangeCost': RES_ICONS.MAPS_ICONS_ACTIONS_480X280_CREW_CHANGE_PROFILE,
 'premiumPacket1Cost': RES_ICONS.MAPS_ICONS_ACTIONS_480X280_PREM_1,
 'premiumPacket3Cost': RES_ICONS.MAPS_ICONS_ACTIONS_480X280_PREM_3,
 'premiumPacket7Cost': RES_ICONS.MAPS_ICONS_ACTIONS_480X280_PREM_7,
 'premiumPacket30Cost': RES_ICONS.MAPS_ICONS_ACTIONS_480X280_PREM_30,
 'premiumPacket180Cost': RES_ICONS.MAPS_ICONS_ACTIONS_480X280_PREM_180,
 'premiumPacket360Cost': RES_ICONS.MAPS_ICONS_ACTIONS_480X280_PREM_360,
 'winXPFactorMode/always': RES_ICONS.MAPS_ICONS_ACTIONS_480X280_TANK_EXP,
 'winXPFactorMode/daily': RES_ICONS.MAPS_ICONS_ACTIONS_480X280_TANK_EXP,
 'freeXPToTManXPRate': RES_ICONS.MAPS_ICONS_ACTIONS_480X280_CREW_EXP,
 'clanCreationCost': RES_ICONS.MAPS_ICONS_ACTIONS_480X280_CLAN,
 'cond_VehPrice': RES_ICONS.MAPS_ICONS_ACTIONS_480X280_VEHICLES,
 'mul_VehPrice': RES_ICONS.MAPS_ICONS_ACTIONS_480X280_VEHICLES,
 'set_VehPrice': RES_ICONS.MAPS_ICONS_ACTIONS_480X280_VEHICLES,
 'mul_VehPriceAll': RES_ICONS.MAPS_ICONS_ACTIONS_480X280_VEHICLES,
 'mul_VehPriceNation': RES_ICONS.MAPS_ICONS_ACTIONS_480X280_VEHICLES,
 'set_VehSellPrice': RES_ICONS.MAPS_ICONS_ACTIONS_480X280_VEHICLES,
 'cond_VehRentPrice': RES_ICONS.MAPS_ICONS_ACTIONS_480X280_TANK_CLOCK,
 'mul_VehRentPrice': RES_ICONS.MAPS_ICONS_ACTIONS_480X280_TANK_CLOCK,
 'mul_VehRentPriceAll': RES_ICONS.MAPS_ICONS_ACTIONS_480X280_TANK_CLOCK,
 'mul_VehRentPriceNation': RES_ICONS.MAPS_ICONS_ACTIONS_480X280_TANK_CLOCK,
 'equipment/goldPrice': RES_ICONS.MAPS_ICONS_ACTIONS_480X280_CONSUMABLES,
 'equipment/creditsPrice': RES_ICONS.MAPS_ICONS_ACTIONS_480X280_CONSUMABLES,
 'mul_EquipmentPriceAll': RES_ICONS.MAPS_ICONS_ACTIONS_480X280_CONSUMABLES,
 'mul_EquipmentPrice': RES_ICONS.MAPS_ICONS_ACTIONS_480X280_CONSUMABLES,
 'set_EquipmentPrice': RES_ICONS.MAPS_ICONS_ACTIONS_480X280_CONSUMABLES,
 'mul_OptionalDevicePriceAll': RES_ICONS.MAPS_ICONS_ACTIONS_480X280_EQUIPMENT,
 'mul_OptionalDevicePrice': RES_ICONS.MAPS_ICONS_ACTIONS_480X280_EQUIPMENT,
 'set_OptionalDevicePrice': RES_ICONS.MAPS_ICONS_ACTIONS_480X280_EQUIPMENT,
 'shell/goldPrice': RES_ICONS.MAPS_ICONS_ACTIONS_480X280_SHELLS,
 'shell/creditsPrice': RES_ICONS.MAPS_ICONS_ACTIONS_480X280_SHELLS,
 'mul_ShellPriceAll': RES_ICONS.MAPS_ICONS_ACTIONS_480X280_SHELLS,
 'mul_ShellPriceNation': RES_ICONS.MAPS_ICONS_ACTIONS_480X280_SHELLS,
 'mul_ShellPrice': RES_ICONS.MAPS_ICONS_ACTIONS_480X280_SHELLS,
 'set_ShellPrice': RES_ICONS.MAPS_ICONS_ACTIONS_480X280_SHELLS,
 'set_PriceGroupPrice': RES_ICONS.MAPS_ICONS_ACTIONS_480X280_CUSTOMIZATION,
 'mul_PriceGroupPrice': RES_ICONS.MAPS_ICONS_ACTIONS_480X280_CUSTOMIZATION,
 'mul_PriceGroupPriceByTag': RES_ICONS.MAPS_ICONS_ACTIONS_480X280_CUSTOMIZATION,
 'mul_PriceGroupPriceAll': RES_ICONS.MAPS_ICONS_ACTIONS_480X280_CUSTOMIZATION,
 'set_GoodiePrice': RES_ICONS.MAPS_ICONS_ACTIONS_480X280_RESERVE,
 'mul_GoodiePrice': RES_ICONS.MAPS_ICONS_ACTIONS_480X280_RESERVE,
 'mul_GoodiePriceAll': RES_ICONS.MAPS_ICONS_ACTIONS_480X280_RESERVE,
 'tradeInSellPriceFactor': RES_ICONS.MAPS_ICONS_ACTIONS_480X280_TRADE_IN,
 'calendar': RES_ICONS.MAPS_ICONS_ACTIONS_480X280_CALENDAR,
 'boxbuying': RES_ICONS.MAPS_ICONS_ACTIONS_480X280_BOXES}
_MODIFIERS_DICT = {'mul_EconomicsParams': EconomicsActionsInfo,
 'set_EconomicsParams': EconomicsActionsInfo,
 'mul_EconomicsPrices': EconomicsActionsInfo,
 'set_EconomicsPrices': EconomicsActionsInfo,
 'set_TradeInParams': EconomicsActionsInfo,
 'cond_VehPrice': VehPriceActionInfo,
 'mul_VehPrice': VehPriceActionInfo,
 'mul_VehRentPrice': VehRentActionInfo,
 'mul_EquipmentPriceAll': EquipmentActionInfo,
 'mul_OptionalDevicePriceAll': OptDeviceActionInfo,
 'mul_ShellPriceAll': ShellPriceActionInfo,
 'set_PriceGroupPrice': C11nPriceGroupPriceActionInfo,
 'mul_PriceGroupPrice': C11nPriceGroupPriceActionInfo,
 'mul_PriceGroupPriceByTag': C11nPriceGroupPriceActionInfo,
 'mul_PriceGroupPriceAll': C11nPriceGroupPriceActionInfo,
 'set_GoodiePrice': BoosterPriceActionInfo,
 'mul_GoodiePrice': BoosterPriceActionInfo,
 'mul_GoodiePriceAll': BoosterPriceActionInfo,
 'calendar': CalendarActionInfo,
 'boxbuying': NyBoxBuyingActionInfo}

def getModifierObj(name, event, modifier):
    return _MODIFIERS_DICT[name](event, modifier) if name in _MODIFIERS_DICT else None


def getActionInfoData(event):
    return _parseAction(event) if event.getType() == constants.EVENT_TYPE.ACTION else []


def getAnnouncedActionInfo(info):
    return ComingSoonActionInfo(info)


def _parseAction(event):
    result = []
    modifiers = event.getActions()
    for modifierName, modifierData in modifiers.iteritems():
        for actionData in modifierData:
            modifier = getModifierObj(modifierName, event, actionData)
            if modifier:
                result.append(modifier)

    return result
