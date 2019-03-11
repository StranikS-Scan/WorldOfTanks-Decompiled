# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/vehiclePreview20/vehicle_preview_buying_panel.py
import time
from collections import namedtuple
import BigWorld
from CurrentVehicle import g_currentPreviewVehicle
from adisp import process
from constants import RentType, GameSeasonType
from gui import DialogsInterface
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.dialogs import I18nConfirmDialogMeta, DIALOG_BUTTON_ID
from gui.Scaleform.daapi.view.lobby.store.browser.ingameshop_helpers import isIngameShopEnabled
from gui.Scaleform.daapi.view.lobby.techtree.techtree_dp import g_techTreeDP
from gui.Scaleform.daapi.view.lobby.vehiclePreview20.vehicle_preview_dp import DefaultVehPreviewDataProvider
from gui.Scaleform.daapi.view.meta.VehiclePreviewBuyingPanelMeta import VehiclePreviewBuyingPanelMeta
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.Scaleform.locale.VEHICLE_PREVIEW import VEHICLE_PREVIEW
from gui.app_loader import g_appLoader
from gui.hangar_cameras.hangar_camera_common import CameraRelatedEvents
from gui.ingame_shop import canBuyGoldForVehicleThroughWeb
from gui.ingame_shop import showBuyVehicleOverlay, showBuyGoldForBundle
from gui.referral_program import showGetVehiclePage
from gui.shared import event_dispatcher, g_eventBus
from gui.shared import events, EVENT_BUS_SCOPE
from gui.shared.economics import getGUIPrice
from gui.shared.event_dispatcher import showVehicleRentDialog
from gui.shared.events import HasCtxEvent
from gui.shared.formatters import icons, text_styles, formatPrice
from gui.shared.gui_items.items_actions import factory
from gui.shared.money import Currency, MONEY_UNDEFINED
from gui.shared.tooltips import ACTION_TOOLTIPS_TYPE
from gui.shared.tooltips.formatters import getActionPriceData, packActionTooltipData
from gui.shared.utils.functions import makeTooltip
from helpers import dependency
from helpers import time_utils
from helpers.i18n import makeString as _ms
from items_kit_helper import lookupItem, BOX_TYPE, showItemTooltip, OFFER_CHANGED_EVENT
from items_kit_helper import getActiveOffer, mayObtainForMoney, mayObtainWithMoneyExchange
from shared_utils import findFirst, first
from skeletons.gui.game_control import IVehicleComparisonBasket
from skeletons.gui.game_control import ITradeInController, IRestoreController, IHeroTankController
from skeletons.gui.goodies import IGoodiesCache
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from web_client_api.common import ItemPackTypeGroup, ItemPackEntry
_ButtonState = namedtuple('_ButtonState', 'enabled, price, label, action, tooltip, title')

def _buildBuyButtonTooltip(key):
    return makeTooltip(TOOLTIPS.vehiclepreview_buybutton_all(key, 'header'), TOOLTIPS.vehiclepreview_buybutton_all(key, 'body'))


