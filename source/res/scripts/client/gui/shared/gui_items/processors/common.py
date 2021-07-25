# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/processors/common.py
from functools import partial
import logging
from string import lower
import BigWorld
from constants import EMPTY_GEOMETRY_ID
from crew2 import settings_globals
from items import makeIntCompactDescrByID
from items.components.c11n_constants import CustomizationType, CustomizationTypeNames, HIDDEN_CAMOUFLAGE_ID
from items.components.detachment_components import isPerksRepartition
from items.components.detachment_constants import DetachmentSlotType, ChangePerksMode, DetachmentOperations, ExcludeInstructorOption
from items.components.dormitory_constants import DormitorySections
from skeletons.gui.shared import IItemsCache
from skeletons.gui.customization import ICustomizationService
from gui import SystemMessages
from gui.impl.gen import R
from gui.impl import backport
from gui.Scaleform.locale.MESSENGER import MESSENGER
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.SystemMessages import SM_TYPE, CURRENCY_TO_SM_TYPE, FIN_TO_SM_TYPE
from gui.shared.formatters import formatPrice, formatGoldPrice, text_styles, icons, getBWFormatter
from gui.shared.gui_items.processors import Processor, makeError, makeSuccess, makeI18nError, makeI18nSuccess, plugins
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.impl.auxiliary.detachment_helper import getDropSkillsPrice
from gui.shared.money import Money, Currency
from messenger import g_settings
from helpers import dependency
from helpers.time_utils import HOURS_IN_DAY
from items.customizations import isEditedStyle
from skeletons.gui.game_control import IVehicleComparisonBasket, IDetachmentController
_logger = logging.getLogger(__name__)

class DormitoryBuyer(Processor):

    def __init__(self, count=1):
        super(DormitoryBuyer, self).__init__()
        items = self.itemsCache.items
        self._roomsCount = items.shop.getDormitoryRoomsCount
        price = items.shop.getDormitoryPrice
        self._currency = price[DormitorySections.CURRENCY]
        self._cost = price[DormitorySections.PRICE] * count
        self._money = Money.makeFrom(self._currency, self._cost)
        self._count = count
        self.addPlugin(plugins.MoneyValidator(self._money))
        self.addPlugin(plugins.DormitoriesBuyingEnableValidator())

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError(sysMsgKey='buy_dormitory/{}'.format(errStr), defaultSysMsgKey='buy_dormitory/server_error')

    def _successHandler(self, code, ctx=None):
        return makeI18nSuccess(sysMsgKey='buy_dormitory/financial_success', money=formatPrice(self._money), amount=text_styles.stats(str(self._roomsCount * self._count)), block=self._count, type=FIN_TO_SM_TYPE.get(self._currency, SM_TYPE.Information)) if self._cost else makeI18nSuccess(sysMsgKey='buy_dormitory/success', amount=text_styles.stats(str(self._roomsCount * self._count)), block=self._count, type=SM_TYPE.Information)

    def _request(self, callback):
        _logger.debug('Make server request to buy dormitory')
        BigWorld.player().stats.buyDormitory(self._count, lambda code: self._response(code, callback))


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
            component = None
            if outfit.style:
                intCD = makeIntCompactDescrByID('customizationItem', CustomizationType.STYLE, outfit.style.id)
                style = self.itemsCache.items.getItemByCD(intCD)
                if style and style.isProgressive:
                    outfit = c11nService.removeAdditionalProgressionData(outfit=outfit, style=style, vehCD=self.vehicle.descriptor.makeCompactDescr(), season=season)
                    component = outfit.pack()
            if component is None:
                component = outfit.pack()
            if component.styleId and isEditedStyle(component):
                intCD = makeIntCompactDescrByID('customizationItem', CustomizationType.STYLE, component.styleId)
                style = self.itemsCache.items.getItemByCD(intCD)
                baseComponent = style.getOutfit(season, self.vehicle.descriptor.makeCompactDescr())
                component = component.getDiff(baseComponent.pack())
            self.__validateOutfitComponent(component)
            requestData.append((component.makeCompDescr(), season))

        BigWorld.player().shop.buyAndEquipOutfit(self.vehicle.invID, requestData, lambda code: self._response(code, callback))
        return

    def __validateOutfitComponent(self, outfitComponent):
        for itemType in CustomizationType.STYLE_ONLY_RANGE:
            typeName = lower(CustomizationTypeNames[itemType])
            componentsAttrName = '{}s'.format(typeName)
            itemsComponents = getattr(outfitComponent, componentsAttrName, None)
            if itemsComponents:
                _logger.error('StyleOnly items cannot be installed manually: itemType=[%s]; components=[%s].Forbidden components removed.', typeName, itemsComponents)
                itemsComponents = []
            setattr(outfitComponent, componentsAttrName, itemsComponents)

        camouflages = []
        for camoComponent in outfitComponent.camouflages:
            if camoComponent.id != HIDDEN_CAMOUFLAGE_ID:
                camouflages.append(camoComponent)
            _logger.error('Hidden Camouflage cannot be installed manually. %s removed.', camoComponent)

        outfitComponent.camouflages = camouflages
        return


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
         'money': formatPrice(self._getTotalPrice())}

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


