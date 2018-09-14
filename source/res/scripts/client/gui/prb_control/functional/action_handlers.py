# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/functional/action_handlers.py
import weakref
from CurrentVehicle import g_currentVehicle
from PlayerEvents import g_playerEvents
from UnitBase import ROSTER_TYPE
from constants import PREBATTLE_TYPE, MAX_VEHICLE_LEVEL, MIN_VEHICLE_LEVEL
from debug_utils import LOG_DEBUG
from gui import DialogsInterface, SystemMessages
from gui.Scaleform.daapi.view.dialogs import I18nConfirmDialogMeta, rally_dialog_meta
from gui.prb_control.context import unit_ctx, SendInvitesCtx
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.formatters import messages
from gui.prb_control.functional.decorators import vehicleAmmoCheck
from gui.prb_control.settings import REQUEST_TYPE, FUNCTIONAL_FLAG
from gui.server_events import g_eventsCache
from messenger.storage import storage_getter
from gui.shared.utils.functions import showSentInviteMessage

class AbstractActionsHandler(object):

    def __init__(self, functional):
        self._functional = weakref.proxy(functional)

    def setPlayerInfoChanged(self, data=None):
        pass

    def setUsersChanged(self, data=None):
        pass

    def setUnitChanged(self, data=None):
        pass

    def executeInit(self, ctx):
        return FUNCTIONAL_FLAG.UNDEFINED

    def execute(self, customData):
        pass

    def clear(self):
        self._functional = None
        return

    def exitFromQueue(self):
        pass

    def _sendBattleQueueRequest(self, vInvID=0):
        ctx = unit_ctx.BattleQueueUnitCtx('prebattle/battle_queue')
        ctx.selectVehInvID = vInvID
        LOG_DEBUG('Unit request', ctx)
        self._functional.doBattleQueue(ctx)


class CommonUnitActionsHandler(AbstractActionsHandler):

    def __init__(self, functional):
        super(CommonUnitActionsHandler, self).__init__(functional)
        g_playerEvents.onKickedFromUnitsQueue += self.__onKickedFromQueue

    def setUnitChanged(self, data=None):
        flags = self._functional.getFlags()
        pInfo = self._functional.getPlayerInfo()
        if flags.isChanged() and pInfo.isInSlot:
            prbType = self._functional.getEntityType()
            if flags.isPreArenaChanged():
                if flags.isInPreArena():
                    g_eventDispatcher.loadPreArenaUnitFromUnit(prbType)
                else:
                    g_eventDispatcher.loadUnitFromPreArenaUnit(prbType)

    def executeInit(self, ctx):
        prbType = self._functional.getEntityType()
        pInfo = self._functional.getPlayerInfo()
        flags = self._functional.getFlags()
        if flags.isInPreArena() and pInfo.isInSlot:
            g_eventDispatcher.loadPreArenaUnit(prbType)
            return FUNCTIONAL_FLAG.LOAD_PAGE
        g_eventDispatcher.loadUnit(prbType)
        if flags.isInIdle():
            g_eventDispatcher.setUnitProgressInCarousel(prbType, True)
        return FUNCTIONAL_FLAG.LOAD_WINDOW

    @vehicleAmmoCheck
    def execute(self, customData):
        pInfo = self._functional.getPlayerInfo()
        if pInfo.isCreator():
            stats = self._functional.getStats()
            _, unit = self._functional.getUnit()
            if not unit.isRated() and stats.freeSlotsCount > self._functional.getRosterSettings().getMaxEmptySlots():
                if self._functional.isParentControlActivated():
                    return
                if self._functional.getFlags().isDevMode():
                    DialogsInterface.showDialog(rally_dialog_meta.UnitConfirmDialogMeta(PREBATTLE_TYPE.UNIT, 'startBattle'), lambda result: self._functional.doBattleQueue(unit_ctx.BattleQueueUnitCtx('prebattle/battle_queue')) if result else None)
                else:
                    ctx = unit_ctx.AutoSearchUnitCtx('prebattle/auto_search')
                    LOG_DEBUG('Unit request', ctx)
                    self._functional.doAutoSearch(ctx)
            else:
                self._sendBattleQueueRequest()
        else:
            self._functional.togglePlayerReadyAction()

    def clear(self):
        g_playerEvents.onKickedFromUnitsQueue -= self.__onKickedFromQueue
        super(CommonUnitActionsHandler, self).clear()

    def __onKickedFromQueue(self, *args):
        SystemMessages.pushMessage(messages.getKickReasonMessage('timeout'), type=SystemMessages.SM_TYPE.Warning)


