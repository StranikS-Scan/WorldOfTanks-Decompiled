# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/Hangar.py
import logging
from functools import partial
import BigWorld
import typing
from shared_utils import nextTick
from ClientSelectableCameraObject import ClientSelectableCameraObject
from CurrentVehicle import g_currentVehicle, g_currentPreviewVehicle
from HeroTank import HeroTank
from PlayerEvents import g_playerEvents
from account_helpers import AccountSettings
from account_helpers.AccountSettings import NATION_CHANGE_VIEWED
from account_helpers.settings_core.ServerSettingsManager import SETTINGS_SECTIONS
from battle_pass_common import BATTLE_PASS_CONFIG_NAME
from constants import Configs, DOG_TAGS_CONFIG, PREBATTLE_TYPE, QUEUE_TYPE, RENEWABLE_SUBSCRIPTION_CONFIG
from frameworks.wulf import WindowFlags, WindowLayer, WindowStatus, ViewStatus
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.Waiting import Waiting
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.LobbySelectableView import LobbySelectableView
from gui.Scaleform.daapi.view.lobby.epicBattle import epic_helpers
from gui.Scaleform.daapi.view.lobby.hangar.carousel_event_entry_widget import isAnyEntryVisible
from gui.Scaleform.daapi.view.lobby.mapbox import mapbox_helpers
from gui.Scaleform.daapi.view.meta.HangarMeta import HangarMeta
from gui.Scaleform.framework.managers.containers import POP_UP_CRITERIA
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.Scaleform.genConsts.HANGAR_ALIASES import HANGAR_ALIASES
from gui.Scaleform.genConsts.HANGAR_CONSTS import HANGAR_CONSTS
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.game_control.links import URLMacros
from gui.game_loading.resources.consts import Milestones
from gui.hangar_cameras.hangar_camera_common import CameraMovementStates, CameraRelatedEvents
from gui.hangar_presets.hangar_gui_helpers import ifComponentAvailable
from gui.impl import backport
from gui.impl.gen import R
from gui.marathon.marathon_event import MarathonEvent
from gui.periodic_battles.models import PrimeTimeStatus
from gui.prb_control import prb_getters
from gui.prb_control.ctrl_events import g_prbCtrlEvents
from gui.prb_control.entities.listener import IGlobalListener
from gui.prestige.prestige_helpers import hasVehiclePrestige
from gui.promo.hangar_teaser_widget import TeaserViewer
from gui.resource_well.resource_well_helpers import isResourceWellRewardVehicle
from gui.shared import EVENT_BUS_SCOPE, event_dispatcher as shared_events, events
from gui.shared.event_dispatcher import showFrontlineInfoWindow
from gui.shared.events import AmmunitionPanelViewEvent, LobbySimpleEvent
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.items_cache import CACHE_SYNC_REASON
from gui.shared.tutorial_helper import getTutorialGlobalStorage
from gui.shared.utils.functions import makeTooltip
from gui.sounds.filters import States, StatesGroup
from helpers import dependency
from helpers.CallbackDelayer import CallbackDelayer
from helpers.i18n import makeString as _ms
from helpers.statistics import HANGAR_LOADING_STATE
from helpers.time_utils import ONE_MINUTE
from nation_change_helpers.client_nation_change_helper import getChangeNationTooltip
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.connection_mgr import IConnectionManager
from skeletons.gui.game_control import IWotPlusController, IBattlePassController, IBattleRoyaleController, IComp7Controller, IEpicBattleMetaGameController, IEventLootBoxesController, IFunRandomController, IIGRController, IMapboxController, IMarathonEventsController, IPromoController, IRankedBattlesController, IHangarGuiController
from skeletons.gui.impl import IGuiLoader
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.offers import IOffersBannerController
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.utils import IHangarSpace
from skeletons.helpers.statistics import IStatisticsCollector
from sound_gui_manager import CommonSoundSpaceSettings
from tutorial.control.context import GLOBAL_FLAG
from uilogging.epic_battle.constants import EpicBattleLogKeys, EpicBattleLogActions, EpicBattleLogButtons
from uilogging.epic_battle.loggers import EpicBattleLogger
if typing.TYPE_CHECKING:
    from frameworks.wulf import Window, View
