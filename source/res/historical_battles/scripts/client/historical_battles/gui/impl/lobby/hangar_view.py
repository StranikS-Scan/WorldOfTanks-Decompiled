# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/lobby/hangar_view.py
import logging
from functools import partial
import SoundGroups
import WWISE
import HBAccountSettings
from historical_battles import hb_constants
from frameworks.wulf import ViewFlags, ViewSettings, WindowLayer, Window, WindowStatus, WindowFlags
from gui.Scaleform.Waiting import Waiting
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.managers.containers import POP_UP_CRITERIA
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl.backport import BackportTooltipWindow, createTooltipData
from gui.impl.gen import R
from gui.impl.lobby.hangar_selectable_view import HangarSelectableView
from gui.prb_control.entities.base.squad.entity import SquadEntity
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from gui.shared.utils import SelectorBattleTypesUtils
from helpers import dependency, time_utils
from helpers.CallbackDelayer import CallbackDelayer
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.game_control import IHangarSpaceSwitchController
from skeletons.gui.impl import IGuiLoader
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.utils import IHangarSpace
from historical_battles.gui.sounds.sound_constants import HangarFullscreenState
from historical_battles.gui.impl.gen.view_models.views.lobby.base_frontman_model import FrontmanState
from historical_battles.gui.impl.gen.view_models.views.lobby.battle_mode_model import BattleModeModel, FrontStateType
from historical_battles.gui.impl.gen.view_models.views.lobby.battle_mode_widget_model import DisableReason
from historical_battles.gui.impl.gen.view_models.views.lobby.hangar_view_model import HangarViewModel
from historical_battles.gui.impl.gen.view_models.views.lobby.order_model import OrderModel, OrderType
from historical_battles.gui.impl.lobby.base_event_view import BaseEventView
from historical_battles.gui.impl.lobby.selectable_view_impl import SelectableViewImpl
from historical_battles.gui.impl.lobby.tooltips.ability_tooltip import AbilityTooltip
from historical_battles.gui.impl.lobby.tooltips.battle_mode_info_tooltip import BattleModeInfoTooltip
from historical_battles.gui.impl.lobby.tooltips.frontmen_tooltip import FrontmanTooltip
from historical_battles.gui.impl.lobby.tooltips.hb_coin_tooltip import HbCoinTooltip
from historical_battles.gui.impl.lobby.tooltips.not_profiled_tooltip import NotProfiledTooltip
from historical_battles.gui.impl.lobby.tooltips.order_tooltip import OrderTooltip
from historical_battles.gui.impl.lobby.widgets.frontman_widget import FrontmanWidget
from historical_battles.gui.prb_control import prb_config
from historical_battles.gui.shared.event_dispatcher import openBuyBoosterBundleWindow, showInfoPage, showShopView, showHBProgressionView, showOrdersX15InfoWindow
from historical_battles.gui.sounds.sound_constants import HANGAR_SOUND_SPACE, HBHangarEvents
from historical_battles_common.hb_constants import AccountSettingsKeys, HB_GAME_PARAMS_KEY
from historical_battles.skeletons.gui.game_event_controller import IGameEventController
_logger = logging.getLogger(__name__)
_BACKGROUND_ALPHA = 0.0
_ORDER_ANIMATION_WAIT_TICK = 0.5
_BATTLE_MODE_ANIMATION_WAIT_TICK = 0.5
CHECK_LAYERS = (WindowLayer.OVERLAY,
 WindowLayer.TOP_WINDOW,
 WindowLayer.FULLSCREEN_WINDOW,
 WindowLayer.TOP_SUB_VIEW)