class EpicPrestigeTrigger(Processor):

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError('epicBattles/prestigeTrigger/error')

    def _request(self, callback):
        _logger.debug('Make server request to trigger prestige')
        BigWorld.player().epicMetaGame.triggerEpicMetaGamePrestige(lambda code, errStr: self._response(code, callback, errStr=errStr))


class EpicPrestigePointsExchange(Processor):

    def _request(self, callback):
        _logger.debug('Make server request to exchange prestige points')
        BigWorld.player().epicMetaGame.exchangePrestigePoints(lambda code, errStr: self._response(code, callback, errStr=errStr))


class EpicRewardsClaimer(Processor):

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError('epicBattles/claimReward/error')

    def _request(self, callback):
        _logger.debug('Make server request to claim final reward')
        BigWorld.player().epicMetaGame.claimEpicMetaGameMaxPrestigeReward(lambda code, errStr: self._response(code, callback, errStr=errStr))


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

    def __init__(self, selectedMaps=None):
        super(_MapsBlackListSelector, self).__init__()
        if selectedMaps is None:
            selectedMaps = ()
        self.__selectedMaps = selectedMaps
        return

    def _getMessagePrefix(self):
        pass

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError(sysMsgKey='{}/server_error/{}'.format(self._getMessagePrefix(), errStr), defaultSysMsgKey='{}/server_error'.format(self._getMessagePrefix()))

    def _successHandler(self, code, ctx=None):
        return makeI18nSuccess(sysMsgKey='{}/success'.format(self._getMessagePrefix()))

    def _request(self, callback):
        _logger.debug('Make server request to select black maps %r', self.__selectedMaps)
        BigWorld.player().stats.setMapsBlackList(self.__selectedMaps, lambda code, errStr, ext: self._response(code, callback, ctx=ext, errStr=errStr))

    def _getLayout(self):
        return [ mapID for mapID, _ in self.itemsCache.items.stats.getMapsBlackList() ]


class MapsBlackListSetter(_MapsBlackListSelector):

    def __init__(self, selectedMapID):
        layout = self._getLayout()
        wasInserted = False
        for idx, mapID in enumerate(layout):
            if mapID == EMPTY_GEOMETRY_ID:
                layout[idx] = selectedMapID
                wasInserted = True
                break

        if not wasInserted:
            layout.append(selectedMapID)
        super(MapsBlackListSetter, self).__init__(layout)


class MapsBlackListRemover(_MapsBlackListSelector):

    def __init__(self, removeMapID):
        layout = self._getLayout()
        if removeMapID in layout:
            layout[layout.index(removeMapID)] = EMPTY_GEOMETRY_ID
        else:
            _logger.error('Cannot remove mapID %d from layout %r', removeMapID, layout)
        super(MapsBlackListRemover, self).__init__(layout)


class MapsBlackListChanger(_MapsBlackListSelector):

    def __init__(self, srcMapID, destMapID):
        layout = self._getLayout()
        if srcMapID in layout:
            layout[layout.index(srcMapID)] = destMapID
        else:
            _logger.error('Cannot change srcMapID %d from layout %r', srcMapID, layout)
        super(MapsBlackListChanger, self).__init__(layout)


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


class UseCrewBookProcessor(Processor):

    def __init__(self, crewBookCD, detInvID, bookCount):
        super(UseCrewBookProcessor, self).__init__()
        self.__crewBookCD = crewBookCD
        self.__detInvID = detInvID
        self.__bookCount = bookCount

    def _successHandler(self, code, ctx=None):
        itemsCache = dependency.instance(IItemsCache)
        return makeI18nSuccess(sysMsgKey='crewBooksNotification/bookUsed', name=itemsCache.items.getItemByCD(self.__crewBookCD).userName)

    def _request(self, callback):
        BigWorld.player().inventory.useCrewBook(self.__crewBookCD, self.__detInvID, self.__bookCount, lambda code: self._response(code, callback))


