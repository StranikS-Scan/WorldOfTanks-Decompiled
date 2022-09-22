# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/Hangar.py
import logging
import typing
from functools import partial
import BigWorld
from gui.marathon.marathon_event import MarathonEvent
from gui.resource_well.resource_well_helpers import isResourceWellRewardVehicle
from shared_utils import nextTick
from CurrentVehicle import g_currentVehicle
from HeroTank import HeroTank
from account_helpers.settings_core.ServerSettingsManager import SETTINGS_SECTIONS
from constants import QUEUE_TYPE, PREBATTLE_TYPE, Configs, DOG_TAGS_CONFIG, RENEWABLE_SUBSCRIPTION_CONFIG
from frameworks.wulf import WindowFlags, WindowLayer, WindowStatus
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.Waiting import Waiting
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.LobbySelectableView import LobbySelectableView
from gui.Scaleform.daapi.view.lobby.epicBattle import epic_helpers
from gui.Scaleform.daapi.view.lobby.mapbox import mapbox_helpers
from gui.Scaleform.daapi.view.meta.HangarMeta import HangarMeta
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
from gui.prb_control.ctrl_events import g_prbCtrlEvents
from gui.prb_control.entities.listener import IGlobalListener
from gui.promo.hangar_teaser_widget import TeaserViewer
from gui.shared import event_dispatcher as shared_events
from gui.shared import events, EVENT_BUS_SCOPE
from gui.shared.event_dispatcher import showAmmunitionSetupView, showEpicBattlesPrimeTimeWindow, showEventBattlesPrimeTimeWindow
from gui.wt_event import wt_event_helpers
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
from skeletons.gui.game_control import IRankedBattlesController, IEpicBattleMetaGameController, IPromoController, IIGRController, IBattlePassController, IBattleRoyaleController, IBootcampController, IMapboxController, IMarathonEventsController, IEventBattlesController
from skeletons.gui.impl import IGuiLoader
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.offers import IOffersBannerController
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.utils import IHangarSpace
from skeletons.helpers.statistics import IStatisticsCollector
from tutorial.control.context import GLOBAL_FLAG
from account_helpers import AccountSettings
from account_helpers.AccountSettings import NATION_CHANGE_VIEWED
from gui.impl.gen import R
from gui.impl import backport
from PlayerEvents import g_playerEvents
from gui.periodic_battles.models import PrimeTimeStatus
if typing.TYPE_CHECKING:
    from frameworks.wulf import Window
_logger = logging.getLogger(__name__)
_HELP_LAYOUT_RESTRICTED_LAYERS = (WindowLayer.TOP_SUB_VIEW,
 WindowLayer.FULLSCREEN_WINDOW,
 WindowLayer.WINDOW,
 WindowLayer.OVERLAY,
 WindowLayer.TOP_WINDOW)
