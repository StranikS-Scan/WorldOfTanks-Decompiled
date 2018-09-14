# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/Hangar.py
from CurrentVehicle import g_currentVehicle
from PlayerEvents import g_playerEvents
from constants import IGR_TYPE, QUEUE_TYPE, IS_SHOW_SERVER_STATS
from debug_utils import LOG_DEBUG
from gui.Scaleform.framework.managers.TextManager import TextType
from gui.shared.formatters.time_formatters import getRentLeftTimeStr
from helpers import i18n
from gui.shared.utils.functions import makeTooltip
from gui import game_control, makeHtmlString
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.managers.containers import POP_UP_CRITERIA
from gui.Scaleform.locale.MENU import MENU
from gui.prb_control.prb_helpers import GlobalListener
from gui.prb_control.settings import PREQUEUE_SETTING_NAME
from gui.prb_control.ctrl_events import g_prbCtrlEvents
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.framework import ViewTypes
from gui.Scaleform.Waiting import Waiting
from gui.Scaleform.daapi.view.meta.HangarMeta import HangarMeta
from gui.Scaleform.daapi import LobbySubView
from gui.shared import events, g_itemsCache
from gui.server_events import g_eventsCache
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.ItemsCache import CACHE_SYNC_REASON
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.shared.events import LobbySimpleEvent
from ConnectionManager import connectionManager