class LearnPerksProcessor(Processor):

    def __init__(self, detachmentID, perks, dropMode, useRecertificationForm, isUIEditMode=False):
        super(LearnPerksProcessor, self).__init__(plugins=[plugins.DetachmentValidator(detachmentID)])
        self._detachmentID = detachmentID
        self._perks = perks
        self._isUIEditMode = isUIEditMode
        self._useRecertificationForm = useRecertificationForm
        detachment = self.detachmentCache.getDetachment(self._detachmentID)
        self._perksCount = self._perksUltimateCount = 0
        self._isPerksRepartition = False
        self._dropMode = dropMode
        self._oldBuildLevel = 0
        self._price = Money()
        if detachment:
            self._price = self._getPrice(detachment)
            self._isPerksRepartition = isPerksRepartition(detachment.build, self._perks)
            self._oldBuildLevel = detachment.getDescriptor().getBuildLevel()
            if self._dropMode == ChangePerksMode.ADD_PERKS or self._dropMode == ChangePerksMode.DROP_PARTIAL:
                self._perksCount, self._perksUltimateCount = self._calculatePerks(detachment, self._perks)
            else:
                self._perksCount, self._perksUltimateCount = self._calculatePerks(detachment, detachment.build)
            if detachment.isInTank:
                vehicle = self.itemsCache.items.getVehicle(detachment.vehInvID)
                self.addPlugin(plugins.VehicleLockValidator(vehicle))

    def _errorHandler(self, code, errStr='', ctx=None):
        sysMsgKey = self._getSysMsgBase() + '/'
        errStr += self._getPerkMsgKey(self._perksCount, self._perksUltimateCount, error=True)
        sysMsgKey += errStr
        return makeI18nError(sysMsgKey=sysMsgKey, defaultSysMsgKey='detachment_learn_perks/server_error')

    def _successHandler(self, code, ctx=None):
        detachment = self.detachmentCache.getDetachment(self._detachmentID)
        sysMsgKey = self._getSysMsgBase()
        if self._dropMode == ChangePerksMode.ADD_PERKS or self._dropMode == ChangePerksMode.DROP_PARTIAL and not self._isPerksRepartition:
            smType = SM_TYPE.DetachmentLearnPerks
            sysMsgKey += self._getPerkMsgKey(self._perksCount, self._perksUltimateCount)
            makeMsg = partial(makeI18nSuccess, number=self._perksCount)
        else:
            if self._dropMode == ChangePerksMode.DROP_PARTIAL:
                newBuildLevel = detachment.getDescriptor().getBuildLevel()
                pointsChanges = self._oldBuildLevel - newBuildLevel
                if pointsChanges > 0:
                    sysMsgKey += '/pointsReturn'
                elif pointsChanges < 0:
                    sysMsgKey += '/noPointsReturn'
                points = text_styles.perkYellow(str(detachment.level - newBuildLevel)) if pointsChanges > 0 else abs(pointsChanges)
                makeMsg = partial(makeI18nSuccess, number=points)
            else:
                makeMsg = partial(makeI18nSuccess, number=text_styles.perkYellow(str(detachment.level)))
            if self._useRecertificationForm:
                smType = SM_TYPE.DetachmentLearnPerks
                sysMsgKey += '/useRecertificationForm'
            elif any(self._price.toDict().itervalues()):
                smType = FIN_TO_SM_TYPE.get(self._price.getCurrency(), SM_TYPE.DetachmentLearnPerks)
                makeMsg = partial(makeMsg, price=formatPrice(self._price, ignoreZeros=True))
            else:
                smType = SM_TYPE.DetachmentLearnPerks
                sysMsgKey += '/discount'
            sysMsgKey += self._getPerkMsgKey(self._perksCount, self._perksUltimateCount)
        return makeMsg(sysMsgKey=sysMsgKey, type=smType)

    def _request(self, callback):
        BigWorld.player().inventory.learnPerks(self._detachmentID, self._perks, self._dropMode, self._useRecertificationForm, lambda code: self._response(code, callback))

    def _getSysMsgBase(self):
        if not self._isUIEditMode:
            sysMsgKey = 'detachment_learn_perks' if self._dropMode == ChangePerksMode.ADD_PERKS else 'detachment_drop_perks'
        elif self._dropMode == ChangePerksMode.ADD_PERKS:
            sysMsgKey = 'detachment_changes_perks'
        elif self._dropMode == ChangePerksMode.DROP_PARTIAL:
            sysMsgKey = 'detachment_drop_partial_perks'
        else:
            sysMsgKey = 'detachment_drop_perks'
        return sysMsgKey

    def _getPerkMsgKey(self, perksCount, perksUltimateCount, error=False):
        key = ''
        if perksCount > 0:
            key += '/perks'
        if perksUltimateCount > 0:
            key += '/ultimate_perks'
        key += '/server_error' if error else '/success'
        return key

    def _calculatePerks(self, detachment, perks):
        perksCount = perksUltimateCount = 0
        if not detachment:
            return (perksCount, perksUltimateCount)
        detDescr = detachment.getDescriptor()
        perksMatrix = detDescr.getPerksMatrix()
        if not perksMatrix:
            return (perksCount, perksUltimateCount)
        perksMat = perksMatrix.perks
        for perkID, count in perks.iteritems():
            perk = perksMat.get(perkID)
            if not perk:
                continue
            if perk.ultimate:
                perksUltimateCount += abs(count)
            perksCount += abs(count)

        return (perksCount, perksUltimateCount)

    def _getPrice(self, detachment):
        _, price, _ = getDropSkillsPrice(detachment.invID)
        return price


