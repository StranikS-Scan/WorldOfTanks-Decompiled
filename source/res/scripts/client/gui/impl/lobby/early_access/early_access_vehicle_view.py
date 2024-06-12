# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/early_access/early_access_vehicle_view.py
import typing
from CurrentVehicle import g_currentPreviewVehicle
from frameworks.wulf import ViewFlags, ViewSettings
from gui.Scaleform.daapi.view.lobby.techtree.techtree_dp import g_techTreeDP
from gui.Scaleform.daapi.view.lobby.vehicle_preview.sound_constants import RESEARCH_PREVIEW_SOUND_SPACE
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.hangar_cameras.hangar_camera_common import CameraRelatedEvents
from gui.impl.backport.backport_tooltip import createTooltipData
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.early_access.early_access_animation_params import EarlyAccessAnimationParams
from gui.impl.gen.view_models.views.lobby.early_access.early_access_vehicle_model import EarlyAccessVehicleModel, State
from gui.impl.gen.view_models.views.lobby.early_access.early_access_vehicle_view_model import EarlyAccessVehicleViewModel
from gui.impl.lobby.common.vehicle_model_helpers import fillVehicleModel
from gui.impl.lobby.common.view_wrappers import createBackportTooltipDecorator
from gui.impl.lobby.early_access.early_access_window_events import showEarlyAccessInfoPage, showBuyTokensWindow, showEarlyAccessVehicleView, showEarlyAccessQuestsView
from gui.impl.lobby.early_access.sounds import setResearchesPreviewSoundState
from gui.impl.lobby.early_access.tooltips.early_access_currency_tooltip_view import EarlyAccessCurrencyTooltipView
from gui.impl.lobby.early_access.tooltips.early_access_state_tooltip import EarlyAccessStateTooltipView
from gui.impl.pub import ViewImpl
from gui.impl.wrappers.user_compound_price_model import BuyPriceModelBuilder
from gui.shared import event_dispatcher
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.event_dispatcher import showVehicleBuyDialog, showVehiclePreview
from gui.shared.events import LobbySimpleEvent
from gui.shared.gui_items import GUI_ITEM_TYPE
from helpers import dependency, time_utils
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.game_control import IEarlyAccessController, IVehicleComparisonBasket
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    import Event
    from gui.shared.gui_items.Vehicle import Vehicle
    from frameworks.wulf import ViewEvent, View, Window

