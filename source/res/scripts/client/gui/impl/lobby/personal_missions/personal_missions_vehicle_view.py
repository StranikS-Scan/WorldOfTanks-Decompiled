# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/personal_missions/personal_missions_vehicle_view.py
import typing
from CurrentVehicle import g_currentPreviewVehicle
from frameworks.wulf import ViewFlags, ViewSettings
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.hangar_cameras.hangar_camera_common import CameraRelatedEvents
from gui.impl import backport
from gui.impl.backport import createTooltipData
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.personal_missions.personal_missions_main_quests_view_model import PageViewIdEnum
from gui.impl.gen.view_models.views.lobby.personal_missions.personal_missions_vehicle_view_model import PersonalMissionsVehicleViewModel
from gui.impl.gen.view_models.views.lobby.personal_missions.pm3_vehicle_model import State
from gui.impl.lobby.buy_vehicle_view import VehicleBuyActionTypes
from gui.impl.lobby.common.vehicle_model_helpers import fillVehicleModel
from gui.impl.lobby.common.view_wrappers import createBackportTooltipDecorator
from gui.impl.lobby.personal_missions.personal_mission_bonuses_packers import packBonusModelAndTooltipData
from gui.impl.lobby.personal_missions.personal_missions_window_events import showPersonalMissionsVehicleView, showPersonalMissionsOperationWindow
from gui.impl.pub import ViewImpl
from gui.server_events.pm3_constants import SOUNDS
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.event_dispatcher import showVehiclePreview, selectVehicleInHangar
from gui.shared.events import LobbySimpleEvent
from gui.shared.formatters import text_styles
from gui.shared.gui_items.items_actions import factory as ItemsActionsFactory
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.game_control import IPersonalMissionsController, IVehicleComparisonBasket, IHangarFeatureStateController
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    import Event
    from gui.shared.gui_items.Vehicle import Vehicle
    from frameworks.wulf import ViewEvent, Window

