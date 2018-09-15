# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/processors/common.py
import BigWorld
from debug_utils import LOG_DEBUG, LOG_ERROR, LOG_WARNING
from gui import SystemMessages
from gui.Scaleform.locale.MESSENGER import MESSENGER
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.SystemMessages import SM_TYPE, CURRENCY_TO_SM_TYPE
from gui.shared.formatters import formatPrice, formatGoldPrice, text_styles, icons
from gui.shared.gui_items.processors import Processor, makeError, makeSuccess, makeI18nError, makeI18nSuccess, plugins
from gui.shared.gui_items.customization.c11n_items import Camouflage, Modification, Style
from gui.shared.money import Money, Currency

class TankmanBerthsBuyer(Processor):

    def __init__(self, berthsPrice, berthsCount):
        super(TankmanBerthsBuyer, self).__init__((plugins.MessageInformator('barracksExpandNotEnoughMoney', activeHandler=lambda : not plugins.MoneyValidator(berthsPrice).validate().success), plugins.MessageConfirmator('barracksExpand', ctx={'price': text_styles.concatStylesWithSpace(text_styles.gold(str(berthsPrice.gold)), icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_GOLDICON_2)),
          'count': text_styles.stats(berthsCount)}), plugins.MoneyValidator(berthsPrice)))
        self.berthsPrice = berthsPrice

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError('buy_tankmen_berths/%s' % errStr, defaultSysMsgKey='buy_tankmen_berths/server_error')

    def _successHandler(self, code, ctx=None):
        return makeI18nSuccess('buy_tankmen_berths/success', money=formatPrice(self.berthsPrice), type=SM_TYPE.PurchaseForGold)

    def _request(self, callback):
        LOG_DEBUG('Make server request to buy tankman berths')
        BigWorld.player().stats.buyBerths(lambda code: self._response(code, callback))


class PremiumAccountBuyer(Processor):

    def __init__(self, period, price, arenaUniqueID=0, withoutBenefits=False):
        self.wasPremium = self.itemsCache.items.stats.isPremium
        super(PremiumAccountBuyer, self).__init__((self.__getConfirmator(withoutBenefits, period, price), plugins.MoneyValidator(Money(gold=price))))
        self.premiumPrice = price
        self.period = period
        self.arenaUniqueID = arenaUniqueID

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError('premium/%s' % errStr, defaultSysMsgKey='premium/server_error', period=self.period, auxData={'errStr': errStr})

    def _successHandler(self, code, ctx=None):
        localKey = 'premium/continueSuccess' if self.wasPremium else 'premium/buyingSuccess'
        return makeI18nSuccess(localKey, period=self.period, money=formatGoldPrice(self.premiumPrice), type=SM_TYPE.PurchaseForGold)

    def _request(self, callback):
        LOG_DEBUG('Make server request to buy premium account', self.period, self.premiumPrice)
        BigWorld.player().stats.upgradeToPremium(self.period, self.arenaUniqueID, lambda code, errStr: self._response(code, callback, errStr=errStr))

    def __getConfirmator(self, withoutBenefits, period, price):
        if withoutBenefits:
            return plugins.HtmlMessageConfirmator('buyPremWithoutBenefitsConfirmation', 'html_templates:lobby/dialogs', 'confirmBuyPremWithoutBenefeits', {'days': text_styles.stats(period),
             Currency.GOLD: text_styles.concatStylesWithSpace(text_styles.gold(BigWorld.wg_getGoldFormat(price)), icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_GOLDICON_2))})
        localKey = 'premiumContinueConfirmation' if self.wasPremium else 'premiumBuyConfirmation'
        return plugins.MessageConfirmator(localKey, ctx={'days': text_styles.stats(period),
         Currency.GOLD: text_styles.concatStylesWithSpace(text_styles.gold(BigWorld.wg_getGoldFormat(price)), icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_GOLDICON_2))})


class GoldToCreditsExchanger(Processor):

    def __init__(self, gold):
        self.gold = gold
        self.credits = int(gold) * self.itemsCache.items.shop.exchangeRate
        super(GoldToCreditsExchanger, self).__init__(plugins=(plugins.HtmlMessageConfirmator('exchangeGoldConfirmation', 'html_templates:lobby/dialogs', 'confirmExchange', {'primaryCurrencyAmount': BigWorld.wg_getGoldFormat(self.gold),
          'resultCurrencyAmount': BigWorld.wg_getIntegralFormat(self.credits)}), plugins.MoneyValidator(Money(gold=self.gold))))

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError('exchange/%s' % errStr, defaultSysMsgKey='exchange/server_error', gold=self.gold)

    def _successHandler(self, code, ctx=None):
        return makeI18nSuccess('exchange/success', gold=BigWorld.wg_getGoldFormat(self.gold), credits=formatPrice(Money(credits=self.credits)), type=SM_TYPE.FinancialTransactionWithGold)

    def _request(self, callback):
        LOG_DEBUG('Make server request to exchange gold to credits')
        BigWorld.player().stats.exchange(self.gold, lambda code: self._response(code, callback))


