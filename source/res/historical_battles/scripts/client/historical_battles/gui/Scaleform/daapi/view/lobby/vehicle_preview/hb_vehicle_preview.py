# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/Scaleform/daapi/view/lobby/vehicle_preview/hb_vehicle_preview.py
import BigWorld
from historical_battles_common.hb_constants import HB_GAME_PARAMS_KEY
from adisp import adisp_process
from CurrentVehicle import g_currentPreviewVehicle
from wg_async import wg_await
from frameworks.wulf import WindowLayer
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.view.lobby.vehicle_preview.vehicle_preview import VehiclePreview
from gui.Scaleform.daapi.view.meta.VehiclePreviewHBPanelMeta import VehiclePreviewHBPanelMeta
from gui.Scaleform.daapi.view.meta.VehiclePreviewHBRestorePanelMeta import VehiclePreviewHBRestorePanelMeta
from gui.Scaleform.framework import ScopeTemplates
from gui.Scaleform.framework.managers.loaders import GuiImplViewLoadParams
from gui.Scaleform.genConsts.VEHPREVIEW_CONSTANTS import VEHPREVIEW_CONSTANTS
from gui.game_control.wallet import WalletController
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.common.fade_manager import FadeManager, waitGuiImplViewLoading
from gui.prb_control.dispatcher import g_prbLoader
from gui.prb_control.entities.base.ctx import PrbAction
from gui.shared import event_dispatcher
from gui.shared.formatters import getItemPricesVO, text_styles, icons, chooseItemPriceVO, time_formatters
from gui.shared.gui_items.gui_item_economics import ItemPrice, getPriceTypeAndValue
from gui.shared.gui_items.items_actions import factory
from gui.shared.gui_items.items_actions.factory import asyncDoAction
from gui.shared.money import MONEY_UNDEFINED, ZERO_MONEY, Money
from gui.shared.utils.functions import makeTooltip
from helpers import dependency, time_utils
from historical_battles.gui.Scaleform.daapi.settings import VIEW_ALIAS
from historical_battles.gui.customizable_objects_manager import AnchorNames
from historical_battles.gui.prb_control.prb_config import PREBATTLE_ACTION_NAME
from historical_battles.gui.shared.gui_items.items_actions.hb_shop import HBShopBuyMainPrizeAction
from historical_battles.skeletons.gui.customizable_objects_manager import ICustomizableObjectsManager
from historical_battles.skeletons.gui.game_event_controller import IGameEventController
from skeletons.gui.game_control import IRestoreController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
FREE_DISCOUNT_VALUE = 100

def isPreviewAvailable():
    lobbyContext = dependency.instance(ILobbyContext)
    hbConfig = lobbyContext.getServerSettings().getSettings().get(HB_GAME_PARAMS_KEY, {})
    return hbConfig.get('isEnabled', False)


class HBVehiclePreview(VehiclePreview):
    _gameEventController = dependency.descriptor(IGameEventController)
    _custObjMgr = dependency.descriptor(ICustomizableObjectsManager)
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, ctx=None):
        super(HBVehiclePreview, self).__init__(ctx)
        eventHeroTankCD = self._gameEventController.heroTank.getVehicleCD()
        self.isEventHeroTank = eventHeroTankCD == self._vehicleCD
        items = self.itemsCache.items
        getItem = items.getItemByCD
        self.isRestorePossible = getItem(self._vehicleCD).isRestorePossible()

    def setBottomPanel(self):
        if self.isEventHeroTank and not self.isRestorePossible:
            self.as_setBottomPanelS(VEHPREVIEW_CONSTANTS.HB_PANEL_LINKAGE)
        elif self.isEventHeroTank:
            self.as_setBottomPanelS(VEHPREVIEW_CONSTANTS.HB_RESTORE_PANEL_LINKAGE)
        else:
            super(HBVehiclePreview, self).setBottomPanel()

    def closeView(self):
        if self._backAlias == VIEW_ALIAS.HB_MAIN_PRIZE:
            layoutID = R.views.historical_battles.lobby.HangarView()
            from historical_battles.gui.impl.lobby.hangar_view import HangarView
            self.showViewWithFade(layoutID, HangarView)
        else:
            super(HBVehiclePreview, self).closeView()

    def _populate(self):
        super(HBVehiclePreview, self)._populate()
        self._deactivateSelectableLogic()
        if self._backAlias == VIEW_ALIAS.HB_MAIN_PRIZE:
            self._custObjMgr.switchByAnchorName(anchorName=AnchorNames.HERO_TANK)

    @adisp_process
    def showViewWithFade(self, layoutID, view, delay=None):
        with FadeManager(WindowLayer.OVERLAY) as fadeManager:
            yield wg_await(fadeManager.show())
            self._custObjMgr.switchByAnchorName()
            yield waitGuiImplViewLoading(GuiImplViewLoadParams(layoutID, view, ScopeTemplates.LOBBY_SUB_SCOPE), delay=delay)
            yield wg_await(fadeManager.hide())


