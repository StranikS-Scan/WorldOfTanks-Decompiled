# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/Hangar.py
import typing
import datetime
from random import choice
import BigWorld
import SoundGroups
from CurrentVehicle import g_currentVehicle, g_currentPreviewVehicle
from HalloweenHangarTank import HalloweenHangarTank
from HeroTank import HeroTank
from account_helpers.settings_core.ServerSettingsManager import SETTINGS_SECTIONS
from constants import QUEUE_TYPE, PREBATTLE_TYPE, Configs, DOG_TAGS_CONFIG, IS_CHINA
from frameworks.wulf import WindowFlags, WindowLayer, WindowStatus
from account_helpers.settings_core.settings_constants import Hw20StorageKeys
from gui.ClientUpdateManager import g_clientUpdateManager
from adisp import process
from gui.sounds.sound_constants import HW20SoundConsts
from helpers.time_utils import getServerRegionalTime
from items import vehicles
from gui.Scaleform.Waiting import Waiting
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.LobbySelectableView import LobbySelectableView
from gui.Scaleform.daapi.view.meta.HangarMeta import HangarMeta
from gui.Scaleform.daapi.view.lobby.halloween_event.event_tanks_highlight_controller import EventTanksHighlightController
from gui.Scaleform.framework.entities.View import CommonSoundSpaceSettings
from gui.Scaleform.framework.managers.containers import POP_UP_CRITERIA
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.Scaleform.genConsts.HANGAR_ALIASES import HANGAR_ALIASES
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.game_control.links import URLMacros
from gui.hangar_cameras.hangar_camera_common import CameraRelatedEvents, CameraMovementStates
from gui.impl.gen.view_models.constants.tutorial_hint_consts import TutorialHintConsts
from gui.impl.auxiliary.crew_books_helper import crewBooksViewedCache
from gui.prb_control.ctrl_events import g_prbCtrlEvents
from gui.prb_control.entities.base.ctx import PrbAction
from gui.prb_control.entities.listener import IGlobalListener
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.settings import PREBATTLE_ACTION_NAME
from gui.promo.hangar_teaser_widget import TeaserViewer
from gui.ranked_battles import ranked_helpers
from gui.ranked_battles.constants import PrimeTimeStatus
from gui.shared import event_dispatcher as shared_events, g_eventBus
from gui.shared import events, EVENT_BUS_SCOPE
from gui.shared.event_dispatcher import showRankedPrimeTimeWindow, showAmmunitionSetupView, showCNLootBoxesWelcomeScreen
from gui.shared.events import LobbySimpleEvent, AmmunitionSetupViewEvent
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.Vehicle import VEHICLE_TAGS
from gui.shared.items_cache import CACHE_SYNC_REASON
from gui.shared.tutorial_helper import getTutorialGlobalStorage
from gui.shared.utils.functions import makeTooltip
from gui.sounds.filters import States, StatesGroup
from battle_pass_common import BATTLE_PASS_CONFIG_NAME
from helpers import dependency
from helpers.i18n import makeString as _ms
from helpers.statistics import HANGAR_LOADING_STATE
from shared_utils import first
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.connection_mgr import IConnectionManager
from skeletons.gui.game_control import IIGRController, IBootcampController, ICNLootBoxesController
from skeletons.gui.game_control import IRankedBattlesController, IEpicBattleMetaGameController, IPromoController, IBattlePassController, IBattleRoyaleController
from skeletons.gui.game_event_controller import IGameEventController
from skeletons.gui.impl import IGuiLoader
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.offers import IOffersBannerController
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.utils import IHangarSpace
from skeletons.helpers.statistics import IStatisticsCollector
from tutorial.control.context import GLOBAL_FLAG
from account_helpers import AccountSettings
from account_helpers.AccountSettings import NATION_CHANGE_VIEWED
from gui.impl.gen import R
from gui.impl import backport
from gui.server_events.awards_formatters import getEventAwardFormatter, AWARDS_SIZES
from gui.shared.formatters.time_formatters import getHWTimeLeftString
_COMM_BONUSES_TO_SHOW = 6
_COMM_RECURRING_BONUS_COUNT = 1
if typing.TYPE_CHECKING:
    from frameworks.wulf import Window
