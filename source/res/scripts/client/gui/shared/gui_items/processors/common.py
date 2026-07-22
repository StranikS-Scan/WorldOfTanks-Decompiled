# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/processors/common.py
import logging
from itertools import chain
from string import lower
from BWUtil import AsyncReturn
from typing import TYPE_CHECKING
import BigWorld
from constants import PREMIUM_TYPE
from gui import SystemMessages
from gui.Scaleform.locale.MESSENGER import MESSENGER
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.SystemMessages import CURRENCY_TO_SM_TYPE, SM_TYPE
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.lobby.customization.shared import removePartsFromOutfit
from gui.impl.lobby.premacc.views_helpers import isSlotAvailableForUI
from gui.shared.formatters import formatGoldPrice, formatPrice, getStyle, icons, text_styles
from gui.shared.gui_items import GUI_ITEM_ECONOMY_CODE, GUI_ITEM_TYPE
from gui.shared.gui_items.processors import GroupedRequestProcessor, Processor, makeError, makeI18nError, makeI18nSuccess, makeSuccess, plugins
from gui.shared.money import Currency, Money
from gui.shared.notifications import NotificationPriorityLevel
from helpers import dependency
from items import makeIntCompactDescrByID
from items.components.c11n_constants import CustomizationType, CustomizationTypeNames, HIDDEN_CAMOUFLAGE_ID
from items.customizations import isEditedStyle
from preferred_maps import BlacklistWrapper, Slot, getConfiguredSlotLayout
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.game_control import IEpicBattleMetaGameController, IVehicleComparisonBasket, IWotPlusController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from th_async import await_callback, th_async, th_await
if TYPE_CHECKING:
    from typing import Dict
_logger = logging.getLogger(__name__)

class TankmanBerthsBuyer(Processor):

    def __init__(self, berthsPrice, countPacksBerths):
        super(TankmanBerthsBuyer, self).__init__()
        self.currency = berthsPrice.getCurrency()
        self.berthsPrice = berthsPrice
        self.countPacksBerths = countPacksBerths
        self.__addPlugins()

    def __addPlugins(self):
        library = R.images.gui.maps.icons.library
        img = backport.image(library.GoldIcon_2()) if self.currency == Currency.GOLD else backport.image(library.CreditsIcon_2())
        style = getStyle(self.currency) if self.currency in Currency.ALL else text_styles.credits
        ctx = {'berthsPrice': text_styles.concatStylesWithSpace(style(backport.getIntegralFormat(abs(self.berthsPrice.get(self.currency)))), icons.makeImageTag(img))}
        self.addPlugins([plugins.MoneyValidator(self.berthsPrice), plugins.MessageInformator('/'.join(['buyBerthsNotEnough', self.currency]), activeHandler=lambda : not plugins.MoneyValidator(self.berthsPrice).validate().success), plugins.MessageConfirmator('buyBerthsConfirmation', ctx=ctx)])

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError(sysMsgKey='buy_tankmen_berths/{}'.format('buy_error' if GUI_ITEM_ECONOMY_CODE.hasValue(errStr) else errStr), defaultSysMsgKey='buy_tankmen_berths/server_error')

    def _successHandler(self, code, ctx=None):
        msgType = SM_TYPE.FinancialTransactionWithGold if self.berthsPrice.getCurrency() == Currency.GOLD else SM_TYPE.FinancialTransactionWithCredits
        return makeI18nSuccess(sysMsgKey='buy_tankmen_berths/{}/success'.format(self.currency), money=formatPrice(self.berthsPrice, useStyle=True, justValue=True), type=msgType)

    def _request(self, callback):
        _logger.debug('Make server request to buy tankman berths')
        BigWorld.player().stats.buyBerths(self.countPacksBerths, lambda code: self._response(code, callback))