class EarlyAccessVehicleView(ViewImpl):
    __slots__ = ('__currentVehicleCD', '__isFromTechTree', '__isAnimationFreeze')
    __itemsCache = dependency.descriptor(IItemsCache)
    __earlyAccessController = dependency.descriptor(IEarlyAccessController)
    __comparisonBasket = dependency.descriptor(IVehicleComparisonBasket)
    __appLoader = dependency.descriptor(IAppLoader)
    _COMMON_SOUND_SPACE = RESEARCH_PREVIEW_SOUND_SPACE

    def __init__(self, layoutID, isFromTechTree=False, selectedVehicleCD=None):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.LOBBY_SUB_VIEW
        settings.model = EarlyAccessVehicleViewModel()
        super(EarlyAccessVehicleView, self).__init__(settings)
        self.__isFromTechTree = isFromTechTree
        self.__currentVehicleCD = selectedVehicleCD
        self.__isAnimationFreeze = False

    @property
    def viewModel(self):
        return super(EarlyAccessVehicleView, self).getViewModel()

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(EarlyAccessVehicleView, self).createToolTip(event)

    def getTooltipData(self, event):
        vehicleCD = event.getArgument('vehicleCD')
        data = createTooltipData(isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.CAROUSEL_VEHICLE, specialArgs=[vehicleCD])
        return data

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.early_access.tooltips.EarlyAccessCurrencyTooltipView():
            return EarlyAccessCurrencyTooltipView()
        return EarlyAccessStateTooltipView(event.getArgument('state')) if contentID == R.views.lobby.early_access.tooltips.EarlyAccessSimpleTooltipView() else super(EarlyAccessVehicleView, self).createToolTipContent(event, contentID)

    @staticmethod
    def getVehicleState(vehicle, isNext2Unlock):
        if vehicle.isInInventory:
            return State.ININVENTORY
        if vehicle.isUnlocked:
            return State.PURCHASABLE
        return State.INPROGRESS if isNext2Unlock else State.LOCKED

    def _initialize(self, *args, **kwargs):
        super(EarlyAccessVehicleView, self)._initialize(*args, **kwargs)
        app = self.__appLoader.getApp()
        app.setBackgroundAlpha(0)
        self.__earlyAccessController.hangarFeatureState.enter(self.layoutID, activateVehicleState=True)

    def _finalize(self):
        self.__earlyAccessController.hangarFeatureState.exit(self.layoutID)
        self.soundManager.playSound('comp_7_progressbar_stop')
        super(EarlyAccessVehicleView, self)._finalize()

    def _onLoading(self, *args, **kwargs):
        super(EarlyAccessVehicleView, self)._onLoading(*args, **kwargs)
        g_techTreeDP.load()
        self.__updateModel(shouldUpdateSelectedVehicle=self.__currentVehicleCD is None)
        return

    def _getEvents(self):
        return ((self.__earlyAccessController.onUpdated, self.__onUpdated),
         (self.__earlyAccessController.onBalanceUpdated, self.__onBalanceUpdated),
         (self.__itemsCache.onSyncCompleted, self.__onInventoryUpdate),
         (self.viewModel.onSelectVehicle, self.__onVehicleSelected),
         (self.viewModel.onCompare, self.__onCompare),
         (self.viewModel.onShowVehiclePreview, self.__onShowVehiclePreview),
         (self.viewModel.onShowInHangar, self.__onShowInHangar),
         (self.viewModel.onBuyVehicle, self.__onBuyVehicle),
         (self.viewModel.onAboutEvent, showEarlyAccessInfoPage),
         (self.viewModel.onBackToHangar, self.__onBackToHangar),
         (self.viewModel.onBackToPrevScreen, self.__onBackToPrevScreen),
         (self.viewModel.onBuyTokens, self.__onShowBuyView),
         (self.viewModel.onGoToQuests, self.__onShowQuestsView),
         (self.viewModel.onStartMoving, self.__onStartMoving),
         (self.viewModel.onMoveSpace, self.__onMoveSpace))

    def __updateModel(self, shouldUpdateSelectedVehicle=True, showCarouselSliderAnimation=False):
        startDate, endDate = self.__earlyAccessController.getSeasonInterval()
        currentTime = time_utils.getServerUTCTime()
        _, endProgressionDate = self.__earlyAccessController.getProgressionTimes()
        with self.viewModel.transaction() as model:
            model.setStartDate(startDate)
            model.setEndDate(endDate)
            model.setCurrentDate(currentTime)
            model.setEndProgressionDate(endProgressionDate)
            model.setFeatureState(self.__earlyAccessController.getState().value)
            model.setIsFromTechTree(self.__isFromTechTree)
            if shouldUpdateSelectedVehicle:
                self.__updateSelectedVehicle(model)
            model.setCurrentVehicleCD(self.__currentVehicleCD)
            self.__fillVehicles(model, showCarouselSliderAnimation)
            model.setTokensBalance(self.__earlyAccessController.getTokensBalance())

    def __fillVehicles(self, model, showCarouselSliderAnimation=False):
        vehicles = (self.__itemsCache.items.getItemByCD(cd) for cd in self.__earlyAccessController.getAffectedVehicles().iterkeys())
        vehicles = sorted(vehicles, key=lambda vehicle: vehicle.level)
        vehicleModelArray = model.getVehicles()
        prevVehiclesStates = tuple((vModel.getState() for vModel in vehicleModelArray))
        vehicleModelArray.clear()
        for idx, veh in enumerate(vehicles):
            vModel = EarlyAccessVehicleModel()
            fillVehicleModel(vModel, veh)
            price = self.__earlyAccessController.getVehiclePrice(veh.compactDescr)
            isNext2Unlock, unlockProps = g_techTreeDP.isNext2Unlock(veh.compactDescr, unlocked=self.__itemsCache.items.stats.unlocks, xps=self.__itemsCache.items.stats.vehiclesXPs)
            state = self.getVehicleState(veh, isNext2Unlock)
            if showCarouselSliderAnimation:
                self.__setAnimationParams(vModel.animationParams, prevVehiclesStates[idx], state, model.getTokensBalance(), price)
            vModel.setState(state)
            vModel.setPrice(price)
            vModel.setIsPostProgression(veh.compactDescr in self.__earlyAccessController.getPostProgressionVehicles())
            if state in (State.LOCKED, State.INPROGRESS):
                vModel.setUnlockPriceAfterEA(unlockProps.xpCost)
            elif state == State.PURCHASABLE:
                BuyPriceModelBuilder.clearPriceModel(vModel.commonPrice)
                BuyPriceModelBuilder.fillPriceModelByItemPrice(vModel.commonPrice, veh.getBuyPrice())
                result, _ = veh.mayPurchase(self.__itemsCache.items.stats.money)
                vModel.setIsAffordable(result)
            vehicleModelArray.addViewModel(vModel)

        vehicleModelArray.invalidate()

    def __setAnimationParams(self, animationParams, prevState, newState, prevBalance, vehPrice):
        newBalance = self.__earlyAccessController.getTokensBalance()
        animationMap = {(State.INPROGRESS, State.INPROGRESS): (prevBalance, newBalance),
         (State.INPROGRESS, State.ININVENTORY): (prevBalance, vehPrice),
         (State.LOCKED, State.INPROGRESS): (0, newBalance),
         (State.LOCKED, State.ININVENTORY): (0, vehPrice)}
        start, end = animationMap.get((prevState, newState), (0, 0))
        animationParams.setStart(start)
        animationParams.setEnd(end)

    def __onVehicleSelected(self, event):
        self.__earlyAccessController.cgfCameraManager.resetCameraTarget(duration=1)
        self.__currentVehicleCD = int(event.get(EarlyAccessVehicleViewModel.ARG_VEHICLE_CD, 0))
        self.viewModel.setCurrentVehicleCD(self.__currentVehicleCD)
        g_currentPreviewVehicle.selectVehicle(self.__currentVehicleCD)

    def __onCompare(self, event):
        vehicleCD = int(event.get(EarlyAccessVehicleViewModel.ARG_VEHICLE_CD, 0))
        self.__comparisonBasket.addVehicle(vehicleCD)

    def __onShowVehiclePreview(self, event):
        self.destroy()
        vehicleCD = int(event.get(EarlyAccessVehicleViewModel.ARG_VEHICLE_CD, 0))
        showVehiclePreview(vehicleCD, previewBackCb=self.__previewBackCallback, isFromVehicleView=True)

    def __onShowInHangar(self, event):
        self.destroy()
        vehicleCD = int(event.get(EarlyAccessVehicleViewModel.ARG_VEHICLE_CD, 0))
        event_dispatcher.selectVehicleInHangar(vehicleCD)

    def __onShowBuyView(self):
        self.__isAnimationFreeze = True
        showBuyTokensWindow(parent=self.getWindow(), backCallback=self.__buyViewBackCallback)

    def __onShowQuestsView(self):
        self.__earlyAccessController.hangarFeatureState.enter(R.views.lobby.early_access.EarlyAccessMainView())
        self.destroy()
        showEarlyAccessQuestsView()

    def __onBuyVehicle(self, event):
        vehicleCD = int(event.get(EarlyAccessVehicleViewModel.ARG_VEHICLE_CD, 0))
        vehicle = self.__itemsCache.items.getItemByCD(vehicleCD)
        showVehicleBuyDialog(vehicle)

    def __onBackToHangar(self):
        self.destroy()
        event_dispatcher.showHangar()

    def __onBackToPrevScreen(self):
        self.destroy()
        event_dispatcher.showTechTree(self.__currentVehicleCD)

    def __buyViewBackCallback(self):
        self.__isAnimationFreeze = False
        self.__onBalanceUpdated()
        setResearchesPreviewSoundState()

    def __previewBackCallback(self):
        showEarlyAccessVehicleView(isFromTechTree=self.__isFromTechTree, selectedVehicleCD=self.__currentVehicleCD)

    def __updateSelectedVehicle(self, model):
        currProgressVehicleCD = self.__earlyAccessController.getCurrProgressVehicleCD()
        if self.__currentVehicleCD != currProgressVehicleCD:
            self.__currentVehicleCD = currProgressVehicleCD
            g_currentPreviewVehicle.selectVehicle(self.__currentVehicleCD)

    def __onUpdated(self):
        eaCtrl = self.__earlyAccessController
        if not eaCtrl.isEnabled() or eaCtrl.isPaused():
            self.__onBackToHangar()
            return
        self.__updateModel()

    def __onBalanceUpdated(self):
        if not self.__isAnimationFreeze:
            self.__updateModel(shouldUpdateSelectedVehicle=False, showCarouselSliderAnimation=True)

    def __onInventoryUpdate(self, _, invDiff):
        if GUI_ITEM_TYPE.VEHICLE in invDiff:
            changedEAVehicles = invDiff[GUI_ITEM_TYPE.VEHICLE] & set(self.__earlyAccessController.getAffectedVehicles().keys())
            if changedEAVehicles:
                purchasableVehicles = set((veh.getVehicleCD() for veh in self.viewModel.getVehicles() if veh.getState() == State.PURCHASABLE))
                if changedEAVehicles & purchasableVehicles:
                    self.__updateModel(shouldUpdateSelectedVehicle=False)

    def __onStartMoving(self):
        g_eventBus.handleEvent(LobbySimpleEvent(LobbySimpleEvent.NOTIFY_CURSOR_OVER_3DSCENE, ctx={'isOver3dScene': True}), EVENT_BUS_SCOPE.GLOBAL)

    def __onMoveSpace(self, args=None):
        if args is None:
            return
        else:
            g_eventBus.handleEvent(CameraRelatedEvents(CameraRelatedEvents.LOBBY_VIEW_MOUSE_MOVE, ctx={'dx': args.get('dx'),
             'dy': args.get('dy'),
             'dz': args.get('dz')}), EVENT_BUS_SCOPE.GLOBAL)
            return
