# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/lobby/hangar_view.py
import logging
import typing
from CurrentVehicle import g_currentVehicle, g_currentPreviewVehicle
from PlayerEvents import g_playerEvents
from last_stand.gui.impl.gen.view_models.views.lobby.artefact_types_view_model import ArtefactTypesViewModel
from last_stand.gui.impl.gen.view_models.views.lobby.widgets.hangar_carousel_view_model import VehicleStates
from last_stand.gui.impl.gen.view_models.views.lobby.widgets.meta_view_model import ArtefactStates
from last_stand.gui.impl.lobby.battle_result_view import BattleResultView
from last_stand.gui.impl.lobby.difficulty_window_view import DifficultyWindowView
from last_stand.gui.impl.lobby.widgets.carousel_view import CarouselView
from last_stand.gui.impl.lobby.widgets.quests_view import QuestsView
from last_stand.skeletons.difficulty_level_controller import IDifficultyLevelController
from frameworks.wulf import ViewFlags, ViewSettings, WindowLayer, WindowStatus
from notification import NotificationMVC
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.game_loading.resources.consts import Milestones
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.managers.containers import POP_UP_CRITERIA
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.app_loader import sf_lobby
from gui.impl.gen import R
from gui.impl.lobby.common.tooltips.extended_text_tooltip import ExtendedTextTooltip
from gui.impl.lobby.tank_setup.ammunition_setup.base_hangar import BaseHangarAmmunitionSetupView
from gui.prb_control import prb_getters
from gui.shared.events import AmmunitionPanelViewEvent
from gui.shared import EVENT_BUS_SCOPE, g_eventBus, events
from last_stand.gui.ls_account_settings import AccountSettingsKeys, getSettings, setSettings
from last_stand.gui.impl.gen.view_models.views.lobby.hangar_view_model import HangarViewModel
from last_stand.gui.impl.gen.view_models.views.lobby.vehicle_title_view_model import VehicleTypes
from last_stand.gui.impl.lobby import getVehicleState, getArtefactState
from last_stand.gui.impl.lobby.hangar_ammunition_panel_view import LSAmmunitionPanelView
from last_stand.gui.impl.lobby.widgets.difficulty_view import DifficultyView
from last_stand.gui.impl.lobby.widgets.keys_view import KeysView
from last_stand.gui.impl.lobby.widgets.meta_view import MetaWidgetView
from last_stand.gui.impl.lobby.widgets.lootbox_entry import LootBoxEntryView
from last_stand.gui.shared.event_dispatcher import showRewardPathView, showHangarAmmunitionSetupView, showIntroVideo, showInfoPage, showHangar
from last_stand.skeletons.ls_artefacts_controller import ILSArtefactsController
from last_stand.skeletons.ls_controller import ILSController
from last_stand.gui.sounds.sound_constants import HANGAR_SOUND_SETTINGS
from helpers import dependency
from helpers.CallbackDelayer import CallbackDelayer
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.impl import IGuiLoader, INotificationWindowController
from skeletons.gui.shared.utils import IHangarSpace
from last_stand.gui.impl.lobby.base_view import BaseView
from skeletons.account_helpers.settings_core import ISettingsCore
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
if typing.TYPE_CHECKING:
    from last_stand.gui.game_control.ls_artefacts_controller import Artefact
_BACKGROUND_ALPHA = 0.0
_AMMO_PANEL_TOOLTIP_IDS = (TOOLTIPS_CONSTANTS.HANGAR_SLOT_SPEC,)
_logger = logging.getLogger(__name__)