class PremiumAccountBuyer(Processor):

    def __init__(self, period, price, arenaUniqueID=0, withoutBenefits=False, requireConfirm=True):
        self.wasPremium = self.itemsCache.items.stats.isPremium
        plugList = [plugins.MoneyValidator(Money(gold=price))]
        if requireConfirm:
            plugList.insert(0, self.__getConfirmator(withoutBenefits, period, price))
        super(PremiumAccountBuyer, self).__init__(plugList)
        self.premiumPrice = price
        self.period = period
        self.arenaUniqueID = arenaUniqueID

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError(sysMsgKey='premium/{}'.format(errStr), defaultSysMsgKey='premium/server_error', auxData={'errStr': errStr}, period=self.period)

    def _successHandler(self, code, ctx=None):
        localKey = 'premium/continueSuccess' if self.wasPremium else 'premium/buyingSuccess'
        return makeI18nSuccess(sysMsgKey=localKey, period=self.period, money=formatGoldPrice(self.premiumPrice), type=SM_TYPE.PurchaseForGold)

    def _request(self, callback):
        _logger.debug('Make server request to buy premium account, %s, %s', self.period, self.premiumPrice)
        BigWorld.player().stats.upgradeToPremium(self.period, self.arenaUniqueID, lambda code, errStr: self._response(code, callback, errStr=errStr))

    def __getConfirmator(self, withoutBenefits, period, price):
        if withoutBenefits:
            return plugins.HtmlMessageConfirmator('buyPremWithoutBenefitsConfirmation', 'html_templates:lobby/dialogs', 'confirmBuyPremWithoutBenefeits', {'days': text_styles.stats(period),
             Currency.GOLD: text_styles.concatStylesWithSpace(text_styles.gold(backport.getGoldFormat(price)), icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_GOLDICON_2))})
        localKey = 'premiumContinueConfirmation' if self.wasPremium else 'premiumBuyConfirmation'
        return plugins.MessageConfirmator(localKey, ctx={'days': text_styles.stats(period),
         Currency.GOLD: text_styles.concatStylesWithSpace(text_styles.gold(backport.getGoldFormat(price)), icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_GOLDICON_2))})


class GoldToCreditsExchanger(Processor):

    def __init__(self, gold, withConfirm=True):
        self.gold = gold
        self.credits = int(gold) * self.itemsCache.items.shop.exchangeRate
        super(GoldToCreditsExchanger, self).__init__()
        if withConfirm:
            self.addPlugin(plugins.HtmlMessageConfirmator('exchangeGoldConfirmation', 'html_templates:lobby/dialogs', 'confirmExchange', {'primaryCurrencyAmount': backport.getGoldFormat(self.gold),
             'resultCurrencyAmount': backport.getIntegralFormat(self.credits)}))
        self.addPlugin(plugins.MoneyValidator(Money(gold=self.gold)))

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError(sysMsgKey='exchange/{}'.format(errStr), defaultSysMsgKey='exchange/server_error', gold=self.gold)

    def _successHandler(self, code, ctx=None):
        return makeI18nSuccess(sysMsgKey='exchange/success', gold=backport.getGoldFormat(self.gold), credits=formatPrice(Money(credits=self.credits)), type=SM_TYPE.FinancialTransactionWithGold)

    def _request(self, callback):
        _logger.debug('Make server request to exchange gold to credits')
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
        return makeI18nError(sysMsgKey='exchangeXP/{}'.format(errStr), defaultSysMsgKey='exchangeXP/server_error', xp=backport.getIntegralFormat(self.xp))

    def _successHandler(self, code, ctx=None):
        return makeI18nSuccess(sysMsgKey='exchangeXP/success', gold=backport.getGoldFormat(self.gold), xp=backport.getIntegralFormat(self.xp), type=SM_TYPE.FinancialTransactionWithGold)

    def _request(self, callback):
        _logger.debug('Make server request to exchange xp for credits')
        BigWorld.player().stats.convertToFreeXP(self.vehiclesCD, self.xp, lambda code: self._response(code, callback), int(self.__freeConversion))

    def __makeConfirmator(self):
        xpLimit = self.itemsCache.items.shop.freeXPConversionLimit
        extra = {'resultCurrencyAmount': backport.getIntegralFormat(self.xp),
         'primaryCurrencyAmount': backport.getGoldFormat(self.gold)}
        if self.__freeConversion:
            sourceKey = 'XP_EXCHANGE_FOR_FREE'
            extra['freeXPLimit'] = backport.getIntegralFormat(xpLimit)
        else:
            sourceKey = 'XP_EXCHANGE_FOR_GOLD'
        return plugins.HtmlMessageConfirmator('exchangeXPConfirmation', 'html_templates:lobby/dialogs', 'confirmExchangeXP', extra, sourceKey=sourceKey)