class FreeXPExchanger(Processor):

    def __init__(self, xp, vehiclesCD, freeConversion=False):
        rate = self.itemsCache.items.shop.freeXPConversion
        self.xp = xp
        self.__freeConversion = bool(freeConversion)
        self.gold = round(rate[1] * xp / rate[0]) if not freeConversion else 0
        self.vehiclesCD = vehiclesCD
        super(FreeXPExchanger, self).__init__(plugins=(self.__makeConfirmator(), plugins.MoneyValidator(Money(gold=self.gold)), plugins.EliteVehiclesValidator(self.vehiclesCD)))

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError('exchangeXP/%s' % errStr, defaultSysMsgKey='exchangeXP/server_error', xp=BigWorld.wg_getIntegralFormat(self.xp))

    def _successHandler(self, code, ctx=None):
        return makeI18nSuccess('exchangeXP/success', gold=BigWorld.wg_getGoldFormat(self.gold), xp=BigWorld.wg_getIntegralFormat(self.xp), type=SM_TYPE.FinancialTransactionWithGold)

    def _request(self, callback):
        LOG_DEBUG('Make server request to exchange xp for credits')
        BigWorld.player().stats.convertToFreeXP(self.vehiclesCD, self.xp, lambda code: self._response(code, callback), int(self.__freeConversion))

    def __makeConfirmator(self):
        xpLimit = self.itemsCache.items.shop.freeXPConversionLimit
        extra = {'resultCurrencyAmount': BigWorld.wg_getIntegralFormat(self.xp),
         'primaryCurrencyAmount': BigWorld.wg_getGoldFormat(self.gold)}
        if self.__freeConversion:
            sourceKey = 'XP_EXCHANGE_FOR_FREE'
            extra['freeXPLimit'] = BigWorld.wg_getIntegralFormat(xpLimit)
        else:
            sourceKey = 'XP_EXCHANGE_FOR_GOLD'
        return plugins.HtmlMessageConfirmator('exchangeXPConfirmation', 'html_templates:lobby/dialogs', 'confirmExchangeXP', extra, sourceKey=sourceKey)


class BattleResultsGetter(Processor):

    def __init__(self, arenaUniqueID):
        super(BattleResultsGetter, self).__init__()
        self.__arenaUniqueID = arenaUniqueID

    def _errorHandler(self, code, errStr='', ctx=None):
        LOG_WARNING('Error on server request to get battle results ', self.__arenaUniqueID, code, errStr, ctx)
        return makeError()

    def _successHandler(self, code, ctx=None):
        return makeSuccess(auxData=ctx)

    def _request(self, callback):
        LOG_DEBUG('Make server request to get battle results')
        BigWorld.player().battleResultsCache.get(self.__arenaUniqueID, lambda code, battleResults: self._response(code, callback, ctx=battleResults))


class OutfitApplier(Processor):
    """ Outfit buyer and applier.
    """

    def __init__(self, vehicle, outfit, season):
        super(OutfitApplier, self).__init__()
        self.vehicle = vehicle
        self.outfit = outfit
        self.season = season

    def _errorHandler(self, code, errStr='', ctx=None):
        if not errStr:
            msg = 'server_error'
        else:
            msg = errStr
        return makeI18nError('customization/{}'.format(msg))

    def _request(self, callback):
        LOG_DEBUG('Make server request to put on outfit on vehicle {}, season {}'.format(self.vehicle.invID, self.season))
        BigWorld.player().shop.buyAndEquipOutfit(self.vehicle.invID, self.season, self.outfit.pack().makeCompDescr(), lambda code: self._response(code, callback))


class StyleApplier(Processor):
    """ Style buyer and applier.
    """

    def __init__(self, vehicle, style=None):
        super(StyleApplier, self).__init__()
        self.vehicle = vehicle
        self.style = style

    def _errorHandler(self, code, errStr='', ctx=None):
        if not errStr:
            msg = 'server_error'
        else:
            msg = errStr
        return makeI18nError('customization/{}'.format(msg))

    def _request(self, callback):
        LOG_DEBUG('Make server request to put on style on vehicle {}'.format(self.vehicle.invID))
        if self.style:
            styleID = self.style.id
        else:
            styleID = 0
        BigWorld.player().shop.buyAndEquipStyle(self.vehicle.invID, styleID, lambda code: self._response(code, callback))


