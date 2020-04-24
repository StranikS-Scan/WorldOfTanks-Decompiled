# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/Hangar.py
import BigWorld
from CurrentVehicle import g_currentVehicle
from HeroTank import HeroTank
from account_helpers.settings_core.ServerSettingsManager import SETTINGS_SECTIONS
from constants import QUEUE_TYPE, PREBATTLE_TYPE, SENIORITY_AWARDS_CONFIG, IS_LOOT_BOXES_ENABLED
from frameworks.wulf import WindowFlags, ViewFlags
from gui.Scaleform.Waiting import Waiting
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.LobbySelectableView import LobbySelectableView
from gui.Scaleform.daapi.view.lobby.hangar.on_boarding_helper import isOnBoardingCurrentBlockVisited, setOnBoardingLastVisitedBlock
from gui.Scaleform.daapi.view.meta.HangarMeta import HangarMeta
from gui.Scaleform.framework import ViewTypes
from gui.Scaleform.framework.entities.View import CommonSoundSpaceSettings
from gui.Scaleform.framework.managers.containers import POP_UP_CRITERIA
from gui.Scaleform.genConsts.HANGAR_ALIASES import HANGAR_ALIASES
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.game_control.links import URLMacros
from gui.hangar_cameras.hangar_camera_common import CameraRelatedEvents, CameraMovementStates
from gui.prb_control.ctrl_events import g_prbCtrlEvents
from gui.prb_control.entities.listener import IGlobalListener
from gui.promo.hangar_teaser_widget import TeaserViewer
from gui.ranked_battles import ranked_helpers
from gui.ranked_battles.constants import PrimeTimeStatus
from gui.shared import event_dispatcher as shared_events
from gui.shared import events, EVENT_BUS_SCOPE
from gui.shared.event_dispatcher import showTenYearsCountdownOnBoarding
from gui.shared.events import LobbySimpleEvent
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.items_cache import CACHE_SYNC_REASON
from gui.shared.tutorial_helper import getTutorialGlobalStorage
from gui.shared.utils.functions import makeTooltip
from gui.sounds.filters import States, StatesGroup
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.impl.auxiliary.crew_books_helper import crewBooksViewedCache
from battle_pass_common import BATTLE_PASS_CONFIG_NAME
from helpers import dependency
from helpers.i18n import makeString as _ms
from helpers.statistics import HANGAR_LOADING_STATE
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.connection_mgr import IConnectionManager
from skeletons.gui.game_control import IIGRController, IBobController
from skeletons.gui.game_control import IRankedBattlesController, IEpicBattleMetaGameController, IPromoController, IBattlePassController, IHangarLoadingController, ITenYearsCountdownController
from skeletons.gui.impl import IGuiLoader
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.utils import IHangarSpace
from skeletons.helpers.statistics import IStatisticsCollector
from tutorial.control.context import GLOBAL_FLAG
from account_helpers import AccountSettings
from account_helpers.AccountSettings import NATION_CHANGE_VIEWED
from gui.impl.gen import R
from gui.impl import backport
from gui.Scaleform.daapi.view.lobby.hangar.seniority_awards import getSeniorityAwardsBoxesCount
from gui.Scaleform.daapi.view.lobby.bob import bob_helpers

def predicateNotEmptyWindow(window):
    return window.content is not None and window.windowFlags != WindowFlags.TOOLTIP and window.content.viewFlags != ViewFlags.COMPONENT