class BattleResultsGetter(Processor):

    def __init__(self, arenaUniqueID):
        super(BattleResultsGetter, self).__init__()
        self.__arenaUniqueID = arenaUniqueID

    def _errorHandler(self, code, errStr='', ctx=None):
        _logger.warning('Error on server request to get battle results: %s, %s, %s, %s', self.__arenaUniqueID, code, errStr, ctx)
        return makeError()

    def _successHandler(self, code, ctx=None):
        return makeSuccess(auxData=ctx)

    def _request(self, callback):
        _logger.debug('Make server request to get battle results')
        BigWorld.player().battleResultsCache.get(self.__arenaUniqueID, lambda code, battleResults: self._response(code, callback, ctx=battleResults))


class OutfitApplier(Processor):

    def __init__(self, vehicle, outfitData):
        super(OutfitApplier, self).__init__((plugins.CustomizationPurchaseValidator(outfitData),))
        self.vehicle = vehicle
        self.outfitData = outfitData

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError('customization/{}'.format(errStr or 'server_error'))

    def _request(self, callback):
        _logger.debug('Make server request to put on outfit on vehicle %s, outfitData %s', self.vehicle.invID, self.outfitData)
        requestData = []
        c11nService = dependency.instance(ICustomizationService)
        for outfit, season in self.outfitData:
            if outfit.style:
                intCD = makeIntCompactDescrByID('customizationItem', CustomizationType.STYLE, outfit.style.id)
                style = self.itemsCache.items.getItemByCD(intCD)
                outfit = removePartsFromOutfit(season, outfit)
                if style and style.isProgressive:
                    outfit = c11nService.removeAdditionalProgressionData(outfit=outfit, style=style, vehCD=self.vehicle.descriptor.makeCompactDescr(), season=season)
            component = outfit.pack()
            self.__removeHiddenCamouflages(component)
            if component.styleId and isEditedStyle(component):
                intCD = makeIntCompactDescrByID('customizationItem', CustomizationType.STYLE, component.styleId)
                style = self.itemsCache.items.getItemByCD(intCD)
                vehicleCD = self.vehicle.descriptor.makeCompactDescr()
                baseOutfit = removePartsFromOutfit(season, style.getOutfit(season, vehicleCD))
                if style.isProgressive:
                    baseOutfit = c11nService.removeAdditionalProgressionData(outfit=baseOutfit, style=style, vehCD=vehicleCD, season=season)
                baseComponent = baseOutfit.pack()
                self.__removeHiddenCamouflages(baseComponent)
                component = component.getDiff(baseComponent)
            self.__validateOutfitComponent(component)
            requestData.append((component.makeCompDescr(), season))

        BigWorld.player().shop.buyAndEquipOutfit(self.vehicle.invID, requestData, lambda code: self._response(code, callback))

    def __validateOutfitComponent(self, outfitComponent):
        for itemType in CustomizationType.STYLE_ONLY_RANGE:
            typeName = lower(CustomizationTypeNames[itemType])
            componentsAttrName = '{}s'.format(typeName)
            itemsComponents = getattr(outfitComponent, componentsAttrName, None)
            if itemsComponents:
                _logger.error('StyleOnly items cannot be installed manually: itemType=[%s]; components=[%s].Forbidden components removed.', typeName, itemsComponents)
                itemsComponents = []
            setattr(outfitComponent, componentsAttrName, itemsComponents)

        return

    @staticmethod
    def __removeHiddenCamouflages(outfitComponent):
        camouflages = []
        for camoComponent in outfitComponent.camouflages:
            if camoComponent.id != HIDDEN_CAMOUFLAGE_ID:
                camouflages.append(camoComponent)

        outfitComponent.camouflages = camouflages


