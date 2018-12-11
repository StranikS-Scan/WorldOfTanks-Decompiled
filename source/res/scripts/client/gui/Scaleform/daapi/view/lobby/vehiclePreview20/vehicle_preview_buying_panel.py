# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/vehiclePreview20/vehicle_preview_buying_panel.py
import math
import time
from collections import namedtuple
import BigWorld
from CurrentVehicle import g_currentPreviewVehicle
from adisp import process
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
from gui.game_control import CalendarInvokeOrigin
from gui.hangar_cameras.hangar_camera_common import CameraRelatedEvents
from gui.ingame_shop import canBuyGoldForVehicleThroughWeb, showBuyVehicleOverlay, showBuyGoldForBundle
from gui.shared import event_dispatcher
from gui.shared import events, EVENT_BUS_SCOPE
from gui.shared.economics import getGUIPrice
from gui.shared.formatters import icons, text_styles, formatPrice
from gui.shared.gui_items.items_actions import factory
from gui.shared.money import Currency, MONEY_UNDEFINED
from gui.shared.tooltips import ACTION_TOOLTIPS_TYPE
from gui.shared.tooltips.formatters import getActionPriceData, packActionTooltipData
from gui.shared.utils.functions import makeTooltip
from helpers import dependency
from helpers import time_utils, i18n
from items_kit_helper import previewStyle, lookupItem, BOX_TYPE, showItemTooltip
from skeletons.gui.game_control import ICalendarController
from skeletons.gui.game_control import IVehicleComparisonBasket, ITradeInController, IRestoreController, IHeroTankController
from skeletons.gui.goodies import IGoodiesCache
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from web_client_api.common import ItemPackTypeGroup
_ButtonState = namedtuple('_ButtonState', 'enabled, price, label, action, tooltip, title')

def _buildBuyButtonTooltip(key):
    return makeTooltip(TOOLTIPS.vehiclepreview_buybutton_all(key, 'header'), TOOLTIPS.vehiclepreview_buybutton_all(key, 'body'))


