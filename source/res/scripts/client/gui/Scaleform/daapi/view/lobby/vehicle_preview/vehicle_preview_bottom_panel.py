# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/vehicle_preview/vehicle_preview_bottom_panel.py
import logging
import time
from collections import namedtuple
import BigWorld
from CurrentVehicle import g_currentPreviewVehicle
from adisp import adisp_async, adisp_process
from collector_vehicle import CollectorVehicleConsts
from constants import GameSeasonType, RentType
from gui import DialogsInterface
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.dialogs import DIALOG_BUTTON_ID, I18nConfirmDialogMeta
from gui.Scaleform.daapi.view.dialogs.ExchangeDialogMeta import ExchangeCreditsWebProductMeta
from gui.Scaleform.daapi.view.lobby.techtree.techtree_dp import g_techTreeDP
from gui.Scaleform.daapi.view.lobby.vehicle_preview.hero_tank_preview_constants import getHeroTankPreviewParams
from gui.Scaleform.daapi.view.lobby.vehicle_preview.vehicle_preview_dp import DefaultVehPreviewDataProvider
from gui.Scaleform.daapi.view.meta.VehiclePreviewBottomPanelMeta import VehiclePreviewBottomPanelMeta
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.Scaleform.locale.VEHICLE_PREVIEW import VEHICLE_PREVIEW
from gui.game_control import CalendarInvokeOrigin
from gui.game_control.links import URLMacros
from gui.game_control.wallet import WalletController
from gui.hangar_cameras.hangar_camera_common import CameraRelatedEvents
from gui.impl import backport
from gui.impl.gen import R
from gui.referral_program import showGetVehiclePage
from gui.shared import event_dispatcher, events, g_eventBus
from gui.shared.event_dispatcher import showVehicleRentDialog
from gui.shared.events import HasCtxEvent
from gui.shared.formatters import chooseItemPriceVO, formatPrice, getItemPricesVO, getItemUnlockPricesVO, icons, text_styles, time_formatters
from gui.shared.gui_items.gui_item_economics import ActualPrice, ITEM_PRICE_EMPTY, ItemPrice, getPriceTypeAndValue
from gui.shared.gui_items.items_actions import factory
from gui.shared.money import Currency, MONEY_UNDEFINED, Money
from gui.shared.tooltips.formatters import getActionPriceData
from gui.shared.utils import vehicle_collector_helper
from gui.shared.utils.functions import makeTooltip
from gui.shop import canBuyGoldForVehicleThroughWeb, showBuyGoldForBundle, showBuyProductOverlay
from helpers import dependency, int2roman, time_utils
from helpers.i18n import makeString as _ms
from items_kit_helper import BOX_TYPE, OFFER_CHANGED_EVENT, getActiveOffer, lookupItem, mayObtainForMoney, mayObtainWithMoneyExchange, showItemTooltip
from shared_utils import findFirst
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.game_control import ICalendarController, IExternalLinksController, IHeroTankController, IMarathonEventsController, IRestoreController, ITradeInController, IVehicleComparisonBasket
from skeletons.gui.goodies import IGoodiesCache
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from uilogging.shop.loggers import ShopBundleVehiclePreviewMetricsLogger
from web.web_client_api.common import ItemPackEntry, ItemPackTypeGroup
_ButtonState = namedtuple('_ButtonState', ('enabled', 'itemPrice', 'label', 'icon', 'iconAlign', 'isAction', 'actionTooltip', 'tooltip', 'title', 'isMoneyEnough', 'isUnlock', 'isPrevItemsUnlock', 'customOffer', 'isShowSpecial'))
_logger = logging.getLogger(__name__)

def _buildBuyButtonTooltip(key):
    return makeTooltip(backport.text(R.strings.tooltips.vehiclePreview.buyButton.dyn(key).header()), backport.text(R.strings.tooltips.vehiclePreview.buyButton.dyn(key).body()))


def _buildRestoreButtonTooltip(timeLeft):
    timeLeftStr = time_formatters.getTillTimeByResource(timeLeft, R.strings.menu.Time.timeLeftShort, removeLeadingZeros=True)
    return makeTooltip(backport.text(R.strings.tooltips.vehiclePreview.buyButton.restoreRequested.header()), backport.text(R.strings.tooltips.vehiclePreview.buyButton.restoreRequested.body(), timeLeft=timeLeftStr))


def _getCollectibleWarningStr(mainString, vehicle):
    return _ms(mainString, level=int2roman(vehicle.level), nation=backport.text(R.strings.nations.dyn(vehicle.nationName).genetiveCase()))


class _CouponData(object):
    __slots__ = ('__item', '__selected', '__discount')

    def __init__(self, item=None, selected=False):
        self.__item = item
        self.__selected = selected
        self.__discount = Money(gold=self.__item.count)

    @property
    def item(self):
        return self.__item

    @item.setter
    def item(self, value):
        self.__item = value

    @property
    def selected(self):
        return self.__selected

    @selected.setter
    def selected(self, value):
        self.__selected = value

    @property
    def discount(self):
        return self.__discount


