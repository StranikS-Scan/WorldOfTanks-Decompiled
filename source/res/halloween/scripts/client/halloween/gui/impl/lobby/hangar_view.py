# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/lobby/hangar_view.py
from __future__ import absolute_import
import logging
import typing
from CurrentVehicle import g_currentVehicle, g_currentPreviewVehicle
from gui.Scaleform.lobby_entry import getLobbyStateMachine
from gui.lobby_state_machine.routable_view import IRoutableView
from gui.lobby_state_machine.router import SubstateRouter
from gui.shared.event_dispatcher import showVehicleHubOverview, showLobbyMenu
from gui.impl.lobby.hangar.presenters.main_menu_presenter import MainMenuPresenter
from gui.impl.pub import WindowImpl
from gui.impl.pub.view_component import ViewComponent
from halloween.gui.impl.lobby.hw_helpers.anomalies_helpers import hasNewAnomalies, isAnomaliesSystemAvailable
from halloween.gui.impl.lobby.hw_helpers.bestiary_helper import getEnemyRole, isEnemyUnlocked
from halloween.gui.impl.lobby.widgets.gsw_view import GswPresenter
from frameworks.wulf import WindowStatus, WindowFlags
from halloween.gui.impl.lobby.widgets.hw_loadout import HalloweenLoadoutPresenter
from halloween.gui.impl.lobby.widgets.vehicle_title_view import VehicleTitlePresenter
from halloween.gui.shared.events import HWHangarEvent
from halloween.uilogging.loggers import HWMetricsLogger
from halloween.uilogging.logging_constants import HWLogKeys
from items.vehicles import getVehicleType
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.app_loader import sf_lobby
from gui.impl.gen import R
from gui.impl.lobby.common.tooltips.extended_text_tooltip import ExtendedTextTooltip
from gui.impl.lobby.hangar.presenters.utils import getSharedMenuItems
from gui.prb_control import prbEntityProperty
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from halloween.gui.impl.gen.view_models.views.lobby.hangar_view_model import HangarViewModel
from halloween.gui.impl.gen.view_models.views.lobby.widgets.hangar_carousel_vehicle_view_model import VehicleStates
from halloween.gui.impl.lobby.hw_helpers import getVehicleState, fillGiftVehicleModel, getEnemyByArtefactID
from halloween.gui.impl.lobby.widgets.carousel_view import CarouselView
from halloween.gui.impl.lobby.widgets.difficulty_view import DifficultyView
from halloween.gui.impl.lobby.widgets.meta_view import MetaWidgetView
from halloween.gui.halloween_account_settings import AccountSettingsKeys, getSettings, setSettings
from halloween.gui.shared.event_dispatcher import showHalloweenShopVehicle, showIntroVideo, showInfoPage, showComparisonWindow, showBestiaryWindow, showAnomaliesWindow
from halloween.skeletons.halloween_anomalies_controller import IHalloweenAnomaliesController
from halloween.skeletons.halloween_artefacts_controller import IHalloweenArtefactsController
from halloween.skeletons.halloween_bestiary_controller import IHalloweenBestiaryController
from halloween.skeletons.halloween_controller import IHalloweenController
from halloween.gui.sounds.sound_constants import HANGAR_SOUND_SETTINGS
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.impl import IGuiLoader, INotificationWindowController
from skeletons.gui.shared.utils import IHangarSpace
from halloween.gui.impl.lobby.base_view import SwitcherPresenter
if typing.TYPE_CHECKING:
    from gui.shared.events import GUICommonEvent
    from halloween.gui.game_control.halloween_bestiary_controller import EnemyData
_BACKGROUND_ALPHA = 0.0
_logger = logging.getLogger(__name__)

