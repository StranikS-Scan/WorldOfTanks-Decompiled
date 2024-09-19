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
from constants import Configs, DOG_TAGS_CONFIG, RENEWABLE_SUBSCRIPTION_CONFIG
from frameworks.wulf import WindowFlags, WindowLayer, WindowStatus, ViewStatus
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.Waiting import Waiting
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.LobbySelectableView import LobbySelectableView
from gui.Scaleform.daapi.view.lobby.hangar.carousel_event_entry_widget import isAnyEntryVisible
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
from gui.prb_control import prb_getters
from gui.prb_control.ctrl_events import g_prbCtrlEvents
from gui.prb_control.entities.listener import IGlobalListener
from gui.prestige.prestige_helpers import hasVehiclePrestige
from gui.promo.hangar_teaser_widget import TeaserViewer
from gui.resource_well.resource_well_helpers import isResourceWellRewardVehicle
from gui.shared import EVENT_BUS_SCOPE, event_dispatcher as shared_events, events
from gui.shared.events import AmmunitionPanelViewEvent, LobbySimpleEvent
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.items_cache import CACHE_SYNC_REASON
from gui.shared.tutorial_helper import getTutorialGlobalStorage
from gui.shared.utils.functions import makeTooltip
from gui.sounds.filters import States, StatesGroup
from gui.tournament.tournament_helpers import isTournamentEnabled
from helpers import dependency
from helpers.CallbackDelayer import CallbackDelayer
from helpers.i18n import makeString as _ms
from helpers.statistics import HANGAR_LOADING_STATE
from helpers.time_utils import ONE_MINUTE
from nation_change_helpers.client_nation_change_helper import getChangeNationTooltip
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.connection_mgr import IConnectionManager
from skeletons.gui.game_control import IWotPlusController, IBattlePassController, IBattleRoyaleController, IComp7Controller, IEpicBattleMetaGameController, IEventLootBoxesController, IIGRController, IMapboxController, IMarathonEventsController, IPromoController, IRankedBattlesController, IHangarGuiController, IEventBattlesController
from skeletons.gui.impl import IGuiLoader
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.offers import IOffersBannerController
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.utils import IHangarSpace
from skeletons.helpers.statistics import IStatisticsCollector
from sound_gui_manager import CommonSoundSpaceSettings
from tutorial.control.context import GLOBAL_FLAG
from gui.wt_event import wt_event_helpers
from gui.periodic_battles.models import PrimeTimeStatus
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
    _COMMON_SOUND_SPACE = CommonSoundSpaceSettings(name='hangar', entranceStates={_SOUND_STATE_PLACE: _SOUND_STATE_PLACE_GARAGE,
     StatesGroup.HANGAR_FILTERED: States.HANGAR_FILTERED_OFF}, exitStates={}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent='', exitEvent='')
    __background_alpha__ = 0.0
    itemsCache = dependency.descriptor(IItemsCache)
    igrCtrl = dependency.descriptor(IIGRController)
    lobbyContext = dependency.descriptor(ILobbyContext)
    statsCollector = dependency.descriptor(IStatisticsCollector)
    gui = dependency.descriptor(IGuiLoader)
    hangarSpace = dependency.descriptor(IHangarSpace)
    rankedController = dependency.descriptor(IRankedBattlesController)
    epicController = dependency.descriptor(IEpicBattleMetaGameController)
    battlePassController = dependency.descriptor(IBattlePassController)
    battleRoyaleController = dependency.descriptor(IBattleRoyaleController)
    _settingsCore = dependency.descriptor(ISettingsCore)
    _promoController = dependency.descriptor(IPromoController)
    _connectionMgr = dependency.descriptor(IConnectionManager)
    _offersBannerController = dependency.descriptor(IOffersBannerController)
    _wotPlusCtrl = dependency.descriptor(IWotPlusController)
    gameEventController = dependency.descriptor(IEventBattlesController)
    __mapboxCtrl = dependency.descriptor(IMapboxController)
    __marathonCtrl = dependency.descriptor(IMarathonEventsController)
    __comp7Controller = dependency.descriptor(IComp7Controller)
    __eventLootBoxes = dependency.descriptor(IEventLootBoxesController)
    __hangarGuiCtrl = dependency.descriptor(IHangarGuiController)

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
        self.__comp7BanTimer = None
        self.__updateDogTagsState()
        nextTick(ClientSelectableCameraObject.switchCamera)(init=True)
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
    def tankMenXpPanel(self):
        return self.getComponent(HANGAR_ALIASES.TMEN_XP_PANEL)

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

    def onPrbEntitySwitched(self):
        self.__onEntityChanged()
        self.__updateCarouselEventEntryState()

    def onEnqueued(self, queueType, *args):
        self.__onEntityChanged()

    def onDequeued(self, queueType, *args):
        self.__onEntityChanged()

    def onRankedUpdate(self):
        self.__updateHeaderComponent()

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
        self.__hangarGuiCtrl.holdHangar(self)
        self.__timer = CallbackDelayer()
        self.__comp7BanTimer = CallbackDelayer()
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
        self.battleRoyaleController.onBattleRoyaleSpaceLoaded += self.__onBattleRoyaleSpaceLoaded
        self.battleRoyaleController.onTournamentBannerStateChanged += self.__updateBattleRoyaleTournamentBanner
        self.epicController.onUpdated += self.__onEpicBattleUpdated
        self.epicController.onPrimeTimeStatusUpdated += self.__onEpicBattleUpdated
        self.epicController.onGameModeStatusTick += self.__updateAlertMessage
        self.gameEventController.onUpdated += self.__updateEventComponents
        self.gameEventController.onPrimeTimeStatusUpdated += self.__updateAlertMessage
        self.gameEventController.onGameEventTick += self.__onGameEventTick
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
        self.addListener(CameraRelatedEvents.CAMERA_ENTITY_UPDATED, self.__handleSelectedEntityUpdated)
        self.addListener(LobbySimpleEvent.WAITING_SHOWN, self.__onWaitingShown, scope=EVENT_BUS_SCOPE.LOBBY)
        self.addListener(events.FightButtonEvent.FIGHT_BUTTON_UPDATE, self.__handleFightButtonUpdated, scope=EVENT_BUS_SCOPE.LOBBY)
        self.addListener(events.HangarEvent.UPDATE_ALERT_MESSAGE, self.__updateAlertMessage, scope=EVENT_BUS_SCOPE.LOBBY)
        self.addListener(events.HangarEvent.UPDATE_PREBATTLE_ENTITY, self.__onEntityUpdated, scope=EVENT_BUS_SCOPE.LOBBY)
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
        self.fireEvent(events.HangarSimpleEvent(events.HangarSimpleEvent.HANGAR_LOADED), scope=EVENT_BUS_SCOPE.LOBBY)

    def _dispose(self):
        self.removeListener(CameraRelatedEvents.CAMERA_ENTITY_UPDATED, self.__handleSelectedEntityUpdated)
        self.removeListener(LobbySimpleEvent.WAITING_SHOWN, self.__onWaitingShown, scope=EVENT_BUS_SCOPE.LOBBY)
        self.removeListener(events.FightButtonEvent.FIGHT_BUTTON_UPDATE, self.__handleFightButtonUpdated, scope=EVENT_BUS_SCOPE.LOBBY)
        self.removeListener(events.HangarEvent.UPDATE_ALERT_MESSAGE, self.__updateAlertMessage, scope=EVENT_BUS_SCOPE.LOBBY)
        self.removeListener(events.HangarEvent.UPDATE_PREBATTLE_ENTITY, self.__onEntityUpdated, scope=EVENT_BUS_SCOPE.LOBBY)
        self.removeListener(AmmunitionPanelViewEvent.SECTION_SELECTED, self.__onOptDeviceClick, scope=EVENT_BUS_SCOPE.LOBBY)
        self.removeListener(AmmunitionPanelViewEvent.CLOSE_VIEW, self.__oAmmunitionPanelViewClose, scope=EVENT_BUS_SCOPE.LOBBY)
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
        self.battleRoyaleController.onTournamentBannerStateChanged -= self.__updateBattleRoyaleTournamentBanner
        self.battleRoyaleController.onUpdated -= self.__updateBattleRoyaleComponents
        self.battleRoyaleController.onBattleRoyaleSpaceLoaded -= self.__onBattleRoyaleSpaceLoaded
        self.epicController.onUpdated -= self.__onEpicBattleUpdated
        self.epicController.onPrimeTimeStatusUpdated -= self.__onEpicBattleUpdated
        self.epicController.onGameModeStatusTick -= self.__updateAlertMessage
        self.gameEventController.onUpdated -= self.__updateEventComponents
        self.gameEventController.onPrimeTimeStatusUpdated -= self.__updateAlertMessage
        self.gameEventController.onGameEventTick -= self.__onGameEventTick
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
        self.__comp7BanTimer.clearCallbacks()
        self.__comp7BanTimer = None
        self.closeHelpLayout()
        self.stopGlobalListening()
        self._offersBannerController.hideBanners()
        self.__hangarGuiCtrl.releaseHangar()
        LobbySelectableView._dispose(self)
        self.fireEvent(events.HangarSimpleEvent(events.HangarSimpleEvent.HANGAR_UNLOADED), scope=EVENT_BUS_SCOPE.LOBBY)
        return

    def __updateEventMode(self):
        self.as_toggleEventModeS(self.gameEventController.isEventPrbActive())

    def __updateDogTagsState(self):
        isDogTagsEnabled = self.lobbyContext.getServerSettings().isDogTagEnabled()
        getTutorialGlobalStorage().setValue(GLOBAL_FLAG.DOGTAGS_ENABLED, isDogTagsEnabled)

    def __onWindowLoaded(self, uniqueID, newStatus):
        window = self.gui.windowsManager.getWindow(uniqueID)
        if window in _HELP_LAYOUT_RESTRICTED_LAYERS and newStatus in (WindowStatus.LOADING, WindowStatus.LOADED):
            self.closeHelpLayout()

    def __switchCarousels(self, force=False):
        prevCarouselAlias = self.__currentCarouselAlias
        newCarouselVisibility = True
        newCarouselAlias, linkage = self.__hangarGuiCtrl.getHangarCarouselSettings()
        if self.prbDispatcher is not None and (newCarouselAlias is None or newCarouselAlias == HANGAR_ALIASES.TANK_CAROUSEL):
            if self.gameEventController.isEventPrbActive():
                newCarouselVisibility = False
        if self.prbDispatcher is not None and self.battlePassController.isVisible() and self.battlePassController.isValidBattleType(self.prbDispatcher.getEntity()):
            newCarouselAlias = HANGAR_ALIASES.BATTLEPASS_TANK_CAROUSEL
        newCarouselAlias = HANGAR_ALIASES.TANK_CAROUSEL if newCarouselAlias is None else newCarouselAlias
        linkage = HANGAR_ALIASES.TANK_CAROUSEL_UI if linkage is None else linkage
        if prevCarouselAlias != newCarouselAlias or force:
            self.as_setCarouselS(linkage, newCarouselAlias)
            self.__currentCarouselAlias = newCarouselAlias
        self.as_setCarouselVisibleS(newCarouselVisibility)
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

    def __onBattleRoyaleSpaceLoaded(self, showAnimation):
        self.as_setBattleRoyaleSpaceLoadedS(showAnimation)

    def __updateEventHeaderComponent(self):
        if self.headerComponent is not None:
            self.headerComponent.updateEventHeader()
        return

    def __updateCrew(self):
        if self.crewWidget is not None:
            self.crewWidget.updateTankmen()
        return

    def __onGameEventTick(self, *_):
        if self.gameEventController.isEventPrbActive() and not self.gameEventController.isAvailable():
            self.__updateEventComponents()
        else:
            self.__updateAlertMessage(None)
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

    def __onEpicBattleUpdated(self, *_):
        self.__updateHeaderComponent()
        self.__updateAmmoPanel()
        self.__updateAlertMessage()

    def __updateEventComponents(self):
        self.__updateHeaderComponent()
        self.__updateEventHeaderComponent()
        self.__updateEventMode()

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
        self.__updateEventHeaderComponent()
        self.__updateCrew()
        self.__hangarGuiCtrl.updateComponentsVisibility()
        self.__updatePrestigeProgressWidget()
        self.__updateEventComponents()
        self.__updateComp7ModifiersWidget()
        self.__updateComp7TournamentWidget()
        self.__updateAlertMessage()
        self.__updateBattleRoyaleTournamentBanner()
        self.__updateEventMode()
        Waiting.hide('updateVehicle')

    def __onCurrentVehicleChanged(self):
        Waiting.show('updateVehicle')
        self.__updateState()
        self.__updateAmmoPanel()
        self.__updateParams()
        self.__updateVehicleInResearchPanel()
        self.__updatePrestigeProgressWidget()
        self.__updateHeaderComponent()
        self.__updateCrew()
        self.__updateEventMode()
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
        self.__updatePrestigeProgressWidget()
        self.__updateHeaderComponent()
        self.__updateParams()

    def __updateState(self, force=False):
        state = g_currentVehicle.getViewState()
        isBattleRoyaleMode = self.battleRoyaleController.isBattleRoyaleMode()
        isEventMode = self.gameEventController.isEventPrbActive()
        isC11nEnabled = self.lobbyContext.getServerSettings().isCustomizationEnabled() and state.isCustomizationEnabled() and not state.isOnlyForEventBattles() and self.__isSpaceReadyForC11n and self.__isVehicleReadyForC11n and self.__isVehicleCameraReadyForC11n and not isBattleRoyaleMode and not isEventMode
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
        self.__hangarGuiCtrl.updateChangeableComponents(state.isUIShown(), force)

    def __onEntityChanged(self):
        self.__updateState(force=True)
        self.__updateAmmoPanel()
        self.__updateNavigationInResearchPanel()
        self.__updateVehicleInResearchPanel()
        self.__updateHeaderComponent()
        self.__switchCarousels()
        self.__hangarGuiCtrl.updateComponentsVisibility()
        self.__updatePrestigeProgressWidget()
        self.__updateComp7ModifiersWidget()
        self.__updateComp7TournamentWidget()
        self.__updateAlertMessage()
        self.__updateBattleRoyaleTournamentBanner()
        self.__updateEventMode()

    def __onEntityUpdated(self, *_):
        self.__onEntityChanged()
        self.__updateCarouselEventEntryState()

    def __onVehicleClientStateChanged(self, modifiedCDs):
        if g_currentVehicle.item is not None and g_currentVehicle.item.intCD in modifiedCDs:
            self.__updateAmmoPanel()
        return

    def __onServerSettingChanged(self, diff):
        if 'isRegularQuestEnabled' in diff:
            self.__updateHeaderComponent()
        if 'isCustomizationEnabled' in diff or 'isNationChangeEnabled' in diff:
            self.__updateState()
        if BATTLE_PASS_CONFIG_NAME in diff:
            self.__switchCarousels()
        if Configs.BATTLE_ROYALE_CONFIG.value in diff:
            self.__updateBattleRoyaleComponents()
            self.__updateState()
            self.__switchCarousels(force=True)
        if Configs.EPIC_CONFIG.value in diff:
            self.__updateHeaderComponent()
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
        isBannerVisible = self.__comp7Controller.isTournamentBannerEnabled and isTournamentEnabled()
        self.as_setEventTournamentBannerVisibleS(HANGAR_ALIASES.COMP7_TOURNAMENT_BANNER, isBannerVisible)

    @ifComponentAvailable(HANGAR_CONSTS.BATTLE_ROYALE_TOURNAMENT_BANNER)
    def __updateBattleRoyaleTournamentBanner(self):
        isBannerVisible = self.battleRoyaleController.isTournamentBannerEnabled and isTournamentEnabled()
        self.as_setEventTournamentBannerVisibleS(HANGAR_ALIASES.BATTLE_ROYALE_TOURNAMENT_BANNER, isBannerVisible)

    @ifComponentAvailable(HANGAR_CONSTS.PRESTIGE_WIDGET)
    def __updatePrestigeProgressWidget(self):
        visible = g_currentVehicle.intCD is not None and hasVehiclePrestige(g_currentVehicle.intCD, checkElite=True, lobbyContext=self.lobbyContext, itemsCache=self.itemsCache)
        if self.gameEventController.isEventPrbActive():
            visible = False
        self.as_setPrestigeWidgetVisibleS(visible)
        return

    @ifComponentAvailable(HANGAR_CONSTS.ALERT_MESSAGE)
    def __updateAlertMessage(self, *_):
        if self.__comp7Controller.isComp7PrbActive() and self.__comp7Controller.isBanned:
            delay = self.__comp7Controller.banDuration % ONE_MINUTE + 1
            self.__comp7BanTimer.delayCallback(delay, self.__updateAlertComp7Ban)
            self.__updateAlertBlock(*self.__hangarGuiCtrl.getHangarAlertBlock())
        elif self.gameEventController.isEventPrbActive():
            self.__updateEventBattleAlertMsg()
        else:
            self.__updateAlertBlock(*self.__hangarGuiCtrl.getHangarAlertBlock())

    def __updateAlertBlock(self, visible, data, callbacks):
        hiddenComponents = [] if visible else [HANGAR_CONSTS.ALERT_MESSAGE]
        visibleComponents = [HANGAR_CONSTS.ALERT_MESSAGE] if visible else []
        self.as_updateHangarComponentsS(visibleComponents, hiddenComponents)
        if visible and self.alertMessage is not None and data is not None:
            self.alertMessage.update(data.asDict(), callbacks)
        return

    def __updateAlertComp7Ban(self):
        if self.__comp7Controller.isComp7PrbActive() and self.__comp7Controller.isBanned:
            self.__updateAlertBlock(*self.__comp7Controller.getAlertBlock())
            return min(self.__comp7Controller.banDuration, ONE_MINUTE)
        else:
            return None

    def __updateEventBattleAlertMsg(self):
        status, _, _ = self.gameEventController.getPrimeTimeStatus()
        isBlockedStatus = status in (PrimeTimeStatus.NOT_AVAILABLE, PrimeTimeStatus.NOT_SET, PrimeTimeStatus.FROZEN)
        buttonCallback = shared_events.showEventBattlesPrimeTimeWindow
        data = wt_event_helpers.getAlertStatusVO()
        self.__updateAlertBlock(isBlockedStatus, data, {'onButtonClick': buttonCallback,
         'onBlockClick': None})
        return
