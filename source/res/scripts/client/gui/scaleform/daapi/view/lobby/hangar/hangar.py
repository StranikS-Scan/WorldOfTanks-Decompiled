# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/Hangar.py
import logging
import typing
from functools import partial
import BigWorld
from shared_utils import nextTick
from CurrentVehicle import g_currentVehicle
from gui.Scaleform.daapi.view.lobby.detachment.detachment_setup_vehicle import g_detachmentTankSetupVehicle
from HeroTank import HeroTank
from account_helpers.settings_core.ServerSettingsManager import SETTINGS_SECTIONS
from constants import QUEUE_TYPE, PREBATTLE_TYPE, Configs, DOG_TAGS_CONFIG
from crew2.detachment_states import CanAssignResult
from frameworks.wulf import WindowFlags, WindowLayer, WindowStatus
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.Waiting import Waiting
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.LobbySelectableView import LobbySelectableView
from gui.Scaleform.daapi.view.lobby.mapbox import mapbox_helpers
from gui.Scaleform.daapi.view.meta.HangarMeta import HangarMeta
from gui.impl.gen.view_models.views.lobby.detachment.common.navigation_view_model import NavigationViewModel
from gui.impl.lobby.detachment.hangar_widget import HangarWidget
from gui.shared.gui_items.Vehicle import VEHICLE_TAGS
from gui.shared.utils.requesters import REQ_CRITERIA
from items.components.detachment_constants import TypeDetachmentAssignToVehicle
from skeletons.gui.detachment import IDetachmentCache
from sound_gui_manager import CommonSoundSpaceSettings
from gui.Scaleform.framework.managers.containers import POP_UP_CRITERIA
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.Scaleform.genConsts.HANGAR_ALIASES import HANGAR_ALIASES
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.genConsts.DAILY_QUESTS_WIDGET_CONSTANTS import DAILY_QUESTS_WIDGET_CONSTANTS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.game_control.links import URLMacros
from gui.hangar_cameras.hangar_camera_common import CameraRelatedEvents, CameraMovementStates
from gui.impl.auxiliary.crew_books_helper import crewBooksViewedCache
from gui.prb_control import prb_getters
from gui.impl.auxiliary.detachment_helper import getVisibleCrewWidgetName, isDetachmentInRecycleBin, canAssignDetachmentToVehicle
from gui.prb_control.ctrl_events import g_prbCtrlEvents
from gui.prb_control.entities.listener import IGlobalListener
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.promo.hangar_teaser_widget import TeaserViewer
from gui.ranked_battles import ranked_helpers
from gui.ranked_battles.constants import PrimeTimeStatus
from gui.shared import event_dispatcher as shared_events
from gui.shared import events, EVENT_BUS_SCOPE
from gui.shared.event_dispatcher import showRankedPrimeTimeWindow, showAmmunitionSetupView, showDetachmentViewById
from gui.shared.events import LobbySimpleEvent
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.items_cache import CACHE_SYNC_REASON
from gui.shared.tutorial_helper import getTutorialGlobalStorage
from gui.shared.utils.functions import makeTooltip
from gui.sounds.filters import States, StatesGroup
from battle_pass_common import BATTLE_PASS_CONFIG_NAME
from helpers import dependency
from helpers.i18n import makeString as _ms
from helpers.CallbackDelayer import CallbackDelayer
from helpers.statistics import HANGAR_LOADING_STATE
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.connection_mgr import IConnectionManager
from skeletons.gui.game_control import IIGRController
from skeletons.gui.game_control import IRankedBattlesController, IEpicBattleMetaGameController, IPromoController, IBattlePassController, IBattleRoyaleController, IBootcampController, IMapboxController
from skeletons.gui.impl import IGuiLoader
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.offers import IOffersBannerController
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.utils import IHangarSpace
from skeletons.helpers.statistics import IStatisticsCollector
from tutorial.control.context import GLOBAL_FLAG
from account_helpers import AccountSettings
from account_helpers.AccountSettings import NATION_CHANGE_VIEWED
from gui.shared.gui_items.items_actions import factory as ActionsFactory
from gui.impl.gen import R
from gui.impl import backport
from PlayerEvents import g_playerEvents
from uilogging.detachment.loggers import DetachmentLogger, g_detachmentFlowLogger
from uilogging.detachment.constants import ACTION, GROUP
if typing.TYPE_CHECKING:
    from frameworks.wulf import Window
_logger = logging.getLogger(__name__)
_HELP_LAYOUT_RESTRICTED_LAYERS = (WindowLayer.TOP_SUB_VIEW,
 WindowLayer.FULLSCREEN_WINDOW,
 WindowLayer.WINDOW,
 WindowLayer.OVERLAY,
 WindowLayer.TOP_WINDOW)

def predicateHelpLayoutAllowedWindow(window):
    return window.typeFlag != WindowFlags.TOOLTIP and window.typeFlag != WindowFlags.CONTEXT_MENU and window.layer in _HELP_LAYOUT_RESTRICTED_LAYERS and window.windowStatus in (WindowStatus.LOADING, WindowStatus.LOADED) and not window.isHidden()