class PersonalMissionsVehicleView(ViewImpl):
    __slots__ = ('__isAnimationPlaying', '__hasDelayedBalanceUpdates', '__currentVehicleCD', '__isFromTechTree', '__isAnimationFreeze', '__operationId', '__operation', '__tooltipData')
    __personalMissionsController = dependency.descriptor(IPersonalMissionsController)
    __appLoader = dependency.descriptor(IAppLoader)
    __itemsCache = dependency.descriptor(IItemsCache)
    __comparisonBasket = dependency.descriptor(IVehicleComparisonBasket)
    __hangarFeatureStateController = dependency.descriptor(IHangarFeatureStateController)

    def __init__(self, layoutID, operationId=8):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.LOBBY_SUB_VIEW
        settings.model = PersonalMissionsVehicleViewModel()
        super(PersonalMissionsVehicleView, self).__init__(settings)
        self.__operation = self.__personalMissionsController.getOperationById(operationId)
        self.__currentVehicleCD = self.__operation.getVehicleBonus().intCD
        self.__isAnimationFreeze = False
        self.__isAnimationPlaying = False
        self.__hasDelayedBalanceUpdates = False
        self.__operationId = operationId
        self.__tooltipData = {}

    def _onShown(self):
        super(PersonalMissionsVehicleView, self)._onShown()
        self.soundManager.setState(SOUNDS.STATE_PLACE, SOUNDS.STATE_OPERATION_REWARD_PREVIEW_SCREEN)
        self.__hangarFeatureStateController.enter(self.layoutID, doHideHeader=False)

    @property
    def viewModel(self):
        return super(PersonalMissionsVehicleView, self).getViewModel()

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(PersonalMissionsVehicleView, self).createToolTip(event)

    def getTooltipData(self, event):
        tooltipDossierData = self.__getBackportTooltipData(event)
        if tooltipDossierData is not None:
            return tooltipDossierData
        else:
            vehicleCD = event.getArgument('vehicleCD')
            data = createTooltipData(isSpecial=True, specialAlias=TOOLTIPS_CONSTANTS.CAROUSEL_VEHICLE, specialArgs=[vehicleCD])
            return data

    @staticmethod
    def getVehicleState(vehicle):
        if vehicle.isInInventory:
            return State.ININVENTORY
        if vehicle.isRestoreAvailable():
            return State.PURCHASABLE
        return State.LOCKED if vehicle.isRestorePossible() else State.INPROGRESS

    def _initialize(self, *args, **kwargs):
        super(PersonalMissionsVehicleView, self)._initialize(*args, **kwargs)
        g_currentPreviewVehicle.onSelectedNoVehicle += self.__onSelectNoVehicle
        app = self.__appLoader.getApp()
        app.setBackgroundAlpha(0)

    def _finalize(self):
        g_currentPreviewVehicle.onSelectedNoVehicle -= self.__onSelectNoVehicle
        g_currentPreviewVehicle.selectNoVehicle()
        self.__hangarFeatureStateController.exit(self.layoutID)
        super(PersonalMissionsVehicleView, self)._finalize()

    def _onLoading(self, *args, **kwargs):
        super(PersonalMissionsVehicleView, self)._onLoading(*args, **kwargs)
        self.__updateModel()
        g_currentPreviewVehicle.selectVehicle(self.__currentVehicleCD)

    def _getEvents(self):
        return ((self.__personalMissionsController.onUpdated, self.__onUpdated),
         (self.__personalMissionsController.onQuestsUpdated, self.__onUpdated),
         (self.__itemsCache.onSyncCompleted, self.__onInventoryUpdate),
         (self.viewModel.onCompare, self.__onCompare),
         (self.viewModel.onShowVehiclePreview, self.__onShowVehiclePreview),
         (self.viewModel.onShowInHangar, self.__onShowInHangar),
         (self.viewModel.onBackToHangar, self.__onBackToHangar),
         (self.viewModel.onStartMoving, self.__onStartMoving),
         (self.viewModel.onMoveSpace, self.__onMoveSpace),
         (self.viewModel.onRestoreVehicle, self.__onRestoreVehicle))

    def __onCompare(self, event):
        vehicleCD = int(event.get(PersonalMissionsVehicleViewModel.ARG_VEHICLE_CD, 0))
        self.__comparisonBasket.addVehicle(vehicleCD)

    def __onShowVehiclePreview(self, event):
        vehicleCD = int(event.get(PersonalMissionsVehicleViewModel.ARG_VEHICLE_CD, 0))
        showVehiclePreview(vehicleCD, previewBackCb=self.__previewBackCallback, isFromVehicleView=True, bottomPanelTextData={'uniqueVehicleTitle': text_styles.tutorial(backport.text(R.strings.vehicle_preview.buyingPanel.pmOperationVehicleLabel(), operationName=self.__operation.getShortUserName()))}, backBtnLabel=backport.text(R.strings.personal_missions_3.VehicleView.vehiclePreviewBack()))

    def __onShowInHangar(self, event):
        vehicleCD = int(event.get(PersonalMissionsVehicleViewModel.ARG_VEHICLE_CD, 0))
        selectVehicleInHangar(vehicleCD)

    def __onBackToHangar(self):
        showPersonalMissionsOperationWindow(PageViewIdEnum.QUESTS, self.__operationId)

    def __updateModel(self):
        with self.viewModel.transaction() as model:
            if self.__operation:
                model.setOperationName(self.__operation.getShortUserName())
            model.setCurrentVehicleCD(self.__currentVehicleCD)
            self.__fillVehicle(model)

    def __fillVehicle(self, model):
        vehicle = self.__itemsCache.items.getItemByCD(self.__currentVehicleCD)
        if vehicle is None:
            return
        else:
            vModel = model.vehicle
            ctrl = self.__personalMissionsController
            operation = ctrl.getOperationById(self.__operationId)
            badges = []
            badges.extend(ctrl.getMainDossierBonusesForOperation(operation))
            badges.extend(ctrl.getAddDossierBonusesForOperation(operation))
            packBonusModelAndTooltipData(badges, vModel.getBadges(), self.__tooltipData)
            fillVehicleModel(vModel, vehicle)
            vehicleState = self.getVehicleState(vehicle)
            vModel.setState(vehicleState)
            vModel.setRestoreSeconds(vehicle.restoreInfo.getRestoreCooldownTimeLeft() if vehicleState == State.LOCKED else 0)
            restorePrice = vehicle.restorePrice
            vModel.setRestorePrice(restorePrice.getSignValue(restorePrice.getCurrency()))
            tileQuestsCount = len(ctrl.getQuestsByOperationId(self.__operationId))
            fullCompletedQuestsCount = len(ctrl.getFullCompletedQuestsByOperationId(self.__operationId))
            completedQuestsCount = len(ctrl.getCompletedQuestsByOperationId(self.__operationId))
            vModel.setDefaultState(State.ININVENTORY if tileQuestsCount == completedQuestsCount else State.INPROGRESS)
            vModel.setHonorState(State.ININVENTORY if tileQuestsCount == fullCompletedQuestsCount else State.INPROGRESS)
            vModel.setProgress(completedQuestsCount)
            vModel.setToUnlock(tileQuestsCount)
            return

    def __getBackportTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        return None if tooltipId is None else self.__tooltipData.get(tooltipId, None)

    def __previewBackCallback(self):
        showPersonalMissionsVehicleView(self.__operationId)

    def __onUpdated(self):
        self.__updateModel()

    def __onInventoryUpdate(self, _, invDiff):
        self.__updateModel()

    def __onRestoreVehicle(self):
        vehicleCD = self.__currentVehicleCD
        vehicle = self.__itemsCache.items.getItemByCD(vehicleCD)
        if not vehicle.isRestoreAvailable():
            return
        ItemsActionsFactory.doAction(ItemsActionsFactory.BUY_VEHICLE, vehicleCD, False, VehicleBuyActionTypes.RESTORE)

    def __onSelectNoVehicle(self):
        if self.__currentVehicleCD is not None and g_currentPreviewVehicle != self.__currentVehicleCD:
            g_currentPreviewVehicle.selectVehicle(self.__currentVehicleCD)
        return

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