class CustomizationsBuyer(Processor):

    def __init__(self, vehicle, item, count):
        super(CustomizationsBuyer, self).__init__()
        self.vehicle = vehicle
        self.item = item
        self.count = count

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError('customization/{}'.format(errStr or 'server_error'))

    def _request(self, callback):
        invID = self.vehicle.invID if self.vehicle else 0
        _logger.debug('Make server request to buy customizations on vehicle %s: %s count %s', invID, self.item, self.count)
        BigWorld.player().shop.buyCustomizations(invID, {self.item.intCD: self.count}, lambda code: self._response(code, callback))

    def _getTotalPrice(self):
        buyPrice = self.item.buyPrices.itemPrice.price
        if not buyPrice:
            _logger.error('Incorrect attempt to buy item %s', self.item)
        return buyPrice * self.count

    def _getMsgCtx(self):
        styleItemType = backport.text(R.strings.item_types.customization.style())
        return {'itemType': styleItemType if self.item.itemTypeID == GUI_ITEM_TYPE.STYLE else self.item.userType,
         'itemName': self.item.userName,
         'count': backport.getIntegralFormat(int(self.count)),
         'money': formatPrice(self._getTotalPrice())}

    def _successHandler(self, code, ctx=None):
        currency = self.item.buyPrices.itemPrice.price.getCurrency(byWeight=True)
        sysMsgType = CURRENCY_TO_SM_TYPE.get(currency, SM_TYPE.PurchaseForGold)
        msgCtx = self._getMsgCtx()
        if self.count == 1:
            msg = backport.text(R.strings.messenger.serviceChannelMessages.sysMsg.customization.buyOne(), **msgCtx)
        else:
            msgCtx = {'items': backport.text(R.strings.messenger.serviceChannelMessages.sysMsg.customization.item(), **msgCtx) + '.',
             'money': msgCtx['money']}
            msg = backport.text(R.strings.messenger.serviceChannelMessages.sysMsg.customization.buyMany(), **msgCtx)
        SystemMessages.pushMessage(msg, type=sysMsgType)
        return makeSuccess(auxData=ctx)


class CustomizationsSeller(Processor):

    def __init__(self, vehicle, item, count=1):
        super(CustomizationsSeller, self).__init__()
        self.vehicle = vehicle
        self.item = item
        self.count = count

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError('customization/{}'.format(errStr or 'server_error'))

    def _getTotalPrice(self):
        sellPrice = self.item.sellPrices.itemPrice.price
        if not sellPrice:
            _logger.error('Attempt to sell item %s that is not sold.', self.item)
        return sellPrice * self.count

    def _getMsgCtx(self):
        styleItemType = backport.text(R.strings.item_types.customization.style())
        return {'itemType': styleItemType if self.item.itemTypeID == GUI_ITEM_TYPE.STYLE else self.item.userType,
         'itemName': self.item.userName,
         'count': backport.getIntegralFormat(int(self.count)),
         'money': formatPrice(self._getTotalPrice()),
         'priority': NotificationPriorityLevel.MEDIUM}

    def _successHandler(self, code, ctx=None):
        messageType = MESSENGER.SERVICECHANNELMESSAGES_SYSMSG_CUSTOMIZATIONS_SELL
        if ctx is not None and 'count' in ctx:
            self.count = ctx['count']
        if self.count > 0:
            SystemMessages.pushI18nMessage(messageType, type=SM_TYPE.Selling, **self._getMsgCtx())
        return makeSuccess(auxData=ctx)

    def _request(self, callback):
        vehicleCD = self.vehicle.intCD if self.vehicle is not None else 0
        _logger.debug('Make server request to sell customizations on vehicle %s, item %s, count %s', vehicleCD, self.item, self.count)
        BigWorld.player().shop.sellCustomizations(vehicleCD, self.item.intCD, self.count, lambda code, ctx={}: self._response(code, callback, ctx=ctx))
        return


class CustomizationsTagsSetter(Processor):

    def __init__(self, itemCD, mask, tagValue=0):
        super(CustomizationsTagsSetter, self).__init__()
        self.itemCD = itemCD
        self.mask = mask
        self.tagValue = tagValue

    def _request(self, callback):
        _logger.debug('Make server request to set customizations tags %s, item %s, value %s', self.mask, self.itemCD, self.tagValue)
        BigWorld.player().inventory.setCustomizationTags(self.itemCD, self.mask, self.tagValue, lambda code, ctx={}: self._response(code, callback, ctx=ctx))


class BadgesSelector(Processor):

    def __init__(self, badges=None):
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
        return makeI18nError(sysMsgKey='{}/server_error/{}'.format(self._getMessagePrefix(), errStr), defaultSysMsgKey='{}/server_error'.format(self._getMessagePrefix()))

    def _request(self, callback):
        _logger.debug('Make server request to select badges %s', self.__badges)
        BigWorld.player().badges.selectBadges(self.__badges, lambda resID, code, errStr: self._response(code, callback, errStr))


class ConvertBlueprintFragmentProcessor(Processor):

    def __init__(self, vehicleCD, count, fragmentPosition, usedNationalFragments):
        super(ConvertBlueprintFragmentProcessor, self).__init__()
        self.__vehicleCD = vehicleCD
        self.__position = fragmentPosition
        self.__count = count
        self.__usedNationalFragments = usedNationalFragments

    def _request(self, callback):
        BigWorld.player().blueprints.convertBlueprintFragment(self.__vehicleCD, self.__position, self.__count, self.__usedNationalFragments, lambda code: self._response(code, callback))