class CustomizationsBuyer(Processor):
    """ Customizations buyer.
    """

    def __init__(self, vehicle, item, count):
        super(CustomizationsBuyer, self).__init__()
        self.vehicle = vehicle
        self.item = item
        self.count = count

    def _errorHandler(self, code, errStr='', ctx=None):
        if not errStr:
            msg = 'server_error'
        else:
            msg = errStr
        return makeI18nError('customization/{}'.format(msg))

    def _request(self, callback):
        if self.vehicle:
            invID = self.vehicle.invID
        else:
            invID = 0
        LOG_DEBUG('Make server request to buy customizations on vehicle {}: {} count {}'.format(invID, self.item, self.count))
        BigWorld.player().shop.buyCustomizations(invID, {self.item.intCD: self.count}, lambda code: self._response(code, callback))

    def _getTotalPrice(self):
        buyPrice = self.item.buyPrices.itemPrice.price
        if not buyPrice:
            LOG_ERROR('Incorrect attempt to buy item {}'.format(self.item))
        return buyPrice * self.count

    def _getMsgCtx(self):
        itemTypeName = ''
        if type(self.item) is not Camouflage:
            itemTypeName = self.item.userType
        return {'itemType': itemTypeName,
         'itemName': self.item.userName,
         'count': BigWorld.wg_getIntegralFormat(int(self.count)),
         'money': formatPrice(self._getTotalPrice())}

    def _successHandler(self, code, ctx=None):
        messageType = MESSENGER.SERVICECHANNELMESSAGES_SYSMSG_CUSTOMIZATIONS_BUY_2
        sysMsgType = CURRENCY_TO_SM_TYPE.get(self.item.buyPrices.itemPrice.price, SM_TYPE.PurchaseForGold)
        if type(self.item) in (Camouflage, Modification, Style):
            messageType = MESSENGER.SERVICECHANNELMESSAGES_SYSMSG_CUSTOMIZATIONS_BUY_1
        SystemMessages.pushI18nMessage(messageType, type=sysMsgType, **self._getMsgCtx())
        return makeSuccess(auxData=ctx)


class CustomizationsSeller(Processor):
    """ Customizations buyer.
    """

    def __init__(self, vehicle, item, count=1):
        super(CustomizationsSeller, self).__init__()
        self.vehicle = vehicle
        self.item = item
        self.count = count

    def _errorHandler(self, code, errStr='', ctx=None):
        if not errStr:
            msg = 'server_error'
        else:
            msg = errStr
        return makeI18nError('customization/{}'.format(msg))

    def _getTotalPrice(self):
        sellPrice = self.item.sellPrices.itemPrice.price
        if not sellPrice:
            LOG_ERROR('Attempt to sell item {} that is not sold.'.format(self.item))
        return sellPrice * self.count

    def _getMsgCtx(self):
        itemTypeName = ''
        if type(self.item) is not Camouflage:
            itemTypeName = self.item.userType
        return {'itemType': itemTypeName,
         'itemName': self.item.userName,
         'count': BigWorld.wg_getIntegralFormat(int(self.count)),
         'money': formatPrice(self._getTotalPrice())}

    def _successHandler(self, code, ctx=None):
        messageType = MESSENGER.SERVICECHANNELMESSAGES_SYSMSG_CUSTOMIZATIONS_SELL_2
        if type(self.item) in (Camouflage, Modification, Style):
            messageType = MESSENGER.SERVICECHANNELMESSAGES_SYSMSG_CUSTOMIZATIONS_SELL_1
        SystemMessages.pushI18nMessage(messageType, type=SM_TYPE.Selling, **self._getMsgCtx())
        return makeSuccess(auxData=ctx)

    def _request(self, callback):
        if self.vehicle:
            invID = self.vehicle.invID
        else:
            invID = 0
        LOG_DEBUG('Make server request to sell customizations on vehicle {}, item {}, count {}'.format(invID, self.item, self.count))
        BigWorld.player().shop.sellCustomizations(invID, self.item.intCD, self.count, lambda code: self._response(code, callback))


class BadgesSelector(Processor):

    def __init__(self, badges=None):
        """
        Processor that selects or removes badges.
        :param badges: list of badges IDs (None for removal)
        """
        if badges is None:
            plugs = ()
            badges = ()
        else:
            plugs = (plugins.BadgesValidator(badges),)
        super(BadgesSelector, self).__init__(plugs)
        self.__badges = badges
        return

    def _getMessagePrefix(self):
        pass

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError('%s/server_error/%s' % (self._getMessagePrefix(), errStr), defaultSysMsgKey='%s/server_error' % self._getMessagePrefix())

    def _request(self, callback):
        LOG_DEBUG('Make server request to select badges', self.__badges)
        BigWorld.player().badges.selectBadges(self.__badges, lambda resID, code: self._response(code, callback))