_logger = logging.getLogger(__name__)
_HELP_LAYOUT_RESTRICTED_LAYERS = (WindowLayer.TOP_SUB_VIEW,
 WindowLayer.FULLSCREEN_WINDOW,
 WindowLayer.WINDOW,
 WindowLayer.OVERLAY,
 WindowLayer.TOP_WINDOW)

def _predicateHelpLayoutRestrictedWindow(window):
    return window.typeFlag != WindowFlags.TOOLTIP and window.typeFlag != WindowFlags.CONTEXT_MENU and window.layer in _HELP_LAYOUT_RESTRICTED_LAYERS and window.windowStatus in (WindowStatus.LOADING, WindowStatus.LOADED) and not window.isHidden()


def _predicateHelpLayoutRestrictedView(view):
    return view.layoutID in (R.views.lobby.tanksetup.HangarAmmunitionSetup(),) and view.viewStatus in (ViewStatus.LOADED, ViewStatus.LOADING)


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
    itemsCache = dependency.descriptor(IItemsCache)
    igrCtrl = dependency.descriptor(IIGRController)
    lobbyContext = dependency.descriptor(ILobbyContext)
    statsCollector = dependency.descriptor(IStatisticsCollector)
    gui = dependency.descriptor(IGuiLoader)
    _settingsCore = dependency.descriptor(ISettingsCore)
    hangarSpace = dependency.descriptor(IHangarSpace)
    _promoController = dependency.descriptor(IPromoController)
    _connectionMgr = dependency.descriptor(IConnectionManager)
    _offersBannerController = dependency.descriptor(IOffersBannerController)
    __mapboxCtrl = dependency.descriptor(IMapboxController)
    __marathonCtrl = dependency.descriptor(IMarathonEventsController)
    __funRandomCtrl = dependency.descriptor(IFunRandomController)
    _wotPlusCtrl = dependency.descriptor(IWotPlusController)
    __eventLootBoxes = dependency.descriptor(IEventLootBoxesController)
    __hangarComponentsCtrl = dependency.descriptor(IHangarGuiController)
    __comp7Controller = dependency.descriptor(IComp7Controller)
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
        self.__banTimer = None
        self.__updateDogTagsState()
        nextTick(ClientSelectableCameraObject.switchCamera)()
        return

    @property
    def ammoPanel(self):
        return self.getComponent(HANGAR_ALIASES.AMMUNITION_PANEL)

    @property
    def paramsPanel(self):
        return self.getComponent(HANGAR_ALIASES.VEHICLE_PARAMETERS)

    @property
    def crewWidget(self):
        return self.getComponent(HANGAR_ALIASES.CREW_PANEL_INJECT)

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

    def onUnitPlayerStateChanged(self, pInfo):
        if pInfo.isCurrentPlayer():
            self.__onEntityChanged()

    def onUnitPlayersListChanged(self):
        self.__updateHeaderComponent()
        self.__updateHeaderEpicWidget()

    def onPrbEntitySwitched(self):
        self.__onEntityChanged()
        self.__updateCarouselEventEntryState()

    def onEnqueued(self, queueType, *args):
        self.__onEntityChanged()

    def onDequeued(self, queueType, *args):
        self.__onEntityChanged()

    def onRankedUpdate(self):
        self.__updateHeaderComponent()
        self.__updateRankedHeaderComponent()

    def onEscape(self):
        dialogsContainer = self.app.containerManager.getContainer(WindowLayer.TOP_WINDOW)
        if not dialogsContainer.getView(criteria={POP_UP_CRITERIA.VIEW_ALIAS: VIEW_ALIAS.LOBBY_MENU}):
            self.fireEvent(events.LoadViewEvent(SFViewLoadParams(VIEW_ALIAS.LOBBY_MENU)), scope=EVENT_BUS_SCOPE.LOBBY)

    def hideTeaser(self):
        self.__teaser.stop(byUser=True)
        self.__teaser = None
        return

    def onTeaserClick(self):
        self._promoController.showLastTeaserPromo()

    def showHelpLayout(self):
        windowsManager = self.gui.windowsManager
        windows = windowsManager.findWindows(_predicateHelpLayoutRestrictedWindow)
        views = windowsManager.findViews(_predicateHelpLayoutRestrictedView)
        if not windows and not views:
            self.gui.windowsManager.onWindowStatusChanged += self.__onWindowLoaded
            self.fireEvent(LobbySimpleEvent(LobbySimpleEvent.SHOW_HELPLAYOUT), scope=EVENT_BUS_SCOPE.LOBBY)
            self.as_showHelpLayoutS()

    def closeHelpLayout(self):
        self.gui.windowsManager.onWindowStatusChanged -= self.__onWindowLoaded
        nextTick(partial(self.fireEvent, LobbySimpleEvent(LobbySimpleEvent.CLOSE_HELPLAYOUT), EVENT_BUS_SCOPE.LOBBY))
        self.as_closeHelpLayoutS()

    def _populate(self):
        LobbySelectableView._populate(self)
        self.__hangarComponentsCtrl.holdHangar(self)
        self.__timer = CallbackDelayer()
        self.__banTimer = CallbackDelayer()
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
        self.__funRandomCtrl.subscription.addSubModesWatcher(self.__onFunRandomUpdate, True)
        self.__funRandomCtrl.subscription.addSubModesWatcher(self.__updateAlertMessage, True, True)
        self.battleRoyaleController.onUpdated += self.__updateBattleRoyaleComponents
        self.battleRoyaleController.onBattleRoyaleSpaceLoaded += self.__onBattleRoyaleSpaceLoaded
        self.epicController.onUpdated += self.__onEpicBattleUpdated
        self.epicController.onPrimeTimeStatusUpdated += self.__onEpicBattleUpdated
        self.epicController.onGameModeStatusTick += self.__updateAlertMessage
        self._promoController.onNewTeaserReceived += self.__onTeaserReceived
        self.__comp7Controller.onStatusUpdated += self.__updateAlertMessage
        self.__comp7Controller.onStatusTick += self.__updateAlertMessage
        self.__comp7Controller.onBanUpdated += self.__updateAlertMessage
        self.__comp7Controller.onOfflineStatusUpdated += self.__updateAlertMessage
        self.__comp7Controller.onTournamentBannerStateChanged += self.__updateComp7TournamentWidget
        self.hangarSpace.setVehicleSelectable(True)
        self.__eventLootBoxes.onStatusChange += self.__onLootBoxesEventStatusChange
        g_prbCtrlEvents.onVehicleClientStateChanged += self.__onVehicleClientStateChanged
        g_playerEvents.onPrebattleInvitationAccepted += self.__onPrebattleInvitationAccepted
        unitMgr = prb_getters.getClientUnitMgr()
        if unitMgr:
            unitMgr.onUnitJoined += self.__onUnitJoined
        g_clientUpdateManager.addCallbacks({'inventory': self.__updateAlertMessage})
        self.lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingChanged
        self._settingsCore.onSettingsChanged += self.__onSettingsChanged
        self.battlePassController.onSeasonStateChanged += self.__switchCarousels
        self.startGlobalListening()
        self.__updateAll()
        self.addListener(LobbySimpleEvent.WAITING_SHOWN, self.__onWaitingShown, EVENT_BUS_SCOPE.LOBBY)
        self.addListener(events.FightButtonEvent.FIGHT_BUTTON_UPDATE, self.__handleFightButtonUpdated, scope=EVENT_BUS_SCOPE.LOBBY)
        self.addListener(CameraRelatedEvents.CAMERA_ENTITY_UPDATED, self.__handleSelectedEntityUpdated)
        self.statsCollector.noteHangarLoadingState(HANGAR_LOADING_STATE.HANGAR_UI_READY)
        g_playerEvents.onLoadingMilestoneReached(Milestones.HANGAR_UI_READY)
        self._offersBannerController.showBanners()
        self.__updateCarouselEventEntryState()
        self.fireEvent(events.HangarCustomizationEvent(events.HangarCustomizationEvent.RESET_VEHICLE_MODEL_TRANSFORM), scope=EVENT_BUS_SCOPE.LOBBY)
        g_currentPreviewVehicle.selectNoVehicle()
        if g_currentVehicle.isPresent():
            g_currentVehicle.refreshModel()
        if self.battleRoyaleController.isBattleRoyaleMode() and self.hangarSpace.spaceInited:
            self.__onBattleRoyaleSpaceLoaded(False)

    def _dispose(self):
        self.removeListener(AmmunitionPanelViewEvent.SECTION_SELECTED, self.__onOptDeviceClick, scope=EVENT_BUS_SCOPE.LOBBY)
        self.removeListener(AmmunitionPanelViewEvent.CLOSE_VIEW, self.__oAmmunitionPanelViewClose, scope=EVENT_BUS_SCOPE.LOBBY)
        self.removeListener(LobbySimpleEvent.WAITING_SHOWN, self.__onWaitingShown, EVENT_BUS_SCOPE.LOBBY)
        self.removeListener(events.FightButtonEvent.FIGHT_BUTTON_UPDATE, self.__handleFightButtonUpdated, scope=EVENT_BUS_SCOPE.LOBBY)
        self.removeListener(CameraRelatedEvents.CAMERA_ENTITY_UPDATED, self.__handleSelectedEntityUpdated)
        self.itemsCache.onSyncCompleted -= self.onCacheResync
        self.__eventLootBoxes.onStatusChange -= self.__onLootBoxesEventStatusChange
        g_currentVehicle.onChanged -= self.__onCurrentVehicleChanged
        self.hangarSpace.onVehicleChangeStarted -= self.__onVehicleLoading
        self.hangarSpace.onVehicleChanged -= self.__onVehicleLoaded
        self.hangarSpace.onSpaceRefresh -= self.__onSpaceRefresh
        self.hangarSpace.onSpaceCreate -= self.__onSpaceCreate
        self.igrCtrl.onIgrTypeChanged -= self.__onIgrTypeChanged
        self.rankedController.onUpdated -= self.onRankedUpdate
        self.rankedController.onGameModeStatusTick -= self.__updateAlertMessage
        self.__mapboxCtrl.onPrimeTimeStatusUpdated -= self.__updateAlertMessage
        self.__funRandomCtrl.subscription.removeSubModesWatcher(self.__updateAlertMessage, True, True)
        self.__funRandomCtrl.subscription.removeSubModesWatcher(self.__onFunRandomUpdate, True)
        self.battleRoyaleController.onUpdated -= self.__updateBattleRoyaleComponents
        self.battleRoyaleController.onBattleRoyaleSpaceLoaded -= self.__onBattleRoyaleSpaceLoaded
        self.epicController.onUpdated -= self.__onEpicBattleUpdated
        self.epicController.onPrimeTimeStatusUpdated -= self.__onEpicBattleUpdated
        self.epicController.onGameModeStatusTick -= self.__updateAlertMessage
        self._promoController.onNewTeaserReceived -= self.__onTeaserReceived
        self.__comp7Controller.onStatusUpdated -= self.__updateAlertMessage
        self.__comp7Controller.onStatusTick -= self.__updateAlertMessage
        self.__comp7Controller.onBanUpdated -= self.__updateAlertMessage
        self.__comp7Controller.onOfflineStatusUpdated -= self.__updateAlertMessage
        self.__comp7Controller.onTournamentBannerStateChanged -= self.__updateComp7TournamentWidget
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
        self.battlePassController.onSeasonStateChanged -= self.__switchCarousels
        self.__timer.clearCallbacks()
        self.__timer = None
        self.__banTimer.clearCallbacks()
        self.__banTimer = None
        self.closeHelpLayout()
        self.stopGlobalListening()
        self._offersBannerController.hideBanners()
        self.__hangarComponentsCtrl.releaseHangar()
        LobbySelectableView._dispose(self)
        return

    def __updateDogTagsState(self):
        isDogTagsEnabled = self.lobbyContext.getServerSettings().isDogTagEnabled()
        getTutorialGlobalStorage().setValue(GLOBAL_FLAG.DOGTAGS_ENABLED, isDogTagsEnabled)

    def __onWindowLoaded(self, uniqueID, newStatus):
        window = self.gui.windowsManager.getWindow(uniqueID)
        if window in _HELP_LAYOUT_RESTRICTED_LAYERS and newStatus in (WindowStatus.LOADING, WindowStatus.LOADED):
            self.closeHelpLayout()

    def __switchCarousels(self, force=False):
        prevCarouselAlias = self.__currentCarouselAlias
        newCarouselAlias, linkage = self.__hangarComponentsCtrl.getHangarCarouselSettings()
        if self.prbDispatcher is not None:
            if newCarouselAlias is None or newCarouselAlias == HANGAR_ALIASES.TANK_CAROUSEL:
                if self.prbDispatcher.getFunctionalState().isInPreQueue(QUEUE_TYPE.RANKED):
                    newCarouselAlias = HANGAR_ALIASES.RANKED_TANK_CAROUSEL
                elif self.prbDispatcher.getFunctionalState().isInPreQueue(QUEUE_TYPE.EPIC) or self.prbDispatcher.getFunctionalState().isInUnit(PREBATTLE_TYPE.EPIC):
                    newCarouselAlias = HANGAR_ALIASES.EPICBATTLE_TANK_CAROUSEL
            if self.prbDispatcher is not None and self.battlePassController.isVisible() and self.battlePassController.isValidBattleType(self.prbDispatcher.getEntity()):
                newCarouselAlias = HANGAR_ALIASES.BATTLEPASS_TANK_CAROUSEL
            newCarouselAlias = HANGAR_ALIASES.TANK_CAROUSEL if newCarouselAlias is None else newCarouselAlias
            linkage = HANGAR_ALIASES.TANK_CAROUSEL_UI if linkage is None else linkage
            (prevCarouselAlias != newCarouselAlias or force) and self.as_setCarouselS(linkage, newCarouselAlias)
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

    def __onBattleRoyaleSpaceLoaded(self, showAnimation):
        self.as_setBattleRoyaleSpaceLoadedS(showAnimation)

    def __updateHeaderEpicWidget(self):
        if self.epicWidget is not None:
            self.epicWidget.update()
        return

    def __updateCrew(self):
        if self.crewWidget is not None:
            self.crewWidget.updateTankmen()
        return

    def __updateBan(self):
        if self.__comp7Controller.isComp7PrbActive() and self.__comp7Controller.isBanned:
            self.__updateAlertBlock(*self.__comp7Controller.getAlertBlock())
            return min(self.__comp7Controller.banDuration, ONE_MINUTE)
        else:
            return None

    def __updateAlertMessage(self, *_):
        if self.prbDispatcher is not None:
            if self.rankedController.isRankedPrbActive():
                self.__updateAlertBlock(*self.rankedController.getAlertBlock())
                return
            if self.__funRandomCtrl.isFunRandomPrbActive():
                desiredSubMode = self.__funRandomCtrl.subModesHolder.getDesiredSubMode()
                alertBlock = desiredSubMode.getAlertBlock() if desiredSubMode else (None, None, False)
                self.__updateAlertBlock(*alertBlock)
                return
            if self.__mapboxCtrl.isMapboxPrbActive():
                self.__updateMapboxAlertMsg()
                return
            if self.epicController.isEpicPrbActive():
                self.__updateEpicBattleAlertMsg()
                return
            if self.__comp7Controller.isComp7PrbActive():
                if self.__comp7Controller.isBanned:
                    delay = self.__comp7Controller.banDuration % ONE_MINUTE + 1
                    self.__banTimer.delayCallback(delay, self.__updateBan)
                self.__updateAlertBlock(*self.__comp7Controller.getAlertBlock())
                return
        self.as_updateHangarComponentsS(hideComponents=[HANGAR_CONSTS.ALERT_MESSAGE])
        return

    def __updateEpicBattleAlertMsg(self):

        def showFLInfoWindow():
            from frontline.gui.impl.gen.view_models.views.lobby.views.info_page_scroll_to_section import InfoPageScrollToSection
            EpicBattleLogger().log(EpicBattleLogActions.CLICK, item=EpicBattleLogButtons.INFO_PAGE, parentScreen=EpicBattleLogKeys.HANGAR)
            showFrontlineInfoWindow(autoscrollSection=InfoPageScrollToSection.BATTLE_SCENARIOS)

        visible = self.epicController.isEnabled()
        data = epic_helpers.getAlertStatusVO()
        callback = showFLInfoWindow if self.epicController.isInPrimeTime() else None
        self.__updateAlertBlock(shared_events.showEpicBattlesPrimeTimeWindow, data, visible, callback)
        return

    def __updateMapboxAlertMsg(self):
        status, _, _ = self.__mapboxCtrl.getPrimeTimeStatus()
        isBlockedStatus = status in (PrimeTimeStatus.NOT_AVAILABLE, PrimeTimeStatus.NOT_SET, PrimeTimeStatus.FROZEN)
        data = mapbox_helpers.getPrimeTimeStatusVO()
        self.__updateAlertBlock(shared_events.showMapboxPrimeTimeWindow, data, isBlockedStatus)

    def __updateAlertBlock(self, callback, data, visible, blockClickCallback=None):
        visibleComponents, hiddenComponents = [], []
        if visible:
            visibleComponents.append(HANGAR_CONSTS.ALERT_MESSAGE)
        else:
            hiddenComponents.append(HANGAR_CONSTS.ALERT_MESSAGE)
        self.as_updateHangarComponentsS(visibleComponents, hiddenComponents)
        if visible and self.alertMessage is not None:
            self.alertMessage.update(data.asDict(), onBtnClickCallback=callback, onBlockClickCallback=blockClickCallback)
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
                    marathons = self.__marathonCtrl.getMarathons()
                    vehicleCD = descriptor.type.compactDescr
                    activeMarathon = next((marathon for marathon in marathons if marathon.vehicleID == vehicleCD), None)
                    if activeMarathon:
                        title = backport.text(R.strings.marathon.vehiclePreview.buyingPanel.title())
                        shared_events.showMarathonVehiclePreview(vehicleCD, activeMarathon.remainingPackedRewards, title, activeMarathon.prefix, True)
                    elif isResourceWellRewardVehicle(vehicleCD=vehicleCD):
                        shared_events.showResourceWellHeroPreview(vehicleCD)
                    else:
                        shared_events.showHeroTankPreview(vehicleCD)
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
            self.addListener(AmmunitionPanelViewEvent.SECTION_SELECTED, self.__onOptDeviceClick, scope=EVENT_BUS_SCOPE.LOBBY)
            self.addListener(AmmunitionPanelViewEvent.CLOSE_VIEW, self.__oAmmunitionPanelViewClose, scope=EVENT_BUS_SCOPE.LOBBY)

    def _onUnregisterFlashComponent(self, viewPy, alias):
        super(Hangar, self)._onUnregisterFlashComponent(viewPy, alias)
        if alias == HANGAR_ALIASES.AMMUNITION_PANEL_INJECT and viewPy.getInjectView():
            self.removeListener(AmmunitionPanelViewEvent.SECTION_SELECTED, self.__onOptDeviceClick, scope=EVENT_BUS_SCOPE.LOBBY)
            self.removeListener(AmmunitionPanelViewEvent.CLOSE_VIEW, self.__oAmmunitionPanelViewClose, scope=EVENT_BUS_SCOPE.LOBBY)

    def __updateBattleRoyaleComponents(self):
        self.__updateHeaderComponent()
        self.__updateBattleRoyaleHeaderComponent()

    def __onEpicBattleUpdated(self, *_):
        self.__updateHeaderComponent()
        self.__updateHeaderEpicWidget()
        self.__updateAmmoPanel()
        self.__updateAlertMessage()

    def __updateAll(self):
        g_playerEvents.onLoadingMilestoneReached(Milestones.UPDATE_VEHICLE)
        Waiting.show('updateVehicle')
        self.__switchCarousels()
        self.__updateState()
        self.__updateAmmoPanel()
        self.__updateParams()
        self.__updateVehicleInResearchPanel()
        self.__updateNavigationInResearchPanel()
        self.__updateHeaderComponent()
        self.__updateRankedHeaderComponent()
        self.__updateHeaderEpicWidget()
        self.__updateCrew()
        self.__updateAlertMessage()
        self.__updateBattleRoyaleComponents()
        self.__hangarComponentsCtrl.updateComponentsVisibility()
        self.__updateComp7ModifiersWidget()
        self.__updateComp7TournamentWidget()
        Waiting.hide('updateVehicle')

    def __onCurrentVehicleChanged(self):
        Waiting.show('updateVehicle')
        self.__updateState()
        self.__updateAmmoPanel()
        self.__updateParams()
        self.__updateVehicleInResearchPanel()
        self.__updateHeaderComponent()
        self.__updateHeaderEpicWidget()
        self.__updateCrew()
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
        self.__updateHeaderComponent()
        self.__updateHeaderEpicWidget()
        self.__updateParams()

    def __updateState(self, force=False):
        state = g_currentVehicle.getViewState()
        isBattleRoyaleMode = self.battleRoyaleController.isBattleRoyaleMode()
        isC11nEnabled = self.lobbyContext.getServerSettings().isCustomizationEnabled() and state.isCustomizationEnabled() and not state.isOnlyForEventBattles() and self.__isSpaceReadyForC11n and self.__isVehicleReadyForC11n and self.__isVehicleCameraReadyForC11n and not isBattleRoyaleMode
        if isC11nEnabled:
            customizationTooltip = makeTooltip(_ms(backport.text(R.strings.tooltips.hangar.tuning.header())), _ms(backport.text(R.strings.tooltips.hangar.tuning.body())))
        else:
            customizationTooltip = makeTooltip(_ms(backport.text(R.strings.tooltips.hangar.tuning.disabled.header())), _ms(backport.text(R.strings.tooltips.hangar.tuning.disabled.body())))
        changeNationVisibility = g_currentVehicle.isPresent() and g_currentVehicle.item.hasNationGroup
        isNationChangeAvailable = g_currentVehicle.isPresent() and g_currentVehicle.item.isNationChangeAvailable
        changeNationTooltip = getChangeNationTooltip(g_currentVehicle.item)
        changeNationIsNew = not AccountSettings.getSettings(NATION_CHANGE_VIEWED)
        isMaintenanceEnabled = state.isMaintenanceEnabled()
        isEquipmentEnabled = g_currentVehicle.isPresent() and not g_currentVehicle.isEquipmentLocked()
        if isMaintenanceEnabled and isEquipmentEnabled:
            maintenanceTooltip = TOOLTIPS.HANGAR_MAINTENANCE
        else:
            maintenanceTooltip = TOOLTIPS.HANGAR_MAINTENANCE_DISABLED
        self.as_setupAmmunitionPanelS({'maintenanceEnabled': isMaintenanceEnabled,
         'maintenanceTooltip': maintenanceTooltip,
         'maintenanceVisible': state.isMaintenanceVisible(),
         'customizationEnabled': isC11nEnabled,
         'customizationTooltip': customizationTooltip,
         'customizationVisible': state.isCustomizationVisible(),
         'changeNationVisible': changeNationVisibility,
         'changeNationEnable': isNationChangeAvailable,
         'changeNationTooltip': changeNationTooltip,
         'changeNationIsNew': changeNationIsNew})
        self.__hangarComponentsCtrl.updateChangeableComponents(state.isUIShown(), force)
        self.__updatePrestigeProgressWidget()

    def __onEntityChanged(self):
        self.__updateState(force=True)
        self.__updateAmmoPanel()
        self.__updateAlertMessage()
        self.__updateNavigationInResearchPanel()
        self.__updateHeaderComponent()
        self.__updateRankedHeaderComponent()
        self.__updateHeaderEpicWidget()
        self.__switchCarousels()
        self.__updateBattleRoyaleComponents()
        self.__hangarComponentsCtrl.updateComponentsVisibility()
        self.__updateComp7ModifiersWidget()
        self.__updateComp7TournamentWidget()

    def __onFunRandomUpdate(self, *_):
        self.__onEntityChanged()
        self.__updateCarouselEventEntryState()

    def __onVehicleClientStateChanged(self, modifiedCDs):
        if g_currentVehicle.item is not None and g_currentVehicle.item.intCD in modifiedCDs:
            self.__updateAmmoPanel()
        return

    def __onServerSettingChanged(self, diff):
        if 'isRegularQuestEnabled' in diff:
            self.__updateHeaderComponent()
            self.__updateHeaderEpicWidget()
        if 'isCustomizationEnabled' in diff or 'isNationChangeEnabled' in diff:
            self.__updateState()
        if BATTLE_PASS_CONFIG_NAME in diff:
            self.__switchCarousels()
        if Configs.BATTLE_ROYALE_CONFIG.value in diff:
            self.__updateBattleRoyaleComponents()
            self.__updateState()
            self.__switchCarousels(force=True)
        if Configs.EPIC_CONFIG.value in diff:
            self.__updateHeaderEpicWidget()
            self.__updateState()
            self.__switchCarousels(force=True)
        if DOG_TAGS_CONFIG in diff:
            self.__updateDogTagsState()
        if RENEWABLE_SUBSCRIPTION_CONFIG in diff:
            self.__updateState()
        if Configs.PRESTIGE_CONFIG.value in diff:
            self.__updatePrestigeProgressWidget()

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

    def __onOptDeviceClick(self, event):
        ctx = event.ctx
        if self.hangarSpace.spaceLoading():
            _logger.warning('Optional Device click was not handled (ctx=%s). HangarSpace is currently loading.', ctx)
        elif not self.__isUnitJoiningInProgress:
            self.as_showSwitchToAmmunitionS()
            shared_events.showAmmunitionSetupView(**ctx)

    def __oAmmunitionPanelViewClose(self, _):
        self.onEscape()

    def __onUnitJoined(self, _, __):
        self.__isUnitJoiningInProgress = False
        if self.__timer:
            self.__timer.stopCallback(self.__onResetUnitJoiningProgress)

    def __onPrebattleInvitationAccepted(self, _, __):
        self.__isUnitJoiningInProgress = True
        if self.__timer:
            self.__timer.delayCallback(15, self.__onResetUnitJoiningProgress)

    def __onResetUnitJoiningProgress(self):
        self.__isUnitJoiningInProgress = False

    def __onLootBoxesEventStatusChange(self):
        self.__updateCarouselEventEntryState()

    def __updateCarouselEventEntryState(self):
        self.as_updateCarouselEventEntryStateS(isAnyEntryVisible())

    @ifComponentAvailable(HANGAR_CONSTS.COMP7_MODIFIERS)
    def __updateComp7ModifiersWidget(self):
        self.as_setComp7ModifiersVisibleS(self.__comp7Controller.isBattleModifiersAvailable())

    @ifComponentAvailable(HANGAR_CONSTS.COMP7_TOURNAMENT_BANNER)
    def __updateComp7TournamentWidget(self):
        self.as_setComp7TournamentBannerVisibleS(self.__comp7Controller.isTournamentBannerEnabled)

    def __updatePrestigeProgressWidget(self):
        if g_currentVehicle.intCD is not None:
            visible = hasVehiclePrestige(g_currentVehicle.intCD, checkElite=True, lobbyContext=self.lobbyContext, itemsCache=self.itemsCache)
        else:
            visible = False
        self.as_setPrestigeWidgetVisibleS(visible)
        return