class _MapsBlackListSelector(Processor):
    __itemsCache = dependency.descriptor(IItemsCache)
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, selectedMaps=None, mapChangeApplied=True):
        super(_MapsBlackListSelector, self).__init__()
        if selectedMaps is None:
            selectedMaps = {}
        self.__selectedMaps = selectedMaps
        self.__mapChangeApplied = mapChangeApplied
        return

    def _getMessagePrefix(self):
        pass

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError(sysMsgKey='{}/server_error/{}'.format(self._getMessagePrefix(), errStr), defaultSysMsgKey='{}/server_error'.format(self._getMessagePrefix()))

    def _successHandler(self, code, ctx=None):
        itemsCache = dependency.instance(IItemsCache)
        wotPLusController = dependency.instance(IWotPlusController)
        isPremiumActive = itemsCache.items.stats.isActivePremium(PREMIUM_TYPE.PLUS)
        isWotPlusActive = wotPLusController.isEnabled()
        isWotPlusEnabled = wotPLusController.isWotPlusEnabled()
        if isWotPlusEnabled:
            if not isPremiumActive and not isWotPlusActive:
                return makeI18nSuccess(sysMsgKey='{}/success/wotPlusEnabled/noSubscriptions'.format(self._getMessagePrefix()))
            if isPremiumActive and not isWotPlusActive:
                return makeI18nSuccess(sysMsgKey='{}/success/wotPlusEnabled/premium'.format(self._getMessagePrefix()))
            if not isPremiumActive and isWotPlusActive:
                return makeI18nSuccess(sysMsgKey='{}/success/wotPlusEnabled/wotPlus'.format(self._getMessagePrefix()))
        return makeI18nSuccess(sysMsgKey='{}/success'.format(self._getMessagePrefix()))

    def _request(self, callback):
        if not self.__mapChangeApplied:
            _logger.debug('Skip maps blacklist request: slot is no longer available for change (layout=%r)', self.__selectedMaps)
            callback(makeSuccess())
            return
        _logger.debug('Make server request to select black maps %r', self.__selectedMaps)
        slots = sorted(self.__selectedMaps.itervalues(), key=lambda slot: slot.id)
        BigWorld.player().stats.setMapsBlackList(list(chain.from_iterable(((slot.id, slot.type, slot.mapID) for slot in slots))), lambda code, errStr, ext: self._response(code, callback, ctx=ext, errStr=errStr))

    def _getLayout(self):
        config = self.__lobbyContext.getServerSettings().getPreferredMapsConfig()
        layout = getConfiguredSlotLayout(config)
        blackList = BlacklistWrapper(self.__itemsCache.items.stats.getMapsBlackList())
        for slotId, _ in layout.iteritems():
            serverSlot = blackList.get(slotId)
            if serverSlot is not None:
                layout[slotId] = serverSlot

        return layout


class MapsBlackListSetter(_MapsBlackListSelector):

    def __init__(self, selectedMapID):
        layout = self._getLayout()
        wasInserted = False
        for slotId in sorted(layout):
            slot = layout[slotId]
            if isSlotAvailableForUI(slot) and slot.isEmpty():
                layout[slot.id] = slot._replace(mapID=selectedMapID, type=slot.type)
                wasInserted = True
                break

        if not wasInserted:
            _logger.debug('No available slots to set map %d (layout=%r)', selectedMapID, layout)
        super(MapsBlackListSetter, self).__init__(layout, mapChangeApplied=wasInserted)


class MapsBlackListRemover(_MapsBlackListSelector):

    def __init__(self, removeMapID):
        layout = self._getLayout()
        wasRemoved = False
        for slotId in sorted(layout):
            slot = layout[slotId]
            if isSlotAvailableForUI(slot) and slot.mapID == removeMapID:
                layout[slot.id] = slot.dropMap()
                wasRemoved = True
                break

        if not wasRemoved:
            _logger.debug('Cannot remove mapID %d from layout %r', removeMapID, layout)
        super(MapsBlackListRemover, self).__init__(layout, mapChangeApplied=wasRemoved)