_HELP_LAYOUT_RESTRICTED_LAYERS = (WindowLayer.TOP_SUB_VIEW,
 WindowLayer.FULLSCREEN_WINDOW,
 WindowLayer.WINDOW,
 WindowLayer.OVERLAY,
 WindowLayer.TOP_WINDOW)

def predicateHelpLayoutAllowedWindow(window):
    return window.typeFlag != WindowFlags.TOOLTIP and window.typeFlag != WindowFlags.CONTEXT_MENU and window.layer in _HELP_LAYOUT_RESTRICTED_LAYERS and window.windowStatus in (WindowStatus.LOADING, WindowStatus.LOADED)


class Hangar(LobbySelectableView, HangarMeta, IGlobalListener):
    _SOUND_STATE_PLACE = 'STATE_hangar_place'
    _SOUND_STATE_PLACE_GARAGE = 'STATE_hangar_place_garage'
    _ENABLED_GF_HINTS = frozenset([TutorialHintConsts.AMMUNITION_PANEL_HINT_MC,
     TutorialHintConsts.BOOTCAMP_PANEL_EQUIPMENT_MC,
     TutorialHintConsts.BOOTCAMP_PANEL_OPT_DEVICE_MC,
     TutorialHintConsts.HANGAR_PANEL_OPT_DEVICE_MC,
     TutorialHintConsts.HANGAR_PANEL_SHELLS_MC])
    _EVENT_SOUND_ENTER_STATE = 'ev_halloween_2019_hangar_metagame_enter'
    _EVENT_SOUND_LEAVE_STATE = 'ev_halloween_2019_hangar_metagame_exit'
    __background_alpha__ = 0.0
    __SOUND_SETTINGS = CommonSoundSpaceSettings(name='hangar', entranceStates={_SOUND_STATE_PLACE: _SOUND_STATE_PLACE_GARAGE,
     StatesGroup.HANGAR_FILTERED: States.HANGAR_FILTERED_OFF}, exitStates={}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent='', exitEvent='')
    gameEventController = dependency.descriptor(IGameEventController)
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
    eventsCache = dependency.descriptor(IEventsCache)
    _bootcamp = dependency.descriptor(IBootcampController)
    __cnLootBoxesCtrl = dependency.descriptor(ICNLootBoxesController)
    _COMMON_SOUND_SPACE = __SOUND_SETTINGS

    def __init__(self, _=None):
        LobbySelectableView.__init__(self, 0)
        self.__currentCarouselAlias = None
        self.__isSpaceReadyForC11n = False
        self.__isVehicleReadyForC11n = False
        self.__isVehicleCameraReadyForC11n = False
        self.__urlMacros = URLMacros()
        self.__teaser = None
        self.__updateDogTagsState()
        self.__highlightController = EventTanksHighlightController()
        self.__helpLayoutShown = False
        self.__enabledParamsToggle = False
        self.__vehiclesController = self.gameEventController.getVehiclesController()
        self.__vehiclesTime = {}
        self.__isCNLootBoxesActive = False
        self.__isLootBoxesAvailable = False
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
        if self.__isInEvent():
            return
        windows = self.gui.windowsManager.findWindows(predicateHelpLayoutAllowedWindow)
        if not windows:
            self.__helpLayoutShown = True
            self.gui.windowsManager.onWindowStatusChanged += self.__onWindowLoaded
            self.fireEvent(LobbySimpleEvent(LobbySimpleEvent.SHOW_HELPLAYOUT), scope=EVENT_BUS_SCOPE.LOBBY)
            self.as_showHelpLayoutS()

    def closeHelpLayout(self):
        if self.__isInEvent() or not self.__helpLayoutShown:
            return
        self.__helpLayoutShown = False
        self.gui.windowsManager.onWindowStatusChanged -= self.__onWindowLoaded
        self.fireEvent(LobbySimpleEvent(LobbySimpleEvent.CLOSE_HELPLAYOUT), scope=EVENT_BUS_SCOPE.LOBBY)
        self.as_closeHelpLayoutS()

    def onEventParamsToggle(self, visible):
        self.__enabledParamsToggle = visible

    def onEventExitClick(self):
        self.__doSelectAction(PREBATTLE_ACTION_NAME.RANDOM)

    @property
    def _isInBootCamp(self):
        return False

    def _populate(self):
        LobbySelectableView._populate(self)
        self.__highlightController.start()
        self.__isSpaceReadyForC11n = self.hangarSpace.spaceInited
        self.__isVehicleReadyForC11n = self.hangarSpace.isModelLoaded
        self.__isCNLootBoxesActive = self.__cnLootBoxesCtrl.isActive()
        self.__isLootBoxesAvailable = self.__cnLootBoxesCtrl.isLootBoxesAvailable()
        self.__checkVehicleCameraState()
        g_currentVehicle.onChanged += self.__onCurrentVehicleChanged
        g_currentPreviewVehicle.onChanged += self.__onCurrentVehicleChanged
        self.hangarSpace.onVehicleChangeStarted += self.__onVehicleLoading
        self.hangarSpace.onVehicleChanged += self.__onVehicleLoaded
        self.hangarSpace.onSpaceRefresh += self.__onSpaceRefresh
        self.hangarSpace.onSpaceCreate += self.__onSpaceCreate
        self.igrCtrl.onIgrTypeChanged += self.__onIgrTypeChanged
        self.itemsCache.onSyncCompleted += self.onCacheResync
        self.eventsCache.onSyncCompleted += self.__onEventsCacheResync
        self.rankedController.onUpdated += self.onRankedUpdate
        self.rankedController.onGameModeStatusTick += self.__updateAlertMessage
        self.battleRoyaleController.onUpdated += self.__updateBattleRoyaleComponents
        self.epicController.onUpdated += self.__onEpicSkillsUpdate
        self.epicController.onPrimeTimeStatusUpdated += self.__onEpicSkillsUpdate
        self._promoController.onNewTeaserReceived += self.__onTeaserReceived
        self.hangarSpace.setVehicleSelectable(True)
        self.__cnLootBoxesCtrl.onStatusChange += self.__cnLBEventStatusChange
        self.__cnLootBoxesCtrl.onAvailabilityChange += self.__onLootBoxesAvailabilityChange
        g_prbCtrlEvents.onVehicleClientStateChanged += self.__onVehicleClientStateChanged
        g_clientUpdateManager.addCallbacks({'inventory': self.__updateAlertMessage})
        self.lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingChanged
        self._settingsCore.onSettingsChanged += self.__onSettingsChanged
        self.battlePassController.onSeasonStateChange += self.__switchCarousels
        g_currentPreviewVehicle.onVehicleInventoryChanged += self.__onInventoryChanged
        self.startGlobalListening()
        g_eventBus.addListener(AmmunitionSetupViewEvent.HINT_ZONE_ADD, self.__onHintZoneAdded, EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.addListener(AmmunitionSetupViewEvent.HINT_ZONE_HIDE, self.__onHintZoneHide, EVENT_BUS_SCOPE.LOBBY)
        self.__updateAll()
        self.addListener(LobbySimpleEvent.WAITING_SHOWN, self.__onWaitingShown, EVENT_BUS_SCOPE.LOBBY)
        self.addListener(events.FightButtonEvent.FIGHT_BUTTON_UPDATE, self.__handleFightButtonUpdated, scope=EVENT_BUS_SCOPE.LOBBY)
        self.addListener(CameraRelatedEvents.CAMERA_ENTITY_UPDATED, self.__handleSelectedEntityUpdated)
        self.__vehiclesController.onTimeToRepairChanged += self.__vehiclesTimeChanged
        self.statsCollector.noteHangarLoadingState(HANGAR_LOADING_STATE.HANGAR_UI_READY, showSummaryNow=True)
        lobbyContext = dependency.instance(ILobbyContext)
        isCrewBooksEnabled = lobbyContext.getServerSettings().isCrewBooksEnabled()
        getTutorialGlobalStorage().setValue(GLOBAL_FLAG.CREW_BOOKS_ENABLED, isCrewBooksEnabled)
        self.as_setNotificationEnabledS(crewBooksViewedCache().haveNewCrewBooks())
        self._offersBannerController.showBanners()
        self.__updateLootBoxesState()

    def _dispose(self):
        self.__vehiclesController.onTimeToRepairChanged -= self.__vehiclesTimeChanged
        self.removeListener(LobbySimpleEvent.WAITING_SHOWN, self.__onWaitingShown, EVENT_BUS_SCOPE.LOBBY)
        self.removeListener(events.FightButtonEvent.FIGHT_BUTTON_UPDATE, self.__handleFightButtonUpdated, scope=EVENT_BUS_SCOPE.LOBBY)
        self.removeListener(CameraRelatedEvents.CAMERA_ENTITY_UPDATED, self.__handleSelectedEntityUpdated)
        self.eventsCache.onSyncCompleted -= self.__onEventsCacheResync
        self.itemsCache.onSyncCompleted -= self.onCacheResync
        self.__cnLootBoxesCtrl.onStatusChange -= self.__cnLBEventStatusChange
        self.__cnLootBoxesCtrl.onAvailabilityChange -= self.__onLootBoxesAvailabilityChange
        g_currentVehicle.onChanged -= self.__onCurrentVehicleChanged
        g_currentPreviewVehicle.onChanged -= self.__onCurrentVehicleChanged
        self.hangarSpace.onVehicleChangeStarted -= self.__onVehicleLoading
        self.hangarSpace.onVehicleChanged -= self.__onVehicleLoaded
        self.hangarSpace.onSpaceRefresh -= self.__onSpaceRefresh
        self.hangarSpace.onSpaceCreate -= self.__onSpaceCreate
        self.igrCtrl.onIgrTypeChanged -= self.__onIgrTypeChanged
        self.rankedController.onUpdated -= self.onRankedUpdate
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
        g_clientUpdateManager.removeObjectCallbacks(self)
        self._settingsCore.onSettingsChanged -= self.__onSettingsChanged
        self.lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingChanged
        self.battlePassController.onSeasonStateChange -= self.__switchCarousels
        g_currentPreviewVehicle.onVehicleInventoryChanged -= self.__onInventoryChanged
        self.closeHelpLayout()
        self.stopGlobalListening()
        g_eventBus.removeListener(AmmunitionSetupViewEvent.HINT_ZONE_ADD, self.__onHintZoneAdded, EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.removeListener(AmmunitionSetupViewEvent.HINT_ZONE_HIDE, self.__onHintZoneHide, EVENT_BUS_SCOPE.LOBBY)
        self._offersBannerController.hideBanners()
        self.__highlightController.stop()
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
            if self.battlePassController.isVisible() and self.battlePassController.isValidBattleType(self.prbDispatcher.getEntity()):
                newCarouselAlias = HANGAR_ALIASES.BATTLEPASS_TANK_CAROUSEL
            elif self.prbDispatcher.getFunctionalState().isInPreQueue(QUEUE_TYPE.RANKED):
                newCarouselAlias = HANGAR_ALIASES.RANKED_TANK_CAROUSEL
            elif self.prbDispatcher.getFunctionalState().isInPreQueue(QUEUE_TYPE.EPIC) or self.prbDispatcher.getFunctionalState().isInUnit(PREBATTLE_TYPE.EPIC):
                newCarouselAlias = HANGAR_ALIASES.EPICBATTLE_TANK_CAROUSEL
            elif self.battleRoyaleController.isBattleRoyaleMode():
                newCarouselAlias = HANGAR_ALIASES.ROYALE_TANK_CAROUSEL
            elif self.prbDispatcher.getFunctionalState().isInPreQueue(QUEUE_TYPE.EVENT_BATTLES) or self.prbDispatcher.getFunctionalState().isInUnit(PREBATTLE_TYPE.EVENT):
                newCarouselAlias = HANGAR_ALIASES.EVENT_TANK_CAROUSEL
        if prevCarouselAlias != newCarouselAlias or force:
            self.as_setCarouselS(linkage, newCarouselAlias)
            self.__currentCarouselAlias = newCarouselAlias
            if newCarouselAlias == HANGAR_ALIASES.EVENT_TANK_CAROUSEL:
                g_currentVehicle.selectEventVehicle()
            elif not self._isBCHangar():
                g_currentVehicle.selectStoredVehicle()
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
            if self.prbDispatcher.getFunctionalState().isInPreQueue(QUEUE_TYPE.EPIC) or self.prbDispatcher.getFunctionalState().isInUnit(PREBATTLE_TYPE.EPIC) or self.battleRoyaleController.isBattleRoyaleMode():
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

    def __updateHeaderEpicWidget(self):
        if self.epicWidget is not None:
            self.epicWidget.update()
        return

    def __updateCrew(self):
        if g_currentVehicle.item is None or g_currentVehicle.item.isEvent:
            return
        else:
            if self.crewPanel is not None:
                self.crewPanel.updateTankmen()
            return

    def __updateAlertMessage(self, *_):
        if self.prbDispatcher is not None:
            if self.prbDispatcher.getFunctionalState().isInPreQueue(QUEUE_TYPE.RANKED):
                self.__updateRankedAlertMsg()
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
            if isinstance(entity, HalloweenHangarTank):
                descriptor = entity.typeDescriptor
                if descriptor:
                    shared_events.showHalloweenTankPreview(descriptor.type.compactDescr)
            elif isinstance(entity, HeroTank):
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
        self.__updateHeader()
        self.__updateHeaderComponent()
        self.__updateHeaderEpicWidget()

    def onPrbEntitySwitched(self):
        self.__onEntityChanged()
        self.__updateEvent()
        self.__updateEventSound()
        self.__updateLootBoxesState()

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
        self.__updateParams()
        self.__updateVehicleInResearchPanel()
        self.__updateNavigationInResearchPanel()
        self.__updateHeader()
        self.__updateHeaderComponent()
        self.__updateRankedHeaderComponent()
        self.__updateHeaderEpicWidget()
        self.__updateCrew()
        self.__updateAlertMessage()
        self.__updateBattleRoyaleComponents()
        self._updateBattleRoyaleMode()
        self.__updateEvent()
        self.__updateEventCrew()
        Waiting.hide('updateVehicle')

    def __onCurrentVehicleChanged(self):
        Waiting.show('updateVehicle')
        self.__updateState()
        self.__updateAmmoPanel()
        self.__updateParams()
        self.__updateVehicleInResearchPanel()
        self.__updateHeader()
        self.__updateHeaderComponent()
        self.__updateHeaderEpicWidget()
        self.__updateCrew()
        self.as_setNotificationEnabledS(crewBooksViewedCache().haveNewCrewBooks())
        self._updateBattleRoyaleMode()
        self.__updateEvent()
        self.__updateEventCrew()
        Waiting.hide('updateVehicle')

    def __onSpaceRefresh(self):
        self.__isSpaceReadyForC11n = False
        self.__updateState()

    def __onSpaceCreate(self):
        self.__isSpaceReadyForC11n = True
        self.__updateState()
        self.__showCNLootBoxesWelcomeScreen()

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

    def __vehiclesTimeChanged(self, vehicleTimes):
        self.__vehiclesTime = vehicleTimes
        INVALID_TIME = -1
        rechargedNames = [ vehicles.getVehicleType(vehicleCD).shortUserString for vehicleCD, secondsLeft in vehicleTimes.items() if secondsLeft == INVALID_TIME ]
        if rechargedNames:
            self.__updateEvent()
        self.__updateEventCrew()

    def __updateState(self):
        state = g_currentVehicle.getViewState()
        self.as_setCrewEnabledS(state.isCrewOpsEnabled() and not self.__isInEvent())
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
        self.as_setupAmmunitionPanelS({'isEvent': self.__isInEvent(),
         'maintenanceEnabled': isMaintenanceEnabled,
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
        self.as_showSwitchToAmmunitionS()
        showAmmunitionSetupView(**kwargs)

    def __updateLootBoxesState(self):
        state = self.prbDispatcher.getFunctionalState()
        isVisible = not self._isInBootCamp and self.__cnLootBoxesCtrl.isActive() and (state.isInPreQueue(QUEUE_TYPE.RANDOMS) or state.isInUnit(PREBATTLE_TYPE.SQUAD) or state.isInLegacy(PREBATTLE_TYPE.TRAINING) or state.isInPreQueue(QUEUE_TYPE.EVENT_BATTLES) or state.isInUnit(PREBATTLE_TYPE.EVENT) or state.isInPreQueue(QUEUE_TYPE.RANKED))
        self.as_setChinaLootboxesVisibleS(isVisible)

    def __onHintZoneAdded(self, event):
        ctx = event.ctx
        if ctx.get('hintName') in self._ENABLED_GF_HINTS:
            self.as_createHintAreaInComponentS(TutorialHintConsts.HANGAR_AMMUNITION_PANEL_COMPONENT, ctx.get('hintName'), ctx.get('posX'), ctx.get('posY'), ctx.get('width'), ctx.get('height'))

    def __onHintZoneHide(self, event):
        ctx = event.ctx
        if ctx.get('hintName') in self._ENABLED_GF_HINTS:
            self.as_removeHintAreaS(ctx.get('hintName'))

    def __getEventCommanderSettings(self):
        return self.gameEventController.getVehicleSettings()

    def __updateEventCrew(self):
        if not self.__isInEvent():
            return
        else:
            currentVehicleId = None
            if g_currentVehicle.item is not None and g_currentVehicle.item.isEvent and g_currentPreviewVehicle.item is None:
                currentVehicleId = g_currentVehicle.item.intCD
            elif g_currentPreviewVehicle.item is not None:
                currentVehicleId = g_currentPreviewVehicle.item.intCD
            if currentVehicleId is None:
                return
            commander = self.gameEventController.getCommander(currentVehicleId)
            if commander is None:
                return
            item = commander.getNextProgressItem()
            if item is None:
                item = commander.getMaxProgressItem()
            currentProgress = commander.getCurrentProgress()
            totalProgress = commander.getTotalProgress()
            bonuses = []
            for currentItem in commander.getItems():
                bonus = self.__getBonusVO(currentItem, currentItem.isCompleted())
                bonuses.append(bonus)

            for _ in xrange(item.getBonusCount()):
                bonus = self.__getBonusVO(item, True)
                bonuses.insert(-1, bonus)

            needItems = ((len(bonuses) - _COMM_RECURRING_BONUS_COUNT - 1) / (_COMM_BONUSES_TO_SHOW - _COMM_RECURRING_BONUS_COUNT) + 1) * (_COMM_BONUSES_TO_SHOW - _COMM_RECURRING_BONUS_COUNT) + _COMM_RECURRING_BONUS_COUNT
            while needItems > len(bonuses):
                bonus = self.__getBonusVO(item, False, False)
                bonuses.append(bonus)

            bonuses = bonuses[-_COMM_BONUSES_TO_SHOW:]
            timeLeft = self.__vehiclesTime.get(currentVehicleId)
            if timeLeft is None or timeLeft == self.__vehiclesController.INVALID_TIME:
                healingTimeLeftStr = ''
                healingTimeLeftTooltipStr = ''
            else:
                healingTimeLeftStr = backport.text(R.strings.event.hangar.crew_healing.panel.timeLeft(), time=getHWTimeLeftString(timeLeft))
                healingTimeLeftTooltipStr = backport.text(R.strings.tooltips.event.healing.timeLeft(), time=getHWTimeLeftString(timeLeft))
            isEventPremium = False
            showPremiumInfo = False
            if g_currentVehicle.item is not None:
                isEventPremium = VEHICLE_TAGS.EVENT_PREMIUM_VEHICLE in g_currentVehicle.item.tags
            if g_currentPreviewVehicle.item is not None:
                showPremiumInfo = isEventPremium = VEHICLE_TAGS.EVENT_PREMIUM_VEHICLE in g_currentPreviewVehicle.item.tags
            self.as_setEventCrewS({'label': _ms(self.__getEventCommanderSettings().getTankManLabel(currentVehicleId)),
             'icon': self.__getEventCommanderSettings().getTankManIcon(currentVehicleId),
             'bonuses': bonuses,
             'progressCurrent': currentProgress,
             'progressTotal': totalProgress,
             'isSick': healingTimeLeftStr != '',
             'healingTimeLeft': healingTimeLeftStr,
             'showPremiumInfo': showPremiumInfo,
             'isPremium': isEventPremium,
             'specialArgs': [currentVehicleId, healingTimeLeftTooltipStr, isEventPremium],
             'specialAlias': TOOLTIPS_CONSTANTS.EVENT_COMMANDERS_INFO,
             'isSpecial': True})
            return

    def __getBonusVO(self, item, completed, addProgress=True):
        bonus = first((bonus for bonus in getEventAwardFormatter().format(item.getBonuses())))
        if bonus:
            vo = {'icon': bonus.getImage(AWARDS_SIZES.SMALL),
             'tooltip': bonus.tooltip,
             'specialArgs': bonus.specialArgs,
             'specialAlias': bonus.specialAlias,
             'isSpecial': bonus.isSpecial,
             'label': bonus.label,
             'completed': completed,
             'currentProgress': item.getCurrentProgress() if addProgress else 0,
             'maxProgress': item.getMaxProgress()}
        else:
            vo = self.__getEmptyBonusVO()
        return vo

    def __getEmptyBonusVO(self):
        return {'icon': '',
         'tooltip': '',
         'specialArgs': [],
         'specialAlias': '',
         'isSpecial': False,
         'label': '',
         'completed': True,
         'currentProgress': 0,
         'maxProgress': 0}

    def __onEventsCacheResync(self):
        self.__updateEvent()

    def __onInventoryChanged(self):
        self.__updateEvent()

    def __updateEvent(self):
        isShow = self.__isInEvent()
        if isShow and not self.battleRoyaleController.isBattleRoyaleMode():
            self.as_toggleBattleRoyaleS(False)
        self.as_showEventHangarS(isShow, self.__enabledParamsToggle)
        if g_currentVehicle.item is None:
            isShow = True
        isBattleRoyalVehicle = g_currentVehicle.isOnlyForBattleRoyaleBattles()
        needHide = isShow or isBattleRoyalVehicle
        componentsToHide = []
        if not self._isBCHangar():
            componentsToHide.extend(['CrewBG',
             'CrewOperationBtn',
             'CrewPanel',
             'TmenXpPanel',
             'TuningBtn'])
        tutorialManager = self.app.tutorialManager
        for component in componentsToHide:
            tutorialManager.setComponentProps(component, {'visible': not needHide})

        isPreviewEventVehicle = g_currentPreviewVehicle.item and g_currentPreviewVehicle.item.isOnlyForEventBattles
        needHide = isPreviewEventVehicle or isBattleRoyalVehicle
        tutorialManager.setComponentProps('AmmunitionPanel', {'visible': not needHide})
        if self.battleRoyaleController.isBattleRoyaleMode():
            self._updateBattleRoyaleMode()
        return

    @process
    def __doSelectAction(self, actionName):
        yield self.prbDispatcher.doSelectAction(PrbAction(actionName))

    def __isInEvent(self):
        if not self.prbDispatcher:
            return False
        else:
            entity = self.prbDispatcher.getEntity()
            return entity is not None and entity.getQueueType() == QUEUE_TYPE.EVENT_BATTLES

    def __updateEventSound(self):
        if self.__isInEvent():
            self.__playInviteStory()

    def __playInviteStory(self):
        if self.__getDayOfMonth() == self.__getValue(Hw20StorageKeys.HANGAR_LAST_HELLO_DATE, 0):
            return
        firstWasPlayed = self.__getValue(Hw20StorageKeys.HANGAR_HELLO_FIRST)
        if firstWasPlayed:
            dailyVosFlags = self.__getDailyVosFlags()
            if all(dailyVosFlags):
                self.__setValue(Hw20StorageKeys.HANGAR_DAILY_HELLO, 0)
                dailyVosFlags = self.__getDailyVosFlags()
            selectedVoIndex = choice(dailyVosFlags)
            voEventId = HW20SoundConsts.HANGAR_DAILY_VOS_TEMPLATE.format(selectedVoIndex + 1)
            self.__setDailyVOAsPlayed(selectedVoIndex)
            SoundGroups.g_instance.playSound2D(voEventId)
        else:
            self.__setValue(Hw20StorageKeys.HANGAR_HELLO_FIRST, True)
            SoundGroups.g_instance.playSound2D(HW20SoundConsts.HANGAR_FIRST_DAILY_VO)
        self.__setValue(Hw20StorageKeys.HANGAR_LAST_HELLO_DATE, self.__getDayOfMonth())

    def __getDailyVosFlags(self):
        dailyVosFlagsPacked = self.__getValue(Hw20StorageKeys.HANGAR_DAILY_HELLO, 0)
        flagsBits = tuple((int(t) for t in bin(dailyVosFlagsPacked)[2::].zfill(HW20SoundConsts.HANGAR_DAILY_VOS_AMOUNT)))
        return tuple((t for t, flag in enumerate(flagsBits[::-1]) if flag is 0))

    def __setDailyVOAsPlayed(self, dailyVOIndex):
        dailyVosFlags = self.__getValue(Hw20StorageKeys.HANGAR_DAILY_HELLO, 0)
        dailyVosFlags |= 1 << dailyVOIndex
        self.__setValue(Hw20StorageKeys.HANGAR_DAILY_HELLO, dailyVosFlags)

    def __setValue(self, name, value):
        self._settingsCore.serverSettings.setHW20NarrativeSettings({name: value})

    def __getValue(self, name, default=None):
        return self._settingsCore.serverSettings.getHW20NarrativeSettings(name, default)

    def __getDayOfMonth(self):
        return datetime.datetime.fromtimestamp(getServerRegionalTime()).day

    def _isBCHangar(self):
        return False

    def __showCNLootBoxesWelcomeScreen(self):
        if IS_CHINA and not self._bootcamp.isInBootcamp() and self.hangarSpace.spaceInited:
            showCNLootBoxesWelcomeScreen()

    def __cnLBEventStatusChange(self):
        self.__updateLootBoxesState()
        isCNLootBoxesActive = self.__cnLootBoxesCtrl.isActive()
        if self.__isCNLootBoxesActive != isCNLootBoxesActive and isCNLootBoxesActive:
            self.__showCNLootBoxesWelcomeScreen()
            self.__isCNLootBoxesActive = isCNLootBoxesActive

    def __onLootBoxesAvailabilityChange(self, *_):
        isLootBoxesAvailable = self.__cnLootBoxesCtrl.isLootBoxesAvailable()
        if self.__isLootBoxesAvailable != isLootBoxesAvailable and isLootBoxesAvailable:
            self.__showCNLootBoxesWelcomeScreen()
            self.__isLootBoxesAvailable = isLootBoxesAvailable