class VehiclePreviewBottomPanel(VehiclePreviewBottomPanelMeta):
    appLoader = dependency.descriptor(IAppLoader)
    _itemsCache = dependency.descriptor(IItemsCache)
    _goodiesCache = dependency.descriptor(IGoodiesCache)
    _comparisonBasket = dependency.descriptor(IVehicleComparisonBasket)
    _tradeIn = dependency.descriptor(ITradeInController)
    _restores = dependency.descriptor(IRestoreController)
    _heroTanks = dependency.descriptor(IHeroTankController)
    _lobbyContext = dependency.descriptor(ILobbyContext)
    _marathonsCtrl = dependency.descriptor(IMarathonEventsController)
    __calendarController = dependency.descriptor(ICalendarController)
    __linksCtrl = dependency.descriptor(IExternalLinksController)

    def __init__(self, skipConfirm=False):
        super(VehiclePreviewBottomPanel, self).__init__()
        heroTankCD = self._heroTanks.getCurrentTankCD()
        self._vehicleCD = g_currentPreviewVehicle.item.intCD
        self._vehicleLevel = g_currentPreviewVehicle.item.level
        self._actionType = None
        self._skipConfirm = skipConfirm
        self._disableBuyButton = False
        self._marathonEvent = None
        self.__previewDP = DefaultVehPreviewDataProvider()
        self.__isHeroTank = heroTankCD and heroTankCD == self._vehicleCD
        self.__price = None
        self.__title = None
        self.__description = None
        self.__items = None
        self.__offers = None
        self.__currentOffer = None
        self.__styleByGroup = {}
        self.__vehicleByGroup = {}
        self.__endTime = None
        self.__oldPrice = MONEY_UNDEFINED
        self.__buyParams = None
        self.__backAlias = None
        self.__backCallback = None
        self.__timeCallbackID = None
        self.__timeLeftIcon = icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_TIME_ICON, 16, 16)
        self.__buttonLabel = None
        self.__cachedVehiclesVOs = None
        self.__cachedItemsVOs = None
        self.__cachedCollapsedItemsVOs = None
        self.__couponInfo = None
        self.__hasSSEDiscount = False
        self.__uniqueVehicleTitle = None
        self.__urlMacros = URLMacros()
        self.__bundlePreviewMetricsLogger = None
        g_techTreeDP.load()
        return

    def onBuyOrResearchClick(self):
        vehicle = g_currentPreviewVehicle.item
        shopPackage = self.__items is not None and self.__couponInfo is None
        frontlineCouponPackage = self.__couponInfo is not None and self.__couponInfo.selected
        if self._marathonEvent:
            self.__purchaseMarathonPackage()
            return
        elif shopPackage or frontlineCouponPackage:
            self.__purchasePackage()
            return
        elif self.__offers is not None:
            self.__purchaseOffer()
            return
        elif self.__isHeroTank:
            self.__purchaseHeroTank()
            return
        elif canBuyGoldForVehicleThroughWeb(vehicle):
            self.__purchaseSingleVehicle(vehicle)
            return
        else:
            self.__research()
            return

    def onCouponSelected(self, isActive):
        if self.__couponInfo:
            self.__couponInfo.selected = isActive
            if isActive:
                self.__title = backport.text(R.strings.vehicle_preview.buyingPanel.frontlinePack.titleLabel.active())
            elif self.__hasSSEDiscount:
                self.__title = backport.text(R.strings.vehicle_preview.buyingPanel.frontlinePack.titleLabel.inactive_add_discount())
            else:
                self.__title = backport.text(R.strings.vehicle_preview.buyingPanel.frontlinePack.titleLabel.inactive())
            self.__update()

    def setMarathonEvent(self, prefix):
        self._marathonEvent = self._marathonsCtrl.getMarathon(prefix)

    def setTimerData(self, endTime):
        if self.__couponInfo is not None:
            return
        else:
            if endTime is not None:
                self.__endTime = endTime
                self.__onLeftTimeUpdated()
            self.__updateBtnState()
            return

    def setInfoTooltip(self):
        tooltip = self._marathonEvent.getVehiclePreviewTitleTooltip()
        self.as_setSetTitleTooltipS(tooltip)

    def setBuyParams(self, buyParams):
        self.__buyParams = buyParams

    def setBundlePreviewMetricsLogger(self, bundlePreviewMetricsLogger):
        if isinstance(bundlePreviewMetricsLogger, ShopBundleVehiclePreviewMetricsLogger):
            self.__bundlePreviewMetricsLogger = bundlePreviewMetricsLogger
        else:
            _logger.warning('[SHOPUILOG] expected instance of class ShopBundleVehiclePreviewMetricsLogger.')

    def setBackAlias(self, backAlias):
        self.__backAlias = backAlias

    def setBackCallback(self, backCallback):
        self.__backCallback = backCallback

    def setIsHeroTank(self, isHero):
        self.__isHeroTank = isHero

    def setPanelTextData(self, title='', buttonLabel=None, uniqueVehicleTitle=None):
        self.__uniqueVehicleTitle = uniqueVehicleTitle
        self.__buttonLabel = buttonLabel
        self.__title = title

    def setPackItems(self, packItems, price, oldPrice):
        self.__price = price
        self.__hasSSEDiscount = oldPrice != MONEY_UNDEFINED
        self.__oldPrice = oldPrice
        self.__items = packItems
        self.__styleByGroup.clear()
        self.__vehicleByGroup.clear()
        vehiclesItems, items = self.__previewDP.separateItemsPack(self.__items)
        for item in items:
            if item.type in ItemPackTypeGroup.STYLE and item.groupID not in self.__styleByGroup:
                self.__styleByGroup[item.groupID] = item.id
            if item.type in ItemPackTypeGroup.DISCOUNT:
                self.__title = backport.text(R.strings.vehicle_preview.buyingPanel.frontlinePack.titleLabel.active())
                self.__couponInfo = _CouponData(item=item, selected=True)
                self.as_setCouponS(self.__previewDP.packCouponData(self.__items, self.__price.get(Currency.GOLD)))
                if not self.__oldPrice:
                    self.__oldPrice = self.__price

        for vehicleItem in vehiclesItems:
            self.__vehicleByGroup[vehicleItem.id] = vehicleItem.groupID

        vehiclesVOs, itemsVOs, collapseItemsVOs = self.__previewDP.getItemsPackData(g_currentPreviewVehicle.item, items, vehiclesItems)
        self.__cachedVehiclesVOs = vehiclesVOs
        self.__cachedItemsVOs = itemsVOs
        self.__cachedCollapsedItemsVOs = collapseItemsVOs
        self.__update()

    def onCarouselVehicleSelected(self, intCD):
        self._vehicleCD = intCD
        g_currentPreviewVehicle.selectVehicle(intCD)

    def setOffers(self, offers, title, description):
        self.__offers = offers
        self.__title = title
        self.__description = description
        selectedID = getActiveOffer(self.__offers).id
        offersData = self.__previewDP.getOffersData(self.__offers, selectedID) if len(self.__offers) > 1 else []
        self.as_setOffersDataS(offersData)
        self.onOfferSelected(selectedID)

    def onOfferSelected(self, offerID):
        self.__currentOffer = findFirst(lambda o: o.id == offerID, self.__offers)
        if self.__currentOffer:
            vehicle = g_currentPreviewVehicle.item
            crew = self.__currentOffer.crew
            g_eventBus.handleEvent(HasCtxEvent(ctx={'vehicleItems': [ItemPackEntry(id=vehicle.intCD, groupID=crew.groupID)],
             'crewItems': [crew],
             'offer': self.__currentOffer}, eventType=OFFER_CHANGED_EVENT))
            self.__buyParams = self.__currentOffer.buyParams
            self.__price = self.__currentOffer.buyPrice
            self.as_setBuyDataS(self.__previewDP.getOffersBuyingPanelData(self.__getBtnData(), self.__uniqueVehicleTitle))
            description = self.__description or self.__getCurrentOfferDescription() or {}
            self.as_setSetTitleTooltipS(makeTooltip(**description))

    def showTooltip(self, intCD, itemType):
        toolTipMgr = self.appLoader.getApp().getToolTipMgr()
        if itemType == BOX_TYPE:
            toolTipMgr.onCreateComplexTooltip(makeTooltip(TOOLTIPS.VEHICLEPREVIEW_BOXTOOLTIP_HEADER, TOOLTIPS.VEHICLEPREVIEW_BOXTOOLTIP_BODY), 'INFO')
            return
        try:
            try:
                itemId = int(intCD)
            except ValueError:
                itemId = intCD

            rawItem = [ item for item in self.__items if item.id == itemId and item.type == itemType ][0]
            item = lookupItem(rawItem, self._itemsCache, self._goodiesCache)
            showItemTooltip(toolTipMgr, rawItem, item)
        except IndexError:
            return

    def updateData(self, useCompactData):
        self.__update(collapseItems=False)

    def _populate(self):
        super(VehiclePreviewBottomPanel, self)._populate()
        g_clientUpdateManager.addMoneyCallback(self.__updateBtnState)
        g_clientUpdateManager.addCallbacks({'stats.freeXP': self.__updateBtnState,
         'inventory': self.__updateBtnState,
         'serverSettings.blueprints_config': self.__onBlueprintsModeChanged})
        g_currentPreviewVehicle.onVehicleUnlocked += self.__updateBtnState
        g_currentPreviewVehicle.onChanged += self.__onVehicleChanged
        self._heroTanks.onUpdated += self.__updateBtnState
        self._restores.onRestoreChangeNotify += self.__onRestoreChanged
        self._lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChanged
        self.addListener(CameraRelatedEvents.VEHICLE_LOADING, self.__onVehicleLoading)

    def _dispose(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        g_currentPreviewVehicle.onVehicleUnlocked -= self.__updateBtnState
        g_currentPreviewVehicle.onChanged -= self.__onVehicleChanged
        self._heroTanks.onUpdated -= self.__updateBtnState
        self._restores.onRestoreChangeNotify -= self.__onRestoreChanged
        self._lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChanged
        self.removeListener(CameraRelatedEvents.VEHICLE_LOADING, self.__onVehicleLoading)
        self.__stopTimer()
        self.__styleByGroup.clear()
        self.__vehicleByGroup.clear()
        self.__urlMacros.clear()
        self.__urlMacros = None
        super(VehiclePreviewBottomPanel, self)._dispose()
        return

    def __update(self, collapseItems=False):
        if self.__cachedVehiclesVOs:
            g_currentPreviewVehicle.selectVehicle(self.__cachedVehiclesVOs[0]['intCD'])
            self.as_setSetVehiclesDataS({'vehicles': self.__cachedVehiclesVOs})
        if self.__couponInfo:
            self.__updateEnabledState(self.__cachedCollapsedItemsVOs, self.__couponInfo.selected)
            self.__updateEnabledState(self.__cachedItemsVOs, self.__couponInfo.selected)
        if collapseItems and self.__cachedCollapsedItemsVOs:
            self.as_setSetItemsDataS({'items': self.__cachedCollapsedItemsVOs})
        elif self.__cachedItemsVOs:
            self.as_setSetItemsDataS({'items': self.__cachedItemsVOs})
        self.__updateBtnState()

    def __getOfferByID(self, offerID):
        return findFirst(lambda o: o.buy_params['transactionID'] == offerID, self.__offers)

    def __isReferralWindow(self):
        return self.__backAlias == VIEW_ALIAS.REFERRAL_PROGRAM_WINDOW

    def __isStoreWindow(self):
        return self.__backAlias == VIEW_ALIAS.LOBBY_STORE

    def __getConfirmationDialogKey(self):
        key = 'buyConfirmation'
        if self.__isReferralWindow():
            key = 'referralReward'
        return key

    def __buyRequestConfirmation(self, key='buyConfirmation'):
        product = self.__title if self.__couponInfo is None else g_currentPreviewVehicle.item.shortUserName
        return DialogsInterface.showDialog(meta=I18nConfirmDialogMeta(key=key, messageCtx={'product': product,
         'price': formatPrice(self.__getPackPrice(), reverse=True, useIcon=True)}, focusedID=DIALOG_BUTTON_ID.SUBMIT))

    def __onVehicleLoading(self, ctxEvent):
        vehicle = g_currentPreviewVehicle.item
        if vehicle is None:
            return
        else:
            groupID = self.__vehicleByGroup.get(vehicle.intCD)
            if not ctxEvent.ctx.get('started') and groupID in self.__styleByGroup:
                customizationStyle = self.__styleByGroup[groupID]
                style = self._itemsCache.items.getItemByCD(customizationStyle)
                if style is not None and not style.isRentable:
                    g_currentPreviewVehicle.previewStyle(style)
            return

    @adisp_process
    def __updateBtnState(self, *_):
        item = g_currentPreviewVehicle.item
        if item is None:
            return
        else:
            btnData = self.__getBtnData()
            self._actionType = self.__previewDP.getBuyType(item)
            if self.__items is not None:
                buyingPanelData = self.__previewDP.getItemPackBuyingPanelData(btnData, self.__items, self.__couponInfo.selected if self.__couponInfo else False, self.__price.get(Currency.GOLD), self.__uniqueVehicleTitle)
            elif self.__offers:
                buyingPanelData = self.__previewDP.getOffersBuyingPanelData(btnData, self.__uniqueVehicleTitle)
            else:
                buyingPanelData = self.__previewDP.getBuyingPanelData(item, btnData, self.__isHeroTank, uniqueVehicleTitle=self.__uniqueVehicleTitle)
            buyingPanelData.update({'isReferralEnabled': self.__isReferralWindow()})
            hasExternalLink = yield self.__hasExternalLink()
            if hasExternalLink:
                btnIcon = backport.image(R.images.gui.maps.icons.library.buyInWeb())
                buyingPanelData.update({'buyButtonIcon': btnIcon,
                 'buyButtonIconAlign': 'right',
                 'isBuyingAvailable': True})
            self.as_setBuyDataS(buyingPanelData)
            return

    def __onVehicleChanged(self, *_):
        if g_currentPreviewVehicle.isPresent():
            self._vehicleCD = g_currentPreviewVehicle.item.intCD
            if not self.__price:
                self.__updateBtnState()

    def __onRestoreChanged(self, vehicles):
        if g_currentPreviewVehicle.isPresent():
            if self._vehicleCD in vehicles:
                self.__updateBtnState()

    def __onServerSettingsChanged(self, diff):
        if self._lobbyContext.getServerSettings().isShopDataChangedInDiff(diff, 'isEnabled') or CollectorVehicleConsts.CONFIG_NAME in diff:
            self.__updateBtnState()

    def __onBlueprintsModeChanged(self, _):
        self.__updateBtnState()

    def __getBtnData(self):
        if self.__price is not None:
            return self.__getBtnDataPack()
        else:
            vehicle = g_currentPreviewVehicle.item
            if vehicle.isCollectible:
                return self.__getBtnDataCollectibleVehicle(vehicle)
            return self.__getBtnDataUnlockedVehicle(vehicle) if vehicle.isUnlocked else self.__getBtnDataLockedVehicle(vehicle)

    def __checkBtnEnableByPrice(self, price):
        currency = price.getCurrency()
        return currency == Currency.GOLD or mayObtainForMoney(price) or mayObtainWithMoneyExchange(price)

    def __getBtnDataPack(self):
        buyButtonTooltip = ''
        actionTooltip = None
        customOffer = None
        price = self.__getPackPrice()
        currency = price.getCurrency()
        walletAvailable = self.__walletAvailableForCurrency(currency)
        enabled = False
        if not walletAvailable:
            buyButtonTooltip = _buildBuyButtonTooltip('walletUnavailable')
        elif self._disableBuyButton:
            buyButtonTooltip = _buildBuyButtonTooltip('endTime')
        elif self.__price.isSet(currency):
            enabled = self.__checkBtnEnableByPrice(price)
        else:
            enabled = True
        if self.__currentOffer and self.__currentOffer.bestOffer and self.__currentOffer.eventType:
            actionTooltip = self.__getBestOfferTooltipData(self.__currentOffer.eventType)
        buttonIcon = None
        buttonIconAlign = None
        itemPrices = ItemPrice(price=price, defPrice=self.__oldPrice)
        specialData = getHeroTankPreviewParams() if self.__isHeroTank else None
        if specialData is not None and specialData.buyButtonLabel:
            buttonLabel = backport.text(specialData.buyButtonLabel)
        elif self.__isReferralWindow():
            buttonLabel = backport.text(R.strings.vehicle_preview.buyingPanel.buyBtn.label.obtain())
        elif self._marathonEvent is not None:
            itemPrices = ITEM_PRICE_EMPTY
            buttonData = self._marathonEvent.getPreviewBuyBtnData()
            buttonLabel = buttonData['label']
            enabled = buttonData['enabled']
            buttonIcon = buttonData['btnIcon']
            buttonIconAlign = buttonData['btnIconAlign']
            buyButtonTooltip = buttonData['btnTooltip']
            customOffer = buttonData['customOffer']
        elif self.__items and self.__couponInfo is None:
            buttonLabel = backport.text(R.strings.vehicle_preview.buyingPanel.buyBtn.label.buyItemPack())
        elif self.__offers and self.__currentOffer:
            buttonLabel = backport.text(R.strings.vehicle_preview.buyingPanel.buyBtn.label.rent())
            currentOffer = self.__currentOffer
            price = currentOffer.buyParams['priceAmount']
            priceCode = currentOffer.buyParams['priceCode']
            defPrice = currentOffer.buyPrice.get(priceCode)
            if price != defPrice:
                self.__oldPrice = Money(**{priceCode: defPrice})
                self.__price = Money(**{priceCode: price})
                itemPrices = ItemPrice(price=self.__price, defPrice=self.__oldPrice)
                enabled = self.__checkBtnEnableByPrice(self.__price)
            self.__title = self.__getCurrentOfferTitle()
        else:
            buttonLabel = backport.text(R.strings.vehicle_preview.buyingPanel.buyBtn.label.buy())
        isAction = self.__oldPrice.isDefined() and self.__oldPrice != self.__price or actionTooltip is not None or self.__couponInfo and self.__couponInfo.selected
        return _ButtonState(enabled=enabled, itemPrice=getItemPricesVO(itemPrices), label=buttonLabel if self.__buttonLabel is None else self.__buttonLabel, icon=buttonIcon, iconAlign=buttonIconAlign, isAction=isAction, actionTooltip=actionTooltip, tooltip=buyButtonTooltip, title=self.__title, isMoneyEnough=True, isUnlock=False, isPrevItemsUnlock=True, customOffer=customOffer, isShowSpecial=False)

    def __getPackPrice(self):
        if self.__couponInfo and self.__couponInfo.selected:
            discount = self.__couponInfo.discount
            currency = self.__price.getCurrency()
            if currency == Currency.GOLD:
                discountPrice = self.__price - discount
                return discountPrice.toNonNegative()
        return self.__price

    def __getBtnDataUnlockedVehicle(self, vehicle):
        money = self._itemsCache.items.stats.money
        money = self._tradeIn.addTradeInPriceIfNeeded(vehicle, money)
        buyButtonTooltip = ''
        actionTooltip = getActionPriceData(vehicle)
        exchangeRate = self._itemsCache.items.shop.exchangeRate
        priceType, price = getPriceTypeAndValue(vehicle, money, exchangeRate)
        itemPrice = chooseItemPriceVO(priceType, price)
        currency = price.getCurrency(byWeight=True)
        walletAvailable = self.__walletAvailableForCurrency(currency)
        buttonLabel = self.__getUnlockedVehicleBtnLabel(priceType)
        buttonIcon = None
        buttonIconAlign = None
        isAction = False
        minRentPricePackage = vehicle.getRentPackage()
        if minRentPricePackage:
            isAction = minRentPricePackage['rentPrice'] != minRentPricePackage['defaultRentPrice']
        elif not vehicle.isRestoreAvailable():
            isAction = vehicle.buyPrices.getSum().isActionPrice()
        mayObtain = self.__isHeroTank or walletAvailable and vehicle.mayObtainWithMoneyExchange(money, exchangeRate)
        isBuyingAvailable = not vehicle.isHidden or vehicle.isRentable or vehicle.isRestorePossible()
        isMoneyEnough = True
        restoreInfo = vehicle.restoreInfo
        if not walletAvailable:
            buyButtonTooltip = _buildBuyButtonTooltip('walletUnavailable')
        elif not mayObtain and isBuyingAvailable:
            if currency == Currency.GOLD:
                mayObtain = True
            elif restoreInfo and restoreInfo.isInCooldown():
                buyButtonTooltip = _buildRestoreButtonTooltip(restoreInfo.getRestoreCooldownTimeLeft())
            else:
                buyButtonTooltip = _buildBuyButtonTooltip('notEnoughCredits')
                isMoneyEnough = False
        if self._disableBuyButton or self.__isHeroTank and self._vehicleCD != self._heroTanks.getCurrentTankCD():
            mayObtain = False
            isMoneyEnough = False
        return _ButtonState(enabled=mayObtain, itemPrice=itemPrice, label=buttonLabel, icon=buttonIcon, iconAlign=buttonIconAlign, isAction=isAction, actionTooltip=actionTooltip, tooltip=buyButtonTooltip, title=self.__title, isMoneyEnough=isMoneyEnough, isUnlock=False, isPrevItemsUnlock=True, customOffer=None, isShowSpecial=False)

    def __getBtnDataCollectibleVehicle(self, vehicle):
        isVehicleCollectorEnabled = self._lobbyContext.getServerSettings().isCollectorVehicleEnabled()
        isNationUnlocked = vehicle_collector_helper.isAvailableForPurchase(vehicle)
        resultVO = self.__getBtnDataUnlockedVehicle(vehicle)
        if isVehicleCollectorEnabled and isNationUnlocked:
            return resultVO
        if not isVehicleCollectorEnabled:
            tooltip = TOOLTIPS_CONSTANTS.VEHICLE_COLLECTOR_DISABLED
            isSpecialTooltip = True
        else:
            key = 'notUnlockedNation'
            tooltip = makeTooltip(header=TOOLTIPS.vehiclepreview_buybutton_all(key, 'header'), body=_getCollectibleWarningStr(TOOLTIPS.vehiclepreview_buybutton_all(key, 'body'), vehicle)) if resultVO.isMoneyEnough else resultVO.tooltip
            isSpecialTooltip = False
        resultVO = resultVO._replace(enabled=False, tooltip=tooltip, isShowSpecial=isSpecialTooltip)
        return resultVO

    def __getBtnDataLockedVehicle(self, vehicle):
        stats = self._itemsCache.items.stats
        tooltip = ''
        buttonIcon = None
        buttonIconAlign = None
        nodeCD = vehicle.intCD
        _, isXpEnough = g_techTreeDP.isVehicleAvailableToUnlock(nodeCD, self._vehicleLevel)
        unlocks = self._itemsCache.items.stats.unlocks
        isNext2Unlock, unlockProps = g_techTreeDP.isNext2Unlock(nodeCD, unlocked=set(unlocks), xps=stats.vehiclesXPs, freeXP=stats.freeXP, level=self._vehicleLevel)
        walletAvailable = self.__walletAvailableForCurrency('freeXP')
        isAvailableToUnlock = isXpEnough and isNext2Unlock and walletAvailable
        if not isAvailableToUnlock:
            if not isXpEnough:
                tooltip = _buildBuyButtonTooltip('notEnoughXp')
            elif not walletAvailable:
                tooltip = _buildBuyButtonTooltip('walletUnavailable')
            elif any((bool(cd in unlocks) for cd in g_techTreeDP.getTopLevel(nodeCD))):
                tooltip = _buildBuyButtonTooltip('parentModuleIsLocked')
            else:
                tooltip = _buildBuyButtonTooltip('parentVehicleIsLocked')
        specialData = getHeroTankPreviewParams() if self.__isHeroTank else None
        if specialData is not None and specialData.buyButtonLabel:
            buyLabel = backport.text(specialData.buyButtonLabel)
        else:
            buyLabel = backport.text(R.strings.vehicle_preview.buyingPanel.buyBtn.label.research())
        return _ButtonState(enabled=isAvailableToUnlock, itemPrice=getItemUnlockPricesVO(unlockProps), label=buyLabel, icon=buttonIcon, iconAlign=buttonIconAlign, isAction=unlockProps.discount > 0, actionTooltip=None, tooltip=tooltip, title=self.__title, isMoneyEnough=isXpEnough, isUnlock=True, isPrevItemsUnlock=isNext2Unlock, customOffer=None, isShowSpecial=False)

    @staticmethod
    def __getBestOfferTooltipData(eventType=None):
        return VEHICLE_PREVIEW.BUYINGPANEL_OFFER_RENT_FRONTLINE_TOOLTIP_BEST_OFFER if eventType == 'frontline' else None

    def __getCurrentOfferTitle(self):
        if self.__offers and self.__currentOffer:
            if self.__currentOffer.eventType == 'frontline':
                return _ms(backport.text(R.strings.vehicle_preview.buyingPanel.offer.rent.title.frontline.ordinal()))
        return self.__title

    def __getCurrentOfferDescription(self):
        return {'header': backport.text(R.strings.vehicle_preview.buyingPanel.offer.rent.frontline.description.header()),
         'body': backport.text(R.strings.vehicle_preview.buyingPanel.offer.rent.frontline.description.body.credits())} if self.__currentOffer and self.__currentOffer.eventType == 'frontline' else None

    def __startTimer(self, interval):
        self.__stopTimer()
        self.__timeCallbackID = BigWorld.callback(interval, self.__onLeftTimeUpdated)

    def __stopTimer(self):
        if self.__timeCallbackID is not None:
            BigWorld.cancelCallback(self.__timeCallbackID)
            self.__timeCallbackID = None
        return

    def __setUsageLeftTime(self, leftTime):
        self.as_updateLeftTimeS(formattedTime='{} {}'.format(self.__timeLeftIcon, text_styles.tutorial(time_utils.getTillTimeString(leftTime, MENU.VEHICLEPREVIEW_TIMELEFT))), hasHoursAndMinutes=True)

    def __setShortLeftTime(self, leftTime):
        self.as_updateLeftTimeS(formattedTime='{} {}'.format(self.__timeLeftIcon, text_styles.tutorial(time_utils.getTillTimeString(leftTime, MENU.VEHICLEPREVIEW_TIMELEFTSHORT))), hasHoursAndMinutes=True)

    def __setDateLeftTime(self):
        tm = time_utils.getTimeStructInLocal(self.__endTime)
        monthName = backport.text(R.strings.menu.dateTime.months.num(tm.tm_mon)())
        fmtValues = backport.text(R.strings.menu.dateTime.order(), day=tm.tm_mday, month=monthName, year=tm.tm_year)
        tooltip = makeTooltip(header=backport.text(R.strings.tooltips.vehiclePreview.shopPack.dateTimeTooltip.header()), body=backport.text(R.strings.tooltips.vehiclePreview.shopPack.dateTimeTooltip.body(), namePack=text_styles.neutral(self.__title), date=fmtValues))
        self.as_setSetTitleTooltipS(tooltip)
        self.as_updateLeftTimeS(formattedTime='')

    def __timeOver(self):
        self.__endTime = None
        self._disableBuyButton = True
        formattedTime = '{} {}'.format(icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_ALERTICON2, vSpace=-2), text_styles.alert(MENU.VEHICLEPREVIEW_ENDTIME))
        self.as_updateLeftTimeS(formattedTime=formattedTime)
        self.__updateBtnState()
        return

    def __onLeftTimeUpdated(self):
        leftTime = self.__endTime - time_utils.getServerUTCTime()
        self.__timeCallbackID = None
        if leftTime < 0:
            self.__timeOver()
        elif leftTime > time_utils.ONE_DAY:
            self.__setDateLeftTime()
            self.__startTimer(leftTime - time_utils.ONE_DAY)
        else:
            gmTime = time.gmtime(leftTime)
            if gmTime.tm_min == 0:
                self.__setShortLeftTime(leftTime)
            else:
                self.__setUsageLeftTime(leftTime)
            self.__startTimer(gmTime.tm_sec + 1)
        return

    @adisp_process
    def __purchasePackage(self):
        if self.__items is not None:
            product = self.__title if self.__couponInfo is None else g_currentPreviewVehicle.item.shortUserName
            price = self.__getPackPrice()
            if not mayObtainForMoney(price) and mayObtainWithMoneyExchange(price):
                isOk, _ = yield DialogsInterface.showDialog(ExchangeCreditsWebProductMeta(name=product, count=1, price=price.get(Currency.CREDITS)))
                if isOk:
                    self.__purchasePackage()
                    return
                return
            loggerEnabled = self.__bundlePreviewMetricsLogger and self.__isStoreWindow()
            if loggerEnabled:
                self.__bundlePreviewMetricsLogger.logOpenPurchaseConfirmation()
            requestConfirmed = yield self.__buyRequestConfirmation(self.__getConfirmationDialogKey())
            if requestConfirmed:
                if self.__isReferralWindow():
                    inventoryVehicle = self._itemsCache.items.getItemByCD(g_currentPreviewVehicle.item.intCD)
                    showGetVehiclePage(inventoryVehicle, self.__buyParams)
                    return
                if mayObtainForMoney(price):
                    if loggerEnabled:
                        self.__bundlePreviewMetricsLogger.logBundlePurchased()
                    showBuyProductOverlay(self.__buyParams)
                elif price.get(Currency.GOLD, 0) > self._itemsCache.items.stats.gold:
                    showBuyGoldForBundle(price.get(Currency.GOLD, 0), self.__buyParams)
            elif loggerEnabled:
                self.__bundlePreviewMetricsLogger.logPurchaseConfirmationClosed()
        return

    def __purchaseOffer(self):
        rent = self.__currentOffer.rent
        cycles = [ r['cycle'] for r in rent if r.get('cycle') ]
        seasons = [ r['season'] for r in rent if r.get('season') ]
        showVehicleRentDialog(g_currentPreviewVehicle.item.intCD, RentType.SEASON_CYCLE_RENT if cycles else RentType.SEASON_RENT, cycles if cycles else seasons, GameSeasonType.EPIC if self.__currentOffer.eventType == 'frontline' else None, self.__currentOffer.buyPrice, self.__currentOffer.buyParams)
        return

    def __purchaseSingleVehicle(self, vehicle):
        event_dispatcher.showVehicleBuyDialog(vehicle, returnAlias=self.__backAlias, returnCallback=self.__backCallback)

    @adisp_process
    def __purchaseHeroTank(self):
        if self._heroTanks.isAdventHero():
            self.__calendarController.showWindow(invokedFrom=CalendarInvokeOrigin.HANGAR)
            return
        shopUrl = self._heroTanks.getCurrentShopUrl()
        if shopUrl:
            event_dispatcher.showShop(shopUrl)
        else:
            url = yield self.__urlMacros.parse(self._heroTanks.getCurrentRelatedURL())
            self.fireEvent(events.OpenLinkEvent(events.OpenLinkEvent.SPECIFIED, url=url))

    @adisp_async
    @adisp_process
    def __hasExternalLink(self, callback=None):
        url = ''
        if self._marathonEvent and not self._marathonEvent.hasIgbLink():
            url = yield self._marathonEvent.getMarathonVehicleUrl()
        elif self.__isHeroTank:
            if not self._heroTanks.isAdventHero() and not self._heroTanks.getCurrentShopUrl():
                url = self._heroTanks.getCurrentRelatedURL()
        callback(self.__linksCtrl.externalAllowed(url) if url else False)

    @adisp_process
    def __purchaseMarathonPackage(self):
        if self._marathonEvent.hasIgbLink():
            url = yield self._marathonEvent.getMarathonVehicleUrlIgb()
            event_dispatcher.showShop(url)
        else:
            url = yield self._marathonEvent.getMarathonVehicleUrl()
            self.fireEvent(events.OpenLinkEvent(events.OpenLinkEvent.SPECIFIED, url=url))

    def __research(self):
        if self._actionType == factory.UNLOCK_ITEM:
            unlockProps = g_techTreeDP.getUnlockProps(self._vehicleCD, self._vehicleLevel)
            factory.doAction(factory.UNLOCK_ITEM, self._vehicleCD, unlockProps, skipConfirm=self._skipConfirm)
        else:
            factory.doAction(factory.BUY_VEHICLE, self._vehicleCD, False, None, VIEW_ALIAS.VEHICLE_PREVIEW, self.__backAlias, self.__backCallback, skipConfirm=self._skipConfirm)
        return

    def __walletAvailableForCurrency(self, currency):
        return self._itemsCache.items.stats.currencyStatuses.get(currency) == WalletController.STATUS.AVAILABLE

    def __getUnlockedVehicleBtnLabel(self, priceType):
        specialData = getHeroTankPreviewParams() if self.__isHeroTank else None
        if specialData is not None and specialData.buyButtonLabel:
            buttonLabel = backport.text(specialData.buyButtonLabel)
        elif priceType == ActualPrice.RESTORE_PRICE:
            buttonLabel = backport.text(R.strings.vehicle_preview.buyingPanel.buyBtn.label.restore())
        elif priceType == ActualPrice.RENT_PRICE:
            buttonLabel = backport.text(R.strings.vehicle_preview.buyingPanel.buyBtn.label.rent())
        elif self.__isHeroTank and self._heroTanks.isAdventHero():
            buttonLabel = backport.text(R.strings.vehicle_preview.buyingPanel.buyBtn.label.showAdventCalendar())
        else:
            buttonLabel = backport.text(R.strings.vehicle_preview.buyingPanel.buyBtn.label.buy())
        return buttonLabel

    @staticmethod
    def __updateEnabledState(collection, enabled):
        if collection is None:
            return
        else:
            for item in collection:
                if 'isEnabled' in item:
                    item['isEnabled'] = enabled

            return
