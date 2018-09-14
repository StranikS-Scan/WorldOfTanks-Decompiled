# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/historicalBattles/HistoricalBattlesListWindow.py
from collections import defaultdict
import BigWorld
import constants
from AccountCommands import LOCK_REASON
from CurrentVehicle import g_currentVehicle
from debug_utils import LOG_DEBUG
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.prb_control import isInHistoricalQueue
from gui.prb_control.settings import PREQUEUE_SETTING_NAME, SELECTOR_BATTLE_TYPES
from gui.shared.ItemsCache import CACHE_SYNC_REASON
from gui.shared.events import FocusEvent
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.server_events.event_items import HistoricalBattle
from gui.shared.utils.MethodsRules import MethodsRules
from gui.shared.utils.functions import getAbsoluteUrl
from helpers import i18n, time_utils
from gui import makeHtmlString, game_control
from gui.shared import events, g_itemsCache, REQ_CRITERIA
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.server_events import g_eventsCache
from gui.Scaleform.daapi.view.meta.HistoricalBattlesListWindowMeta import HistoricalBattlesListWindowMeta
from gui.Scaleform.locale.HISTORICAL_BATTLES import HISTORICAL_BATTLES
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from messenger.ext import channel_num_gen
from gui.shared.utils import SelectorBattleTypesUtils as selectorUtils

