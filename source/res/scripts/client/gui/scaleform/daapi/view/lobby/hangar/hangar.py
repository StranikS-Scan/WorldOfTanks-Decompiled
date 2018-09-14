# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/Hangar.py
import BigWorld
from CurrentVehicle import g_currentVehicle
from PlayerEvents import g_playerEvents
import SoundGroups
from constants import IGR_TYPE, IS_SHOW_SERVER_STATS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.prb_control.ctrl_events import g_prbCtrlEvents
from gui.shared.formatters import text_styles
from gui.shared.utils.HangarSpace import g_hangarSpace
from gui.shared.utils.MethodsRules import MethodsRules
from helpers import i18n
from gui.shared.utils.functions import makeTooltip
from gui import game_control, makeHtmlString
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.managers.containers import POP_UP_CRITERIA
from gui.Scaleform.locale.MENU import MENU
from gui.prb_control.prb_helpers import GlobalListener
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.framework import ViewTypes
from gui.Scaleform.Waiting import Waiting
from gui.Scaleform.daapi.view.meta.HangarMeta import HangarMeta
from gui.Scaleform.daapi import LobbySubView
from gui.shared import g_itemsCache, events, EVENT_BUS_SCOPE
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.ItemsCache import CACHE_SYNC_REASON
from gui.shared.events import LobbySimpleEvent
from ConnectionManager import connectionManager
from helpers.i18n import makeString as _ms
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.genConsts.HANGAR_ALIASES import HANGAR_ALIASES