class HangarView(BaseView):
    _POP_UP_PADDING_X = 5
    _POP_UP_PADDING_Y = 207
    _appLoader = dependency.descriptor(IAppLoader)
    _guiLoader = dependency.descriptor(IGuiLoader)
    lsCtrl = dependency.descriptor(ILSController)
    lsArtifactsCtrl = dependency.descriptor(ILSArtefactsController)
    _hangarSpace = dependency.descriptor(IHangarSpace)
    _notificationMgr = dependency.descriptor(INotificationWindowController)
    _settingsCore = dependency.descriptor(ISettingsCore)
    _difficultyController = dependency.descriptor(IDifficultyLevelController)
    _COMMON_SOUND_SPACE = HANGAR_SOUND_SETTINGS

    def __init__(self, layoutID=R.views.last_stand.mono.lobby.hangar(), artefactID=None):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.LOBBY_SUB_VIEW
        settings.model = HangarViewModel()
        super(HangarView, self).__init__(settings)
        self.__isUnitJoiningInProgress = False
        self.__timer = None
        self.__ammoPanel = None
        self.__metaWidget = None
        self.__prevOptimizationEnabled = False
        self.__selectedMissionIndex = 1
        self.__selectedArtefactID = artefactID
        self.__needSlideToNext = False
        return

    @property
    def viewModel(self):
        return super(HangarView, self).getViewModel()

    def createContextMenu(self, event):
        return self.__ammoPanel.createContextMenu(event) if self.__ammoPanel is not None else super(HangarView, self).createContextMenu(event)

    def createToolTip(self, event):
        dialogsContainer = self.__app.containerManager.getContainer(WindowLayer.TOP_WINDOW)
        if dialogsContainer.getView(criteria={POP_UP_CRITERIA.VIEW_ALIAS: VIEW_ALIAS.LOBBY_MENU}):
            return None
        else:
            tooltipID = event.getArgument('tooltip')
            return self.__ammoPanel.createToolTip(event) if self.__ammoPanel is not None and tooltipID in _AMMO_PANEL_TOOLTIP_IDS else super(HangarView, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.common.tooltips.ExtendedTextTooltip():
            text = event.getArgument('text', '')
            stringifyKwargs = event.getArgument('stringifyKwargs', '')
            return ExtendedTextTooltip(text, stringifyKwargs)
        return super(HangarView, self).createToolTipContent(event, contentID)

    def selectSlideByArtefact(self, artefactID):
        self.viewModel.setSelectedSlide(self.lsArtifactsCtrl.getIndex(artefactID))

    def selectNextSlide(self):
        self.__needSlideToNext = True

    def updateSlide(self):
        self.__prepareSelectedArtefact()
        self.__fillCore()

    def _onLoading(self, *args, **kwargs):
        super(HangarView, self)._onLoading()
        self.__timer = CallbackDelayer()
        app = self._appLoader.getApp()
        app.setBackgroundAlpha(_BACKGROUND_ALPHA)
        self.__ammoPanel = LSAmmunitionPanelView()
        self.__metaWidget = MetaWidgetView(parent=self)
        self._setComponents()
        self.__prepareSelectedArtefact()
        self.__fillCore()
        self.__fillMetaWidget()
        self.__metaWidget.updateData(int(self.__selectedMissionIndex))
        self.__fillVehicleTitle()
        self.__prevOptimizationEnabled = app.graphicsOptimizationManager.getEnable()
        if self.__prevOptimizationEnabled:
            app.graphicsOptimizationManager.switchOptimizationEnabled(False)

    def _onLoaded(self, *args, **kwargs):
        super(HangarView, self)._onLoaded(*args, **kwargs)
        if g_currentPreviewVehicle is not None:
            g_currentPreviewVehicle.selectNoVehicle()
        if getSettings(AccountSettingsKeys.IS_EVENT_NEW):
            showIntroVideo()
            setSettings(AccountSettingsKeys.IS_EVENT_NEW, False)
        if self._hangarSpace.spaceInited:
            self.__updateNotificationsLayout()
        else:
            g_playerEvents.onLoadingMilestoneReached += self.__onLoadingMilestoneReached
        return

    def _finalize(self):
        app = self._appLoader.getApp()
        if self.__prevOptimizationEnabled:
            app.graphicsOptimizationManager.switchOptimizationEnabled(True)
        notificationsModel = NotificationMVC.g_instance.getModel()
        if notificationsModel is not None:
            notificationsModel.onPopUpPaddingChanged(False)
        self.__ammoPanel = None
        self.__metaWidget = None
        super(HangarView, self)._finalize()
        return

    def _getEvents(self):
        return [(g_playerEvents.onPrebattleInvitationAccepted, self.__onPrebattleInvitationAccepted),
         (self._guiLoader.windowsManager.onWindowStatusChanged, self.__windowStatusChanged),
         (self.viewModel.onEscPressed, self.__onEscape),
         (self.viewModel.onExitClick, self.__onExitClick),
         (self.viewModel.onAboutClick, self.__onAboutClick),
         (self.viewModel.onMetaClick, self.__onMetaClick),
         (self.viewModel.onViewLoaded, self.__onViewLoaded),
         (self.viewModel.onSlide, self.__onSlide),
         (self.lsArtifactsCtrl.onArtefactStatusUpdated, self.__onArtefactStatusUpdated),
         (self.lsArtifactsCtrl.onArtefactSettingsUpdated, self.__onArtefactSettingsUpdated),
         (self._difficultyController.onChangeDifficultyLevel, self.__onDifficultyChange),
         (g_currentVehicle.onChanged, self.__onCurrentVehicleChanged),
         (g_currentPreviewVehicle.onChanged, self.__onCurrentVehicleChanged)]

    def _subscribe(self):
        super(HangarView, self)._subscribe()
        unitMgr = prb_getters.getClientUnitMgr()
        if unitMgr:
            unitMgr.onUnitJoined += self.__onUnitJoined
        g_eventBus.addListener(AmmunitionPanelViewEvent.SECTION_SELECTED, self.__onTankSetupChange, scope=EVENT_BUS_SCOPE.LOBBY)

    def _unsubscribe(self):
        g_eventBus.removeListener(AmmunitionPanelViewEvent.SECTION_SELECTED, self.__onTankSetupChange, scope=EVENT_BUS_SCOPE.LOBBY)
        g_clientUpdateManager.removeObjectCallbacks(self)
        unitMgr = prb_getters.getClientUnitMgr()
        if unitMgr:
            unitMgr.onUnitJoined -= self.__onUnitJoined
        if self.__timer is not None:
            self.__timer.clearCallbacks()
            self.__timer = None
        g_playerEvents.onLoadingMilestoneReached -= self.__onLoadingMilestoneReached
        super(HangarView, self)._unsubscribe()
        return

    def _setComponents(self):
        self.setChildView(resourceID=R.views.last_stand.lobby.virtual_res.KeysView(), view=KeysView())
        self.setChildView(resourceID=R.views.last_stand.lobby.virtual_res.DifficultyView(), view=DifficultyView())
        self.setChildView(resourceID=R.views.last_stand.lobby.virtual_res.TankSetupView(), view=self.__ammoPanel)
        self.setChildView(resourceID=R.views.last_stand.lobby.virtual_res.MetaView(), view=self.__metaWidget)
        self.setChildView(resourceID=R.views.last_stand.lobby.virtual_res.CarouselView(), view=CarouselView())
        self.setChildView(resourceID=R.views.last_stand.lobby.virtual_res.QuestsView(), view=QuestsView())
        self.setChildView(resourceID=R.views.last_stand.lobby.virtual_res.LootboxEntryView(), view=LootBoxEntryView())

    def _onClose(self):
        pass

    def __selectNextSlide(self):
        if self.__metaWidget is not None:
            self.__metaWidget.updateData(int(self.__selectedMissionIndex))
        self.__selectedArtefactID = None
        self.__prepareSelectedArtefact()
        self.viewModel.setSelectedSlide(self.__selectedMissionIndex)
        self.__needSlideToNext = False
        self.__updateButtonLock(self.viewModel)
        return

    def __prepareSelectedArtefact(self):
        artefacts = self.lsArtifactsCtrl.artefactsSorted()
        if self.__selectedArtefactID is None:
            artefactID = None
            if self.lsArtifactsCtrl.getCurrentArtefactProgress() >= self.lsArtifactsCtrl.getMaxArtefactsProgress():
                artefactID = self.lsArtifactsCtrl.getFinalArtefact().artefactID
            else:
                for artefact in artefacts:
                    if not self.lsArtifactsCtrl.isArtefactOpened(artefact.artefactID):
                        artefactID = artefact.artefactID
                        break

            if artefactID is None:
                artefactID = artefacts[0].artefactID
            self.__selectedMissionIndex = self.lsArtifactsCtrl.getIndex(artefactID)
            self.__selectedArtefactID = artefactID
        else:
            self.__selectedMissionIndex = self.lsArtifactsCtrl.getIndex(self.__selectedArtefactID)
        return

    def __onPrebattleInvitationAccepted(self, _, __):
        self.__isUnitJoiningInProgress = True
        self.__timer.delayCallback(15, self.__onResetUnitJoiningProgress)

    def __onResetUnitJoiningProgress(self):
        self.__isUnitJoiningInProgress = False

    def __onUnitJoined(self, _, __):
        self.__isUnitJoiningInProgress = False
        if self.__timer is not None:
            self.__timer.stopCallback(self.__onResetUnitJoiningProgress)
        return

    def __onArtefactStatusUpdated(self, _):
        self.__fillMetaWidget()
        if self.lsArtifactsCtrl.isArtefactOpened(self.__selectedArtefactID):
            self.__updateButtonLock(self.viewModel)
            return
        self.__metaWidget.updateData(int(self.__selectedMissionIndex))

    def __onArtefactSettingsUpdated(self):
        self.__fillCore()

    def __onDifficultyChange(self, _):
        self.__setBackground()

    def __onSlide(self, args):
        if args is None:
            return
        else:
            slideIndex = int(args.get('slide', 1))
            self.viewModel.setSelectedSlide(slideIndex)
            self.__selectedMissionIndex = slideIndex
            self.__selectedArtefactID = self.lsArtifactsCtrl.getArtefactIDByIndex(slideIndex)
            self.__metaWidget.updateData(slideIndex)
            self.__updateButtonLock(self.viewModel)
            return

    def __updateButtonLock(self, tx):
        selectedArtefactState = getArtefactState(self.__selectedArtefactID)
        tx.setIsLockedNextSlide(selectedArtefactState != ArtefactStates.OPEN)

    @sf_lobby
    def __app(self):
        return None

    def __fillMetaWidget(self):
        with self.viewModel.transaction() as tx:
            maxProgress = self.lsArtifactsCtrl.getMaxArtefactsProgress()
            currentProgress = self.lsArtifactsCtrl.getCurrentArtefactProgress()
            tx.progress.setMaxProgress(maxProgress)
            tx.progress.setCurrentProgress(currentProgress)
            tx.progress.setIsCompleted(currentProgress >= maxProgress)

    def __fillVehicleTitle(self):
        vehicle = g_currentVehicle.item
        with self.viewModel.transaction() as tx:
            vehicleTitle = tx.vehicleTitle
            tx.setShowRandomLable(False)
            if vehicle is not None:
                vehState = getVehicleState(vehicle)
                tx.setShowRandomLable(vehState == VehicleStates.REPAIR.value or vehState == VehicleStates.CREWINCOMPLETE.value)
                vehicleTitle.setName(vehicle.descriptor.type.shortUserString)
                vehicleTitle.setIsPremium(vehicle.isPremium)
                vehicleTitle.setIsElite(vehicle.isElite)
                vehicleTitle.setIsPremiumIGR(vehicle.isPremiumIGR)
                vehicleTitle.setVehicleType(VehicleTypes(vehicle.type) if vehicle.type != '' else VehicleTypes.NONE)
            else:
                vehicleTitle.setName('')
                vehicleTitle.setIsPremium(False)
                vehicleTitle.setIsElite(False)
                vehicleTitle.setIsPremiumIGR(False)
                vehicleTitle.setVehicleType(VehicleTypes.NONE)
        return

    def __setBackground(self):
        with self.viewModel.transaction() as tx:
            tx.setSelectedDifficulty(self._difficultyController.getSelectedLevel())

    def __fillCore(self):
        with self.viewModel.transaction() as tx:
            tx.setSelectedSlide(self.__selectedMissionIndex)
            tx.setSelectedDifficulty(self._difficultyController.getSelectedLevel())
            tx.setSlidesCount(self.lsArtifactsCtrl.getArtefactsCount())
            artefacts = tx.getArtefacts()
            artefacts.clear()
            for artefact in self.lsArtifactsCtrl.artefactsSorted():
                artefactType = ArtefactTypesViewModel()
                artefactType.setId(artefact.artefactID)
                artefactType.setIndex(self.lsArtifactsCtrl.getIndex(artefact.artefactID))
                artefactType.setTypes(','.join(artefact.artefactTypes))
                artefacts.addViewModel(artefactType)

            self.__updateButtonLock(tx)

    def __updateNotificationsLayout(self):
        notificationsModel = NotificationMVC.g_instance.getModel()
        if notificationsModel is not None:
            notificationsModel.onPopUpPaddingChanged(True, self._POP_UP_PADDING_X, self._POP_UP_PADDING_Y)
        return

    def __onLoadingMilestoneReached(self, milestoneName):
        if milestoneName == Milestones.HANGAR_READY:
            g_playerEvents.onLoadingMilestoneReached -= self.__onLoadingMilestoneReached
            self.__updateNotificationsLayout()

    def __onExitClick(self):
        self.lsCtrl.selectRandomMode()

    def __onAboutClick(self):
        showInfoPage()

    def __onMetaClick(self):
        showRewardPathView(selectedArtefactID=self.__selectedArtefactID)

    def __showLastMission(self):
        showHangar(self.__selectedArtefactID)

    def __onEscape(self):
        dialogsContainer = self.__app.containerManager.getContainer(WindowLayer.TOP_WINDOW)
        if not dialogsContainer.getView(criteria={POP_UP_CRITERIA.VIEW_ALIAS: VIEW_ALIAS.LOBBY_MENU}):
            g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.LOBBY_MENU)), scope=EVENT_BUS_SCOPE.LOBBY)

    def __onCurrentVehicleChanged(self):
        if g_currentVehicle.item is None:
            return
        else:
            self.__fillVehicleTitle()
            return

    def __onTankSetupChange(self, event):
        ctx = event.ctx
        if self._hangarSpace.spaceLoading():
            _logger.warning('Optional Device click was not handled (kwargs=%s). HangarSpace is currently  loading.', ctx)
        elif not self.__isUnitJoiningInProgress:
            with self.viewModel.transaction() as tx:
                tx.setIsLoadedSetup(True)
            showHangarAmmunitionSetupView(**ctx)

    def __windowStatusChanged(self, uniqueID, newStatus):
        if newStatus == WindowStatus.DESTROYING:
            window = self._guiLoader.windowsManager.getWindow(uniqueID)
            if window.content is None:
                return
            if isinstance(window.content, BaseHangarAmmunitionSetupView):
                with self.viewModel.transaction() as tx:
                    tx.setIsLoadedSetup(False)
                return
            if isinstance(window.content, DifficultyWindowView) or isinstance(window.content, BattleResultView) and self._notificationMgr.activeQueueLength == 0:
                self.viewModel.setShowDailyAnim(not self.viewModel.getShowDailyAnim())
        if newStatus == WindowStatus.DESTROYED:
            if self._guiLoader.windowsManager.getViewByLayoutID(R.views.lobby.lootbox_system.MainView()):
                return
            if self.__needSlideToNext and self._notificationMgr.activeQueueLength == 0:
                self.__selectNextSlide()
        return

    def __onViewLoaded(self):
        g_eventBus.handleEvent(events.ViewReadyEvent(self.layoutID))