class VehiclePreviewBuyingPanel(VehiclePreviewBuyingPanelMeta):
    itemsCache = dependency.descriptor(IItemsCache)
    goodiesCache = dependency.descriptor(IGoodiesCache)
    comparisonBasket = dependency.descriptor(IVehicleComparisonBasket)
    tradeIn = dependency.descriptor(ITradeInController)
    restores = dependency.descriptor(IRestoreController)
    heroTanks = dependency.descriptor(IHeroTankController)
    lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self, skipConfirm=False):
        super(VehiclePreviewBuyingPanel, self).__init__()
        heroTankCD = self.heroTanks.getCurrentTankCD()
        self._actionType = None
        self._vehicleCD = g_currentPreviewVehicle.item.intCD
        self._skipConfirm = skipConfirm
        self._disableBuyButton = False
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
        self.__timeCallbackID = None
        self.__timeLeftIcon = icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_TIME_ICON, 16, 16)
        self.__cachedVehiclesVOs = None
        self.__cachedItemsVOs = None
        self.__cachedCollapsedItemsVOs = None
        return

    def onBuyOrResearchClick(self):
        vehicle = g_currentPreviewVehicle.item
        if self.__items is not None:
            self.__purchasePackage()
        elif self.__offers is not None:
            self.__purchaseOffer()
        elif canBuyGoldForVehicleThroughWeb(vehicle):
            self.__purchaseSingleVehicle(vehicle)
        elif self.__isHeroTank:
            self.__purchaseHeroTank()
        else:
            self.__research()
        return

    def setTimerData(self, endTime, oldPrice):
        self.__oldPrice = oldPrice
        if endTime is not None:
            self.__endTime = endTime
            self.__onLeftTimeUpdated()
        self.__updateBtnState()
        return

    def setBuyParams(self, buyParams):
        self.__buyParams = buyParams

    def setBackAlias(self, backAlias):
        self.__backAlias = backAlias

    def setPackItems(self, packItems, price, title):
        self.__title = title if title is not None else ''
        self.__price = price
        self.__items = packItems
        self.__styleByGroup.clear()
        self.__vehicleByGroup.clear()
        vehiclesItems, items = self.__previewDP.separateItemsPack(self.__items)
        for item in items:
            if item.type in ItemPackTypeGroup.STYLE and item.groupID not in self.__styleByGroup:
                self.__styleByGroup[item.groupID] = item.id

        for vehicleItem in vehiclesItems:
            self.__vehicleByGroup[vehicleItem.id] = vehicleItem.groupID

        vehiclesVOs, itemsVOs, collapseItemsVOs = self.__previewDP.getItemsPackData(g_currentPreviewVehicle.item, items, vehiclesItems)
        self.__cachedVehiclesVOs = vehiclesVOs
        self.__cachedItemsVOs = itemsVOs
        self.__cachedCollapsedItemsVOs = collapseItemsVOs
        self.__update()
        return

    def onCarouselVehilceSelected(self, intCD):
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
             'crewItems': [crew]}, eventType=OFFER_CHANGED_EVENT))
            self.__buyParams = self.__currentOffer.buyParams
            self.__price = self.__currentOffer.buyPrice
            self.as_setBuyDataS(self.__previewDP.getOffersBuyingPanelData(self.__getBtnData()))
            description = self.__description or self.__getCurrentOfferDescription() or {}
            self.as_setSetTitleTooltipS(makeTooltip(**description))

    def showTooltip(self, intCD, itemType):
        toolTipMgr = g_appLoader.getApp().getToolTipMgr()
        if itemType == BOX_TYPE:
            toolTipMgr.onCreateComplexTooltip(makeTooltip(TOOLTIPS.VEHICLEPREVIEW_BOXTOOLTIP_HEADER, TOOLTIPS.VEHICLEPREVIEW_BOXTOOLTIP_BODY), 'INFO')
            return
        try:
            try:
                itemId = int(intCD)
            except ValueError:
                itemId = intCD

            rawItem = [ item for item in self.__items if item.id == itemId and item.type == itemType ][0]
            item = lookupItem(rawItem, self.itemsCache, self.goodiesCache)
            showItemTooltip(toolTipMgr, rawItem, item)
        except IndexError:
            return

    def updateData(self, useCompactData):
        self.__update(collapseItems=useCompactData)

    def _populate(self):
        super(VehiclePreviewBuyingPanel, self)._populate()
        g_clientUpdateManager.addMoneyCallback(self.__updateBtnState)
        g_clientUpdateManager.addCallbacks({'stats.freeXP': self.__updateBtnState,
         'inventory': self.__updateBtnState})
        g_currentPreviewVehicle.onVehicleUnlocked += self.__updateBtnState
        g_currentPreviewVehicle.onChanged += self.__onVehicleChanged
        self.restores.onRestoreChangeNotify += self.__onRestoreChanged
        self.lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChanged
        self.addListener(CameraRelatedEvents.VEHICLE_LOADING, self.__onVehicleLoading, EVENT_BUS_SCOPE.DEFAULT)

    def _dispose(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        g_currentPreviewVehicle.onVehicleUnlocked -= self.__updateBtnState
        g_currentPreviewVehicle.onChanged -= self.__onVehicleChanged
        self.restores.onRestoreChangeNotify -= self.__onRestoreChanged
        self.lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChanged
        self.removeListener(CameraRelatedEvents.VEHICLE_LOADING, self.__onVehicleLoading, EVENT_BUS_SCOPE.DEFAULT)
        self.__stopTimer()
        self.__styleByGroup.clear()
        self.__vehicleByGroup.clear()
        super(VehiclePreviewBuyingPanel, self)._dispose()

    def __isReferralWindow(self):
        return self.__backAlias == VIEW_ALIAS.REFERRAL_PROGRAM_WINDOW

    def __getConfirmationDialogKey(self):
        key = 'buyConfirmation'
        if self.__isReferralWindow():
            key = 'referralReward'
        return key

    def __update(self, collapseItems=False):
        if self.__cachedVehiclesVOs:
            g_currentPreviewVehicle.selectVehicle(self.__cachedVehiclesVOs[0]['intCD'])
            self.as_setSetVehiclesDataS({'vehicles': self.__cachedVehiclesVOs})
        if collapseItems and self.__cachedCollapsedItemsVOs:
            self.as_setSetItemsDataS({'items': self.__cachedCollapsedItemsVOs})
        elif self.__cachedItemsVOs:
            self.as_setSetItemsDataS({'items': self.__cachedItemsVOs})
        self.__updateBtnState()

    def __getOfferByID(self, offerID):
        return findFirst(lambda o: o.buy_params['transactionID'] == offerID, self.__offers)

    def __buyRequestConfirmation(self, key='buyConfirmation'):
        return DialogsInterface.showDialog(meta=I18nConfirmDialogMeta(key=key, messageCtx={'product': self.__title or '"This Pack"',
         'price': formatPrice(self.__price, reverse=True, useIcon=True)}, focusedID=DIALOG_BUTTON_ID.SUBMIT))

    def __onVehicleLoading(self, ctxEvent):
        vehicle = g_currentPreviewVehicle.item
        if vehicle is None:
            return
        else:
            groupID = self.__vehicleByGroup.get(vehicle.intCD)
            if not ctxEvent.ctx.get('started') and groupID in self.__styleByGroup:
                customizationStyle = self.__styleByGroup[groupID]
                style = self.itemsCache.items.getItemByCD(customizationStyle)
                if style is not None and not style.isRentable:
                    g_currentPreviewVehicle.previewStyle(style)
            return

    def __updateBtnState(self, *args):
        item = g_currentPreviewVehicle.item
        if item is None:
            return
        else:
            btnData = self.__getBtnData()
            self._actionType = self.__previewDP.getBuyType(item)
            if self.__items:
                buyingPanelData = self.__previewDP.getItemPackBuyingPanelData(item, btnData, self.__items)
            elif self.__offers:
                buyingPanelData = self.__previewDP.getOffersBuyingPanelData(btnData)
            else:
                buyingPanelData = self.__previewDP.getBuyingPanelData(item, btnData, self.__isHeroTank)
            buyingPanelData.update({'isReferralEnabled': self.__isReferralWindow()})
            self.as_setBuyDataS(buyingPanelData)
            return

    def __onVehicleChanged(self, *args):
        if g_currentPreviewVehicle.isPresent():
            self._vehicleCD = g_currentPreviewVehicle.item.intCD
            if not self.__price:
                self.__updateBtnState()

    def __onRestoreChanged(self, vehicles):
        if g_currentPreviewVehicle.isPresent():
            if self._vehicleCD in vehicles:
                self.__updateBtnState()

    def __onServerSettingsChanged(self, diff):
        if self.lobbyContext.getServerSettings().isIngameDataChangedInDiff(diff, 'isEnabled'):
            self.__updateBtnState()

    def __getBtnData(self):
        if self.__price is not None:
            return self.__getBtnDataPack()
        else:
            vehicle = g_currentPreviewVehicle.item
            return self.__getBtnDataUnlockedVehicle(vehicle) if vehicle.isUnlocked else self.__getBtnDataLockedVehicle(vehicle)

    def __getBtnDataPack(self):
        priceVO = []
        enabled = True
        action = None
        tooltip = ''
        for curr in [ c for c in Currency.ALL if self.__price.get(c) is not None ]:
            priceVO.append(curr)
            priceVO.append(self.__price.getSignValue(curr))

        if self._disableBuyButton:
            tooltip = _buildBuyButtonTooltip('endTime')
            enabled = False
        if self.__oldPrice.isDefined():
            action = packActionTooltipData(ACTION_TOOLTIPS_TYPE.ECONOMICS, 'itemsPack', True, self.__price, self.__oldPrice)
        if self.__currentOffer and self.__currentOffer.bestOffer and self.__currentOffer.eventType:
            action = makeTooltip(**self.__getBestOfferTooltipData(self.__currentOffer.eventType))
        if self.__isReferralWindow():
            buttonLabel = VEHICLE_PREVIEW.BUYINGPANEL_BUYBTN_LABEL_OBTAIN
        elif self.__items:
            buttonLabel = VEHICLE_PREVIEW.BUYINGPANEL_BUYBTN_LABEL_BUYITEMPACK
        elif self.__offers and self.__currentOffer:
            if self.__price.getCurrency() == Currency.GOLD:
                enabled = isIngameShopEnabled()
            else:
                enabled = mayObtainForMoney(self.__price) or mayObtainWithMoneyExchange(self.__price)
            buttonLabel = VEHICLE_PREVIEW.BUYINGPANEL_BUYBTN_LABEL_RENT
            self.__title = self.__getCurrentOfferTitle()
        else:
            buttonLabel = VEHICLE_PREVIEW.BUYINGPANEL_BUYBTN_LABEL_BUY
        return _ButtonState(enabled, priceVO, buttonLabel, action, tooltip, self.__title)

    def __getBtnDataUnlockedVehicle(self, vehicle):
        money = self.itemsCache.items.stats.money
        money = self.tradeIn.addTradeInPriceIfNeeded(vehicle, money)
        tooltip = ''
        exchangeRate = self.itemsCache.items.shop.exchangeRate
        price = getGUIPrice(vehicle, money, exchangeRate)
        currency = price.getCurrency(byWeight=True)
        action = getActionPriceData(vehicle)
        mayObtain = self.__isHeroTank or vehicle.mayObtainWithMoneyExchange(money, exchangeRate)
        isBuyingAvailable = not vehicle.isHidden or vehicle.isRentable or vehicle.isRestorePossible()
        if currency == Currency.GOLD:
            if not mayObtain:
                if isBuyingAvailable:
                    tooltip = _buildBuyButtonTooltip('notEnoughGold')
                    if isIngameShopEnabled():
                        mayObtain = True
        elif not mayObtain and isBuyingAvailable:
            tooltip = _buildBuyButtonTooltip('notEnoughCredits')
        if self._disableBuyButton:
            mayObtain = False
        return _ButtonState(mayObtain, [currency, price.getSignValue(currency)], VEHICLE_PREVIEW.BUYINGPANEL_BUYBTN_LABEL_RESTORE if vehicle.isRestorePossible() else VEHICLE_PREVIEW.BUYINGPANEL_BUYBTN_LABEL_BUY, action, tooltip, self.__title)

    def __getBtnDataLockedVehicle(self, vehicle):
        stats = self.itemsCache.items.stats
        tooltip = ''
        nodeCD = vehicle.intCD
        isAvailableToUnlock, xpCost, _ = g_techTreeDP.isVehicleAvailableToUnlock(nodeCD)
        if not isAvailableToUnlock:
            g_techTreeDP.load()
            unlocks = self.itemsCache.items.stats.unlocks
            next2Unlock, _ = g_techTreeDP.isNext2Unlock(nodeCD, unlocked=set(unlocks), xps=stats.vehiclesXPs, freeXP=stats.freeXP)
            if next2Unlock:
                tooltip = _buildBuyButtonTooltip('notEnoughXp')
            elif any((bool(cd in unlocks) for cd in g_techTreeDP.getTopLevel(nodeCD))):
                tooltip = _buildBuyButtonTooltip('parentModuleIsLocked')
            else:
                tooltip = _buildBuyButtonTooltip('parentVehicleIsLocked')
        return _ButtonState(isAvailableToUnlock, ['xp', xpCost], VEHICLE_PREVIEW.BUYINGPANEL_BUYBTN_LABEL_RESEARCH, None, tooltip, self.__title)

    def __getBestOfferTooltipData(self, eventType=None):
        return {'header': VEHICLE_PREVIEW.BUYINGPANEL_OFFER_RENT_FRONTLINE_TOOLTIP_BEST_OFFER_HEADER,
         'body': VEHICLE_PREVIEW.BUYINGPANEL_OFFER_RENT_FRONTLINE_TOOLTIP_BEST_OFFER_BODY} if eventType == 'frontline' else None

    def __getCurrentOfferTitle(self):
        if self.__offers and self.__currentOffer:
            if self.__currentOffer.eventType == 'frontline':
                firstRent = first(self.__currentOffer.rent)
                if len(self.__offers) > 1 or firstRent and firstRent.get('season') is not None:
                    return _ms(VEHICLE_PREVIEW.BUYINGPANEL_OFFER_RENT_TITLE_FRONTLINE_ORDINAL)
                return _ms(VEHICLE_PREVIEW.BUYINGPANEL_OFFER_RENT_TITLE_FRONTLINE_SINGLE_CYCLE, cycles=self.__currentOffer.name)
        return self.__title

    def __getCurrentOfferDescription(self):
        return {'header': VEHICLE_PREVIEW.BUYINGPANEL_OFFER_RENT_FRONTLINE_DESCRIPTION_HEADER,
         'body': VEHICLE_PREVIEW.BUYINGPANEL_OFFER_RENT_FRONTLINE_DESCRIPTION_BODY_CREDITS} if self.__currentOffer and self.__currentOffer.eventType == 'frontline' else None

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
        gmTime = time_utils.getTimeStructInLocal(self.__endTime)
        monthName = _ms(MENU.datetime_months(gmTime.tm_mon))
        fmtValues = _ms('%s %s %s' % (gmTime.tm_mday, monthName, gmTime.tm_year))
        tooltip = makeTooltip(header=TOOLTIPS.VEHICLEPREVIEW_SHOPPACK_DATETIMETOOLTIP_HEADER, body=_ms(TOOLTIPS.VEHICLEPREVIEW_SHOPPACK_DATETIMETOOLTIP_BODY, namePack=text_styles.neutral(self.__title), date=fmtValues))
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

    @process
    def __purchasePackage(self):
        requestConfirmed = yield self.__buyRequestConfirmation(self.__getConfirmationDialogKey())
        if requestConfirmed:
            if self.__isReferralWindow():
                vehicle = g_currentPreviewVehicle.item
                inventoryVehicle = self.itemsCache.items.getItemByCD(vehicle.intCD)
                showGetVehiclePage(inventoryVehicle, self.__buyParams)
                return
            goldPrice = self.__price.get(Currency.GOLD, 0)
            if goldPrice > self.itemsCache.items.stats.gold:
                showBuyGoldForBundle(goldPrice, self.__buyParams)
            else:
                showBuyVehicleOverlay(self.__buyParams)

    def __purchaseOffer(self):
        rent = self.__currentOffer.rent
        cycles = [ r['cycle'] for r in rent if r.get('cycle') ]
        seasons = [ r['season'] for r in rent if r.get('season') ]
        showVehicleRentDialog(g_currentPreviewVehicle.item.intCD, RentType.SEASON_CYCLE_RENT if cycles else RentType.SEASON_RENT, cycles if cycles else seasons, GameSeasonType.EPIC if self.__currentOffer.eventType == 'frontline' else None, self.__currentOffer.buyPrice, self.__currentOffer.buyParams)
        return

    def __purchaseSingleVehicle(self, vehicle):
        event_dispatcher.showVehicleBuyDialog(vehicle)

    def __purchaseHeroTank(self):
        url = self.heroTanks.getCurrentRelatedURL()
        self.fireEvent(events.OpenLinkEvent(events.OpenLinkEvent.SPECIFIED, url=url))

    def __research(self):
        if self._actionType == factory.UNLOCK_ITEM:
            unlockProps = g_techTreeDP.getUnlockProps(self._vehicleCD)
            factory.doAction(factory.UNLOCK_ITEM, self._vehicleCD, unlockProps.parentID, unlockProps.unlockIdx, unlockProps.xpCost, skipConfirm=self._skipConfirm)
        else:
            factory.doAction(factory.BUY_VEHICLE, self._vehicleCD, False, VIEW_ALIAS.VEHICLE_PREVIEW_20, skipConfirm=self._skipConfirm)