class HangarView(SelectableViewImpl, HangarSelectableView, BaseEventView):
    _COMMON_SOUND_SPACE = HANGAR_SOUND_SPACE
    _lobbyContext = dependency.descriptor(ILobbyContext)
    _itemsCache = dependency.descriptor(IItemsCache)
    _appLoader = dependency.descriptor(IAppLoader)
    _spaceSwitchController = dependency.descriptor(IHangarSpaceSwitchController)
    guiLoader = dependency.descriptor(IGuiLoader)
    _hangarSpace = dependency.descriptor(IHangarSpace)
    __gameEventController = dependency.descriptor(IGameEventController)

    def __init__(self, layoutID):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.LOBBY_SUB_VIEW
        settings.model = HangarViewModel()
        super(HangarView, self).__init__(settings)
        self.__frontmanWidget = FrontmanWidget(self.viewModel)
        self.__needToShowFrontmanProgress = False
        self.__tooltipEnabled = True
        self.__callbackDelayer = CallbackDelayer()

    @property
    def viewModel(self):
        return super(HangarView, self).getViewModel()

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId')
            specialArgs = []
            if tooltipId == TOOLTIPS_CONSTANTS.HB_VEHICLE:
                vehicleId = event.getArgument('vehicleId', None)
                isLocked = event.getArgument('isLocked', False)
                if vehicleId is not None:
                    specialArgs = [int(vehicleId), isLocked]
            window = BackportTooltipWindow(createTooltipData(isSpecial=True, specialAlias=tooltipId, specialArgs=specialArgs), self.getParentWindow())
            window.load()
            return window
        else:
            return super(HangarView, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        if not self.__tooltipEnabled:
            return
        elif contentID == R.views.historical_battles.lobby.tooltips.NotProfiledVehicleTooltip():
            return NotProfiledTooltip()
        elif contentID == R.views.historical_battles.lobby.tooltips.HbCoinTooltip():
            coinType = event.getArgument('coinType')
            if coinType is None:
                _logger.error('HbCoinTooltip must receive a viable coinType param. Received: None')
                return
            return HbCoinTooltip(coinType)
        elif contentID == R.views.historical_battles.lobby.tooltips.OrderTooltip():
            orderType = event.getArgument('orderType')
            isPreview = event.getArgument('isPreview')
            isUsedInBattle = event.getArgument('isUsedInBattle')
            return OrderTooltip(orderType, isPreview, isUsedInBattle)
        elif contentID == R.views.historical_battles.lobby.tooltips.BattleModeInfoTooltip():
            frontName = event.getArgument('frontName')
            return BattleModeInfoTooltip(frontName)
        elif contentID == R.views.historical_battles.lobby.tooltips.AbilityTooltip():
            abilityID = event.getArgument('abilityID')
            isRoleAbility = event.getArgument('isRoleAbility')
            return AbilityTooltip(abilityID, isRoleAbility)
        elif contentID == R.views.historical_battles.lobby.tooltips.FrontmanTooltip():
            frontmanID = event.getArgument('frontmanID')
            showRoleAbility = event.getArgument('showRoleAbility')
            return FrontmanTooltip(frontmanID, showRoleAbility)
        else:
            return super(HangarView, self).createToolTipContent(event, contentID)

    def _onLoading(self, *args, **kwargs):
        super(HangarView, self)._onLoading(*args, **kwargs)
        self.__addEventListeners()
        self.__frontmanWidget.onLoading()
        self.__fillViewModel()
        app = self._appLoader.getApp()
        app.setBackgroundAlpha(_BACKGROUND_ALPHA)

    def _onLoaded(self, *args, **kwargs):
        super(HangarView, self)._onLoaded(*args, **kwargs)
        SelectorBattleTypesUtils.setBattleTypeAsKnown(prb_config.PREBATTLE_ACTION_NAME.HISTORICAL_BATTLES)

    def _onReady(self):
        super(HangarView, self)._onReady()
        self.__gameEventController.updateVehicle()

    def _finalize(self):
        self.__removeEventListeners()
        self.__frontmanWidget.destroy()
        self.__frontmanWidget = None
        self.__callbackDelayer.clearCallbacks()
        super(HangarView, self)._finalize()
        return

    def _highlight3DEntityAndShowTT(self, entity):
        tooltipMgr = self._appLoader.getApp().getToolTipMgr()
        self.showTooltipOnEntity(tooltipMgr, TOOLTIPS_CONSTANTS.HANGAR_INTERACTIVE_OBJECT, entity)

    def _fade3DEntityAndHideTT(self, entity):
        tooltipMgr = self._appLoader.getApp().getToolTipMgr()
        self.hideTooltipOnEntity(tooltipMgr, TOOLTIPS_CONSTANTS.HANGAR_INTERACTIVE_OBJECT, entity)

    def __addEventListeners(self):
        self.viewModel.onFrontmanChanged += self.__onFrontmanChanged
        self.viewModel.onEscapePressed += self.__onEscape
        self.viewModel.orders.onIconAnimationStart += self.__onOrderIconAnimationStart
        self.viewModel.orders.onIconAnimationFinish += self.__onOrderIconAnimationFinish
        self.viewModel.orders.onBorderAnimationStart += self.__onOrderBorderAnimationStart
        self.viewModel.orders.onBorderAnimationFinish += self.__onOrderBorderAnimationFinish
        self.viewModel.orders.onBuyOrdersPressed += self.__onBuyOrderPressed
        self.viewModel.orders.onGetOrdersPressed += self.__onGetOrderPressed
        self.viewModel.battleModeWidget.onBattleModeChanged += self.__onBattleModeChanged
        self.viewModel.shopButton.onShopButtonClick += self.__onShopButtonClick
        self.viewModel.progressionButton.onProgressionButtonClick += self.__onProgressionButtonClick
        self.viewModel.onInfoClick += self.__onInfoClick
        self.viewModel.onCloseClick += self.__onCloseClick
        self.viewModel.onMousePressed += self.__onMousePressed
        self._gameEventController.onFrontmanLockChanged += self.__onFrontmanLockChanged
        self._gameEventController.onQuestsUpdated += self.__onQuestsSyncCompleted
        self._gameEventController.onProgressChanged += self.__onQuestsSyncCompleted
        self._lobbyContext.getServerSettings().onServerSettingsChange += self.__onSettingsChanged
        self._gameEventController.onFrontmanVehicleChanged += self.__onVehicleChanged
        self._gameEventController.onSelectedFrontmanChanged += self.__onSelectedFrontmanChanged
        self._gameEventController.onSelectedFrontChanged += self.__onSelectedFrontChanged
        self._gameEventController.onDisableFrontsWidget += self.__onDisableFrontsWidget
        self.guiLoader.windowsManager.onWindowStatusChanged += self.__onWindowStatusChanged
        self._gameEventController.onFrontTimeStatusUpdated += self.__updateBattleModes
        self._gameEventController.coins.onCoinsCountChanged += self.__onCoinsCountChanged
        frontCoupons = self._gameEventController.frontCoupons
        if frontCoupons:
            frontCoupons.onFrontCouponsUpdated += self.__onFrontCouponsUpdated

    def __removeEventListeners(self):
        self.viewModel.onFrontmanChanged -= self.__onFrontmanChanged
        self.viewModel.onEscapePressed -= self.__onEscape
        self.viewModel.orders.onIconAnimationStart -= self.__onOrderIconAnimationStart
        self.viewModel.orders.onIconAnimationFinish -= self.__onOrderIconAnimationFinish
        self.viewModel.orders.onBorderAnimationStart -= self.__onOrderBorderAnimationStart
        self.viewModel.orders.onBorderAnimationFinish -= self.__onOrderBorderAnimationFinish
        self.viewModel.orders.onBuyOrdersPressed -= self.__onBuyOrderPressed
        self.viewModel.orders.onGetOrdersPressed -= self.__onGetOrderPressed
        self.viewModel.battleModeWidget.onBattleModeChanged -= self.__onBattleModeChanged
        self.viewModel.shopButton.onShopButtonClick -= self.__onShopButtonClick
        self.viewModel.progressionButton.onProgressionButtonClick -= self.__onProgressionButtonClick
        self.viewModel.onInfoClick -= self.__onInfoClick
        self.viewModel.onCloseClick -= self.__onCloseClick
        self.viewModel.onMousePressed -= self.__onMousePressed
        self._gameEventController.onFrontmanLockChanged -= self.__onFrontmanLockChanged
        self._gameEventController.onQuestsUpdated -= self.__onQuestsSyncCompleted
        self._gameEventController.onProgressChanged -= self.__onQuestsSyncCompleted
        self._lobbyContext.getServerSettings().onServerSettingsChange -= self.__onSettingsChanged
        self._gameEventController.onFrontmanVehicleChanged -= self.__onVehicleChanged
        self._gameEventController.onSelectedFrontmanChanged -= self.__onSelectedFrontmanChanged
        self._gameEventController.onSelectedFrontChanged -= self.__onSelectedFrontChanged
        self._gameEventController.onDisableFrontsWidget -= self.__onDisableFrontsWidget
        self.guiLoader.windowsManager.onWindowStatusChanged -= self.__onWindowStatusChanged
        self._gameEventController.onFrontTimeStatusUpdated -= self.__updateBattleModes
        coins = self._gameEventController.coins
        if coins:
            coins.onCoinsCountChanged -= self.__onCoinsCountChanged
        frontCoupons = self._gameEventController.frontCoupons
        if frontCoupons:
            frontCoupons.onFrontCouponsUpdated -= self.__onFrontCouponsUpdated

    def __fillViewModel(self):
        with self.viewModel.transaction() as tx:
            tx.setSelectedFrontmanId(self._gameEventController.frontController.getSelectedFrontmanID())
            self.__fillFrontmenCarousel(tx)
            self.__fillBattleModes(tx)
            self.__fillOrders(tx)
            self.__fillShopButton(tx)
            self.__frontmanWidget.updateModel(tx)
            self.__updadeStatusFrontWidget(tx)

    def __fillFrontmenCarousel(self, tx):
        gameEventController = self._gameEventController
        frontmen = tx.getFrontmen()
        frontmen.clear()
        frontmenItems = gameEventController.frontController.getFrontmenForSelectedFront()
        for frontmanItem in frontmenItems.values():
            model = self.__frontmanWidget.createFrontmanModel(frontmanItem)
            if model is not None:
                frontmen.addViewModel(model)

        frontmen.invalidate()
        return

    def __fillOrders(self, tx):
        orders = tx.orders.getOrders()
        showOrderAnimation = self.__animationCanBeShown()
        rechargeTime = 0
        rechargeableFrontCoupon = self._gameEventController.frontCoupons.getRechargeableFrontCoupon()
        if rechargeableFrontCoupon is not None and not rechargeableFrontCoupon.getCurrentCount():
            rechargeTime = rechargeableFrontCoupon.getNextRechargeTime()
        tx.orders.setOrderCountdown(rechargeTime)
        activeFrontCoupon = self._gameEventController.frontCoupons.getActiveFrontCoupon()
        tx.orders.setSelectedOrderId(activeFrontCoupon.getLabel() if activeFrontCoupon and activeFrontCoupon.isDrawActive() else '')
        orders.clear()
        frontCoupons = self._gameEventController.frontCoupons.getGroupedFrontCoupons()
        for frontCoupon in frontCoupons:
            if not frontCoupon.isDrawActive():
                continue
            model = self.__createOrderModel(frontCoupon, showOrderAnimation)
            orders.addViewModel(model)

        orders.invalidate()
        if showOrderAnimation:
            self._gameEventController.frontCoupons.markFrontCouponsAsViewed()
        else:
            self.__startWindowsPollingForAnimation()
        return

    def __startWindowsPollingForAnimation(self):
        if not self.__callbackDelayer.hasDelayedCallback(self.__onShowOrderAnimation):
            self.__callbackDelayer.delayCallback(_ORDER_ANIMATION_WAIT_TICK, self.__onShowOrderAnimation)
        if not self.__callbackDelayer.hasDelayedCallback(self.__onShowBattleModeAnimation()):
            self.__callbackDelayer.delayCallback(_BATTLE_MODE_ANIMATION_WAIT_TICK, self.__onShowBattleModeAnimation)

    def __createOrderModel(self, frontCoupon, showOrderAnimation):
        order = OrderModel()
        order.setId(frontCoupon.getLabel())
        order.setType(hb_constants.MultiplierToOrderType.get(frontCoupon.getModifier(), OrderType.SMALL))
        order.setCount(frontCoupon.getCurrentCount())
        order.setIsActive(frontCoupon.isActive())
        if showOrderAnimation:
            coupons = self._gameEventController.frontCoupons.getGroupedFrontCoupons()
            animateOtherIcon = any((coupon.needToShowAnimation() and not frontCoupon == coupon for coupon in coupons))
            animateThisIcon = frontCoupon.needToShowAnimation()
            order.setIsIconAnimated(animateThisIcon)
            order.setIsBorderAnimated(frontCoupon.isActive() and (not animateOtherIcon or animateThisIcon))
        return order

    def __onFrontCouponsUpdated(self):
        with self.viewModel.transaction() as tx:
            self.__fillOrders(tx)

    def __onShowOrderAnimation(self):
        if self.__animationCanBeShown():
            self.__onFrontCouponsUpdated()
            return None
        else:
            return _ORDER_ANIMATION_WAIT_TICK

    def __onShowBattleModeAnimation(self):
        if self.__animationCanBeShown():
            with self.viewModel.transaction() as tx:
                self.__fillBattleModes(tx)
            return
        else:
            return _BATTLE_MODE_ANIMATION_WAIT_TICK

    def __fillShopButton(self, tx):
        shopButtonModel = tx.shopButton
        isNew = not HBAccountSettings.getNotifications(AccountSettingsKeys.SEEN_HISTORICAL_BATTLES_SHOP)
        shopButtonModel.setIsNew(isNew)
        shopButtonModel.setIsHighlighted(True)

    def __fillBattleModes(self, tx):
        modes = tx.battleModeWidget.getBattleModes()
        modes.clear()
        currentSelectedFront = self._gameEventController.frontController.getSelectedFront()
        latestFront = self._gameEventController.frontController.getLatestFront()
        if latestFront is not None and not self._gameEventController.frontController.isFrontSeen(latestFront.getID()):
            currentSelectedFront = latestFront
        for front in self._gameEventController.frontController.getOrderedFrontsList():
            modes.addViewModel(self.__createBattleMode(front))

        if currentSelectedFront is None:
            return
        else:
            frontName = currentSelectedFront.getName()
            self.__onBattleModeChanged({'frontName': frontName})
            self.__updateSelectedFront(frontName)
            modes.invalidate()
            self.__updateBattleModesProgress()
            canShowAnimation = self.__animationCanBeShown()
            tx.battleModeWidget.setCanShowAnimation(canShowAnimation)
            if not canShowAnimation:
                self.__startWindowsPollingForAnimation()
            return

    def __updadeStatusFrontWidget(self, tx):
        if isinstance(self.prbEntity, SquadEntity):
            tx.battleModeWidget.setIsDisabled(not self.prbEntity.isCommander())

    def __onDisableFrontsWidget(self, isDisabled):
        with self.viewModel.transaction() as tx:
            if isDisabled:
                tx.battleModeWidget.setDisableReason(DisableReason.NOTPLATOONLEADER)
            tx.battleModeWidget.setIsDisabled(isDisabled)

    def __onCoinsCountChanged(self, coinName):
        self.__updateFrontsCoins((self._gameEventController.frontController.getFrontByCoinName(coinName).getID(),))

    def __updateBattleModesProgress(self):
        self.__updateFrontsCoins(self._gameEventController.frontController.getFronts().keys())

    def __updateFrontsCoins(self, frontsIDs):
        with self.viewModel.transaction() as tx:
            modes = tx.battleModeWidget.getBattleModes()
            for frontID in frontsIDs:
                front = self._gameEventController.frontController.getFrontByID(frontID)
                mode = next((m for m in tx.battleModeWidget.getBattleModes() if m.getFrontName() == front.getName()), None)
                if mode:
                    mode.earnings.setAmount(self._gameEventController.coins.getCount(front.getCoinsName()))

            modes.invalidate()
        return

    def __onSettingsChanged(self, diff):
        if HB_GAME_PARAMS_KEY not in diff:
            return
        self.__updateBattleModes()

    def __updateBattleModes(self, *_):
        with self.viewModel.transaction() as tx:
            self.__updateBattleModeStates(tx)

    def __onQuestsSyncCompleted(self):
        with self.viewModel.transaction() as tx:
            self.__updateBattleModeStates(tx)
            if self.__hasOverlappingWindows():
                self.__needToShowFrontmanProgress = True
            else:
                self.__onFrontmanProgressChanged(model=tx)

    def __onEscape(self):
        dialogsContainer = self._appLoader.getApp().containerManager.getContainer(WindowLayer.TOP_WINDOW)
        if not dialogsContainer.getView(criteria={POP_UP_CRITERIA.VIEW_ALIAS: VIEW_ALIAS.LOBBY_MENU}):
            g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.LOBBY_MENU)), scope=EVENT_BUS_SCOPE.LOBBY)

    def __onOrderIconAnimationStart(self, args):
        SoundGroups.g_instance.playSound2D(HBHangarEvents.ORDER_ANIMATION)

    def __onOrderIconAnimationFinish(self, args):
        orderID = args.get('id')
        for order in self.viewModel.orders.getOrders():
            if order.getId() == orderID:
                order.setIsIconAnimated(False)
                break

    def __onOrderBorderAnimationStart(self, args):
        SoundGroups.g_instance.playSound2D(HBHangarEvents.ORDER_ANIMATION)

    def __onOrderBorderAnimationFinish(self, args):
        orderID = args.get('id')
        for order in self.viewModel.orders.getOrders():
            if order.getId() == orderID:
                order.setIsBorderAnimated(False)
                break

    @staticmethod
    def __onBuyOrderPressed():
        openBuyBoosterBundleWindow()

    @staticmethod
    def __onGetOrderPressed():
        showOrdersX15InfoWindow()

    def __createBattleMode(self, front):
        battleMode = BattleModeModel()
        battleMode.setFrontName(front.getName())
        battleMode.setFrontState(FrontStateType.SOON)
        battleMode.earnings.setType(front.getCoinsName())
        self.__updateBattleModeState(battleMode)
        return battleMode

    def __updateBattleModeStates(self, tx, currentMode=None):
        modes = tx.battleModeWidget.getBattleModes()
        if currentMode is None:
            currentMode = tx.battleModeWidget.getSelectedMode()
        for mode in modes:
            self.__updateBattleModeState(mode)
            if mode.getFrontName() == currentMode:
                frontState = mode.getFrontState()
                tx.battleModeWidget.setIsSelectedModeAvailable(frontState == FrontStateType.AVAILABLE or frontState == FrontStateType.HIGHLIGHTED)

        modes.invalidate()
        return

    def __updateBattleModeState(self, mode):
        front = self._gameEventController.frontController.getFrontByName(mode.getFrontName())
        if front is None:
            return
        else:
            enabled = front.isEnabled()
            startTimeLeft = time_utils.getTimeDeltaFromNow(front.getStartTime())
            mode.setCountDownSeconds(startTimeLeft)
            if enabled:
                if startTimeLeft <= 0:
                    isFrontSeen = self._gameEventController.frontController.isFrontSeen(front.getID())
                    mode.setFrontState(FrontStateType.AVAILABLE if isFrontSeen else FrontStateType.HIGHLIGHTED)
                else:
                    mode.setFrontState(FrontStateType.COUNTDOWN)
            else:
                mode.setFrontState(FrontStateType.SOON)
            return

    def __onFrontmanLockChanged(self):
        with self.viewModel.transaction() as tx:
            for frontman in tx.getFrontmen():
                frontmen = self._gameEventController.frontController.getFrontmenForSelectedFront()
                frontmanItem = frontmen.get(int(frontman.getId()))
                if frontmanItem and frontmanItem.isInBattle():
                    frontman.setState(FrontmanState.INBATTLE)
                if frontmanItem and frontmanItem.isInUnit():
                    frontman.setState(FrontmanState.INPLATOON)
                frontman.setState(FrontmanState.DEFAULT)

            self.__frontmanWidget.updateModel(tx)

    def __onFrontmanProgressChanged(self, model=None):
        self.__needToShowFrontmanProgress = False
        self.__frontmanWidget.updateModel(model)

    def __onFrontmanChanged(self, args):
        frontmanID = args.get('id')
        if frontmanID is None:
            return
        else:
            front = self._gameEventController.frontController.getSelectedFront()
            if front.setSelectedFrontmanID(frontmanID):
                self._gameEventController.setSelectedFrontmanID(frontmanID)
            return

    def __onSelectedFrontChanged(self):
        self.__updateSelectedFront(self._gameEventController.frontController.getSelectedFront().getName())
        self.__onSelectedFrontmanChanged()

    def __onBattleModeChanged(self, args):
        frontName = args.get('frontName')
        front = self._gameEventController.frontController.getFrontByName(frontName)
        self._gameEventController.frontController.setSelectedFrontID(front.getID())

    def __updateSelectedFront(self, frontName):
        with self.viewModel.transaction() as tx:
            tx.battleModeWidget.setSelectedMode(frontName)
            self.__updateBattleModeStates(tx, frontName)
            self.__fillFrontmenCarousel(tx)

    def __onShopButtonClick(self):
        HBAccountSettings.setNotifications(AccountSettingsKeys.SEEN_HISTORICAL_BATTLES_SHOP, True)
        showShopView()

    def __onProgressionButtonClick(self):
        showHBProgressionView()

    def __onVehicleChanged(self):
        with self.viewModel.transaction() as tx:
            self.__frontmanWidget.updateFrontmanVehicle(tx)
            self._gameEventController.updateVehicle()

    def __onSelectedFrontmanChanged(self):
        with self.viewModel.transaction() as tx:
            self.__frontmanWidget.updateModel(tx)
            frontmanId = self._gameEventController.frontController.getSelectedFrontmanID()
            tx.setSelectedFrontmanId(frontmanId)

    def __onWindowStatusChanged(self, uniqueID, newStatus):
        if newStatus == WindowStatus.DESTROYING:
            window = self.guiLoader.windowsManager.getWindow(uniqueID)
            if window.layer in CHECK_LAYERS:
                self.__startWindowsPollingForAnimation()
        hasOverlappingWindows = self.__hasOverlappingWindows(uniqueID if newStatus == WindowStatus.CREATED else None)
        if self.__needToShowFrontmanProgress and not hasOverlappingWindows:
            with self.viewModel.transaction() as tx:
                self.__onFrontmanProgressChanged(model=tx)
        newTooltipEnabled = not hasOverlappingWindows
        if newTooltipEnabled != self.__tooltipEnabled:
            if not newTooltipEnabled:
                self.notifyCursorOver3DScene(False)
                tooltips = self.guiLoader.windowsManager.findWindows(lambda w: w.content is not None and w.typeFlag == WindowFlags.TOOLTIP)
                for tooltip in tooltips:
                    tooltip.destroy()

            self.__tooltipEnabled = newTooltipEnabled
        return

    @staticmethod
    def __isOverlappingWindow(excludedUniqueId, window):
        return window.uniqueID != excludedUniqueId and window.windowStatus in (WindowStatus.LOADING, WindowStatus.LOADED) and window.layer in CHECK_LAYERS

    def __hasOverlappingWindows(self, excludedUniqueId=None):
        return self.guiLoader.windowsManager.findWindows(partial(self.__isOverlappingWindow, excludedUniqueId))

    @staticmethod
    def __onInfoClick():
        showInfoPage()

    def __onCloseClick(self):
        self.__gameEventController.selectRandomMode()
        self.destroyWindow()

    def __onMousePressed(self, args):
        WWISE.WW_setState(HangarFullscreenState.GROUP, HangarFullscreenState.OPEN if args.get('isPressed', False) else HangarFullscreenState.CLOSE)

    def __animationCanBeShown(self):
        return not Waiting.isVisible() and not self.__hasOverlappingWindows()