class Hangar(LobbySelectableView, HangarMeta, IGlobalListener):
    _SOUND_STATE_PLACE = 'STATE_hangar_place'
    _SOUND_STATE_PLACE_GARAGE = 'STATE_hangar_place_garage'
    __background_alpha__ = 0.0
    __SOUND_SETTINGS = CommonSoundSpaceSettings(name='hangar', entranceStates={_SOUND_STATE_PLACE: _SOUND_STATE_PLACE_GARAGE,
     StatesGroup.HANGAR_FILTERED: States.HANGAR_FILTERED_OFF}, exitStates={}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent='', exitEvent='')
    rankedController = dependency.descriptor(IRankedBattlesController)
    epicController = dependency.descriptor(IEpicBattleMetaGameController)
    battlePassController = dependency.descriptor(IBattlePassController)
    battleRoyaleController = dependency.descriptor(IBattleRoyaleController)
    bootcampController = dependency.descriptor(IBootcampController)
    itemsCache = dependency.descriptor(IItemsCache)
    detachmentCache = dependency.descriptor(IDetachmentCache)
    igrCtrl = dependency.descriptor(IIGRController)
    lobbyContext = dependency.descriptor(ILobbyContext)
    statsCollector = dependency.descriptor(IStatisticsCollector)
    gui = dependency.descriptor(IGuiLoader)
    _settingsCore = dependency.descriptor(ISettingsCore)
    hangarSpace = dependency.descriptor(IHangarSpace)
    _promoController = dependency.descriptor(IPromoController)
    _connectionMgr = dependency.descriptor(IConnectionManager)
    _offersBannerController = dependency.descriptor(IOffersBannerController)
    uiLogger = DetachmentLogger(GROUP.HANGAR_DETACHMENT_WIDGET_BUTTONS)
    __mapboxCtrl = dependency.descriptor(IMapboxController)
    _COMMON_SOUND_SPACE = __SOUND_SETTINGS

    def __init__(self, _=None):
        LobbySelectableView.__init__(self, 0)
        self.__currentCarouselAlias = None
        self.__isSpaceReadyForC11n = False
        self.__isVehicleReadyForC11n = False
        self.__isVehicleCameraReadyForC11n = False
        self.__isUnitJoiningInProgress = False
        self.__urlMacros = URLMacros()
        self.__teaser = None
        self.__timer = None
        self.__updateDogTagsState()
        return

    def onEscape(self):
        dialogsContainer = self.app.containerManager.getContainer(WindowLayer.TOP_WINDOW)
        if not dialogsContainer.getView(criteria={POP_UP_CRITERIA.VIEW_ALIAS: VIEW_ALIAS.LOBBY_MENU}):
            self.fireEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.LOBBY_MENU)), scope=EVENT_BUS_SCOPE.LOBBY)

    def onCloseBtnClick(self):
        self.battleRoyaleController.selectRandomBattle()

    def hideTeaser(self):
        self.__teaser.stop(byUser=True)
        self.__teaser = None
        return

    def onTeaserClick(self):
        self._promoController.showLastTeaserPromo()

    def showHelpLayout(self):
        windows = self.gui.windowsManager.findWindows(predicateHelpLayoutAllowedWindow)
        if not windows:
            self.gui.windowsManager.onWindowStatusChanged += self.__onWindowLoaded
            self.fireEvent(LobbySimpleEvent(LobbySimpleEvent.SHOW_HELPLAYOUT), scope=EVENT_BUS_SCOPE.LOBBY)
            self.as_showHelpLayoutS()

    def closeHelpLayout(self):
        self.gui.windowsManager.onWindowStatusChanged -= self.__onWindowLoaded
        nextTick(partial(self.fireEvent, LobbySimpleEvent(LobbySimpleEvent.CLOSE_HELPLAYOUT), EVENT_BUS_SCOPE.LOBBY))
        self.as_closeHelpLayoutS()

    @uiLogger.dLog(ACTION.DETACHMENT_MOVE_TO_BARRACKS)
    def onUnloadBtnClick(self):
        if not g_currentVehicle.isPresent():
            return
        detInvID = g_currentVehicle.item.getLinkedDetachmentID()
        if detInvID:
            ActionsFactory.doAction(ActionsFactory.RESET_DETACHMENT_VEHICLE_LINK, detInvID)

    @g_detachmentFlowLogger.dFlow(uiLogger.group, GROUP.RAISE_EFFICIENCY)
    def onRaisePerfBtnClick(self):
        showDetachmentViewById(NavigationViewModel.PERSONAL_CASE_PROGRESSION, {'detInvID': g_currentVehicle.item.getLinkedDetachmentID()})

    @g_detachmentFlowLogger.dFlow(uiLogger.group, GROUP.ASSIGN_DETACHMENT)
    def onReplaceDetachmentBtnClick(self):
        shared_events.showAssignDetachmentToVehicleView(g_currentVehicle.invID)

    def onReturnPrevDetachmentBtnClick(self):
        if not g_currentVehicle.isPresent():
            return
        ActionsFactory.doAction(ActionsFactory.ASSIGN_DETACHMENT, g_currentVehicle.item.lastDetachmentID, g_currentVehicle.item.invID, TypeDetachmentAssignToVehicle.IS_LAST)

    def _populate(self):
        LobbySelectableView._populate(self)
        g_detachmentTankSetupVehicle.restoreCurrentVehicle()
        self.__isSpaceReadyForC11n = self.hangarSpace.spaceInited
        self.__isVehicleReadyForC11n = self.hangarSpace.isModelLoaded
        self.__checkVehicleCameraState()
        g_currentVehicle.onChanged += self.__onCurrentVehicleChanged
        self.hangarSpace.onVehicleChangeStarted += self.__onVehicleLoading
        self.hangarSpace.onVehicleChanged += self.__onVehicleLoaded
        self.hangarSpace.onSpaceRefresh += self.__onSpaceRefresh
        self.hangarSpace.onSpaceCreate += self.__onSpaceCreate
        self.igrCtrl.onIgrTypeChanged += self.__onIgrTypeChanged
        self.itemsCache.onSyncCompleted += self.onCacheResync
        self.rankedController.onUpdated += self.onRankedUpdate
        self.rankedController.onGameModeStatusTick += self.__updateAlertMessage
        self.__mapboxCtrl.onPrimeTimeStatusUpdated += self.__updateAlertMessage
        self.battleRoyaleController.onUpdated += self.__updateBattleRoyaleComponents
        self.epicController.onUpdated += self.__onEpicSkillsUpdate
        self.epicController.onPrimeTimeStatusUpdated += self.__onEpicSkillsUpdate
        self._promoController.onNewTeaserReceived += self.__onTeaserReceived
        self.hangarSpace.setVehicleSelectable(True)
        g_prbCtrlEvents.onVehicleClientStateChanged += self.__onVehicleClientStateChanged
        g_playerEvents.onPrebattleInvitationAccepted += self.__onPrebattleInvitationAccepted
        unitMgr = prb_getters.getClientUnitMgr()
        if unitMgr:
            unitMgr.onUnitJoined += self.__onUnitJoined
        g_clientUpdateManager.addCallbacks({'inventory': self.__onInventoryUpdate})
        self.lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingChanged
        self._settingsCore.onSettingsChanged += self.__onSettingsChanged
        self.battlePassController.onSeasonStateChange += self.__switchCarousels
        self.startGlobalListening()
        self.__updateAll()
        self.addListener(LobbySimpleEvent.WAITING_SHOWN, self.__onWaitingShown, EVENT_BUS_SCOPE.LOBBY)
        self.addListener(events.FightButtonEvent.FIGHT_BUTTON_UPDATE, self.__handleFightButtonUpdated, scope=EVENT_BUS_SCOPE.LOBBY)
        self.addListener(CameraRelatedEvents.CAMERA_ENTITY_UPDATED, self.__handleSelectedEntityUpdated)
        self.statsCollector.noteHangarLoadingState(HANGAR_LOADING_STATE.HANGAR_UI_READY, showSummaryNow=True)
        lobbyContext = dependency.instance(ILobbyContext)
        isCrewBooksEnabled = lobbyContext.getServerSettings().isCrewBooksEnabled()
        getTutorialGlobalStorage().setValue(GLOBAL_FLAG.CREW_BOOKS_ENABLED, isCrewBooksEnabled)
        self.__timer = CallbackDelayer()
        self._offersBannerController.showBanners()
        self.fireEvent(events.HangarCustomizationEvent(events.HangarCustomizationEvent.RESET_VEHICLE_MODEL_TRANSFORM), scope=EVENT_BUS_SCOPE.LOBBY)
        if g_currentVehicle.isPresent():
            g_currentVehicle.refreshModel()
        if self.bootcampController.isInBootcamp():
            self.as_setDQWidgetLayoutS(DAILY_QUESTS_WIDGET_CONSTANTS.WIDGET_LAYOUT_SINGLE)

    def _dispose(self):
        self.removeListener(LobbySimpleEvent.WAITING_SHOWN, self.__onWaitingShown, EVENT_BUS_SCOPE.LOBBY)
        self.removeListener(events.FightButtonEvent.FIGHT_BUTTON_UPDATE, self.__handleFightButtonUpdated, scope=EVENT_BUS_SCOPE.LOBBY)
        self.removeListener(CameraRelatedEvents.CAMERA_ENTITY_UPDATED, self.__handleSelectedEntityUpdated)
        self.itemsCache.onSyncCompleted -= self.onCacheResync
        g_currentVehicle.onChanged -= self.__onCurrentVehicleChanged
        self.hangarSpace.onVehicleChangeStarted -= self.__onVehicleLoading
        self.hangarSpace.onVehicleChanged -= self.__onVehicleLoaded
        self.hangarSpace.onSpaceRefresh -= self.__onSpaceRefresh
        self.hangarSpace.onSpaceCreate -= self.__onSpaceCreate
        self.igrCtrl.onIgrTypeChanged -= self.__onIgrTypeChanged
        self.rankedController.onUpdated -= self.onRankedUpdate
        self.__mapboxCtrl.onPrimeTimeStatusUpdated -= self.__updateAlertMessage
        self.rankedController.onGameModeStatusTick -= self.__updateAlertMessage
        self.battleRoyaleController.onUpdated -= self.__updateBattleRoyaleComponents
        self.epicController.onUpdated -= self.__onEpicSkillsUpdate
        self.epicController.onPrimeTimeStatusUpdated -= self.__onEpicSkillsUpdate
        self._promoController.onNewTeaserReceived -= self.__onTeaserReceived
        if self.__teaser is not None:
            self.__teaser.stop()
            self.__teaser = None
        self.hangarSpace.setVehicleSelectable(False)
        g_prbCtrlEvents.onVehicleClientStateChanged -= self.__onVehicleClientStateChanged
        unitMgr = prb_getters.getClientUnitMgr()
        if unitMgr:
            unitMgr.onUnitJoined -= self.__onUnitJoined
        g_playerEvents.onPrebattleInvitationAccepted -= self.__onPrebattleInvitationAccepted
        g_clientUpdateManager.removeObjectCallbacks(self)
        self._settingsCore.onSettingsChanged -= self.__onSettingsChanged
        self.lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingChanged
        self.battlePassController.onSeasonStateChange -= self.__switchCarousels
        self.__timer.clearCallbacks()
        self.__timer = None
        self.closeHelpLayout()
        self.stopGlobalListening()
        self._offersBannerController.hideBanners()
        LobbySelectableView._dispose(self)
        return

    def _updateBattleRoyaleMode(self):
        self.as_toggleBattleRoyaleS(g_currentVehicle.isOnlyForBattleRoyaleBattles())

    def __updateDogTagsState(self):
        isDogTagsEnabled = self.lobbyContext.getServerSettings().isDogTagEnabled()
        getTutorialGlobalStorage().setValue(GLOBAL_FLAG.DOGTAGS_ENABLED, isDogTagsEnabled)

    def __onWindowLoaded(self, uniqueID, newStatus):
        window = self.gui.windowsManager.getWindow(uniqueID)
        if window in _HELP_LAYOUT_RESTRICTED_LAYERS and newStatus in (WindowStatus.LOADING, WindowStatus.LOADED):
            self.closeHelpLayout()

    def __switchCarousels(self, force=False):
        prevCarouselAlias = self.__currentCarouselAlias
        linkage = HANGAR_ALIASES.TANK_CAROUSEL_UI
        newCarouselAlias = HANGAR_ALIASES.TANK_CAROUSEL
        if self.prbDispatcher is not None:
            if self.prbDispatcher.getFunctionalState().isInPreQueue(QUEUE_TYPE.RANKED):
                newCarouselAlias = HANGAR_ALIASES.RANKED_TANK_CAROUSEL
            elif self.prbDispatcher.getFunctionalState().isInPreQueue(QUEUE_TYPE.EPIC) or self.prbDispatcher.getFunctionalState().isInUnit(PREBATTLE_TYPE.EPIC):
                newCarouselAlias = HANGAR_ALIASES.EPICBATTLE_TANK_CAROUSEL
            elif self.battleRoyaleController.isBattleRoyaleMode():
                newCarouselAlias = HANGAR_ALIASES.ROYALE_TANK_CAROUSEL
            elif self.__mapboxCtrl.isMapboxMode():
                newCarouselAlias = HANGAR_ALIASES.MAPBOX_TANK_CAROUSEL
            elif self.battlePassController.isVisible() and self.battlePassController.isValidBattleType(self.prbDispatcher.getEntity()):
                newCarouselAlias = HANGAR_ALIASES.BATTLEPASS_TANK_CAROUSEL
        if prevCarouselAlias != newCarouselAlias or force:
            self.as_setCarouselS(linkage, newCarouselAlias)
            self.__currentCarouselAlias = newCarouselAlias
        return

    def __updateAmmoPanel(self):
        if self.ammoPanel:
            self.ammoPanel.update()

    def __updateParams(self):
        if self.paramsPanel:
            self.paramsPanel.update()

    def __updateVehicleInResearchPanel(self):
        if self.researchPanel is not None:
            self.researchPanel.onCurrentVehicleChanged()
        return

    def __updateNavigationInResearchPanel(self):
        if self.prbDispatcher is not None and self.researchPanel is not None:
            self.researchPanel.setNavigationEnabled(not self.prbDispatcher.getFunctionalState().isNavigationDisabled())
        return

    def __updateHeader(self):
        if self.prbDispatcher is not None:
            if self.prbDispatcher.getFunctionalState().isInPreQueue(QUEUE_TYPE.EPIC) or self.prbDispatcher.getFunctionalState().isInUnit(PREBATTLE_TYPE.EPIC):
                if not self.epicWidget:
                    self.as_setHeaderTypeS(HANGAR_ALIASES.EPIC_WIDGET)
            elif not self.headerComponent:
                self.as_setDefaultHeaderS()
        return

    def __updateHeaderComponent(self):
        if self.headerComponent is not None:
            self.headerComponent.update()
        return

    def __updateRankedHeaderComponent(self):
        if self.headerComponent is not None:
            self.headerComponent.updateRankedHeader()
        return

    def __updateBattleRoyaleHeaderComponent(self):
        if self.headerComponent is not None:
            self.headerComponent.updateBattleRoyaleHeader()
        return

    def __updateHeaderEpicWidget(self):
        if self.epicWidget is not None:
            self.epicWidget.update()
        return

    def __updateCrew(self):
        state = g_currentVehicle.getViewState()
        self.as_setCrewEnabledS(state.isCrewOpsEnabled() and not (g_currentVehicle.isInBattle() or g_currentVehicle.isInUnit() or g_currentVehicle.isCrewLocked()))
        if self.crewPanel is not None:
            self.crewPanel.updateRecruitPanel()
        self.as_setDetachmentWidgetVisibleS(getVisibleCrewWidgetName() == HANGAR_ALIASES.DETACHMENT_WIDGET)
        return

    def __onInventoryUpdate(self, *_):
        self.__updateDetachmentButtons()
        self.__updateAlertMessage()

    def __updateAlertMessage(self, *_):
        if self.prbDispatcher is not None:
            if self.prbDispatcher.getFunctionalState().isInPreQueue(QUEUE_TYPE.RANKED):
                self.__updateRankedAlertMsg()
                return
            if self.prbDispatcher.getFunctionalState().isInPreQueue(QUEUE_TYPE.MAPBOX):
                self.__updateMapboxAlertMsg()
                return
        self.as_setAlertMessageBlockVisibleS(False)
        return

    def __updateRankedAlertMsg(self):
        status, _, _ = self.rankedController.getPrimeTimeStatus()
        hasSuitVehs = self.rankedController.hasSuitableVehicles()
        isBlockedStatus = status in (PrimeTimeStatus.NOT_AVAILABLE, PrimeTimeStatus.NOT_SET, PrimeTimeStatus.FROZEN)
        buttonCallback = showRankedPrimeTimeWindow if hasSuitVehs else g_eventDispatcher.loadRankedUnreachable
        data = ranked_helpers.getAlertStatusVO()
        self.__updateAlertBlock(buttonCallback, data, isBlockedStatus or not hasSuitVehs)

    def __updateMapboxAlertMsg(self):
        status, _, _ = self.__mapboxCtrl.getPrimeTimeStatus()
        isBlockedStatus = status in (PrimeTimeStatus.NOT_AVAILABLE, PrimeTimeStatus.NOT_SET, PrimeTimeStatus.FROZEN)
        data = mapbox_helpers.getPrimeTimeStatusVO()
        self.__updateAlertBlock(shared_events.showMapboxPrimeTimeWindow, data, isBlockedStatus)

    def __updateAlertBlock(self, callback, data, visible):
        self.as_setAlertMessageBlockVisibleS(visible)
        if visible and self.alertMessage is not None:
            self.alertMessage.update(data._asdict(), onBtnClickCallback=callback)
        return

    def __onWaitingShown(self, _):
        self.closeHelpLayout()

    def __handleFightButtonUpdated(self, _):
        self.__updateNavigationInResearchPanel()

    def __handleSelectedEntityUpdated(self, event):
        ctx = event.ctx
        if ctx['state'] != CameraMovementStates.FROM_OBJECT:
            entity = BigWorld.entities.get(ctx['entityId'], None)
            if isinstance(entity, HeroTank):
                descriptor = entity.typeDescriptor
                if descriptor:
                    shared_events.showHeroTankPreview(descriptor.type.compactDescr)
        self.__checkVehicleCameraState()
        self.__updateState()
        return

    def __onTeaserReceived(self, teaserData, showCallback, closeCallback):
        if self.__teaser is None:
            self.__teaser = TeaserViewer(self, showCallback, closeCallback)
        self.__teaser.show(teaserData, self._promoController.getPromoCount())
        return

    def _highlight3DEntityAndShowTT(self, entity):
        itemId = entity.selectionId
        if itemId:
            self.as_show3DSceneTooltipS(TOOLTIPS_CONSTANTS.ENVIRONMENT, [itemId])

    def _fade3DEntityAndHideTT(self, entity):
        self.as_hide3DSceneTooltipS()

    def _onRegisterFlashComponent(self, viewPy, alias):
        super(Hangar, self)._onRegisterFlashComponent(viewPy, alias)
        if alias == HANGAR_ALIASES.AMMUNITION_PANEL_INJECT:
            event = viewPy.getOnPanelSectionSelected()
            event += self.__onOptDeviceClick

    def _onUnregisterFlashComponent(self, viewPy, alias):
        super(Hangar, self)._onUnregisterFlashComponent(viewPy, alias)
        if alias == HANGAR_ALIASES.AMMUNITION_PANEL_INJECT and viewPy.getInjectView():
            event = viewPy.getOnPanelSectionSelected()
            event -= self.__onOptDeviceClick

    @property
    def detachmentWidgetInject(self):
        return self.getComponent(HANGAR_ALIASES.DETACHMENT_WIDGET).getInjectView()

    @property
    def ammoPanel(self):
        return self.getComponent(HANGAR_ALIASES.AMMUNITION_PANEL)

    @property
    def paramsPanel(self):
        return self.getComponent(HANGAR_ALIASES.VEHICLE_PARAMETERS)

    @property
    def crewPanel(self):
        return self.getComponent(HANGAR_ALIASES.CREW)

    @property
    def researchPanel(self):
        return self.getComponent(HANGAR_ALIASES.RESEARCH_PANEL)

    @property
    def headerComponent(self):
        return self.getComponent(HANGAR_ALIASES.HEADER)

    @property
    def alertMessage(self):
        return self.getComponent(HANGAR_ALIASES.ALERT_MESSAGE_BLOCK)

    @property
    def epicWidget(self):
        return self.getComponent(HANGAR_ALIASES.EPIC_WIDGET)

    def onCacheResync(self, reason, diff):
        if reason == CACHE_SYNC_REASON.SHOP_RESYNC:
            self.__updateAll()
            return
        else:
            if diff is not None and GUI_ITEM_TYPE.VEHICLE in diff and g_currentVehicle.isPresent():
                if g_currentVehicle.item.invID in diff[GUI_ITEM_TYPE.VEHICLE]:
                    self.__updateAmmoPanel()
            return

    def onPlayerStateChanged(self, entity, roster, accountInfo):
        if accountInfo.isCurrentPlayer():
            self.__updateState()
            self.__updateAmmoPanel()
            self.__updateCrew()

    def onUnitPlayerStateChanged(self, pInfo):
        if pInfo.isCurrentPlayer():
            self.__onEntityChanged()

    def onUnitPlayersListChanged(self):
        self.__updateHeader()
        self.__updateHeaderComponent()
        self.__updateHeaderEpicWidget()

    def onPrbEntitySwitched(self):
        self.__onEntityChanged()

    def onEnqueued(self, queueType, *args):
        self.__onEntityChanged()

    def onDequeued(self, queueType, *args):
        self.__onEntityChanged()

    def onRankedUpdate(self):
        self.__updateHeader()
        self.__updateHeaderComponent()
        self.__updateRankedHeaderComponent()

    def __updateBattleRoyaleComponents(self):
        self.__updateHeader()
        self.__updateHeaderComponent()
        self.__updateBattleRoyaleHeaderComponent()

    def __onEpicSkillsUpdate(self, *_):
        self.__updateHeader()
        self.__updateHeaderComponent()
        self.__updateHeaderEpicWidget()
        self.__updateAmmoPanel()

    def __updateAll(self):
        Waiting.show('updateVehicle')
        self.__switchCarousels()
        self.__updateState()
        self.__updateAmmoPanel()
        self.__updateCrew()
        self.__updateParams()
        self.__updateVehicleInResearchPanel()
        self.__updateNavigationInResearchPanel()
        self.__updateHeader()
        self.__updateHeaderComponent()
        self.__updateRankedHeaderComponent()
        self.__updateHeaderEpicWidget()
        self.__updateAlertMessage()
        self.__updateBattleRoyaleComponents()
        self._updateBattleRoyaleMode()
        Waiting.hide('updateVehicle')

    def __onCurrentVehicleChanged(self):
        Waiting.show('updateVehicle')
        self.__updateState()
        self.__updateAmmoPanel()
        self.__updateCrew()
        self.__updateParams()
        self.__updateVehicleInResearchPanel()
        self.__updateHeader()
        self.__updateHeaderComponent()
        self.__updateHeaderEpicWidget()
        self._updateBattleRoyaleMode()
        Waiting.hide('updateVehicle')

    def __onSpaceRefresh(self):
        self.__isSpaceReadyForC11n = False
        self.__updateState()

    def __onSpaceCreate(self):
        self.__isSpaceReadyForC11n = True
        self.__updateState()

    def __onVehicleLoading(self):
        self.__isVehicleReadyForC11n = False
        self.__updateState()

    def __onVehicleLoaded(self):
        self.__isVehicleReadyForC11n = True
        self.__checkVehicleCameraState()
        self.__updateState()

    def __onIgrTypeChanged(self, *args):
        self.__updateVehicleInResearchPanel()
        self.__updateHeader()
        self.__updateHeaderComponent()
        self.__updateHeaderEpicWidget()
        self.__updateParams()

    def __getDetachmentButtonsState(self):
        if g_currentVehicle.isInBattle():
            return (True, TOOLTIPS.FASTOPERATION_INBATTLE_BODY)
        return (True, TOOLTIPS.FASTOPERATION_INPLATOON_BODY) if g_currentVehicle.isInUnit() else (False, '')

    def __updateDetachmentButtons(self):
        if not g_currentVehicle.isPresent():
            return
        isLocked, tooltipBody = self.__getDetachmentButtonsState()
        self.as_setDetachmentBtnsLockedS(isLocked, makeTooltip(body=tooltipBody) if tooltipBody else '')
        if getVisibleCrewWidgetName() != HANGAR_ALIASES.DETACHMENT_WIDGET:
            return
        dataVO = {'returnPrevious': self.__getReturnDetachmentOperationData(),
         'raisePerf': self.__getRaiseDetachmentOperationData(),
         'unload': self.__getUnloadDetachmentOperationData(),
         'replace': self.__getReplaceDetachhmentOperationData()}
        booksCount = crewBooksViewedCache().getNewBooksCount()
        self.as_updateDetachmentBtnsS(dataVO)
        self.as_setRaisePerfBtnCounterS(booksCount)
        self.as_setDetachmentLinkedS(g_currentVehicle.getLinkedDetachmentID())
        if self.detachmentWidgetInject:
            self.detachmentWidgetInject.updateView()

    def __updateState(self):
        state = g_currentVehicle.getViewState()
        if g_currentVehicle.hasOldCrew():
            if g_currentVehicle.isInBattle():
                operationsBtnTooltip = makeTooltip(body=backport.text(R.strings.crew_operations.crewOperationsDisabled.btn.tooltip.inBattle.body()))
            elif g_currentVehicle.isInUnit():
                operationsBtnTooltip = makeTooltip(body=backport.text(R.strings.crew_operations.crewOperationsDisabled.btn.tooltip.inUnit.body()))
            elif g_currentVehicle.isCrewLocked():
                operationsBtnTooltip = makeTooltip(body=backport.text(R.strings.crew_operations.crewOperationsDisabled.btn.tooltip.crewLocked.body()))
            else:
                operationsBtnTooltip = makeTooltip(_ms(backport.text(R.strings.crew_operations.crewOperations.btn.tooltip.header())), _ms(backport.text(R.strings.crew_operations.crewOperations.btn.tooltip.body())))
            self.as_setOpeationsBtnTooltipS(operationsBtnTooltip)
        self.__updateDetachmentButtons()
        isBattleRoyaleMode = self.battleRoyaleController.isBattleRoyaleMode()
        isC11nEnabled = self.lobbyContext.getServerSettings().isCustomizationEnabled() and state.isCustomizationEnabled() and not state.isOnlyForEventBattles() and self.__isSpaceReadyForC11n and self.__isVehicleReadyForC11n and self.__isVehicleCameraReadyForC11n and not isBattleRoyaleMode
        if isC11nEnabled:
            customizationTooltip = makeTooltip(_ms(backport.text(R.strings.tooltips.hangar.tuning.header())), _ms(backport.text(R.strings.tooltips.hangar.tuning.body())))
        else:
            customizationTooltip = makeTooltip(_ms(backport.text(R.strings.tooltips.hangar.tuning.disabled.header())), _ms(backport.text(R.strings.tooltips.hangar.tuning.disabled.body())))
        changeNationVisibility = g_currentVehicle.isPresent() and g_currentVehicle.item.hasNationGroup
        isNationChangeAvailable = g_currentVehicle.isPresent() and g_currentVehicle.item.isNationChangeAvailable
        if changeNationVisibility:
            if isNationChangeAvailable:
                changeNationTooltipHeader = R.strings.tooltips.hangar.nationChange.header()
                changeNationTooltipBody = R.strings.tooltips.hangar.nationChange.body()
            else:
                changeNationTooltipHeader = R.strings.tooltips.hangar.nationChange.disabled.header()
                if g_currentVehicle.item.isBroken:
                    changeNationTooltipBody = R.strings.tooltips.hangar.nationChange.disabled.body.destroyed()
                elif g_currentVehicle.item.isInBattle:
                    changeNationTooltipBody = R.strings.tooltips.hangar.nationChange.disabled.body.inBattle()
                elif g_currentVehicle.item.isInUnit:
                    changeNationTooltipBody = R.strings.tooltips.hangar.nationChange.disabled.body.inSquad()
                else:
                    changeNationTooltipBody = ''
            if changeNationTooltipBody == '':
                changeNationTooltip = makeTooltip(_ms(backport.text(changeNationTooltipHeader)), '')
            else:
                changeNationTooltip = makeTooltip(_ms(backport.text(changeNationTooltipHeader)), _ms(backport.text(changeNationTooltipBody)))
        else:
            changeNationTooltip = ''
        changeNationIsNew = not AccountSettings.getSettings(NATION_CHANGE_VIEWED)
        isMaintenanceEnabled = state.isMaintenanceEnabled()
        isEquipmentEnabled = g_currentVehicle.isPresent() and not g_currentVehicle.isEquipmentLocked()
        if isMaintenanceEnabled and isEquipmentEnabled:
            maintenanceTooltip = TOOLTIPS.HANGAR_MAINTENANCE
        else:
            maintenanceTooltip = TOOLTIPS.HANGAR_MAINTENANCE_DISABLED
        self.as_setupAmmunitionPanelS({'maintenanceEnabled': isMaintenanceEnabled,
         'maintenanceTooltip': maintenanceTooltip,
         'customizationEnabled': isC11nEnabled,
         'customizationTooltip': customizationTooltip,
         'changeNationVisible': changeNationVisibility,
         'changeNationEnable': isNationChangeAvailable,
         'changeNationTooltip': changeNationTooltip,
         'changeNationIsNew': changeNationIsNew})
        self.as_setControlsVisibleS(state.isUIShown())

    def __onEntityChanged(self):
        self.__updateState()
        self.__updateAmmoPanel()
        self.__updateCrew()
        self.__updateAlertMessage()
        self.__updateNavigationInResearchPanel()
        self.__updateHeader()
        self.__updateHeaderComponent()
        self.__updateRankedHeaderComponent()
        self.__updateHeaderEpicWidget()
        self.__switchCarousels()
        self.__updateBattleRoyaleComponents()

    def __isSpecialMode(self):
        return self.prbDispatcher is not None and self.prbDispatcher.getFunctionalState().isInUnit() or self.prbDispatcher.getFunctionalState().isInPreQueue(QUEUE_TYPE.RANKED) or self.prbDispatcher.getFunctionalState().isInPreQueue(QUEUE_TYPE.EPIC)

    def __onVehicleClientStateChanged(self, _):
        self.__updateAmmoPanel()
        self.__updateState()
        self.__updateCrew()

    def __onServerSettingChanged(self, diff):
        if 'isRegularQuestEnabled' in diff:
            self.__updateHeader()
            self.__updateHeaderComponent()
            self.__updateHeaderEpicWidget()
        if 'isCustomizationEnabled' in diff:
            self.__updateState()
        if BATTLE_PASS_CONFIG_NAME in diff:
            self.__switchCarousels()
        if Configs.BATTLE_ROYALE_CONFIG.value in diff:
            self.__updateBattleRoyaleComponents()
            self.__updateState()
            self.__switchCarousels(force=True)
        if DOG_TAGS_CONFIG in diff:
            self.__updateDogTagsState()

    def __onSettingsChanged(self, diff):
        if SETTINGS_SECTIONS.UI_STORAGE in diff:
            if self.ammoPanel:
                self.ammoPanel.update()

    def __checkVehicleCameraState(self):
        vehicleEntity = self.hangarSpace.getVehicleEntity()
        if vehicleEntity is None:
            return
        else:
            self.__isVehicleCameraReadyForC11n = vehicleEntity.state == CameraMovementStates.ON_OBJECT
            return

    def __onOptDeviceClick(self, **kwargs):
        if self.hangarSpace.spaceLoading():
            _logger.warning('Optional Device click was not handled (kwargs=%s). HangarSpace is currently  loading.', kwargs)
        elif not self.__isUnitJoiningInProgress:
            self.as_showSwitchToAmmunitionS()
            showAmmunitionSetupView(**kwargs)

    def __onUnitJoined(self, _, __):
        self.__isUnitJoiningInProgress = False
        self.__timer.stopCallback(self.__onResetUnitJoiningProgress)

    def __onPrebattleInvitationAccepted(self, _, __):
        self.__isUnitJoiningInProgress = True
        self.__timer.delayCallback(15, self.__onResetUnitJoiningProgress)

    def __onResetUnitJoiningProgress(self):
        self.__isUnitJoiningInProgress = False

    def __getAvailableRecruits(self, nationID):
        items = self.itemsCache.items
        criteria = REQ_CRITERIA.TANKMAN.ACTIVE | ~REQ_CRITERIA.TANKMAN.DISMISSED | REQ_CRITERIA.NATIONS([nationID]) | ~REQ_CRITERIA.TANKMAN.IN_TANK
        excludeCriteria = ~REQ_CRITERIA.VEHICLE.LOCKED | ~REQ_CRITERIA.VEHICLE.HAS_TAGS([VEHICLE_TAGS.CREW_LOCKED])
        excludeCriteria |= ~REQ_CRITERIA.VEHICLE.BATTLE_ROYALE | ~REQ_CRITERIA.VEHICLE.EVENT_BATTLE
        dirtyRecruits = items.getTankmen(criteria)
        suitableRecruits = items.removeUnsuitableTankmen(dirtyRecruits.itervalues(), excludeCriteria)
        return len(suitableRecruits)

    def __getReplaceDetachhmentOperationData(self):
        recruitCount = self.__getAvailableRecruits(g_currentVehicle.item.nationID)
        if g_currentVehicle.isCrewLocked():
            return self.__getDetachmentButtonTooltipObject('replaceDetachment', False, 'locked')
        return self.__getDetachmentButtonTooltipObject('replaceDetachment', True, 'hasRecruits') if recruitCount else self.__getDetachmentButtonTooltipObject('replaceDetachment', True, 'noRecruits')

    def __getUnloadDetachmentOperationData(self):
        return self.__getDetachmentButtonTooltipObject('unloadDetachment', False, 'locked') if g_currentVehicle.isCrewLocked() else self.__getDetachmentButtonTooltipObject('unloadDetachment', g_currentVehicle.hasDetachment())

    def __getRaiseDetachmentOperationData(self):
        return self.__getDetachmentButtonTooltipObject('raisePerformance', True)

    def __getReturnDetachmentOperationData(self):
        currentVehicle = g_currentVehicle.item
        lastCrewIDs = currentVehicle.lastCrew
        if lastCrewIDs and not all((recruit is None for recruit in lastCrewIDs)):
            return self.__getDetachmentButtonTooltipObject('returnDetachment', False, 'usedOldCrew')
        lastDetachmentID = currentVehicle.lastDetachmentID
        if lastDetachmentID is None:
            return self.__getDetachmentButtonTooltipObject('returnDetachment', False, 'noPrevious')
        lastDetachment = self.detachmentCache.getDetachment(lastDetachmentID)
        if lastDetachment is None or isDetachmentInRecycleBin(lastDetachment):
            return self.__getDetachmentButtonTooltipObject('returnDetachment', False, 'dismissed')
        assignResult = canAssignDetachmentToVehicle(lastDetachment, currentVehicle)
        if assignResult == CanAssignResult.DETACHMENT_LOCKED:
            return self.__getDetachmentButtonTooltipObject('returnDetachment', False, 'inBattle')
        elif assignResult == CanAssignResult.DETACHMENT_LOCKED_BY_LOCK_CREW:
            return self.__getDetachmentButtonTooltipObject('returnDetachment', False, 'otherVehicleLocked')
        elif assignResult == CanAssignResult.NON_SUITABLE_TYPE or assignResult == CanAssignResult.WRONG_CLASS:
            return self.__getDetachmentButtonTooltipObject('returnDetachment', False, 'retrained')
        else:
            return self.__getDetachmentButtonTooltipObject('returnDetachment', False, 'alreadyLinked') if assignResult == CanAssignResult.SAME_VEHICLE else self.__getDetachmentButtonTooltipObject('returnDetachment', True)

    def __getDetachmentButtonTooltipObject(self, tooltipId, isEnabled, stateId=None):
        tooltipHeaderText = backport.text(R.strings.crew_operations.dyn(tooltipId).btn.tooltip.header())
        if stateId:
            tooltipBodyText = backport.text(R.strings.crew_operations.dyn(tooltipId).btn.tooltip.dyn(stateId).body())
        else:
            tooltipBodyText = backport.text(R.strings.crew_operations.dyn(tooltipId).btn.tooltip.body())
        return {'tooltip': makeTooltip(tooltipHeaderText, tooltipBodyText),
         'isEnabled': isEnabled}