_VIEWS_WITH_ESC_HANDLER = [HANGAR_ALIASES.AMMUNITION_PANEL_INJECT,
 HANGAR_ALIASES.EVENT_CAROUSEL_WIDGET,
 HANGAR_ALIASES.EVENT_CREW_WIDGET,
 HANGAR_ALIASES.EVENT_PARAMS_WIDGET,
 HANGAR_ALIASES.LOOTBOXES_WIDGET]

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
    gameEventController = dependency.descriptor(IEventBattlesController)
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
        self.__wotPlusInfo = BigWorld.player().renewableSubscription
        self.__updateDogTagsState()
        self.__updateWotPlusState()
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

    def _populate(self):
        LobbySelectableView._populate(self)
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
        self.epicController.onUpdated += self.__onEpicBattleUpdated
        self.epicController.onPrimeTimeStatusUpdated += self.__onEpicBattleUpdated
        self.epicController.onGameModeStatusTick += self.__updateAlertMessage
        self.gameEventController.onUpdated += self.__updateEventComponents
        self.gameEventController.onPrimeTimeStatusUpdated += self.__updateAlertMessage
        self.gameEventController.onGameEventTick += self.__onGameEventTick
        self._promoController.onNewTeaserReceived += self.__onTeaserReceived
        self.hangarSpace.setVehicleSelectable(True)
        g_prbCtrlEvents.onVehicleClientStateChanged += self.__onVehicleClientStateChanged
        g_playerEvents.onPrebattleInvitationAccepted += self.__onPrebattleInvitationAccepted
        unitMgr = prb_getters.getClientUnitMgr()
        if unitMgr:
            unitMgr.onUnitJoined += self.__onUnitJoined
        g_clientUpdateManager.addCallbacks({'inventory': self.__updateAlertMessage})
        self.lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingChanged
        self._settingsCore.onSettingsChanged += self.__onSettingsChanged
        self.__wotPlusInfo.onRenewableSubscriptionDataChanged += self.__onWotPlusDataChanged
        self.battlePassController.onSeasonStateChanged += self.__switchCarousels
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
        self.as_setNotificationEnabledS(crewBooksViewedCache().haveNewCrewBooks())
        self._offersBannerController.showBanners()
        self.fireEvent(events.HangarCustomizationEvent(events.HangarCustomizationEvent.RESET_VEHICLE_MODEL_TRANSFORM), scope=EVENT_BUS_SCOPE.LOBBY)
        if g_currentVehicle.isPresent():
            g_currentVehicle.refreshModel()
        self.__updateLootBoxesState()
        if self.bootcampController.isInBootcamp():
            self.as_setDQWidgetLayoutS(DAILY_QUESTS_WIDGET_CONSTANTS.WIDGET_LAYOUT_SINGLE)
        self.fireEvent(events.HangarSimpleEvent(events.HangarSimpleEvent.HANGAR_LOADED), scope=EVENT_BUS_SCOPE.LOBBY)

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
        self.gameEventController.onPrimeTimeStatusUpdated -= self.__updateAlertMessage
        self.battleRoyaleController.onUpdated -= self.__updateBattleRoyaleComponents
        self.epicController.onUpdated -= self.__onEpicBattleUpdated
        self.epicController.onPrimeTimeStatusUpdated -= self.__onEpicBattleUpdated
        self.epicController.onGameModeStatusTick -= self.__updateAlertMessage
        self.gameEventController.onUpdated -= self.__updateEventComponents
        self.gameEventController.onPrimeTimeStatusUpdated -= self.__updateAlertMessage
        self.gameEventController.onGameEventTick -= self.__onGameEventTick
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
        self.__wotPlusInfo.onRenewableSubscriptionDataChanged -= self.__onWotPlusDataChanged
        self.battlePassController.onSeasonStateChanged -= self.__switchCarousels
        self.__timer.clearCallbacks()
        self.__timer = None
        self.closeHelpLayout()
        self.stopGlobalListening()
        self._offersBannerController.hideBanners()
        LobbySelectableView._dispose(self)
        self.fireEvent(events.HangarSimpleEvent(events.HangarSimpleEvent.HANGAR_UNLOADED), scope=EVENT_BUS_SCOPE.LOBBY)
        return

    def _updateCnSubscriptionMode(self):
        toggleGFPanel = self.lobbyContext.getServerSettings().isRenewableSubEnabled()
        self.as_toggleCnSubscriptionS(toggleGFPanel)

    def _updateBattleRoyaleMode(self):
        self.as_toggleBattleRoyaleS(g_currentVehicle.isOnlyForBattleRoyaleBattles())

    def _updateEventMode(self):
        self.as_toggleEventModeS(self.gameEventController.isEventPrbActive())

    def __updateDogTagsState(self):
        isDogTagsEnabled = self.lobbyContext.getServerSettings().isDogTagEnabled()
        getTutorialGlobalStorage().setValue(GLOBAL_FLAG.DOGTAGS_ENABLED, isDogTagsEnabled)

    def __updateWotPlusState(self):
        isWotPlusGoldEnabled = self.lobbyContext.getServerSettings().isRenewableSubGoldReserveEnabled()
        hasWotPlusActive = BigWorld.player().renewableSubscription.isEnabled()
        getTutorialGlobalStorage().setValue(GLOBAL_FLAG.WOTPLUS_ENABLED, hasWotPlusActive and isWotPlusGoldEnabled)
        self._updateCnSubscriptionMode()

    def __onWindowLoaded(self, uniqueID, newStatus):
        window = self.gui.windowsManager.getWindow(uniqueID)
        if window in _HELP_LAYOUT_RESTRICTED_LAYERS and newStatus in (WindowStatus.LOADING, WindowStatus.LOADED):
            self.closeHelpLayout()

    def __switchCarousels(self, force=False):
        prevCarouselAlias = self.__currentCarouselAlias
        linkage = HANGAR_ALIASES.TANK_CAROUSEL_UI
        newCarouselAlias = HANGAR_ALIASES.TANK_CAROUSEL
        newCarouselVisibility = True
        if self.prbDispatcher is not None:
            if self.prbDispatcher.getFunctionalState().isInPreQueue(QUEUE_TYPE.RANKED):
                newCarouselAlias = HANGAR_ALIASES.RANKED_TANK_CAROUSEL
            elif self.prbDispatcher.getFunctionalState().isInPreQueue(QUEUE_TYPE.EPIC) or self.prbDispatcher.getFunctionalState().isInUnit(PREBATTLE_TYPE.EPIC):
                newCarouselAlias = HANGAR_ALIASES.EPICBATTLE_TANK_CAROUSEL
            elif self.battleRoyaleController.isBattleRoyaleMode():
                linkage = HANGAR_ALIASES.BR_TANK_CAROUSEL_UI
                newCarouselAlias = HANGAR_ALIASES.ROYALE_TANK_CAROUSEL
            elif self.__mapboxCtrl.isMapboxMode():
                newCarouselAlias = HANGAR_ALIASES.MAPBOX_TANK_CAROUSEL
            elif self.battlePassController.isVisible() and self.battlePassController.isValidBattleType(self.prbDispatcher.getEntity()):
                newCarouselAlias = HANGAR_ALIASES.BATTLEPASS_TANK_CAROUSEL
            elif self.gameEventController.isEventPrbActive():
                newCarouselVisibility = False
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

    def __updateRankedHeaderComponent(self):
        if self.headerComponent is not None:
            self.headerComponent.updateRankedHeader()
        return

    def __updateBattleRoyaleHeaderComponent(self):
        if self.headerComponent is not None:
            self.headerComponent.updateBattleRoyaleHeader()
        return

    def __updateEventHeaderComponent(self):
        if self.headerComponent is not None:
            self.headerComponent.updateEventHeader()
        return

    def __updateHeaderEpicWidget(self):
        if self.epicWidget is not None:
            self.epicWidget.update()
        return

    def __updateCrew(self):
        if self.crewPanel is not None:
            self.crewPanel.updateTankmen()
        return

    def __onGameEventTick(self, *_):
        if self.gameEventController.isEventPrbActive() and not self.gameEventController.isAvailable():
            self.__updateEventComponents()
        else:
            self.__updateAlertMessage(None)
        return

    def __updateAlertMessage(self, *_):
        if self.prbDispatcher is not None:
            if self.rankedController.isRankedPrbActive():
                self.__updateAlertBlock(*self.rankedController.getAlertBlock())
                return
            if self.__mapboxCtrl.isMapboxPrbActive():
                self.__updateMapboxAlertMsg()
                return
            if self.epicController.isEpicPrbActive():
                self.__updateEpicBattleAlertMsg()
                return
            if self.gameEventController.isEventPrbActive():
                self.__updateEventBattleAlertMsg()
                return
        self.as_setAlertMessageBlockVisibleS(False)
        return

    def __updateEpicBattleAlertMsg(self):
        visible = not self.epicController.isInPrimeTime() and self.epicController.isEnabled()
        data = epic_helpers.getAlertStatusVO()
        self.__updateAlertBlock(showEpicBattlesPrimeTimeWindow, data, visible)

    def __updateMapboxAlertMsg(self):
        status, _, _ = self.__mapboxCtrl.getPrimeTimeStatus()
        isBlockedStatus = status in (PrimeTimeStatus.NOT_AVAILABLE, PrimeTimeStatus.NOT_SET, PrimeTimeStatus.FROZEN)
        data = mapbox_helpers.getPrimeTimeStatusVO()
        self.__updateAlertBlock(shared_events.showMapboxPrimeTimeWindow, data, isBlockedStatus)

    def __updateEventBattleAlertMsg(self):
        status, _, _ = self.gameEventController.getPrimeTimeStatus()
        isBlockedStatus = status in (PrimeTimeStatus.NOT_AVAILABLE, PrimeTimeStatus.NOT_SET, PrimeTimeStatus.FROZEN)
        buttonCallback = showEventBattlesPrimeTimeWindow
        data = wt_event_helpers.getAlertStatusVO()
        self.__updateAlertBlock(buttonCallback, data, isBlockedStatus)

    def __updateAlertBlock(self, callback, data, visible):
        self.as_setAlertMessageBlockVisibleS(visible)
        if visible and self.alertMessage is not None:
            self.alertMessage.update(data.asDict(), onBtnClickCallback=callback)
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
            event = viewPy.getOnPanelSectionSelected()
            event += self.__onOptDeviceClick
        if alias in _VIEWS_WITH_ESC_HANDLER:
            event = viewPy.getOnEscKeyDown()
            event += self.onEscape

    def _onUnregisterFlashComponent(self, viewPy, alias):
        super(Hangar, self)._onUnregisterFlashComponent(viewPy, alias)
        if alias == HANGAR_ALIASES.AMMUNITION_PANEL_INJECT and viewPy.getInjectView():
            event = viewPy.getOnPanelSectionSelected()
            event -= self.__onOptDeviceClick
        if alias in _VIEWS_WITH_ESC_HANDLER and viewPy.getInjectView():
            event = viewPy.getOnEscKeyDown()
            event -= self.onEscape

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

    @property
    def tankMenXpPanel(self):
        return self.getComponent(HANGAR_ALIASES.TMEN_XP_PANEL)

    def onCacheResync(self, reason, diff):
        if diff is not None and GUI_ITEM_TYPE.CREW_BOOKS in diff:
            self.as_setNotificationEnabledS(crewBooksViewedCache().haveNewCrewBooks())
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
        self.__updateLootBoxesState()

    def onEnqueued(self, queueType, *args):
        self.__onEntityChanged()

    def onDequeued(self, queueType, *args):
        self.__onEntityChanged()

    def onRankedUpdate(self):
        self.__updateHeaderComponent()
        self.__updateRankedHeaderComponent()

    def __updateBattleRoyaleComponents(self):
        self.__updateHeaderComponent()
        self.__updateBattleRoyaleHeaderComponent()

    def __onEpicBattleUpdated(self, *_):
        self.__updateHeaderComponent()
        self.__updateHeaderEpicWidget()
        self.__updateAmmoPanel()
        self.__updateAlertMessage()

    def __updateEventComponents(self):
        self.__updateHeaderComponent()
        self.__updateEventHeaderComponent()
        self.__updateLootBoxesState()
        self._updateEventMode()
        self.as_setCloseBtnVisibleS(self.gameEventController.isEventPrbActive())

    def __updateAll(self):
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
        self.__updateEventHeaderComponent()
        self.__updateCrew()
        self.__updateAlertMessage()
        self.__updateBattleRoyaleComponents()
        self._updateCnSubscriptionMode()
        self.__updateEventComponents()
        self._updateBattleRoyaleMode()
        self._updateEventMode()
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
        self.as_setNotificationEnabledS(crewBooksViewedCache().haveNewCrewBooks())
        self._updateCnSubscriptionMode()
        self._updateBattleRoyaleMode()
        self._updateEventMode()
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

    def __updateState(self):
        state = g_currentVehicle.getViewState()
        self.as_setCrewEnabledS(state.isCrewOpsEnabled())
        isBattleRoyaleMode = self.battleRoyaleController.isBattleRoyaleMode()
        isEventMode = self.gameEventController.isEventPrbActive()
        isC11nEnabled = self.lobbyContext.getServerSettings().isCustomizationEnabled() and state.isCustomizationEnabled() and self.__isSpaceReadyForC11n and self.__isVehicleReadyForC11n and self.__isVehicleCameraReadyForC11n and not isBattleRoyaleMode and not isEventMode
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
        self.__updateAlertMessage()
        self.__updateNavigationInResearchPanel()
        self.__updateVehicleInResearchPanel()
        self.__updateHeaderComponent()
        self.__updateRankedHeaderComponent()
        self.__updateHeaderEpicWidget()
        self.__switchCarousels()
        self.__updateBattleRoyaleComponents()
        self.__updateEventComponents()
        self._updateEventMode()

    def __onVehicleClientStateChanged(self, _):
        self.__updateAmmoPanel()

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
            self.__updateWotPlusState()

    def __onSettingsChanged(self, diff):
        if SETTINGS_SECTIONS.UI_STORAGE in diff:
            if self.ammoPanel:
                self.ammoPanel.update()

    def __onWotPlusDataChanged(self, diff):
        if 'isEnabled' in diff:
            self.__updateWotPlusState()

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

    def __updateLootBoxesState(self):
        if self.prbDispatcher:
            state = self.prbDispatcher.getFunctionalState()
            isVisible = not self.bootcampController.isInBootcamp() and self.gameEventController.isEnabled() and (state.isInPreQueue(QUEUE_TYPE.RANDOMS) or state.isInUnit(PREBATTLE_TYPE.SQUAD) or state.isInLegacy(PREBATTLE_TYPE.TRAINING) or state.isInPreQueue(QUEUE_TYPE.EVENT_BATTLES) or state.isInUnit(PREBATTLE_TYPE.EVENT))
        else:
            isVisible = False
        self.as_setLootboxesVisibleS(isVisible)