class HBVehiclePreviewPanel(VehiclePreviewHBPanelMeta):
    lobbyContext = dependency.descriptor(ILobbyContext)
    eventsCache = dependency.descriptor(IEventsCache)
    gameEventController = dependency.descriptor(IGameEventController)
    itemsCache = dependency.descriptor(IItemsCache)
    MAIN_PRIZE_VEHICLE_BUNDLE_ID = 'hb22BundleMainPrizeVehicle'

    def __init__(self):
        super(HBVehiclePreviewPanel, self).__init__()
        self.__acceptButtonCommand = None
        self.__secondaryButtonCommand = None
        return

    @property
    def shop(self):
        return getattr(BigWorld.player(), 'HBShopAccountComponent', None)

    def _populate(self):
        super(HBVehiclePreviewPanel, self)._populate()
        g_clientUpdateManager.addMoneyCallback(self._updateState)
        BigWorld.player().objectsSelectionEnabled(False)
        self._updateState()

    def _destroy(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        if BigWorld.player():
            BigWorld.player().objectsSelectionEnabled(True)
        super(HBVehiclePreviewPanel, self)._destroy()

    def _updateState(self, *_):
        hbConfig = self.lobbyContext.getServerSettings().getSettings().get(HB_GAME_PARAMS_KEY, {})
        isEventInProgress = time_utils.getTimeDeltaFromNowInLocal(hbConfig.get('endDate', False)) > 0
        isFree = False
        mainPrizeBundle = self.shop.getBundle(self.MAIN_PRIZE_VEHICLE_BUNDLE_ID)
        money = self.itemsCache.items.stats.actualMoney
        price = Money.makeFrom(mainPrizeBundle.price.currency, mainPrizeBundle.price.amount)
        discountedPrice = self.shop.getBundleDiscountedPrice(mainPrizeBundle)
        if discountedPrice:
            price = Money.makeFrom(discountedPrice.currency, discountedPrice.amount) if discountedPrice is not None else MONEY_UNDEFINED
        oldPrice = Money.makeFrom(mainPrizeBundle.price.currency, mainPrizeBundle.price.amount)
        itemPrices = ItemPrice(price=price, defPrice=oldPrice)
        itemPrice = getItemPricesVO(itemPrices)
        shortage = max(price.get(mainPrizeBundle.price.currency) - money.get(mainPrizeBundle.price.currency), 0)
        priceVO = {'price': itemPrice,
         'shortage': shortage}
        self.__acceptButtonCommand = self.__purchaseMainPrize
        if price <= ZERO_MONEY:
            isFree = True
            acceptBtnLabel = backport.text(R.strings.hb_lobby.vehiclePreviewPanel.acceptBtn.label.getVehicle())
        else:
            acceptBtnLabel = backport.text(R.strings.hb_lobby.vehiclePreviewPanel.acceptBtn.label.buyVehicle())
        if isEventInProgress:
            title = backport.text(R.strings.hb_lobby.vehiclePreviewPanel.title.eventInProgress())
            secondaryBtnLabel = backport.text(R.strings.hb_lobby.vehiclePreviewPanel.secondaryBtn.label.showEvent())
            self.__secondaryButtonCommand = self.__showEventHangar
        else:
            title = backport.text(R.strings.hb_lobby.vehiclePreviewPanel.title.eventFinished())
            secondaryBtnLabel = backport.text(R.strings.hb_lobby.vehiclePreviewPanel.secondaryBtn.label.showEventShop())
            self.__secondaryButtonCommand = self.__showShop
        iconIcon = icons.makeImageTag(backport.image(R.images.gui.maps.icons.library.info()), height=24, width=24)
        resulVO = {'title': text_styles.concatStylesWithSpace(title, iconIcon),
         'acceptBtnLabel': acceptBtnLabel,
         'secondaryBtnLabel': secondaryBtnLabel,
         'isFree': isFree}
        resulVO.update(priceVO)
        self.setDataVO(resulVO)
        return

    def setDataVO(self, vo):
        self.as_setDataS(vo)

    def onAcceptClicked(self):
        if self.__acceptButtonCommand is not None:
            self.__acceptButtonCommand()
        return

    def onSecondaryClicked(self):
        if self.__secondaryButtonCommand is not None:
            self.__secondaryButtonCommand()
        return

    def __getEventTimes(self):
        return (time_utils.getCurrentLocalServerTimestamp(), self.gameEventController.getEventStartTime(), self.gameEventController.getEventFinishTime())

    @adisp_process
    def __purchaseMainPrize(self):
        bundle = self.shop.getBundle(self.MAIN_PRIZE_VEHICLE_BUNDLE_ID)
        yield wg_await(asyncDoAction(HBShopBuyMainPrizeAction(bundle, showHangarOnClose=True)))

    @adisp_process
    def __showEventHangar(self):
        ct, st, et = self.__getEventTimes()
        if st < ct < et:
            yield g_prbLoader.getDispatcher().doSelectAction(PrbAction(PREBATTLE_ACTION_NAME.HISTORICAL_BATTLES))

    def __showShop(self):
        pass


class HBVehicleRestorePanel(VehiclePreviewHBRestorePanelMeta):
    _restores = dependency.descriptor(IRestoreController)
    _itemsCache = dependency.descriptor(IItemsCache)

    def onBuyClick(self):
        vehicleCD = g_currentPreviewVehicle.item.intCD
        factory.doAction(factory.BUY_VEHICLE, vehicleCD, False, None, None, VIEW_ALIAS.LOBBY_HANGAR)
        return

    def _populate(self):
        super(HBVehicleRestorePanel, self)._populate()
        g_clientUpdateManager.addMoneyCallback(self.__updateData)
        self._restores.onRestoreChangeNotify += self.__updateData
        self.__updateData()

    def _dispose(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        self._restores.onRestoreChangeNotify -= self.__updateData
        super(HBVehicleRestorePanel, self)._dispose()

    def __updateData(self, *args):
        self.as_setBuyDataS(self.__getVO())

    def __getVO(self):
        vehicle = g_currentPreviewVehicle.item
        money = self._itemsCache.items.stats.money
        exchangeRate = self._itemsCache.items.shop.exchangeRate
        priceType, price = getPriceTypeAndValue(vehicle, money, exchangeRate)
        itemPrice = chooseItemPriceVO(priceType, price)
        buttonLabel = backport.text(R.strings.vehicle_preview.buyingPanel.buyBtn.label.restore())
        currency = price.getCurrency(byWeight=True)
        walletAvailable = self.__walletAvailableForCurrency(currency)
        mayObtain = walletAvailable and vehicle.mayObtainWithMoneyExchange(money, exchangeRate)
        restoreInfo = vehicle.restoreInfo
        isMoneyEnough = True
        restoreTitle = backport.text(R.strings.hb_lobby.shopPrize.messageVehicleSold())
        if walletAvailable and not mayObtain:
            if restoreInfo and restoreInfo.isInCooldown():
                restoreTitle = ''
            else:
                isMoneyEnough = False
        shortage = self._itemsCache.items.stats.money.getShortage(price)
        return {'uniqueVehicleTitle': restoreTitle,
         'isMoneyEnough': isMoneyEnough,
         'shortage': shortage,
         'buyButtonEnabled': mayObtain,
         'buyButtonLabel': buttonLabel,
         'price': itemPrice}

    def __buildBuyButtonTooltip(self, key):
        return makeTooltip(backport.text(R.strings.tooltips.vehiclePreview.buyButton.dyn(key).header()), backport.text(R.strings.tooltips.vehiclePreview.buyButton.dyn(key).body()))

    def __buildRestoreButtonTooltip(self, timeLeft):
        timeLeftStr = time_formatters.getTillTimeByResource(timeLeft, R.strings.menu.Time.timeLeftShort, removeLeadingZeros=True)
        return makeTooltip(backport.text(R.strings.tooltips.vehiclePreview.buyButton.restoreRequested.header()), backport.text(R.strings.tooltips.vehiclePreview.buyButton.restoreRequested.body(), timeLeft=timeLeftStr))

    def __walletAvailableForCurrency(self, currency):
        return self._itemsCache.items.stats.currencyStatuses.get(currency) == WalletController.STATUS.AVAILABLE

    def __purchaseSingleVehicle(self, vehicle):
        event_dispatcher.showVehicleBuyDialog(vehicle)