class RemoveInstructorFromDetachmentProcessor(Processor):
    __detachmentController = dependency.descriptor(IDetachmentController)

    def __init__(self, detachmentID, slotID, optionID):
        super(RemoveInstructorFromDetachmentProcessor, self).__init__(plugins=[plugins.InstructorSlotsBreakerValidator(), plugins.DetachmentValidator(detachmentID), plugins.InstructorSlotValidator(detachmentID, slotID)])
        self.__detachment = self.detachmentCache.getDetachment(detachmentID)
        self.__slotID = slotID
        self.__optionID = optionID
        instructorsIDs = self.__detachment.getInstructorsIDs()
        instructorInvID = instructorsIDs[slotID]
        self.__instructor = self.detachmentCache.getInstructor(instructorInvID)
        capacity = self.__instructor.descriptor.getSlotsCount()
        self.__animationSlots = [ slotID for slotID in xrange(slotID, slotID + capacity) ]
        priceGroups = self.itemsCache.items.shop.detachmentPriceGroups
        priceGroup = priceGroups[self.__detachment.progression.priceGroup]
        excludeOption = priceGroup[DetachmentOperations.REMOVE_INSTRUCTOR_FROM_SLOT][ExcludeInstructorOption.PAID]
        self.__price = Money(**excludeOption)
        self.__exclusionDays = settings_globals.g_instructorSettingsProvider.exclusionHours / HOURS_IN_DAY

    def _successHandler(self, code, ctx=None):
        self.__detachmentController.renewSlotsAnimation(self.__detachment.invID, DetachmentSlotType.INSTRUCTORS, self.__animationSlots)
        return self._getPaidOperationMessage() if self.__optionID == ExcludeInstructorOption.PAID else self._getFreeOperationMessage()

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError(sysMsgKey='detachment_remove_instructor/{}'.format(errStr), defaultSysMsgKey='detachment_remove_instructor/server_error')

    def _request(self, callback):
        BigWorld.player().inventory.removeInstructorFromDetachment(self.__detachment.invID, self.__slotID, self.__optionID, lambda code: self._response(code, callback))

    def _getFreeOperationMessage(self):
        return makeI18nSuccess(sysMsgKey=self._getSysMsgBase(), instructorName=text_styles.stats(self.__instructor.getFullName()), detName=text_styles.stats(self.__detachment.cmdrFullName), exclusionDays=text_styles.highlightText(self.__exclusionDays))

    def _getPaidOperationMessage(self):
        return makeI18nSuccess(sysMsgKey=self._getSysMsgBase(), instructorName=text_styles.stats(self.__instructor.getFullName()), detName=text_styles.stats(self.__detachment.cmdrFullName), price=formatPrice(self.__price, ignoreZeros=True), type=FIN_TO_SM_TYPE.get(self.__price.getCurrency(byWeight=True)))

    def _getSysMsgBase(self):
        prefix = 'detachment_remove_instructor'
        msgType = 'paid' if self.__optionID == ExcludeInstructorOption.PAID else 'free'
        opResult = 'success'
        msg = '{}/{}/{}'.format(prefix, msgType, opResult)
        return msg


