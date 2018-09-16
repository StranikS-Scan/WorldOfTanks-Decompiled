# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/Hangar.py
import BigWorld
import SoundGroups
from CurrentVehicle import g_currentVehicle
from constants import QUEUE_TYPE
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.Waiting import Waiting
from gui.Scaleform.daapi import LobbySubView
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.meta.HangarMeta import HangarMeta
from gui.Scaleform.framework import ViewTypes
from gui.Scaleform.framework.managers.containers import POP_UP_CRITERIA
from gui.Scaleform.genConsts.HANGAR_ALIASES import HANGAR_ALIASES
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.prb_control.ctrl_events import g_prbCtrlEvents
from gui.prb_control.entities.listener import IGlobalListener
from gui.ranked_battles.constants import PRIME_TIME_STATUS
from gui.shared import events, EVENT_BUS_SCOPE
from gui.shared.events import LobbySimpleEvent
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.items_cache import CACHE_SYNC_REASON
from gui.shared.utils.HangarSpace import g_hangarSpace
from gui.shared.utils.functions import makeTooltip
from helpers import dependency
from helpers.i18n import makeString as _ms
from skeletons.gui.game_control import IFalloutController, IRankedBattlesController
from skeletons.gui.game_control import IIGRController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from skeletons.new_year import INewYearController