class MapsBlackListChanger(_MapsBlackListSelector):

    def __init__(self, srcMapID, destMapID):
        layout = self._getLayout()
        wasChanged = False
        for slotId in sorted(layout):
            slot = layout[slotId]
            if isSlotAvailableForUI(slot) and slot.mapID == srcMapID:
                layout[slot.id] = slot._replace(mapID=destMapID)
                wasChanged = True
                break

        if not wasChanged:
            _logger.debug('Cannot change srcMapID %d to %d: slot disabled or map missing (layout=%r)', srcMapID, destMapID, layout)
        super(MapsBlackListChanger, self).__init__(layout, mapChangeApplied=wasChanged)


class PremiumBonusApplier(Processor):

    def __init__(self, arenaUniqueID=None, vehTypeCompDescr=None):
        super(PremiumBonusApplier, self).__init__()
        self.__arenaUniqueID = arenaUniqueID
        self.__vehTypeCompDescr = vehTypeCompDescr

    def _getMessagePrefix(self):
        pass

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError(sysMsgKey='{}/server_error/{}'.format(self._getMessagePrefix(), errStr), defaultSysMsgKey='{}/server_error'.format(self._getMessagePrefix()))

    def _request(self, callback):
        _logger.debug('Make server request to apply premium XP bonus %d', self.__arenaUniqueID)
        BigWorld.player().shop.applyPremiumXPBonus(self.__arenaUniqueID, self.__vehTypeCompDescr, lambda resID, code, errStr: self._response(code, callback, errStr))


class UseCrewBookProcessor(GroupedRequestProcessor):

    def __init__(self, crewBookCD, crewBookCount, vehInvID, tmanInvID, groupID=0, groupSize=1):
        self.__crewBookCD = crewBookCD
        self.__crewBookCount = crewBookCount
        self.__vehInvID = vehInvID
        self.__tmanInvID = tmanInvID
        super(UseCrewBookProcessor, self).__init__(BigWorld.player().inventory.useCrewBook, crewBookCD, crewBookCount, vehInvID, tmanInvID, groupID=groupID, groupSize=groupSize)

    @staticmethod
    def _makeSuccessData(*args, **kwargs):
        itemsCache = dependency.instance(IItemsCache)
        auxData = []
        for item in iter(kwargs.get('ctx', [])):
            if item.itemCount == 1:
                auxData.append(makeI18nSuccess(sysMsgKey='crewBooksNotification/bookUsed', name=itemsCache.items.getItemByCD(item.itemID).userName))
                continue
            auxData.append(makeI18nSuccess(sysMsgKey='crewBooksNotification/booksUsed', name=itemsCache.items.getItemByCD(item.itemID).userName, count=item.itemCount))

        return auxData

    def _successHandler(self, code, ctx=None):
        return makeI18nSuccess(sysMsgKey='crewBooksNotification/success', auxData=self._makeSuccessData(ctx=ctx))

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError(sysMsgKey='crewBooks/{}'.format(errStr), auxData=self._makeErrorData(errStr), defaultSysMsgKey='crewBooks/failed')


class VehicleChangeNation(Processor):
    _comparisonBasket = dependency.descriptor(IVehicleComparisonBasket)

    def __init__(self, cvh, nvh):
        super(VehicleChangeNation, self).__init__()
        self._cvh = cvh
        self._nvh = nvh

    def _request(self, callback):
        BigWorld.player().inventory.switchNation(self._cvh.name, self._nvh.name, lambda code: self._response(code, callback))

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError(sysMsgKey=backport.text(R.strings.system_messages.nation_change.dyn(errStr)()), defaultSysMsgKey=backport.text(R.strings.system_messages.nation_change.error()))

    def _successHandler(self, code, ctx=None):
        return makeI18nSuccess(sysMsgKey=backport.text(R.strings.system_messages.nation_change.success()), veh_name=self._cvh.userName)


class BuyBattleAbilitiesProcessor(Processor):
    __epicMetaGameCtrl = dependency.descriptor(IEpicBattleMetaGameController)

    def __init__(self, skillIds):
        super(BuyBattleAbilitiesProcessor, self).__init__()
        self.__skillIds = skillIds

    @th_async
    def _request(self, callback):
        errorCode = yield th_await(self._requestChain())
        callback(makeError(errorCode) if errorCode else makeSuccess())

    @th_async
    def _requestChain(self):
        for skillId in self.__skillIds:
            _, errorCode = yield await_callback(self.__epicMetaGameCtrl.increaseSkillLevel)(skillId)
            if errorCode:
                raise AsyncReturn(errorCode)

        raise AsyncReturn(None)
        return