class RecoverInstructorProcessor(Processor):

    def __init__(self, instructorID):
        super(RecoverInstructorProcessor, self).__init__(plugins=[plugins.InstructorValidator(instructorID)])
        self.__instructor = self.detachmentCache.getInstructor(instructorID)
        self.__price = self.itemsCache.items.shop.recoverInstructorCost

    def _successHandler(self, code, ctx=None):
        return makeI18nSuccess(sysMsgKey='detachment_recover_instructor/success', price=formatPrice(self.__price, ignoreZeros=True), instructorName=text_styles.stats(self.__instructor.getFullName()), type=FIN_TO_SM_TYPE.get(self.__price.getCurrency(byWeight=True)))

    def _request(self, callback):
        BigWorld.player().inventory.recoverInstructor(self.__instructor.invID, lambda code: self._response(code, callback))


class AddInstructorToSlotProcessor(Processor):
    __detachmentController = dependency.descriptor(IDetachmentController)

    def __init__(self, detachmentID, instructorID, slotID, isActive=False, isAnim=True):
        super(AddInstructorToSlotProcessor, self).__init__(plugins=[plugins.InstructorSlotsBreakerValidator(),
         plugins.InstructorValidator(instructorID),
         plugins.DetachmentValidator(detachmentID),
         plugins.InstructorSlotValidator(detachmentID, slotID)])
        self.__detachment = self.detachmentCache.getDetachment(detachmentID)
        self.__instructor = self.detachmentCache.getInstructor(instructorID)
        self.__slotID = slotID
        self.__isActive = isActive
        self.__isAnim = isAnim

    def _successHandler(self, code, ctx=None):
        if self.__isAnim:
            capacity = self.__instructor.descriptor.getSlotsCount()
            slotIDStart = ctx.get('slotID', 0)
            self.__detachmentController.renewSlotsAnimation(self.__detachment.invID, DetachmentSlotType.INSTRUCTORS, [ slotID for slotID in xrange(slotIDStart, slotIDStart + capacity) ])
        return makeI18nSuccess(sysMsgKey='detachment_add_instructor/success', instructorName=text_styles.stats(self.__instructor.getFullName()), detName=text_styles.stats(self.__detachment.cmdrFullName))

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError(sysMsgKey='detachment_add_instructor/{}'.format(errStr), defaultSysMsgKey='detachment_add_instructor/server_error')

    def _request(self, callback):
        BigWorld.player().inventory.addInstructorToSlot(self.__detachment.invID, self.__instructor.invID, self.__slotID, self.__isActive, lambda code, ext=None: self._response(code, callback, ctx=ext))
        return


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


class BuyBattlePass(Processor):

    def __init__(self, seasonID, chapter):
        super(BuyBattlePass, self).__init__()
        self.__seasonID = seasonID
        self.__chapter = chapter

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError(sysMsgKey='battlePass_buy/server_error')

    def _successHandler(self, code, ctx=None):
        itemsCache = dependency.instance(IItemsCache)
        return makeSuccess(msgType=SM_TYPE.BattlePassBuy, userMsg='', auxData={'header': backport.text(R.strings.messenger.serviceChannelMessages.battlePassReward.header.buyBP()),
         'description': backport.text(R.strings.messenger.serviceChannelMessages.battlePassReward.buyWithoutRewards.text(), chapter=backport.text(R.strings.battle_pass.chapter.name.num(self.__chapter)())),
         'additionalText': self.__makeGoldString(itemsCache.items.shop.getBattlePassCost().get(Currency.GOLD, 0))})

    @staticmethod
    def __makeGoldString(gold):
        if not gold:
            return ''
        formatter = getBWFormatter(Currency.GOLD)
        return g_settings.htmlTemplates.format('battlePassGold', {Currency.GOLD: formatter(gold)})

    def _request(self, callback):
        _logger.debug('Make server request to buy battle pass %d for chapter %d', self.__seasonID, self.__chapter)
        BigWorld.player().shop.buyBattlePass(self.__seasonID, self.__chapter, lambda resID, code, errStr: self._response(code, callback, errStr))


class BuyBattlePassLevels(Processor):

    def __init__(self, seasonID, levels):
        super(BuyBattlePassLevels, self).__init__()
        self.__seasonID = seasonID
        self.__levels = levels

    def _errorHandler(self, code, errStr='', ctx=None):
        return makeI18nError(sysMsgKey='battlePassLevels_buy/server_error')

    def _request(self, callback):
        _logger.debug('Make server request to buy battle pass levels: %d season %d', self.__levels, self.__seasonID)
        BigWorld.player().shop.buyBattlePassLevels(self.__seasonID, self.__levels, lambda resID, code, errStr: self._response(code, callback, errStr))