class HangarView(ViewComponent[HangarViewModel], IRoutableView):
    _appLoader = dependency.descriptor(IAppLoader)
    _guiLoader = dependency.descriptor(IGuiLoader)
    _hwController = dependency.descriptor(IHalloweenController)
    _hwAnomaliesCtrl = dependency.descriptor(IHalloweenAnomaliesController)
    _hwArtefactsCtrl = dependency.descriptor(IHalloweenArtefactsController)
    _hwBestiaryCtrl = dependency.descriptor(IHalloweenBestiaryController)
    _hangarSpace = dependency.descriptor(IHangarSpace)
    _notificationMgr = dependency.descriptor(INotificationWindowController)
    _COMMON_SOUND_SPACE = HANGAR_SOUND_SETTINGS

    def __init__(self, *args, **kwargs):
        super(HangarView, self).__init__(R.views.halloween.mono.lobby.hangar(), HangarViewModel, *args, **kwargs)
        self.__metaWidget = None
        self._router = None
        self.__inputManager = None
        self.__uiLogger = HWMetricsLogger(HWLogKeys.HW_LOBBY)
        return

    @property
    def viewModel(self):
        return super(HangarView, self).getViewModel()

    def getRouterModel(self):
        return self.getViewModel()

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.common.tooltips.ExtendedTextTooltip():
            text = event.getArgument('text', '')
            stringifyKwargs = event.getArgument('stringifyKwargs', '')
            return ExtendedTextTooltip(text, stringifyKwargs)
        return super(HangarView, self).createToolTipContent(event, contentID)

    def selectSlideByArtefact(self, artefactID):
        self.viewModel.setSelectedSlide(self._hwArtefactsCtrl.getIndex(artefactID))

    def updateSlide(self):
        self.__fillCore()

    @prbEntityProperty
    def prbEntity(self):
        return None

    def _onLoading(self, *args, **kwargs):
        self.__inputManager = self.__app.gameInputManager
        self._initializeRouter()
        super(HangarView, self)._onLoading()
        self.__metaWidget.updateData(self.__selectedMissionIndex)
        self.__fillCore()
        self.__fillGiftVehicle()
        self.__updateVehicleLocked()
        self.__updateAnomaliesInfo()

    def _onLoaded(self, *args, **kwargs):
        super(HangarView, self)._onLoaded(*args, **kwargs)
        if g_currentPreviewVehicle is not None:
            g_currentPreviewVehicle.selectNoVehicle()
        return

    def _onShown(self):
        super(HangarView, self)._onShown()
        if getSettings(AccountSettingsKeys.IS_EVENT_NEW):
            showIntroVideo()
            setSettings(AccountSettingsKeys.IS_EVENT_NEW, False)
        if self._hwArtefactsCtrl.needSelectNextSlide and self._notificationMgr.activeQueueLength == 0:
            self.__selectNextSlide()

    def _finalize(self):
        self.__metaWidget = None
        self._router.fini()
        self._router = None
        super(HangarView, self)._finalize()
        return

    def _initializeRouter(self):
        lsm = getLobbyStateMachine()
        self._router = SubstateRouter(lsm, self, lsm.getStateFromView(self))
        self._router.init()

    def _getEvents(self):
        return [(self._guiLoader.windowsManager.onWindowStatusChanged, self.__windowStatusChanged),
         (self.viewModel.onAboutClick, self.__onAboutClick),
         (self.viewModel.onTasksClick, self.__onTasksClick),
         (self.viewModel.onPacksClick, self.__onPacksClick),
         (self.viewModel.onViewLoaded, self.__onViewLoaded),
         (self.viewModel.onSlide, self.__onSlide),
         (self.viewModel.onPreview, self.__onPreview),
         (self.viewModel.onWidgetsUpdate, self.__onWidgetsUpdate),
         (self.viewModel.onComparisonClick, self.__onComparisonClick),
         (self.viewModel.onAnomaliesClick, self.__onAnomaliesClick),
         (self.viewModel.onEnemyClick, self.__onEnemyClick),
         (self.viewModel.onBestiaryClick, self.__onBestiaryClick),
         (self._hwArtefactsCtrl.onArtefactStatusUpdated, self.__onArtefactStatusUpdated),
         (self._hwArtefactsCtrl.onArtefactSettingsUpdated, self.__onArtefactSettingsUpdated),
         (self._hwController.onSettingsUpdate, self.__fillCore),
         (self._hwAnomaliesCtrl.onChangeSystemAnomaliesUnlock, self.__updateAnomaliesInfo),
         (self._hwAnomaliesCtrl.onRefreshData, self.__updateAnomaliesInfo),
         (g_currentVehicle.onChanged, self.__onCurrentVehicleChanged),
         (g_currentPreviewVehicle.onChanged, self.__onCurrentVehicleChanged)]

    def _subscribe(self):
        super(HangarView, self)._subscribe()
        g_clientUpdateManager.addCallbacks({'cache.vehsLock': self.__onVehicleLockUpdated})
        self.__inputManager.addEscapeListener(self.__escapeHandler)

    def _unsubscribe(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.__inputManager.removeEscapeListener(self.__escapeHandler)
        self.__inputManager = None
        super(HangarView, self)._unsubscribe()
        return

    def _getListeners(self):
        return ((HWHangarEvent.REFRESH, self.__refresh, EVENT_BUS_SCOPE.LOBBY),)

    def _getChildComponents(self):
        self.__metaWidget = MetaWidgetView(parent=self)
        halloween = R.aliases.halloween.shared
        coreRandom = R.aliases.hangar.shared
        return {halloween.Switcher(): SwitcherPresenter,
         halloween.Difficulty(): DifficultyView,
         halloween.Carousel(): CarouselView,
         R.aliases.hangar.shared.MainMenu(): lambda : MainMenuPresenter(getSharedMenuItems()),
         halloween.Gsw(): GswPresenter,
         halloween.Meta(): lambda : self.__metaWidget,
         coreRandom.Loadout(): HalloweenLoadoutPresenter,
         halloween.VehicleTitle(): VehicleTitlePresenter}

    def __refresh(self, event):
        self.__fillCore()

    def __selectNextSlide(self):
        if self.__metaWidget is not None:
            self.__metaWidget.updateData(self.__selectedMissionIndex)
        with self.viewModel.transaction() as tx:
            tx.setSelectedSlide(self.__selectedMissionIndex)
            self._hwArtefactsCtrl.resetSelectedArtefactID()
            tx.setScrollToSlide(self.__selectedMissionIndex)
            tx.setIsCompleted(self._hwArtefactsCtrl.getCurrentArtefactProgress() >= self._hwArtefactsCtrl.getMaxArtefactsProgress())
        self._hwArtefactsCtrl.needSelectNextSlide = False
        return

    @property
    def __selectedArtefactID(self):
        artefactID = self._hwArtefactsCtrl.selectedArtefactID
        if artefactID is None:
            artefacts = self._hwArtefactsCtrl.artefactsSorted()
            if self._hwArtefactsCtrl.getCurrentArtefactProgress() >= self._hwArtefactsCtrl.getMaxArtefactsProgress():
                artefact = self._hwArtefactsCtrl.getFinalArtefact()
                artefactID = artefact.artefactID if artefact is not None else None
            else:
                for artefact in artefacts:
                    if not self._hwArtefactsCtrl.isArtefactOpened(artefact.artefactID):
                        artefactID = artefact.artefactID
                        break

            if artefactID is None and artefacts:
                artefactID = artefacts[0].artefactID
            self._hwArtefactsCtrl.selectedArtefactID = artefactID
        return artefactID

    @property
    def __selectedMissionIndex(self):
        return self._hwArtefactsCtrl.getIndex(self.__selectedArtefactID)

    def __onVehicleLockUpdated(self, *args):
        if g_currentVehicle.item:
            self.viewModel.setIsVehicleInBattle(g_currentVehicle.item.isInBattle)

    def __onArtefactStatusUpdated(self, _):
        if self._hwArtefactsCtrl.isArtefactOpened(self.__selectedArtefactID):
            return
        self.__metaWidget.updateData(self.__selectedMissionIndex)
        self.__updateBestiaryInfo()

    def __onArtefactSettingsUpdated(self):
        self.__fillCore()
        self.__updateVehicleLocked()

    def __onSlide(self, args):
        if args is None:
            return
        else:
            slideIndex = int(args.get('slide', 1))
            selectedArtefactID = self._hwArtefactsCtrl.getArtefactIDByIndex(slideIndex)
            with self.viewModel.transaction() as tx:
                tx.setSelectedSlide(slideIndex)
                tx.setIsOpened(self._hwArtefactsCtrl.isArtefactOpened(selectedArtefactID))
                tx.setScrollToSlide(0)
            self._hwArtefactsCtrl.selectedArtefactID = selectedArtefactID
            self.__uiLogger.onClick(HWLogKeys.ARROW, selectedArtefactID)
            return

    def __onWidgetsUpdate(self, args):
        if args is None:
            return
        else:
            slideIndex = int(args.get('slide', 1))
            self.__updateBestiaryInfo()
            self.__metaWidget.updateData(slideIndex)
            return

    @sf_lobby
    def __app(self):
        return None

    def __fillGiftVehicle(self):
        with self.viewModel.transaction() as tx:
            vehGift = tx.mainGiftVehicle
            fillGiftVehicleModel(vehGift)

    def __fillCore(self):
        with self.viewModel.transaction() as tx:
            tx.setSlidesCount(self._hwArtefactsCtrl.getArtefactsCount())
            tx.setIsCompleted(self._hwArtefactsCtrl.getCurrentArtefactProgress() >= self._hwArtefactsCtrl.getMaxArtefactsProgress())
            tx.setIsOpened(self._hwArtefactsCtrl.isArtefactOpened(self.__selectedArtefactID))
            tx.setIsInfoPageEnabled(self._hwController.isInfoPageEnabled())
            tx.setSelectedSlide(self.__selectedMissionIndex)
            self.__updateBestiaryInfo()
            if self._hwArtefactsCtrl.needSelectNextSlide:
                self._hwArtefactsCtrl.needSelectNextSlide = False
                self._hwArtefactsCtrl.resetSelectedArtefactID()
                tx.setScrollToSlide(self.__selectedMissionIndex)

    def __updateVehicleLocked(self):
        vehicle = g_currentVehicle.item
        if vehicle is not None:
            vehicleLocked = getVehicleState(vehicle) == VehicleStates.LOCKED
            self.viewModel.setIsVehicleLocked(vehicleLocked)
            if vehicleLocked:
                missionID = self._hwArtefactsCtrl.getArtefactIDForAccessToVehicle(vehicle.intCD)
                if missionID is not None:
                    self.viewModel.setLockedMissionIndex(self._hwArtefactsCtrl.getIndex(missionID))
            self.viewModel.setIsVehicleInBattle(vehicle.isInBattle)
        return

    def __updateAnomaliesInfo(self):
        isSysAnomaliesAvailable = isAnomaliesSystemAvailable()
        with self.viewModel.transaction() as tx:
            tx.setAreAnomaliesUnlocked(isSysAnomaliesAvailable)
            tx.setHasNewAnomaly(isSysAnomaliesAvailable and hasNewAnomalies())

    def __updateBestiaryInfo(self):
        enemyData = getEnemyByArtefactID(self.__selectedArtefactID)
        with self.viewModel.transaction() as tx:
            bestiaryInfoModel = tx.bestiaryInfo
            hasUnlockedEnemies = self._hwBestiaryCtrl.hasUnlockedEnemies
            bestiaryInfoModel.setHasUnlockedEnemies(hasUnlockedEnemies)
            bestiaryInfoModel.setHasNewEnemies(bool(self._hwBestiaryCtrl.getFirstNewEnemy()) if hasUnlockedEnemies else False)
            currentEnemyModel = bestiaryInfoModel.currentEnemy
            if enemyData and enemyData.enemy.needShowInHangar:
                enemyType = getVehicleType(enemyData.intCD)
                currentEnemyModel.setName(enemyType.userString)
                currentEnemyModel.setRole(getEnemyRole(enemyType))
                currentEnemyModel.setIsAvailable(isEnemyUnlocked(enemyData.enemy))
            else:
                currentEnemyModel.setName('')
                currentEnemyModel.setRole('')
                currentEnemyModel.setIsAvailable(False)

    def __onAboutClick(self):
        self.__uiLogger.onClick(HWLogKeys.INFO_BUTTON)
        showInfoPage()

    def __onEnemyClick(self):
        enemyData = getEnemyByArtefactID(self.__selectedArtefactID)
        showBestiaryWindow(enemyIntCD=enemyData.intCD)

    def __onBestiaryClick(self):
        self.__uiLogger.onClick(HWLogKeys.BESTIARY_BUTTON)
        showBestiaryWindow()

    def __onComparisonClick(self):
        self.__uiLogger.onClick(HWLogKeys.COMPARISON_BUTTON)
        showComparisonWindow()

    def __onAnomaliesClick(self):
        self.__uiLogger.onClick(HWLogKeys.ANOMALIES_BUTTON)
        showAnomaliesWindow()

    def __onPreview(self):
        vehicle = self._hwArtefactsCtrl.getMainGiftVehicle()
        if vehicle is not None:
            showVehicleHubOverview(vehicle.intCD)
        return

    def __onTasksClick(self):
        vehicle = g_currentVehicle.item
        if not vehicle:
            return
        else:
            artefactID = self._hwArtefactsCtrl.getArtefactIDForAccessToVehicle(vehicle.intCD)
            if artefactID is None:
                return
            self.viewModel.setSelectedSlide(self._hwArtefactsCtrl.getIndex(artefactID))
            return

    def __onPacksClick(self):
        showHalloweenShopVehicle()

    def __onCurrentVehicleChanged(self):
        if g_currentVehicle.item is None:
            return
        else:
            self.__updateVehicleLocked()
            return

    def __escapeHandler(self):
        showLobbyMenu()

    def __windowStatusChanged(self, uniqueID, newStatus):
        window = self._guiLoader.windowsManager.getWindow(uniqueID)
        if window is None or window.content is None:
            if newStatus == WindowStatus.DESTROYED:
                if self._hwArtefactsCtrl.needSelectNextSlide and self._notificationMgr.activeQueueLength == 0:
                    if not self._hwBestiaryCtrl.hasEnemy(self._hwArtefactsCtrl.getOpenedArtefactToken(self.__selectedArtefactID)):
                        self.viewModel.setIsOpened(True)
                        self.__selectNextSlide()
        return

    def __onViewLoaded(self):
        g_eventBus.handleEvent(events.ViewReadyEvent(self.layoutID))


class HangarWindow(WindowImpl):

    def __init__(self, layer, **kwargs):
        super(HangarWindow, self).__init__(content=HangarView(), wndFlags=WindowFlags.WINDOW, layer=layer)