class Hangar(LobbySubView, HangarMeta, GlobalListener, MethodsRules):
    __background_alpha__ = 0.0

    def __init__(self, _=None):
        LobbySubView.__init__(self, 0)
        self.__isCursorOver3dScene = False
        self.__selected3DEntity = None
        self.__currentCarouselAlias = None
        return

    @MethodsRules.delayable()
    def _populate(self):
        LobbySubView._populate(self)
        g_playerEvents.onVehicleBecomeElite += self.__onVehicleBecomeElite
        g_playerEvents.onBattleResultsReceived += self.onFittingUpdate
        g_currentVehicle.onChanged += self.__onCurrentVehicleChanged
        game_control.g_instance.igr.onIgrTypeChanged += self.__onIgrTypeChanged
        game_control.g_instance.fallout.onSettingsChanged += self.__switchCarousels
        g_itemsCache.onSyncCompleted += self.onCacheResync
        g_hangarSpace.onObjectSelected += self.__on3DObjectSelected
        g_hangarSpace.onObjectUnselected += self.__on3DObjectUnSelected
        g_hangarSpace.onObjectClicked += self.__on3DObjectClicked
        g_prbCtrlEvents.onVehicleClientStateChanged += self.__onVehicleClientStateChanged
        g_clientUpdateManager.addCallbacks({'stats.credits': self.onMoneyUpdate,
         'stats.gold': self.onMoneyUpdate,
         'stats.vehicleSellsLeft': self.onFittingUpdate,
         'stats.slots': self.onFittingUpdate,
         'goodies': self.onFittingUpdate})
        self.startGlobalListening()
        self.__onIgrTypeChanged()
        self.__updateAll()
        self.addListener(LobbySimpleEvent.HIDE_HANGAR, self._onCustomizationShow)
        self.addListener(LobbySimpleEvent.NOTIFY_CURSOR_OVER_3DSCENE, self.__onNotifyCursorOver3dScene)
        self.addListener(LobbySimpleEvent.WAITING_SHOWN, self.__onWaitingShown, EVENT_BUS_SCOPE.LOBBY)

    def _onCustomizationShow(self, event):
        self.as_setVisibleS(not event.ctx)

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

    def toggleGUIEditor(self):
        self.app.toggleEditor()

    @MethodsRules.delayable('_populate')
    def _dispose(self):
        """
        Dispose method should never be called before populate finish. So, we're delaying
        its invoke til populate load is finished.
        """
        self.removeListener(LobbySimpleEvent.HIDE_HANGAR, self._onCustomizationShow)
        self.removeListener(LobbySimpleEvent.NOTIFY_CURSOR_OVER_3DSCENE, self.__onNotifyCursorOver3dScene)
        self.removeListener(LobbySimpleEvent.WAITING_SHOWN, self.__onWaitingShown, EVENT_BUS_SCOPE.LOBBY)
        g_itemsCache.onSyncCompleted -= self.onCacheResync
        g_clientUpdateManager.removeObjectCallbacks(self)
        g_playerEvents.onVehicleBecomeElite -= self.__onVehicleBecomeElite
        g_playerEvents.onBattleResultsReceived -= self.onFittingUpdate
        g_currentVehicle.onChanged -= self.__onCurrentVehicleChanged
        game_control.g_instance.igr.onIgrTypeChanged -= self.__onIgrTypeChanged
        game_control.g_instance.fallout.onSettingsChanged -= self.__switchCarousels
        g_hangarSpace.onObjectSelected -= self.__on3DObjectSelected
        g_hangarSpace.onObjectUnselected -= self.__on3DObjectUnSelected
        g_hangarSpace.onObjectClicked -= self.__on3DObjectClicked
        g_prbCtrlEvents.onVehicleClientStateChanged -= self.__onVehicleClientStateChanged
        if self.__selected3DEntity is not None:
            BigWorld.wgDelEdgeDetectEntity(self.__selected3DEntity)
            self.__selected3DEntity = None
        self.closeHelpLayout()
        self.stopGlobalListening()
        LobbySubView._dispose(self)
        return

    def __switchCarousels(self):
        prevCarouselAlias = self.__currentCarouselAlias
        if game_control.g_instance.fallout.isSelected():
            linkage = HANGAR_ALIASES.FALLOUT_TANK_CAROUSEL_UI
            newCarouselAlias = HANGAR_ALIASES.FALLOUT_TANK_CAROUSEL
        else:
            linkage = HANGAR_ALIASES.TANK_CAROUSEL_UI
            newCarouselAlias = HANGAR_ALIASES.TANK_CAROUSEL
        if prevCarouselAlias != newCarouselAlias:
            self.as_setCarouselS(linkage, newCarouselAlias)
            self.__currentCarouselAlias = newCarouselAlias
            self.__updateCarouselVehicles()

    def __updateAmmoPanel(self):
        if self.ammoPanel:
            self.ammoPanel.update()

    def __updateParams(self):
        if self.paramsPanel:
            self.paramsPanel.update()

    def __updateCarouselVehicles(self, vehicles=None):
        if self.tankCarousel is not None:
            self.tankCarousel.updateVehicles(vehicles)
        return

    def __updateCarouselParams(self):
        if self.tankCarousel is not None:
            self.tankCarousel.updateParams()
        return

    def __updateResearchPanel(self):
        if self.researchPanel is not None:
            self.researchPanel.onCurrentVehicleChanged()
        return

    def __updateHeader(self):
        if self.headerComponent is not None:
            self.headerComponent.update()
        return

    def __updateCrew(self):
        if self.crewPanel is not None:
            self.crewPanel.updateTankmen()
        return

    def __highlight3DEntityAndShowTT(self, entity):
        entity.highlight(True)
        itemId = entity.selectionId
        if len(itemId) > 0:
            self.as_show3DSceneTooltipS(TOOLTIPS_CONSTANTS.ENVIRONMENT, [itemId])

    def __fade3DEntityAndHideTT(self, entity):
        entity.highlight(False)
        self.as_hide3DSceneTooltipS()

    def __onWaitingShown(self, event):
        self.closeHelpLayout()

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
    def tankCarousel(self):
        return self.getComponent(self.__currentCarouselAlias)

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

    def onCacheResync(self, reason, diff):
        if reason == CACHE_SYNC_REASON.SHOP_RESYNC:
            self.__updateAll()
            return
        else:
            if reason in (CACHE_SYNC_REASON.STATS_RESYNC, CACHE_SYNC_REASON.INVENTORY_RESYNC, CACHE_SYNC_REASON.CLIENT_UPDATE):
                self.__updateCarouselParams()
                self.__updateCarouselEnabled()
            if diff is not None and GUI_ITEM_TYPE.VEHICLE in diff:
                self.__updateCarouselVehicles(diff.get(GUI_ITEM_TYPE.VEHICLE))
                self.__updateAmmoPanel()
            return

    def onPlayerStateChanged(self, functional, roster, accountInfo):
        if accountInfo.isCurrentPlayer():
            self.__updateState()
            self.__updateAmmoPanel()

    def onUnitPlayerStateChanged(self, pInfo):
        if pInfo.isCurrentPlayer():
            self.__onFunctionalChanged()

    def onPrbFunctionalInited(self):
        self.__onFunctionalChanged()

    def onUnitFunctionalInited(self):
        self.__onFunctionalChanged()

    def onPrbFunctionalFinished(self):
        self.__onFunctionalChanged()

    def onUnitFunctionalFinished(self):
        self.__onFunctionalChanged()

    def onEnqueued(self, queueType, *args):
        self.__onFunctionalChanged()

    def onDequeued(self, queueType, *args):
        self.__onFunctionalChanged()

    def __onVehicleBecomeElite(self, vehTypeCompDescr):
        self.__updateCarouselVehicles([vehTypeCompDescr])

    def onFittingUpdate(self, *args):
        self.__updateCarouselParams()

    def onMoneyUpdate(self, *args):
        self.__updateAmmoPanel()
        self.__updateCarouselParams()

    def __updateAll(self):
        Waiting.show('updateVehicle')
        self.__switchCarousels()
        self.__updateState()
        self.__updateAmmoPanel()
        self.__updateCarouselVehicles()
        self.__updateCarouselParams()
        self.__updateParams()
        self.__updateResearchPanel()
        self.__updateHeader()
        self.__updateCrew()
        Waiting.hide('updateVehicle')

    def __onCurrentVehicleChanged(self):
        Waiting.show('updateVehicle')
        self.__updateState()
        self.__updateAmmoPanel()
        self.__updateParams()
        self.__updateResearchPanel()
        self.__updateHeader()
        self.__updateCrew()
        self.__updateCarouselParams()
        Waiting.hide('updateVehicle')

    def __onIgrTypeChanged(self, *args):
        self.__updateResearchPanel()
        self.__updateHeader()
        self.__updateParams()

    def __updateState(self):
        state = g_currentVehicle.getViewState()
        self.as_setCrewEnabledS(state.isCrewOpsEnabled())
        self.__updateCarouselEnabled()
        if state.isOnlyForEventBattles():
            customizationTooltip = makeTooltip(_ms(TOOLTIPS.HANGAR_TUNING_DISABLEDFOREVENTVEHICLE_HEADER), _ms(TOOLTIPS.HANGAR_TUNING_DISABLEDFOREVENTVEHICLE_BODY))
        else:
            customizationTooltip = makeTooltip(_ms(TOOLTIPS.HANGAR_TUNING_HEADER), _ms(TOOLTIPS.HANGAR_TUNING_BODY))
        self.as_setupAmmunitionPanelS(state.isMaintenanceEnabled(), makeTooltip(_ms(TOOLTIPS.HANGAR_MAINTENANCE_HEADER), _ms(TOOLTIPS.HANGAR_MAINTENANCE_BODY)), state.isCustomizationEnabled(), customizationTooltip)
        self.as_setControlsVisibleS(state.isUIShown())

    def __updateCarouselEnabled(self):
        state = g_currentVehicle.getViewState()
        self.as_setCarouselEnabledS(not state.isLocked())

    def __onFunctionalChanged(self):
        self.__updateState()
        self.__updateAmmoPanel()

    def __onVehicleClientStateChanged(self, vehicles):
        self.__updateCarouselVehicles(vehicles)
        self.__updateAmmoPanel()