def _buildRestoreButtonTooltip(key, timeLeft):
    return makeTooltip(header=TOOLTIPS.vehiclepreview_buybutton_all(key, 'header'), body=i18n.makeString(TOOLTIPS.vehiclepreview_buybutton_all(key, 'body'), days=int(math.ceil(timeLeft / 86400))))


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
        self._backAlias = ''
        self._vehicleCD = g_currentPreviewVehicle.item.intCD
        self.__previewDP = DefaultVehPreviewDataProvider()
        self.__isHeroTank = heroTankCD and heroTankCD == self._vehicleCD
        self._skipConfirm = skipConfirm
        self._disableBuyButton = False
        self.__packPrice = None
        self.__packTitle = None
        self.__packItems = None
        self.__customizationStyle = None
        self.__endTime = None
        self.__oldPrice = MONEY_UNDEFINED
        self.__buyParams = None
        self.__timeCallbackID = None
        self.__timeLeftIcon = icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_TIME_ICON, 16, 16)
        return

    @process
    def onBuyOrResearchClick(self):
        vehicle = g_currentPreviewVehicle.item
        if self.__packItems is not None:
            requestConfirmed = yield self.__requestConfirmation()
            if requestConfirmed:
                goldPrice = self.__packPrice.get(Currency.GOLD, 0)
                if goldPrice > self.itemsCache.items.stats.gold:
                    showBuyGoldForBundle(goldPrice, self.__buyParams)
                else:
                    showBuyVehicleOverlay(self.__buyParams)
        elif canBuyGoldForVehicleThroughWeb(vehicle):
            event_dispatcher.showVehicleBuyDialog(vehicle)
        elif self.__isHeroTank and not vehicle.isRestorePossible() and self._backAlias == VIEW_ALIAS.LOBBY_HANGAR:
            if self.heroTanks.isOverloaded():
                calendarCtrl = dependency.instance(ICalendarController)
                calendarCtrl.showCalendar(invokedFrom=CalendarInvokeOrigin.HANGAR)
                event_dispatcher.showHangar()
            else:
                url = self.heroTanks.getCurrentRelatedURL()
                self.fireEvent(events.OpenLinkEvent(events.OpenLinkEvent.SPECIFIED, url=url))
        elif self._actionType == factory.UNLOCK_ITEM:
            unlockProps = g_techTreeDP.getUnlockProps(self._vehicleCD)
            factory.doAction(factory.UNLOCK_ITEM, self._vehicleCD, unlockProps.parentID, unlockProps.unlockIdx, unlockProps.xpCost, skipConfirm=self._skipConfirm)
        else:
            factory.doAction(factory.BUY_VEHICLE, self._vehicleCD, False, VIEW_ALIAS.VEHICLE_PREVIEW_20, skipConfirm=self._skipConfirm)
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

    def setCallSource(self, openedFrom):
        self._backAlias = openedFrom

    def setPackItems(self, packItems, price, title):
        self.__packTitle = title if title is not None else ''
        self.__packPrice = price
        self.__packItems = packItems
        self.__customizationStyle = None
        vehiclesItems = []
        items = []
        for item in packItems:
            if item.type in ItemPackTypeGroup.VEHICLE:
                vehiclesItems.append(item)
            if item.type in ItemPackTypeGroup.STYLE and not self.__customizationStyle:
                self.__customizationStyle = item.id
            items.append(item)

        vehiclesVOs, itemsVOs = self.__previewDP.getItemsPackData(g_currentPreviewVehicle.item, items, vehiclesItems)
        if vehiclesVOs:
            g_currentPreviewVehicle.selectVehicle(vehiclesVOs[0]['intCD'])
            self.as_setSetVehiclesDataS({'vehicles': vehiclesVOs})
        if itemsVOs:
            self.as_setSetItemsDataS({'items': itemsVOs})
        self.__updateBtnState()
        return

    def onCarouselVehilceSelected(self, intCD):
        self._vehicleCD = intCD
        g_currentPreviewVehicle.selectVehicle(intCD)

    def showTooltip(self, intCD, itemType):
        toolTipMgr = g_appLoader.getApp().getToolTipMgr()
        if itemType == BOX_TYPE:
            header = i18n.makeString(TOOLTIPS.VEHICLEPREVIEW_BOXTOOLTIP_HEADER)
            body = i18n.makeString(TOOLTIPS.VEHICLEPREVIEW_BOXTOOLTIP_BODY)
            tooltip = '{{HEADER}}{header}{{/HEADER}}{{BODY}}{body}{{/BODY}}'.format(header=header, body=body)
            toolTipMgr.onCreateComplexTooltip(tooltip, 'INFO')
            return
        try:
            try:
                itemId = int(intCD)
            except ValueError:
                itemId = intCD

            rawItem = [ item for item in self.__packItems if item.id == itemId and item.type == itemType ][0]
            item = lookupItem(rawItem, self.itemsCache, self.goodiesCache)
            showItemTooltip(toolTipMgr, rawItem, item)
        except IndexError:
            return

    def _populate(self):
        super(VehiclePreviewBuyingPanel, self)._populate()
        g_clientUpdateManager.addMoneyCallback(self.__updateBtnState)
        g_clientUpdateManager.addCallbacks({'stats.freeXP': self.__updateBtnState,
         'inventory': self.__updateBtnState})
        g_currentPreviewVehicle.onVehicleUnlocked += self.__updateBtnState
        g_currentPreviewVehicle.onChanged += self.__onVehicleChanged
        self.restores.onRestoreChangeNotify += self.__onRestoreChanged
        self.lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChanged
        if g_currentPreviewVehicle.isPresent():
            self.__updateBtnState()
        self.addListener(CameraRelatedEvents.VEHICLE_LOADING, self.__onVehicleLoading, EVENT_BUS_SCOPE.DEFAULT)

    def _dispose(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        g_currentPreviewVehicle.onVehicleUnlocked -= self.__updateBtnState
        g_currentPreviewVehicle.onChanged -= self.__onVehicleChanged
        self.restores.onRestoreChangeNotify -= self.__onRestoreChanged
        self.lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChanged
        self.removeListener(CameraRelatedEvents.VEHICLE_LOADING, self.__onVehicleLoading, EVENT_BUS_SCOPE.DEFAULT)
        self.__stopTimer()
        super(VehiclePreviewBuyingPanel, self)._dispose()

    def __requestConfirmation(self):
        return DialogsInterface.showDialog(meta=I18nConfirmDialogMeta(key='buyConfirmation', messageCtx={'product': self.__packTitle or '"This Pack"',
         'price': formatPrice(self.__packPrice, reverse=True, useIcon=True)}, focusedID=DIALOG_BUTTON_ID.SUBMIT))

    def __onVehicleLoading(self, _):
        vehicle = g_currentPreviewVehicle.item
        if vehicle and self.__customizationStyle:
            style = self.itemsCache.items.getItemByCD(self.__customizationStyle)
            if style is not None:
                previewStyle(vehicle, style)
        return

    def __updateBtnState(self, *args):
        item = g_currentPreviewVehicle.item
        if item is None:
            return
        else:
            btnData = self.__getBtnData()
            self._actionType = self.__previewDP.getBuyType(item)
            if self.__packItems:
                buyingPanelData = self.__previewDP.getItemPackBuyingPanelData(item, btnData, self.__packItems)
            else:
                buyingPanelData = self.__previewDP.getBuyingPanelData(item, btnData, self.__isHeroTank)
            self.as_setBuyDataS(buyingPanelData)
            return

    def __onVehicleChanged(self, *args):
        if g_currentPreviewVehicle.isPresent():
            self._vehicleCD = g_currentPreviewVehicle.item.intCD
            if not self.__packPrice:
                self.__updateBtnState()

    def __onRestoreChanged(self, vehicles):
        if g_currentPreviewVehicle.isPresent():
            if self._vehicleCD in vehicles:
                self.__updateBtnState()

    def __onServerSettingsChanged(self, diff):
        if self.lobbyContext.getServerSettings().isIngameDataChangedInDiff(diff, 'isEnabled'):
            self.__updateBtnState()

    def __getBtnData(self):
        if self.__packPrice is not None:
            return self.__getBtnDataPack()
        else:
            vehicle = g_currentPreviewVehicle.item
            return self.__getBtnDataUnlockedVehicle(vehicle) if vehicle.isUnlocked else self.__getBtnDataLockedVehicle(vehicle)

    def __getBtnDataPack(self):
        priceVO = []
        enabled = True
        action = None
        tooltip = ''
        for curr in [ c for c in Currency.ALL if self.__packPrice.get(c) is not None ]:
            priceVO.append(curr)
            priceVO.append(self.__packPrice.getSignValue(curr))

        if self._disableBuyButton:
            tooltip = _buildBuyButtonTooltip('endTime')
            enabled = False
        if self.__oldPrice.isDefined():
            action = packActionTooltipData(ACTION_TOOLTIPS_TYPE.ECONOMICS, 'itemsPack', True, self.__packPrice, self.__oldPrice)
        if self.__packItems:
            buttonLabel = VEHICLE_PREVIEW.BUYINGPANEL_BUYBTN_LABEL_BUYITEMPACK
        else:
            buttonLabel = VEHICLE_PREVIEW.BUYINGPANEL_BUYBTN_LABEL_BUY
        return _ButtonState(enabled, priceVO, buttonLabel, action, tooltip, self.__packTitle)

    def __getBtnDataUnlockedVehicle(self, vehicle):
        money = self.itemsCache.items.stats.money
        money = self.tradeIn.addTradeInPriceIfNeeded(vehicle, money)
        tooltip = ''
        exchangeRate = self.itemsCache.items.shop.exchangeRate
        price = getGUIPrice(vehicle, money, exchangeRate)
        currency = price.getCurrency(byWeight=True)
        action = getActionPriceData(vehicle)
        buttonHasToBeEnabled = self.__isHeroTank or vehicle.mayObtainWithMoneyExchange(money, exchangeRate)
        if self.__isHeroTank and self.heroTanks.isOverloaded() and vehicle.isRestoreAvailable() != vehicle.isRestorePossible():
            buttonHasToBeEnabled = False
        isBuyingAvailable = not vehicle.isHidden or vehicle.isRentable or vehicle.isRestorePossible()
        if vehicle.isRestorePossible() and not vehicle.isRestoreAvailable():
            tooltip = _buildRestoreButtonTooltip('restoreRequested', vehicle.restoreInfo.getRestoreCooldownTimeLeft())
        elif currency == Currency.GOLD:
            if not buttonHasToBeEnabled:
                if isBuyingAvailable:
                    tooltip = _buildBuyButtonTooltip('notEnoughGold')
                    if isIngameShopEnabled():
                        buttonHasToBeEnabled = True
        elif not buttonHasToBeEnabled and isBuyingAvailable:
            tooltip = _buildBuyButtonTooltip('notEnoughCredits')
        if self._disableBuyButton:
            buttonHasToBeEnabled = False
        return _ButtonState(buttonHasToBeEnabled, [currency, price.getSignValue(currency)], VEHICLE_PREVIEW.BUYINGPANEL_BUYBTN_LABEL_RESTORE if vehicle.isRestorePossible() else (VEHICLE_PREVIEW.BUYINGPANEL_BUYBTN_LABEL_TOCALENDAR if self.__isHeroTank and self.heroTanks.isOverloaded() and self._backAlias == VIEW_ALIAS.LOBBY_HANGAR else VEHICLE_PREVIEW.BUYINGPANEL_BUYBTN_LABEL_BUY), action, tooltip, self.__packTitle)

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
        return _ButtonState(isAvailableToUnlock, ['xp', xpCost], VEHICLE_PREVIEW.BUYINGPANEL_BUYBTN_LABEL_RESEARCH, None, tooltip, self.__packTitle)

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
        monthName = i18n.makeString(MENU.datetime_months(gmTime.tm_mon))
        fmtValues = i18n.makeString('%s %s %s' % (gmTime.tm_mday, monthName, gmTime.tm_year))
        tooltip = makeTooltip(header=TOOLTIPS.VEHICLEPREVIEW_SHOPPACK_DATETIMETOOLTIP_HEADER, body=i18n.makeString(TOOLTIPS.VEHICLEPREVIEW_SHOPPACK_DATETIMETOOLTIP_BODY, namePack=text_styles.neutral(self.__packTitle), date=fmtValues))
        self.as_updateLeftTimeS(formattedTime='', tooltip=tooltip)

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