class Hangar(LobbySubView, HangarMeta, IGlobalListener):
    __background_alpha__ = 0.0
    rankedController = dependency.descriptor(IRankedBattlesController)
    itemsCache = dependency.descriptor(IItemsCache)
    falloutCtrl = dependency.descriptor(IFalloutController)
    igrCtrl = dependency.descriptor(IIGRController)
    lobbyContext = dependency.descriptor(ILobbyContext)
    _newYearController = dependency.descriptor(INewYearController)

    def __init__(self, _=None):
        LobbySubView.__init__(self, 0)
        self.__isCursorOver3dScene = False
        self.__selected3DEntity = None
        self.__currentCarouselAlias = None
        return

    def _populate(self):
        self._onPopulateStarted()
        LobbySubView._populate(self)
        g_currentVehicle.onChanged += self.__onCurrentVehicleChanged
        self.igrCtrl.onIgrTypeChanged += self.__onIgrTypeChanged
        self.falloutCtrl.onSettingsChanged += self.__onFalloutSettingsChanged
        self.itemsCache.onSyncCompleted += self.onCacheResync
        self.rankedController.onUpdated += self.onRankedUpdate
        self.rankedController.onPrimeTimeStatusUpdated += self.__onRankedPrimeStatusUpdate
        g_hangarSpace.onObjectSelected += self.__on3DObjectSelected
        g_hangarSpace.onObjectUnselected += self.__on3DObjectUnSelected
        g_hangarSpace.onObjectClicked += self.__on3DObjectClicked
        g_hangarSpace.setVehicleSelectable(True)
        g_prbCtrlEvents.onVehicleClientStateChanged += self.__onVehicleClientStateChanged
        self.lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingChanged
        self._newYearController.onStateChanged += self.__onNYStateChanged
        self._newYearController.boxStorage.onCountChanged += self.__onBoxesCountChanged
        g_clientUpdateManager.addMoneyCallback(self.onMoneyUpdate)
        g_clientUpdateManager.addCallbacks({})
        self.startGlobalListening()
        self.as_initNYS(self._newYearController.isAvailable(), self._newYearController.isAvailable(), self._newYearController.boxStorage.count)
        self.__updateAll()
        self.addListener(LobbySimpleEvent.NOTIFY_CURSOR_OVER_3DSCENE, self.__onNotifyCursorOver3dScene)
        self.addListener(LobbySimpleEvent.WAITING_SHOWN, self.__onWaitingShown, EVENT_BUS_SCOPE.LOBBY)
        self.addListener(events.FightButtonEvent.FIGHT_BUTTON_UPDATE, self.__handleFightButtonUpdated, scope=EVENT_BUS_SCOPE.LOBBY)
        selectedHangarEntityId = BigWorld.player().selectedHangarEntityId
        if selectedHangarEntityId is not None:
            entity = BigWorld.entities.get(selectedHangarEntityId, None)
            if entity is not None:
                self.__on3DObjectSelected(entity)
        self._onPopulateEnd()
        return

    def onEscape(self):
        dialogsContainer = self.app.containerManager.getContainer(ViewTypes.TOP_WINDOW)
        if not dialogsContainer.getView(criteria={POP_UP_CRITERIA.VIEW_ALIAS: VIEW_ALIAS.LOBBY_MENU}):
            self.fireEvent(events.LoadViewEvent(VIEW_ALIAS.LOBBY_MENU), scope=EVENT_BUS_SCOPE.LOBBY)

    def showHelpLayout(self):
        containerManager = self.app.containerManager
        dialogsContainer = containerManager.getContainer(ViewTypes.TOP_WINDOW)
        windowsContainer = containerManager.getContainer(ViewTypes.WINDOW)
        browserWindowContainer = containerManager.getContainer(ViewTypes.BROWSER)
        if not dialogsContainer.getViewCount() and not windowsContainer.getViewCount() and not browserWindowContainer.getViewCount():
            containerManager.onViewAddedToContainer += self.__onViewAddedToContainer
            self.fireEvent(LobbySimpleEvent(LobbySimpleEvent.SHOW_HELPLAYOUT), scope=EVENT_BUS_SCOPE.LOBBY)
            self.as_showHelpLayoutS()

    def __onViewAddedToContainer(self, _, pyEntity):
        self.closeHelpLayout()

    def closeHelpLayout(self):
        self.app.containerManager.onViewAddedToContainer -= self.__onViewAddedToContainer
        self.fireEvent(LobbySimpleEvent(LobbySimpleEvent.CLOSE_HELPLAYOUT), scope=EVENT_BUS_SCOPE.LOBBY)
        self.as_closeHelpLayoutS()

    def _dispose(self):
        """
        Dispose method should never be called before populate finish. So, we're delaying
        its invoke til populate load is finished.
        """
        self.removeListener(LobbySimpleEvent.NOTIFY_CURSOR_OVER_3DSCENE, self.__onNotifyCursorOver3dScene)
        self.removeListener(LobbySimpleEvent.WAITING_SHOWN, self.__onWaitingShown, EVENT_BUS_SCOPE.LOBBY)
        self.removeListener(events.FightButtonEvent.FIGHT_BUTTON_UPDATE, self.__handleFightButtonUpdated, scope=EVENT_BUS_SCOPE.LOBBY)
        self.itemsCache.onSyncCompleted -= self.onCacheResync
        g_clientUpdateManager.removeObjectCallbacks(self)
        g_currentVehicle.onChanged -= self.__onCurrentVehicleChanged
        self.igrCtrl.onIgrTypeChanged -= self.__onIgrTypeChanged
        self.falloutCtrl.onSettingsChanged -= self.__onFalloutSettingsChanged
        self.rankedController.onUpdated -= self.onRankedUpdate
        self.rankedController.onPrimeTimeStatusUpdated -= self.__onRankedPrimeStatusUpdate
        g_hangarSpace.onObjectSelected -= self.__on3DObjectSelected
        g_hangarSpace.onObjectUnselected -= self.__on3DObjectUnSelected
        g_hangarSpace.onObjectClicked -= self.__on3DObjectClicked
        g_hangarSpace.setVehicleSelectable(False)
        g_prbCtrlEvents.onVehicleClientStateChanged -= self.__onVehicleClientStateChanged
        self.lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingChanged
        self._newYearController.onStateChanged -= self.__onNYStateChanged
        self._newYearController.boxStorage.onCountChanged -= self.__onBoxesCountChanged
        if self.__selected3DEntity is not None:
            BigWorld.wgDelEdgeDetectEntity(self.__selected3DEntity)
            self.__selected3DEntity = None
        self.closeHelpLayout()
        self.stopGlobalListening()
        LobbySubView._dispose(self)
        return

    def __onNYStateChanged(self, _):
        available = self._newYearController.isAvailable()
        self.as_updateNYEnabledS(available)
        self.as_updateNYAvailableS(available)

    def __onBoxesCountChanged(self, *args):
        self.as_updateNYBoxCounterS(self._newYearController.boxStorage.count)

    def __switchCarousels(self):
        prevCarouselAlias = self.__currentCarouselAlias
        if self.falloutCtrl.isSelected():
            linkage = HANGAR_ALIASES.FALLOUT_TANK_CAROUSEL_UI
            newCarouselAlias = HANGAR_ALIASES.FALLOUT_TANK_CAROUSEL
        elif self.prbDispatcher is not None and self.prbDispatcher.getFunctionalState().isInPreQueue(QUEUE_TYPE.RANKED):
            linkage = HANGAR_ALIASES.TANK_CAROUSEL_UI
            newCarouselAlias = HANGAR_ALIASES.RANKED_TANK_CAROUSEL
        else:
            linkage = HANGAR_ALIASES.TANK_CAROUSEL_UI
            newCarouselAlias = HANGAR_ALIASES.TANK_CAROUSEL
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
        if not self.prbDispatcher.getFunctionalState().isInPreQueue(QUEUE_TYPE.RANKED) and not self.headerComponent:
            self.as_setDefaultHeaderS(True)
        if self.headerComponent is not None:
            self.headerComponent.update()
        return

    def __updateCrew(self):
        if self.crewPanel is not None:
            self.crewPanel.updateTankmen()
        return

    def __updateRankedWidget(self):
        if self.prbDispatcher.getFunctionalState().isInPreQueue(QUEUE_TYPE.RANKED) and not self.rankedWidget:
            self.as_setDefaultHeaderS(False)
        if self.rankedWidget is not None:
            vehicle = g_currentVehicle.item
            ranks = self.rankedController.getAllRanksChain(vehicle)
            currentRank = self.rankedController.getCurrentRank(vehicle)
            lastRank = self.rankedController.getLastRank(vehicle)
            self.rankedWidget.update(ranks, currentRank, lastRank)
        return

    def __updateAlertMessage(self):
        if self.prbDispatcher.getFunctionalState().isInPreQueue(QUEUE_TYPE.RANKED):
            status, timeLeft = self.rankedController.getPrimeTimeStatus()
            visible = status == PRIME_TIME_STATUS.NOT_AVAILABLE
            self.as_setAlertMessageBlockVisibleS(visible)
            if visible and self.alertMessage is not None:
                self.alertMessage.updateTimeLeft(timeLeft)
        else:
            self.as_setAlertMessageBlockVisibleS(False)
        return

    def __highlight3DEntityAndShowTT(self, entity):
        entity.highlight(True)
        itemId = entity.selectionId
        if itemId:
            self.as_show3DSceneTooltipS(TOOLTIPS_CONSTANTS.ENVIRONMENT, [itemId])

    def __fade3DEntityAndHideTT(self, entity):
        entity.highlight(False)
        self.as_hide3DSceneTooltipS()

    def __onWaitingShown(self, event):
        self.closeHelpLayout()

    def __handleFightButtonUpdated(self, _):
        self.__updateNavigationInResearchPanel()

    def __onNotifyCursorOver3dScene(self, event):
        self.__isCursorOver3dScene = event.ctx.get('isOver3dScene', False)
        if self.__selected3DEntity is not None:
            if self.__isCursorOver3dScene:
                self.__highlight3DEntityAndShowTT(self.__selected3DEntity)
            else:
                self.__fade3DEntityAndHideTT(self.__selected3DEntity)
        return

    def __on3DObjectSelected(self, entity):
        self.__selected3DEntity = entity
        if self.__isCursorOver3dScene:
            self.__highlight3DEntityAndShowTT(entity)
            if entity.mouseOverSoundName:
                SoundGroups.g_instance.playSound3D(entity.model.root, entity.mouseOverSoundName)

    def __on3DObjectUnSelected(self, entity):
        self.__selected3DEntity = None
        if self.__isCursorOver3dScene:
            self.__fade3DEntityAndHideTT(entity)
        return

    def __on3DObjectClicked(self):
        if self.__isCursorOver3dScene:
            if self.__selected3DEntity is not None:
                self.__selected3DEntity.onClicked()
        return

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

    def onCacheResync(self, reason, diff):
        if reason == CACHE_SYNC_REASON.SHOP_RESYNC:
            self.__updateAll()
            return
        else:
            if diff is not None and GUI_ITEM_TYPE.VEHICLE in diff:
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

    def onPrbEntitySwitched(self):
        self.__onEntityChanged()

    def onEnqueued(self, queueType, *args):
        self.__onEntityChanged()

    def onDequeued(self, queueType, *args):
        self.__onEntityChanged()

    def onMoneyUpdate(self, *args):
        pass

    def onRankedUpdate(self):
        self.__updateRankedWidget()

    def _onPopulateStarted(self):
        pass

    def _onPopulateEnd(self):
        pass

    def __onRankedPrimeStatusUpdate(self, status):
        if self.prbDispatcher.getFunctionalState().isInPreQueue(QUEUE_TYPE.RANKED):
            self.as_setAlertMessageBlockVisibleS(status != PRIME_TIME_STATUS.AVAILABLE)

    def __updateAll(self):
        Waiting.show('updateVehicle')
        self.__switchCarousels()
        self.__updateState()
        self.__updateAmmoPanel()
        self.__updateParams()
        self.__updateVehicleInResearchPanel()
        self.__updateNavigationInResearchPanel()
        self.__updateHeader()
        self.__updateCrew()
        self.__updateRankedWidget()
        self.__updateAlertMessage()
        Waiting.hide('updateVehicle')

    def __onCurrentVehicleChanged(self):
        Waiting.show('updateVehicle')
        self.__updateState()
        self.__updateAmmoPanel()
        self.__updateParams()
        self.__updateVehicleInResearchPanel()
        self.__updateHeader()
        self.__updateCrew()
        self.__updateRankedWidget()
        Waiting.hide('updateVehicle')

    def __onIgrTypeChanged(self, *args):
        self.__updateVehicleInResearchPanel()
        self.__updateHeader()
        self.__updateParams()

    def __onFalloutSettingsChanged(self):
        self.__switchCarousels()

    def __updateState(self):
        state = g_currentVehicle.getViewState()
        self.as_setCrewEnabledS(state.isCrewOpsEnabled())
        isC11nEnabled = self.lobbyContext.getServerSettings().isCustomizationEnabled() and state.isCustomizationEnabled() and not state.isOnlyForEventBattles()
        if isC11nEnabled:
            customizationTooltip = makeTooltip(_ms(TOOLTIPS.HANGAR_TUNING_HEADER), _ms(TOOLTIPS.HANGAR_TUNING_BODY))
        else:
            customizationTooltip = makeTooltip(_ms(TOOLTIPS.HANGAR_TUNING_DISABLED_HEADER), _ms(TOOLTIPS.HANGAR_TUNING_DISABLED_BODY))
        self.as_setupAmmunitionPanelS(state.isMaintenanceEnabled(), makeTooltip(_ms(TOOLTIPS.HANGAR_MAINTENANCE_HEADER), _ms(TOOLTIPS.HANGAR_MAINTENANCE_BODY)), isC11nEnabled, customizationTooltip)
        self.as_setControlsVisibleS(state.isUIShown())

    def __onEntityChanged(self):
        self.__updateState()
        self.__updateAmmoPanel()
        self.__updateRankedWidget()
        self.__updateAlertMessage()
        self.__updateNavigationInResearchPanel()
        self.__updateHeader()
        self.__switchCarousels()

    def __onVehicleClientStateChanged(self, vehicles):
        self.__updateAmmoPanel()

    def __onServerSettingChanged(self, diff):
        if 'isRegularQuestEnabled' in diff:
            self.__updateHeader()
        if 'isCustomizationEnabled' in diff:
            self.__updateState()