class Hangar(LobbySelectableView, HangarMeta, IGlobalListener):
    _SOUND_STATE_PLACE = 'STATE_hangar_place'
    _SOUND_STATE_PLACE_GARAGE = 'STATE_hangar_place_garage'
    __background_alpha__ = 0.0
    __SOUND_SETTINGS = CommonSoundSpaceSettings(name='hangar', entranceStates={_SOUND_STATE_PLACE: _SOUND_STATE_PLACE_GARAGE,
     StatesGroup.HANGAR_FILTERED: States.HANGAR_FILTERED_OFF}, exitStates={}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent='', exitEvent='')
    rankedController = dependency.descriptor(IRankedBattlesController)
    epicController = dependency.descriptor(IEpicBattleMetaGameController)
    battlePassController = dependency.descriptor(IBattlePassController)
    itemsCache = dependency.descriptor(IItemsCache)
    igrCtrl = dependency.descriptor(IIGRController)
    lobbyContext = dependency.descriptor(ILobbyContext)
    statsCollector = dependency.descriptor(IStatisticsCollector)
    gui = dependency.descriptor(IGuiLoader)
    _settingsCore = dependency.descriptor(ISettingsCore)
    hangarSpace = dependency.descriptor(IHangarSpace)
    _promoController = dependency.descriptor(IPromoController)
    _connectionMgr = dependency.descriptor(IConnectionManager)
    _bobController = dependency.descriptor(IBobController)
    _countdownController = dependency.descriptor(ITenYearsCountdownController)
    _hangarLoadingController = dependency.descriptor(IHangarLoadingController)
    _COMMON_SOUND_SPACE = __SOUND_SETTINGS

    def __init__(self, _=None):
        LobbySelectableView.__init__(self, 0)
        self.__currentCarouselAlias = None
        self.__isSpaceReadyForC11n = False
        self.__isVehicleReadyForC11n = False
        self.__isVehicleCameraReadyForC11n = False
        self.__urlMacros = URLMacros()
        self.__teaser = None
        self.__seniorityAwardsIsActive = False
        return

    def onEscape(self):
        dialogsContainer = self.app.containerManager.getContainer(ViewTypes.TOP_WINDOW)
        if not dialogsContainer.getView(criteria={POP_UP_CRITERIA.VIEW_ALIAS: VIEW_ALIAS.LOBBY_MENU}):
            self.fireEvent(events.LoadViewEvent(VIEW_ALIAS.LOBBY_MENU), scope=EVENT_BUS_SCOPE.LOBBY)

    def hideTeaser(self):
        self.__teaser.stop(byUser=True)
        self.__teaser = None
        return

    def onTeaserClick(self):
        self._promoController.showLastTeaserPromo()

    def showHelpLayout(self):
        containerManager = self.app.containerManager
        dialogsContainer = containerManager.getContainer(ViewTypes.TOP_WINDOW)
        windowsContainer = containerManager.getContainer(ViewTypes.WINDOW)
        browserWindowContainer = containerManager.getContainer(ViewTypes.BROWSER)
        overlayContainer = containerManager.getContainer(ViewTypes.OVERLAY)
        unboundWindows = self.gui.windowsManager.findWindows(predicateNotEmptyWindow)
        if not dialogsContainer.getViewCount() and not windowsContainer.getViewCount() and not browserWindowContainer.getViewCount() and not overlayContainer.getViewCount() and not unboundWindows:
            containerManager.onViewAddedToContainer += self.__onViewAddedToContainer
            self.fireEvent(LobbySimpleEvent(LobbySimpleEvent.SHOW_HELPLAYOUT), scope=EVENT_BUS_SCOPE.LOBBY)
            self.as_showHelpLayoutS()

    def closeHelpLayout(self):
        self.app.containerManager.onViewAddedToContainer -= self.__onViewAddedToContainer
        self.fireEvent(LobbySimpleEvent(LobbySimpleEvent.CLOSE_HELPLAYOUT), scope=EVENT_BUS_SCOPE.LOBBY)
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
        self.epicController.onUpdated += self.__onEpicSkillsUpdate
        self.epicController.onPrimeTimeStatusUpdated += self.__onEpicSkillsUpdate
        self._promoController.onNewTeaserReceived += self.__onTeaserReceived
        self._bobController.onUpdated += self.onBobUpdate
        self._bobController.onPrimeTimeStatusUpdated += self.__updateAlertMessage
        self.hangarSpace.setVehicleSelectable(True)
        g_prbCtrlEvents.onVehicleClientStateChanged += self.__onVehicleClientStateChanged
        self.lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingChanged
        self._settingsCore.onSettingsChanged += self.__onSettingsChanged
        self.battlePassController.onSeasonStateChange += self.__switchCarousels
        self._countdownController.onEventStateChanged += self.__updateTenYearsCountdownEntryPointVisibility
        self._countdownController.onEventBlockChanged += self.__updateTenYearsCountdownEntryPointVisibility
        self._countdownController.onBlocksDataValidityChanged += self.__updateTenYearsCountdownEntryPointVisibility
        self._hangarLoadingController.onHangarLoadedAfterLogin += self.__onHangarLoadedAfterLogin
        self.startGlobalListening()
        self.__updateAll()
        self.addListener(LobbySimpleEvent.WAITING_SHOWN, self.__onWaitingShown, EVENT_BUS_SCOPE.LOBBY)
        self.addListener(events.FightButtonEvent.FIGHT_BUTTON_UPDATE, self.__handleFightButtonUpdated, scope=EVENT_BUS_SCOPE.LOBBY)
        self.addListener(CameraRelatedEvents.CAMERA_ENTITY_UPDATED, self.__handleSelectedEntityUpdated)
        self._onPopulateEnd()
        self.statsCollector.noteHangarLoadingState(HANGAR_LOADING_STATE.HANGAR_UI_READY, showSummaryNow=True)
        lobbyContext = dependency.instance(ILobbyContext)
        isCrewBooksEnabled = lobbyContext.getServerSettings().isCrewBooksEnabled()
        getTutorialGlobalStorage().setValue(GLOBAL_FLAG.CREW_BOOKS_ENABLED, isCrewBooksEnabled)
        self.as_setNotificationEnabledS(crewBooksViewedCache().haveNewCrewBooks())
        self.__updateSenorityEntryPoint()
        self.__updateTenYearsCountdownEntryPointVisibility()

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
        self.rankedController.onGameModeStatusTick -= self.__updateAlertMessage
        self.epicController.onUpdated -= self.__onEpicSkillsUpdate
        self.epicController.onPrimeTimeStatusUpdated -= self.__onEpicSkillsUpdate
        self._promoController.onNewTeaserReceived -= self.__onTeaserReceived
        self._bobController.onUpdated -= self.onBobUpdate
        self._bobController.onPrimeTimeStatusUpdated -= self.__updateAlertMessage
        if self.__teaser is not None:
            self.__teaser.stop()
            self.__teaser = None
        self.hangarSpace.setVehicleSelectable(False)
        g_prbCtrlEvents.onVehicleClientStateChanged -= self.__onVehicleClientStateChanged
        self._settingsCore.onSettingsChanged -= self.__onSettingsChanged
        self.lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingChanged
        self.battlePassController.onSeasonStateChange -= self.__switchCarousels
        self._countdownController.onEventStateChanged -= self.__updateTenYearsCountdownEntryPointVisibility
        self._countdownController.onEventBlockChanged -= self.__updateTenYearsCountdownEntryPointVisibility
        self._countdownController.onBlocksDataValidityChanged -= self.__updateTenYearsCountdownEntryPointVisibility
        self._hangarLoadingController.onHangarLoadedAfterLogin -= self.__onHangarLoadedAfterLogin
        self.closeHelpLayout()
        self.stopGlobalListening()
        LobbySelectableView._dispose(self)
        return

    def __updateSenorityEntryPoint(self):
        curStatus = self.__seniorityAwardsIsActive
        hasBoxes = getSeniorityAwardsBoxesCount() > 0
        config = self.lobbyContext.getServerSettings().getSeniorityAwardsConfig()
        seniorityAwardsWidgetVisibility = config.hangarWidgetIsVisible()
        self.__seniorityAwardsIsActive = config.isEnabled and hasBoxes and seniorityAwardsWidgetVisibility
        if curStatus != self.__seniorityAwardsIsActive:
            self.__seniorityAwardsIsActive = hasBoxes and self.__seniorityAwardsIsActive
            self.as_updateSeniorityAwardsEntryPointS(self.__seniorityAwardsIsActive)

    def __onViewAddedToContainer(self, _, pyEntity):
        self.closeHelpLayout()

    def __switchCarousels(self):
        prevCarouselAlias = self.__currentCarouselAlias
        linkage = HANGAR_ALIASES.TANK_CAROUSEL_UI
        newCarouselAlias = HANGAR_ALIASES.TANK_CAROUSEL
        if self.prbDispatcher is not None:
            if self.battlePassController.isVisible() and self.battlePassController.isValidBattleType(self.prbDispatcher.getEntity()):
                newCarouselAlias = HANGAR_ALIASES.BATTLEPASS_TANK_CAROUSEL
            elif self.prbDispatcher.getFunctionalState().isInPreQueue(QUEUE_TYPE.RANKED):
                linkage = HANGAR_ALIASES.TANK_CAROUSEL_UI
                newCarouselAlias = HANGAR_ALIASES.RANKED_TANK_CAROUSEL
            elif self.prbDispatcher.getFunctionalState().isInPreQueue(QUEUE_TYPE.EPIC) or self.prbDispatcher.getFunctionalState().isInUnit(PREBATTLE_TYPE.EPIC):
                linkage = HANGAR_ALIASES.TANK_CAROUSEL_UI
                newCarouselAlias = HANGAR_ALIASES.EPICBATTLE_TANK_CAROUSEL
            elif self.prbDispatcher.getFunctionalState().isInPreQueue(QUEUE_TYPE.BOB) or self.prbDispatcher.getFunctionalState().isInUnit(PREBATTLE_TYPE.BOB):
                linkage = HANGAR_ALIASES.TANK_CAROUSEL_UI
                newCarouselAlias = HANGAR_ALIASES.BOB_TANK_CAROUSEL
        if prevCarouselAlias != newCarouselAlias:
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
            if self.prbDispatcher.getFunctionalState().isInPreQueue(QUEUE_TYPE.RANKED):
                if not self.rankedWidget:
                    self.as_setHeaderTypeS(HANGAR_ALIASES.RANKED_WIDGET)
            elif self.prbDispatcher.getFunctionalState().isInPreQueue(QUEUE_TYPE.EPIC) or self.prbDispatcher.getFunctionalState().isInUnit(PREBATTLE_TYPE.EPIC):
                if not self.epicWidget:
                    self.as_setHeaderTypeS(HANGAR_ALIASES.EPIC_WIDGET)
            elif not self.headerComponent:
                self.as_setDefaultHeaderS()
        return

    def __updateHeaderComponent(self):
        if self.headerComponent is not None:
            self.headerComponent.update()
        return

    def __updateHeaderEpicWidget(self):
        if self.epicWidget is not None:
            self.epicWidget.update()
        return

    def __updateHeaderRankedWidget(self):
        if self.rankedWidget is not None:
            self.rankedWidget.update()
        return

    def __updateCrew(self):
        if self.crewPanel is not None:
            self.crewPanel.updateTankmen()
        return

    def __updateAlertMessage(self, *args):
        if self.prbDispatcher is not None:
            state = self.prbDispatcher.getFunctionalState()
            if state.isInPreQueue(QUEUE_TYPE.RANKED):
                self.__updateRankedAlertMsg()
                return
            if state.isInPreQueue(QUEUE_TYPE.BOB):
                self.__updateBobAlertMsg()
                return
        self.as_setAlertMessageBlockVisibleS(False)
        return

    def __updateRankedAlertMsg(self):
        status, _, _ = self.rankedController.getPrimeTimeStatus()
        visible = self.__isAlertBlockVisible(status)
        data = ranked_helpers.getAlertStatusVO()
        self.__updateAlertBlock(shared_events.showRankedPrimeTimeWindow, data, visible)

    def __updateBobAlertMsg(self):
        status, _, _ = self._bobController.getPrimeTimeStatus()
        visible = self.__isAlertBlockVisible(status)
        data = bob_helpers.getPrimeTimeStatusVO(status, self._bobController.hasAnyPeripheryWithPrimeTime())
        self.__updateAlertBlock(shared_events.showBobPrimeTimeWindow, data, visible)

    def __isAlertBlockVisible(self, status):
        return status in (PrimeTimeStatus.NOT_AVAILABLE, PrimeTimeStatus.NOT_SET, PrimeTimeStatus.FROZEN)

    def __updateAlertBlock(self, callback, data, visible):
        self.as_setAlertMessageBlockVisibleS(visible)
        if visible and self.alertMessage is not None:
            self.alertMessage.update(data._asdict(), onBtnClickCallback=callback)
        return

    def __updateTenYearsCountdownEntryPointVisibility(self):
        isVisible = self._countdownController.isEventInProgress() and self._countdownController.isBlocksDataValid()
        self.as_updateEventEntryPointS(HANGAR_ALIASES.TEN_YEARS_COUNTDOWN_ENTRY_POINT_INJECT, isVisible)

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
    def rankedWidget(self):
        return self.getComponent(HANGAR_ALIASES.RANKED_WIDGET)

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
            self.__updateSenorityEntryPoint()
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

    def onEnqueued(self, queueType, *args):
        self.__onEntityChanged()

    def onDequeued(self, queueType, *args):
        self.__onEntityChanged()

    def onRankedUpdate(self):
        self.__updateHeader()
        self.__updateHeaderComponent()
        self.__updateHeaderRankedWidget()

    def onBobUpdate(self):
        self.__updateHeader()
        self.__updateHeaderComponent()
        self.__updateAlertMessage()

    def _onPopulateEnd(self):
        pass

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
        self.__updateHeaderEpicWidget()
        self.__updateHeaderRankedWidget()
        self.__updateCrew()
        self.__updateAlertMessage()
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

    def __updateState(self):
        state = g_currentVehicle.getViewState()
        self.as_setCrewEnabledS(state.isCrewOpsEnabled())
        isC11nEnabled = self.lobbyContext.getServerSettings().isCustomizationEnabled() and state.isCustomizationEnabled() and not state.isOnlyForEventBattles() and self.__isSpaceReadyForC11n and self.__isVehicleReadyForC11n and self.__isVehicleCameraReadyForC11n
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
        self.as_setupAmmunitionPanelS({'maintenanceEnabled': state.isMaintenanceEnabled(),
         'maintenanceTooltip': TOOLTIPS.HANGAR_MAINTENANCE,
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
        self.__updateHeaderEpicWidget()
        self.__updateHeaderRankedWidget()
        self.__switchCarousels()

    def __onVehicleClientStateChanged(self, vehicles):
        self.__updateAmmoPanel()

    def __onServerSettingChanged(self, diff):
        if 'isRegularQuestEnabled' in diff:
            self.__updateHeader()
            self.__updateHeaderComponent()
            self.__updateHeaderEpicWidget()
        if 'isCustomizationEnabled' in diff:
            self.__updateState()
        if {SENIORITY_AWARDS_CONFIG, IS_LOOT_BOXES_ENABLED}.intersection(diff):
            self.__updateSenorityEntryPoint()
        if BATTLE_PASS_CONFIG_NAME in diff:
            self.__switchCarousels()

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

    def __onHangarLoadedAfterLogin(self):
        isEnabled = self._countdownController.isEnabled()
        isBlocksDataValid = self._countdownController.isBlocksDataValid()
        currentBlockNumber = self._countdownController.getCurrentBlockNumber()
        if isEnabled and isBlocksDataValid and not isOnBoardingCurrentBlockVisited(currentBlockNumber):
            setOnBoardingLastVisitedBlock(currentBlockNumber)
            showTenYearsCountdownOnBoarding(currentBlockNumber, self._countdownController.isCurrentBlockActive(), self._countdownController.getMonths(), self._countdownController.getBlocksCount())