class Hangar(LobbySubView, HangarMeta, GlobalListener):

    class COMPONENTS:
        CAROUSEL = 'tankCarousel'
        PARAMS = 'params'
        CREW = 'crew'
        AMMO_PANEL = 'ammunitionPanel'
        RESEARCH_PANEL = 'researchPanel'
        TMEN_XP_PANEL = 'tmenXpPanel'

    def __init__(self, ctx = None):
        LobbySubView.__init__(self, 0)

    def _populate(self):
        LobbySubView._populate(self)
        g_playerEvents.onVehicleBecomeElite += self.__onVehicleBecomeElite
        g_playerEvents.onBattleResultsReceived += self.onFittingUpdate
        g_currentVehicle.onChanged += self.__onCurrentVehicleChanged
        game_control.g_instance.igr.onIgrTypeChanged += self.__onIgrTypeChanged
        game_control.g_instance.serverStats.onStatsReceived += self.__onStatsReceived
        g_prbCtrlEvents.onPreQueueFunctionalChanged += self.onPreQueueFunctionalChanged
        self.startGlobalListening()
        g_itemsCache.onSyncCompleted += self.onCacheResync
        g_eventsCache.onSyncCompleted += self.onEventsCacheResync
        g_clientUpdateManager.addCallbacks({'stats.credits': self.onMoneyUpdate,
         'stats.gold': self.onMoneyUpdate,
         'stats.vehicleSellsLeft': self.onFittingUpdate,
         'stats.slots': self.onFittingUpdate})
        self.__onIgrTypeChanged()
        if IS_SHOW_SERVER_STATS:
            self._updateCurrentServerInfo()
        self.__updateAll()
        self.addListener(LobbySimpleEvent.HIDE_HANGAR, self._onCustomizationShow)

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
            self.fireEvent(LobbySimpleEvent(LobbySimpleEvent.SHOW_HELPLAYOUT), scope=EVENT_BUS_SCOPE.LOBBY)
            self.as_showHelpLayoutS()

    def closeHelpLayout(self):
        self.fireEvent(LobbySimpleEvent(LobbySimpleEvent.CLOSE_HELPLAYOUT), scope=EVENT_BUS_SCOPE.LOBBY)
        self.as_closeHelpLayoutS()

    def toggleGUIEditor(self):
        self.app.toggleEditor()

    def _updateCurrentServerInfo(self):
        if connectionManager.serverUserName and IS_SHOW_SERVER_STATS:
            tooltipBody = i18n.makeString('#tooltips:header/info/players_online_full/body')
            tooltipFullData = makeTooltip('#tooltips:header/info/players_online_full/header', tooltipBody % {'servername': connectionManager.serverUserName})
            self.as_setServerStatsInfoS(tooltipFullData)
        self.__onStatsReceived(game_control.g_instance.serverStats.getStats())

    def _dispose(self):
        self.removeListener(LobbySimpleEvent.HIDE_HANGAR, self._onCustomizationShow)
        g_eventsCache.onSyncCompleted -= self.onEventsCacheResync
        g_itemsCache.onSyncCompleted -= self.onCacheResync
        g_clientUpdateManager.removeObjectCallbacks(self)
        g_prbCtrlEvents.onPreQueueFunctionalChanged -= self.onPreQueueFunctionalChanged
        g_playerEvents.onVehicleBecomeElite -= self.__onVehicleBecomeElite
        g_playerEvents.onBattleResultsReceived -= self.onFittingUpdate
        g_currentVehicle.onChanged -= self.__onCurrentVehicleChanged
        game_control.g_instance.igr.onIgrTypeChanged -= self.__onIgrTypeChanged
        game_control.g_instance.serverStats.onStatsReceived -= self.__onStatsReceived
        self.closeHelpLayout()
        self.stopGlobalListening()
        LobbySubView._dispose(self)

    def __updateAmmoPanel(self):
        if self.ammoPanel:
            self.ammoPanel.update()

    def __clearHistoricalAmmoPanel(self):
        if self.ammoPanel:
            self.ammoPanel.clearHistorical()

    def __updateParams(self):
        if self.paramsPanel:
            self.paramsPanel.update()

    def __clearHistoricalParams(self):
        if self.paramsPanel:
            self.paramsPanel.clearHistorical()

    def __updateCarouselVehicles(self, vehicles = None):
        if self.tankCarousel is not None:
            self.tankCarousel.updateVehicles(vehicles)
        return

    def __updateCarouselParams(self):
        if self.tankCarousel is not None:
            self.tankCarousel.updateParams()
        return

    def __updateResearchPanel(self):
        panel = self.researchPanel
        if panel is not None:
            panel.onCurrentVehicleChanged()
        return

    def __updateCrew(self):
        if self.crewPanel is not None:
            self.crewPanel.updateTankmen()
        return

    @property
    def tankCarousel(self):
        return self.components.get(self.COMPONENTS.CAROUSEL)

    @property
    def ammoPanel(self):
        return self.components.get(self.COMPONENTS.AMMO_PANEL)

    @property
    def paramsPanel(self):
        return self.components.get(self.COMPONENTS.PARAMS)

    @property
    def crewPanel(self):
        return self.components.get(self.COMPONENTS.CREW)

    @property
    def researchPanel(self):
        return self.components.get(self.COMPONENTS.RESEARCH_PANEL)

    def onCacheResync(self, reason, diff):
        if reason == CACHE_SYNC_REASON.SHOP_RESYNC:
            self.__updateAll()
            return
        else:
            if reason in (CACHE_SYNC_REASON.STATS_RESYNC, CACHE_SYNC_REASON.INVENTORY_RESYNC):
                self.__updateCarouselParams()
            if diff is not None and GUI_ITEM_TYPE.VEHICLE in diff:
                self.__updateCarouselVehicles(diff.get(GUI_ITEM_TYPE.VEHICLE))
                self.__updateAmmoPanel()
            return

    def onEventsCacheResync(self):
        if self.preQueueFunctional.getQueueType() == QUEUE_TYPE.HISTORICAL:
            self.tankCarousel.updateVehicles()

    def onPlayerStateChanged(self, functional, roster, accountInfo):
        if accountInfo.isCurrentPlayer():
            self.__updateState()
            self.__updateAmmoPanel()

    def onUnitPlayerStateChanged(self, pInfo):
        if pInfo.isCurrentPlayer():
            self.__updateState()
            self.__updateAmmoPanel()

    def onPrbFunctionalInited(self):
        self.__updateState()
        self.__updateAmmoPanel()

    def onUnitFunctionalInited(self):
        self.__updateState()
        self.__updateAmmoPanel()

    def onPrbFunctionalFinished(self):
        self.__updateState()
        self.__updateAmmoPanel()

    def onUnitFunctionalFinished(self):
        self.__updateState()
        self.__updateAmmoPanel()

    def onPreQueueSettingsChanged(self, diff):
        if PREQUEUE_SETTING_NAME.BATTLE_ID in diff:
            self.tankCarousel.updateVehicles()
        self.__updateAmmoPanel()
        self.__updateParams()

    def onPreQueueFunctionalChanged(self):
        self.tankCarousel.updateVehicles()
        self.__updateAmmoPanel()
        self.__updateParams()

    def onPreQueueFunctionalFinished(self):
        if self.preQueueFunctional.getQueueType() == QUEUE_TYPE.HISTORICAL:
            self.__clearHistoricalAmmoPanel()
            self.__clearHistoricalParams()

    def __onVehicleBecomeElite(self, vehTypeCompDescr):
        self.__updateCarouselVehicles([vehTypeCompDescr])

    def onFittingUpdate(self, *args):
        self.__updateCarouselParams()

    def onMoneyUpdate(self, *args):
        self.__updateAmmoPanel()
        self.__updateCarouselParams()

    def __updateAll(self):
        Waiting.show('updateVehicle')
        self.__updateState()
        self.__updateAmmoPanel()
        self.__updateCarouselVehicles()
        self.__updateCarouselParams()
        self.__updateParams()
        self.__updateResearchPanel()
        self.__updateCrew()
        Waiting.hide('updateVehicle')

    def __onCurrentVehicleChanged(self):
        Waiting.show('updateVehicle')
        self.__updateState()
        self.__updateAmmoPanel()
        self.__updateParams()
        self.__updateResearchPanel()
        self.__updateCrew()
        self.__updateCarouselParams()
        self.__updateVehIGRStatus()
        Waiting.hide('updateVehicle')

    def __onIgrTypeChanged(self, *args):
        type = game_control.g_instance.igr.getRoomType()
        icon = makeHtmlString('html_templates:igr/iconBig', 'premium' if type == IGR_TYPE.PREMIUM else 'basic', {})
        self.as_setIsIGRS(type != IGR_TYPE.NONE, i18n.makeString(MENU.IGR_INFO, igrIcon=icon))
        self.__updateVehIGRStatus()

    def __updateVehIGRStatus(self):
        vehicleIgrTimeLeft = ''
        igrType = game_control.g_instance.igr.getRoomType()
        if g_currentVehicle.isPresent() and g_currentVehicle.isPremiumIGR() and igrType == IGR_TYPE.PREMIUM:
            igrActionIcon = makeHtmlString('html_templates:igr/iconSmall', 'premium', {})
            localization = '#menu:vehicleIgr/%s'
            timeLeft = g_currentVehicle.item.rentLeftTime
            vehicleIgrTimeLeft = getRentLeftTimeStr(localization, timeLeft, timeStyle=TextType.STATS_TEXT, ctx={'igrIcon': igrActionIcon})
        self.as_setVehicleIGRS(vehicleIgrTimeLeft)

    def __updateState(self):
        maintenanceEnabledInRent = True
        customizationEnabledInRent = False
        if g_currentVehicle.isPresent():
            customizationEnabledInRent = not g_currentVehicle.isDisabledInRent()
            if g_currentVehicle.isPremiumIGR():
                vehDoss = g_itemsCache.items.getVehicleDossier(g_currentVehicle.item.intCD)
                battlesCount = 0 if vehDoss is None else vehDoss.getTotalStats().getBattlesCount()
                if battlesCount == 0:
                    customizationEnabledInRent = maintenanceEnabledInRent = not g_currentVehicle.isDisabledInPremIGR() and not g_currentVehicle.isDisabledInRent()
        isVehicleDisabled = False
        if self.prbDispatcher is not None:
            permission = self.prbDispatcher.getGUIPermissions()
            if permission is not None:
                isVehicleDisabled = not permission.canChangeVehicle()
        crewEnabled = not isVehicleDisabled and g_currentVehicle.isInHangar()
        carouselEnabled = not isVehicleDisabled
        maintenanceEnabled = not isVehicleDisabled and g_currentVehicle.isInHangar() and maintenanceEnabledInRent
        customizationEnabled = g_currentVehicle.isInHangar() and not isVehicleDisabled and not g_currentVehicle.isBroken() and customizationEnabledInRent
        self.as_setCrewEnabledS(crewEnabled)
        self.as_setCarouselEnabledS(carouselEnabled)
        self.as_setupAmmunitionPanelS(maintenanceEnabled, customizationEnabled)
        self.as_setControlsVisibleS(g_currentVehicle.isPresent())
        return

    def __onStatsReceived(self, stats):
        if IS_SHOW_SERVER_STATS:
            self.as_setServerStatsS(*game_control.g_instance.serverStats.getFormattedStats())