class SquadActionsHandler(AbstractActionsHandler):

    def __init__(self, functional):
        super(SquadActionsHandler, self).__init__(functional)
        g_playerEvents.onKickedFromRandomQueue += self.__onKickedFromQueue

    @storage_getter('users')
    def usersStorage(self):
        return None

    def setUnitChanged(self, flags):
        if flags.isInQueueChanged():
            if self._functional.getPlayerInfo().isReady and flags.isInQueue():
                g_eventDispatcher.loadBattleQueue()
            else:
                g_eventDispatcher.loadHangar()

    def setPlayerInfoChanged(self, data=None):
        g_eventDispatcher.updateUI()

    def setUsersChanged(self, data=None):
        g_eventDispatcher.setSquadTeamReadyInCarousel(self._functional.getEntityType(), isTeamReady=self._getTeamReady())

    def executeInit(self, ctx):
        initResult = FUNCTIONAL_FLAG.UNDEFINED
        if self._functional.getPlayerInfo().isReady and self._functional.getFlags().isInQueue():
            g_eventDispatcher.loadBattleQueue()
            initResult = FUNCTIONAL_FLAG.LOAD_PAGE
        squadCtx = None
        if ctx is not None:
            isCreationCtx = ctx.getRequestType() is REQUEST_TYPE.CREATE
            if isCreationCtx:
                accountsToInvite = ctx.getAccountsToInvite()
                showInvitesWindow = True
                if accountsToInvite:
                    showInvitesWindow = False
                    self._functional.request(SendInvitesCtx(accountsToInvite, ''))
                    self._showInviteSentMessage(accountsToInvite)
                squadCtx = {'showInvitesWindow': showInvitesWindow}
        self._loadWindow(squadCtx)
        return initResult

    @vehicleAmmoCheck
    def execute(self, customData):
        if self._functional.isCreator():
            func = self._functional
            fullData = func.getUnitFullData(unitIdx=self._functional.getUnitIdx())
            if fullData is None:
                return {}
            _, _, unitStats, pInfo, slotsIter = fullData
            notReadyCount = 0
            for slot in slotsIter:
                slotPlayer = slot.player
                if slotPlayer:
                    if slotPlayer.isInArena() or slotPlayer.isInPreArena() or pInfo.isInSearch() or pInfo.isInQueue():
                        DialogsInterface.showI18nInfoDialog('squadHavePlayersInBattle', lambda result: None)
                        return True
                    if not slotPlayer.isReady:
                        notReadyCount += 1

            if not pInfo.isReady:
                notReadyCount -= 1
            if unitStats.occupiedSlotsCount == 1:
                DialogsInterface.showDialog(I18nConfirmDialogMeta('squadHaveNoPlayers'), self._setCreatorReady)
                return True
            if notReadyCount > 0:
                if notReadyCount == 1:
                    DialogsInterface.showDialog(I18nConfirmDialogMeta('squadHaveNotReadyPlayer'), self._setCreatorReady)
                    return True
                DialogsInterface.showDialog(I18nConfirmDialogMeta('squadHaveNotReadyPlayers'), self._setCreatorReady)
                return True
            self._setCreatorReady(True)
        else:
            self._functional.togglePlayerReadyAction(True)
        return True

    def exitFromQueue(self):
        self._functional.doBattleQueue(unit_ctx.BattleQueueUnitCtx('prebattle/battle_queue', action=0))

    def clear(self):
        g_playerEvents.onKickedFromRandomQueue -= self.__onKickedFromQueue
        super(SquadActionsHandler, self).clear()

    def _loadWindow(self, ctx):
        g_eventDispatcher.loadSquad(ctx, self._getTeamReady())

    def _setCreatorReady(self, result):
        if not result:
            return
        self._sendBattleQueueRequest(g_currentVehicle.item.invID if not self._functional.getPlayerInfo().isReady else 0)

    def _getTeamReady(self):
        for slot in self._functional.getSlotsIterator(*self._functional.getUnit(unitIdx=self._functional.getUnitIdx())):
            if slot.player and not slot.player.isReady:
                return False

        return True

    def _showInviteSentMessage(self, accountsToInvite):
        getUser = self.usersStorage.getUser
        for dbID in accountsToInvite:
            user = getUser(dbID)
            showSentInviteMessage(user)

    def __onKickedFromQueue(self, *args):
        SystemMessages.pushMessage(messages.getKickReasonMessage('timeout'), type=SystemMessages.SM_TYPE.Warning)


class EventSquadActionsHandler(SquadActionsHandler):

    def _loadWindow(self, ctx):
        g_eventDispatcher.loadEventSquad(ctx, self._getTeamReady())
        if not self._functional.getPlayerInfo().isReady:
            eventVehicle = g_eventsCache.getEventVehicles()[0]
            g_currentVehicle.selectVehicle(eventVehicle.invID)