class HistoricalBattlesListWindow(HistoricalBattlesListWindowMeta, MethodsRules):
    COOLDOWN_TRESHOLD = 172800
    COOLDOWN_TICK = 60

    def __init__(self, ctx = None):
        super(HistoricalBattlesListWindow, self).__init__()
        self.selectedBattleID = self.preQueueFunctional.getSetting(PREQUEUE_SETTING_NAME.BATTLE_ID, -1)
        defaultVehicleID = -1
        if g_currentVehicle.isPresent():
            defaultVehicleID = g_currentVehicle.item.intCD
        self.selectedVehicleID = defaultVehicleID
        self.priceIndex, _ = self.preQueueFunctional.getSelectedPrice(self.selectedBattleID, self.selectedVehicleID)
        self.startCooldownCBID = None
        self.cooldownUpdateCBID = None
        selectorUtils.setBattleTypeAsKnown(SELECTOR_BATTLE_TYPES.HISTORICAL)
        return

    def requestToEnqueue(self):
        self.preQueueFunctional.doAction()

    def onWindowClose(self):
        self.preQueueFunctional.doLeaveAction(self.prbDispatcher)

    def getClientID(self):
        return channel_num_gen.getClientID4PreQueue(constants.QUEUE_TYPE.HISTORICAL)

    def onFocusIn(self, alias):
        self.fireEvent(FocusEvent(FocusEvent.COMPONENT_FOCUSED, {'clientID': self.getClientID()}))

    def startListening(self):
        super(HistoricalBattlesListWindow, self).startListening()
        self.addListener(events.HideWindowEvent.HIDE_HISTORICAL_BATTLES_WINDOW, self.__handleWindowHide, scope=EVENT_BUS_SCOPE.LOBBY)

    def stopListening(self):
        self.removeListener(events.HideWindowEvent.HIDE_HISTORICAL_BATTLES_WINDOW, self.__handleWindowHide, scope=EVENT_BUS_SCOPE.LOBBY)
        super(HistoricalBattlesListWindow, self).stopListening()

    def _populate(self):
        super(HistoricalBattlesListWindow, self)._populate()
        g_clientUpdateManager.addCallbacks({'stats.credits': self.onMoneyChanged,
         'stats.gold': self.onMoneyChanged})
        g_itemsCache.onSyncCompleted += self.onCacheResync
        g_eventsCache.onSyncCompleted += self.onEventsCacheResync
        self.updateCarouselData()
        self.as_selectBattleS(self.selectedBattleID)
        if isInHistoricalQueue():
            self.as_setCarouselEnabledS(False)
            self.as_setListEnabledS(False)
            self.as_setPriceDDEnabledS(False)
            self.as_setCloseBtnEnabledS(False)

    def _dispose(self):
        g_eventsCache.onSyncCompleted -= self.onEventsCacheResync
        g_itemsCache.onSyncCompleted -= self.onCacheResync
        g_clientUpdateManager.removeObjectCallbacks(self)
        self._clearCallbacks()
        super(HistoricalBattlesListWindow, self)._dispose()

    def _clearCallbacks(self):
        if self.startCooldownCBID is not None:
            BigWorld.cancelCallback(self.startCooldownCBID)
            self.startCooldownCBID = None
        if self.cooldownUpdateCBID is not None:
            BigWorld.cancelCallback(self.cooldownUpdateCBID)
            self.cooldownUpdateCBID = None
        return

    def __handleWindowHide(self, _):
        self.destroy()

    def onMoneyChanged(self, *args):
        self.updateStatusMessage()
        self.updatePriceStatus()
        self.updatePriceBlock()
        self.updateFightButton()

    def onCacheResync(self, reason, diff):
        if reason == CACHE_SYNC_REASON.SHOP_RESYNC:
            self.updatePriceStatus()
            self.updatePriceBlock()
            self.updateFightButton()
            return
        else:
            if diff is not None and GUI_ITEM_TYPE.VEHICLE in diff:
                self.updateVehiclesList()
                self.updateStatusMessage()
                self.updatePriceBlock()
                self.updatePriceStatus()
                self.updateFightButton()
            return

    def onEventsCacheResync(self, *args):
        self.updateCarouselData()

    def onEnqueued(self):
        self.destroy()

    def onDequeued(self):
        self.as_setCarouselEnabledS(True)
        self.as_setListEnabledS(True)
        self.as_setPriceDDEnabledS(True)
        self.as_setCloseBtnEnabledS(True)
        self.updateFightButton()

    def showFullDescription(self):
        battle = g_eventsCache.getHistoricalBattles().get(self.selectedBattleID)
        game_control.g_instance.browser.load(battle.getDescriptionUrl(), battle.getUserName(), False)

    def onBattleSelected(self, battleID):
        self.selectedBattleID = int(battleID)
        self.preQueueFunctional.changeSetting(PREQUEUE_SETTING_NAME.BATTLE_ID, self.selectedBattleID)
        self.updateBattleInfo()
        self.updateVehiclesList()
        if self.selectedVehicleID != -1:
            self.as_selectVehicleS(self.selectedVehicleID)
            self.priceIndex, _ = self.preQueueFunctional.getSelectedPrice(self.selectedBattleID, self.selectedVehicleID)
        self.updateStatusMessage()
        self.updatePriceStatus()
        self.updatePriceBlock()
        self.updateFightButton()

    def onVehicleSelected(self, vehicleID, setSelection = False):
        self.selectedVehicleID = int(vehicleID)
        self.priceIndex, _ = self.preQueueFunctional.getSelectedPrice(self.selectedBattleID, self.selectedVehicleID)
        self.preQueueFunctional.changeSetting(PREQUEUE_SETTING_NAME.SELECTED_VEHICLE_ID, self.selectedVehicleID)
        self.updateStatusMessage()
        self.updatePriceBlock()
        self.updatePriceStatus()
        self.updateFightButton()
        if self.selectedVehicleID != -1:
            vehicle = g_itemsCache.items.getItemByCD(self.selectedVehicleID)
            if vehicle.invID != g_currentVehicle.invID:
                self.skipListenerNotification(self._handleCurrentVehicleChanged)
                g_currentVehicle.selectVehicle(vehicle.invID)

    def onPriceSelected(self, priceIndex):
        battle = g_eventsCache.getHistoricalBattles().get(self.selectedBattleID)
        if battle.canParticipateWith(self.selectedVehicleID):
            self.priceIndex = int(priceIndex)
            price = battle.getShellsLayoutPrice(self.selectedVehicleID)
            isCreditsAmmo = price[self.priceIndex][1] == 0
            storedSetting = self.preQueueFunctional.getSetting(PREQUEUE_SETTING_NAME.PRICE_INDEX, defaultdict(dict))
            storedSetting[self.selectedBattleID][self.selectedVehicleID] = (self.priceIndex, isCreditsAmmo)
            self.preQueueFunctional.changeSetting(PREQUEUE_SETTING_NAME.PRICE_INDEX, storedSetting)
            self.updatePriceStatus()
            self.updateFightButton()

    def updateCarouselData(self):
        LOG_DEBUG('Historical battles list updated.')
        items = []
        for battle in sorted(g_eventsCache.getHistoricalBattles().itervalues()):
            items.append({'id': battle.getID(),
             'name': battle.getUserName(),
             'image': battle.getIcon(),
             'tooltipHeader': battle.getUserName(),
             'tooltipDescription': battle.getDescription(),
             'isFuture': battle.isFuture()})

        if items:
            self.as_setCarouselDataS(items)

    def updateBattleInfo(self):
        battle = g_eventsCache.getHistoricalBattles().get(self.selectedBattleID)
        self.as_setBattleDataS({'id': self.selectedBattleID,
         'name': battle.getUserName(),
         'isFuture': battle.isFuture(),
         'datesInfo': battle.getDatesInfo(),
         'descriptionText': battle.getLongDescription(),
         'mapName': battle.getMapName(),
         'mapImage': battle.getMapIcon(),
         'mapInfo': battle.getMapInfo(),
         'arenaID': battle.getArenaTypeID(),
         'descriptionURL': battle.getDescriptionUrl(),
         'sideA': battle.getSideUserName(HistoricalBattle.SIDES.A),
         'sideB': battle.getSideUserName(HistoricalBattle.SIDES.B)})
        self.initBattleTimer()

    def initBattleTimer(self):
        battle = g_eventsCache.getHistoricalBattles().get(self.selectedBattleID)
        if battle.isFuture():
            date = battle.getStartDate()
            timeRemaining = battle.getStartTimeLeft()
            ttHeader = i18n.makeString(TOOLTIPS.HISTORICALBATTLES_DATESTATUS_STARTDATE)
            ttBody = i18n.makeString(TOOLTIPS.HISTORICALBATTLES_DATESTATUS_FUTURE, date=date)
        else:
            date = battle.getFinishDate()
            timeRemaining = battle.getFinishTimeLeft()
            ttHeader = i18n.makeString(TOOLTIPS.HISTORICALBATTLES_DATESTATUS_ENDDATE)
            ttBody = i18n.makeString(TOOLTIPS.HISTORICALBATTLES_DATESTATUS_ACTIVE, date=date)
        dateString = makeHtmlString('html_templates:lobby/historicalBattles', 'dateLabel', {'icon': getAbsoluteUrl(RES_ICONS.MAPS_ICONS_BUTTONS_CALENDAR),
         'text': date})
        self.as_setDateS(dateString, ttHeader, ttBody)
        self._clearCallbacks()
        if not battle.isFuture() and timeRemaining > self.COOLDOWN_TRESHOLD:
            self.updateRemainimgTime()
            self.startCooldownCBID = BigWorld.callback(timeRemaining + 1 - self.COOLDOWN_TRESHOLD, self.updateCooldown)
        else:
            self.updateCooldown()

    def updateRemainimgTime(self):
        battle = g_eventsCache.getHistoricalBattles().get(self.selectedBattleID)
        if battle.isFuture():
            timeRemaining = battle.getStartTimeLeft()
        else:
            timeRemaining = battle.getFinishTimeLeft()
        headerTimerText = ''
        footerTimerText = ''
        if battle.isFuture() or timeRemaining <= self.COOLDOWN_TRESHOLD:
            remainingText = time_utils.getTillTimeString(timeRemaining, MENU.TIME_TIMEVALUE)
            headerTimerText = i18n.makeString(HISTORICAL_BATTLES.TIMER_TOSTART if battle.isFuture() else HISTORICAL_BATTLES.TIMER_TOFINISH, time=remainingText)
            footerTimerText = i18n.makeString(HISTORICAL_BATTLES.BATTLESTATUS_REMAININGTIME, time=remainingText)
        self.as_updateTimerS(headerTimerText, footerTimerText)

    def updateCooldown(self):
        if self.startCooldownCBID is not None:
            self.startCooldownCBID = None
        self.updateRemainimgTime()
        self.cooldownUpdateCBID = BigWorld.callback(self.COOLDOWN_TICK, self.updateCooldown)
        return

    def updateVehiclesList(self):
        battle = g_eventsCache.getHistoricalBattles().get(self.selectedBattleID)
        teamARoster = battle.getTeamRoster(HistoricalBattle.SIDES.A)
        teamBRoster = battle.getTeamRoster(HistoricalBattle.SIDES.B)
        teamAVehicles = g_itemsCache.items.getVehicles(REQ_CRITERIA.IN_CD_LIST(teamARoster)).itervalues()
        teamBVehicles = g_itemsCache.items.getVehicles(REQ_CRITERIA.IN_CD_LIST(teamBRoster)).itervalues()

        def sortFunction(a, b):
            if a.isInInventory and not b.isInInventory:
                return -1
            if not a.isInInventory and b.isInInventory:
                return 1
            if a.isReadyToFight and not b.isReadyToFight:
                return -1
            if not a.isReadyToFight and b.isReadyToFight:
                return 1
            return 0

        teamAVehicles = sorted(teamAVehicles, sortFunction)
        teamBVehicles = sorted(teamBVehicles, sortFunction)
        teamAData = map(self._makeVehicleListItemVO, teamAVehicles)
        teamBData = map(self._makeVehicleListItemVO, teamBVehicles)
        self.as_setTeamsDataS(teamAData, teamBData)

    def updateStatusMessage(self):
        battle = g_eventsCache.getHistoricalBattles().get(self.selectedBattleID)
        message = ''
        templateName = 'notValid'
        if battle.isFuture():
            templateName = 'notReady'
            message = ''
        elif self.selectedVehicleID == -1:
            templateName = 'notSelected'
            message = i18n.makeString(HISTORICAL_BATTLES.TANKSTATUS_NOTSELECTED)
        elif not battle.canParticipateWith(self.selectedVehicleID):
            message = i18n.makeString(HISTORICAL_BATTLES.TANKSTATUS_NOTVALID)
        else:
            vehicle = g_itemsCache.items.getItemByCD(self.selectedVehicleID)
            if vehicle.isReadyToFight or vehicle.lock == LOCK_REASON.IN_QUEUE:
                templateName = 'ready'
                message = i18n.makeString(HISTORICAL_BATTLES.TANKSTATUS_READY, tankName=vehicle.userName)
            else:
                templateName = 'notReady'
                if not vehicle.isCrewFull:
                    message = i18n.makeString(HISTORICAL_BATTLES.TANKSTATUS_NOTREADY_CREW, tankName=vehicle.userName)
                elif vehicle.isInBattle:
                    message = i18n.makeString(HISTORICAL_BATTLES.TANKSTATUS_NOTREADY_INBATTLE, tankName=vehicle.userName)
                elif vehicle.isBroken:
                    message = i18n.makeString(HISTORICAL_BATTLES.TANKSTATUS_NOTREADY_BROKEN, tankName=vehicle.userName)
        status = makeHtmlString('html_templates:lobby/historicalBattles/tankStatus', templateName, {'message': message})
        self.as_setStatusMessageS(status)

    def updatePriceBlock(self):
        battle = g_eventsCache.getHistoricalBattles().get(self.selectedBattleID)
        if self.selectedVehicleID == -1 or not battle.canParticipateWith(self.selectedVehicleID):
            params = {'value': 0,
             'color': self.app.colorManager.getColorScheme('textColorError').get('rgb'),
             'icon': getAbsoluteUrl(RES_ICONS.MAPS_ICONS_LIBRARY_CREDITSICON_2)}
            data = (makeHtmlString('html_templates:lobby/historicalBattles/ammoStatus', 'priceLabel', params),)
            selected = 0
        else:
            data = battle.getShellsLayoutFormatedPrice(self.selectedVehicleID, self.app.colorManager)
            price = battle.getShellsLayoutPrice(self.selectedVehicleID)
            selected = self._getSelectedPriceIndex(price)
        self.as_setPricesS(data, selected)

    def updatePriceStatus(self):
        battle = g_eventsCache.getHistoricalBattles().get(self.selectedBattleID)
        message = ''
        templateName = 'notValid'
        if self.selectedVehicleID == -1:
            message = i18n.makeString(HISTORICAL_BATTLES.AMMOSTATUS_VEHICLENOTSELECTED)
        elif not battle.canParticipateWith(self.selectedVehicleID):
            message = i18n.makeString(HISTORICAL_BATTLES.AMMOSTATUS_VEHICLENOTVALID)
        else:
            vehicle = g_itemsCache.items.getItemByCD(self.selectedVehicleID)
            price = battle.getShellsLayoutPrice(self.selectedVehicleID)
            selected = self._getSelectedPriceIndex(price)
            enoughGold, enoughCredits = battle.getShellsLayoutPriceStatus(self.selectedVehicleID)[selected]
            if enoughGold and enoughCredits:
                templateName = 'valid'
                message = i18n.makeString(HISTORICAL_BATTLES.AMMOSTATUS_NORMAL, tankName=vehicle.userName)
            else:
                message = i18n.makeString(HISTORICAL_BATTLES.AMMOSTATUS_NOTENOUGH, tankName=vehicle.userName)
        status = makeHtmlString('html_templates:lobby/historicalBattles/ammoStatus', templateName, {'message': message})
        self.as_setPriceInfoS(status)

    def updateFightButton(self):
        battle = g_eventsCache.getHistoricalBattles().get(self.selectedBattleID)
        enabled = False
        tooltip = ''
        if battle.isFuture():
            tooltip = i18n.makeString(TOOLTIPS.HISTORICALBATTLES_FIGHTBUTTON_DISABLED_FUTURE)
        elif self.selectedVehicleID == -1 or not battle.canParticipateWith(self.selectedVehicleID):
            tooltip = i18n.makeString(TOOLTIPS.HISTORICALBATTLES_FIGHTBUTTON_DISABLED_NOVEHICLE)
        else:
            vehicle = g_itemsCache.items.getItemByCD(self.selectedVehicleID)
            price = battle.getShellsLayoutPrice(self.selectedVehicleID)
            selected = self._getSelectedPriceIndex(price)
            enoughGold, enoughCredits = battle.getShellsLayoutPriceStatus(self.selectedVehicleID)[selected]
            if vehicle.isReadyToFight:
                if enoughGold and enoughCredits:
                    tooltip = i18n.makeString(TOOLTIPS.HISTORICALBATTLES_FIGHTBUTTON_ENABLED_DESCRIPTION)
                    enabled = True
                else:
                    tooltip = i18n.makeString(TOOLTIPS.HISTORICALBATTLES_FIGHTBUTTON_DISABLED_MONEY)
            elif not vehicle.isCrewFull:
                tooltip = i18n.makeString(TOOLTIPS.HISTORICALBATTLES_FIGHTBUTTON_DISABLED_CREW)
            elif vehicle.isInBattle:
                tooltip = i18n.makeString(TOOLTIPS.HISTORICALBATTLES_FIGHTBUTTON_DISABLED_INBATTLE)
            elif vehicle.isBroken:
                tooltip = i18n.makeString(TOOLTIPS.HISTORICALBATTLES_FIGHTBUTTON_DISABLED_BROKEN)
        if enabled:
            tooltipHeader = i18n.makeString(TOOLTIPS.HISTORICALBATTLES_FIGHTBUTTON_ENABLED)
        else:
            tooltipHeader = i18n.makeString(TOOLTIPS.HISTORICALBATTLES_FIGHTBUTTON_DISABLED)
        self.as_updateFightButtonS(enabled, tooltipHeader, tooltip, False)

    def _makeVehicleListItemVO(self, vehicle):
        enabled = vehicle.invID != -1
        warnTTHeader = ''
        warnTTBody = ''
        if enabled:
            if vehicle.isReadyToFight or vehicle.lock == LOCK_REASON.IN_QUEUE:
                showWarning = False
            else:
                warnTTHeader = i18n.makeString(TOOLTIPS.HISTORICALBATTLES_VEHICLE_NOTREADY_HEADER)
                if not vehicle.isCrewFull:
                    warnTTBody = i18n.makeString(TOOLTIPS.HISTORICALBATTLES_VEHICLE_NOTREADY_CREW)
                elif vehicle.isInBattle:
                    warnTTBody = i18n.makeString(TOOLTIPS.HISTORICALBATTLES_VEHICLE_NOTREADY_INBATTLE)
                elif vehicle.isBroken:
                    warnTTBody = i18n.makeString(TOOLTIPS.HISTORICALBATTLES_VEHICLE_NOTREADY_BROKEN)
                showWarning = True
        else:
            showWarning = False
        item = {'intCD': vehicle.intCD,
         'invID': vehicle.invID,
         'name': vehicle.shortUserName,
         'image': '../maps/icons/vehicle/small/{0}.png'.format(vehicle.name.replace(':', '-')),
         'enabled': enabled,
         'showWarning': showWarning,
         'warnTTHeader': warnTTHeader,
         'warnTTBody': warnTTBody}
        return item

    @MethodsRules.skipable
    def _handleCurrentVehicleChanged(self):
        if g_currentVehicle.isPresent():
            self.as_selectVehicleS(g_currentVehicle.item.intCD)
        else:
            self.as_selectVehicleS(-1)

    def _getSelectedPriceIndex(self, prices):
        if self.priceIndex is not None:
            return self.priceIndex
        else:
            return len(prices) - 1