class BalancedSquadActionsHandler(SquadActionsHandler):

    def execute(self, customData):
        if self._functional.isCreator():
            func = self._functional
            fullData = func.getUnitFullData(unitIdx=self._functional.getUnitIdx())
            if fullData is None:
                return {}
            _, _, unitStats, pInfo, slotsIter = fullData
            notReadyCount = 0
            for slot in slotsIter:
                slotPlayer = slot.player
                if slotPlayer:
                    if slotPlayer.isInArena() or slotPlayer.isInPreArena() or pInfo.isInSearch() or pInfo.isInQueue():
                        DialogsInterface.showI18nInfoDialog('squadHavePlayersInBattle', lambda result: None)
                        return True
                    if not slotPlayer.isReady:
                        notReadyCount += 1

            if not pInfo.isReady:
                notReadyCount -= 1
            if unitStats.occupiedSlotsCount == 1:
                DialogsInterface.showDialog(I18nConfirmDialogMeta('squadHaveNoPlayers'), self._setCreatorReady)
                return True
            if notReadyCount > 0:
                if notReadyCount == 1:
                    DialogsInterface.showDialog(I18nConfirmDialogMeta('squadHaveNotReadyPlayer'), self._setCreatorReady)
                    return True
                DialogsInterface.showDialog(I18nConfirmDialogMeta('squadHaveNotReadyPlayers'), self._setCreatorReady)
                return True
            if not g_currentVehicle.isLocked():
                _, unit = self._functional.getUnit()
                playerVehicles = unit.getVehicles()
                if playerVehicles:
                    commanderLevel = g_currentVehicle.item.level
                    lowerBound, upperBound = self._functional.getSquadLevelBounds()
                    minLevel = max(MIN_VEHICLE_LEVEL, commanderLevel + lowerBound)
                    maxLevel = min(MAX_VEHICLE_LEVEL, commanderLevel + upperBound)
                    levelRange = range(minLevel, maxLevel + 1)
                    for _, unitVehicles in playerVehicles.iteritems():
                        for vehicle in unitVehicles:
                            if vehicle.vehLevel not in levelRange:
                                DialogsInterface.showDialog(I18nConfirmDialogMeta('squadHaveNoPlayers'), self._setCreatorReady)
                                return True

            self._setCreatorReady(True)
        else:
            self._functional.togglePlayerReadyAction(True)
        return True


class FalloutSquadActionsHandler(SquadActionsHandler):

    def clear(self):
        g_eventDispatcher.unloadFallout()
        super(FalloutSquadActionsHandler, self).clear()

    def execute(self, customData):
        if self._functional.isCreator():
            func = self._functional
            fullData = func.getUnitFullData(unitIdx=self._functional.getUnitIdx())
            if fullData is None:
                return {}
            _, _, unitStats, pInfo, slotsIter = fullData
            isAutoFill = func.getRosterType() == ROSTER_TYPE.FALLOUT_MULTITEAM_ROSTER
            notReadyCount = 0
            for slot in slotsIter:
                slotPlayer = slot.player
                if slotPlayer:
                    if slotPlayer.isInArena() or slotPlayer.isInPreArena() or pInfo.isInSearch() or pInfo.isInQueue():
                        DialogsInterface.showI18nInfoDialog('squadHavePlayersInBattle', lambda result: None)
                        return True
                    if not slotPlayer.isReady:
                        notReadyCount += 1

            if not pInfo.isReady:
                notReadyCount -= 1
            if isAutoFill:
                if notReadyCount == 1:
                    DialogsInterface.showDialog(I18nConfirmDialogMeta('squadHaveNotReadyPlayerAuto'), self._setCreatorReady)
                    return True
                if unitStats.freeSlotsCount == 1:
                    DialogsInterface.showDialog(I18nConfirmDialogMeta('squadHaveNoPlayerAuto'), self._setCreatorReady)
                    return True
            else:
                if unitStats.occupiedSlotsCount == 1:
                    DialogsInterface.showDialog(I18nConfirmDialogMeta('squadHaveNoPlayers'), self._setCreatorReady)
                    return True
                if notReadyCount > 0:
                    if notReadyCount == 1:
                        DialogsInterface.showDialog(I18nConfirmDialogMeta('squadHaveNotReadyPlayer'), self._setCreatorReady)
                        return True
                    DialogsInterface.showDialog(I18nConfirmDialogMeta('squadHaveNotReadyPlayers'), self._setCreatorReady)
                    return True
            self._setCreatorReady(True)
        else:
            self._functional.togglePlayerReadyAction()
        return True

    def _loadWindow(self, ctx):
        g_eventDispatcher.loadFalloutSquad(ctx, self._getTeamReady())

    def _setCreatorReady(self, result):
        if not result:
            return
        self._sendBattleQueueRequest()
