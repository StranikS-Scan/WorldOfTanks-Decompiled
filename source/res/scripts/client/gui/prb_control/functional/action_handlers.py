# Embedded file name: scripts/client/gui/prb_control/functional/action_handlers.py
import weakref
from CurrentVehicle import g_currentVehicle
from constants import PREBATTLE_TYPE
from debug_utils import LOG_DEBUG
from gui import DialogsInterface
from gui.Scaleform.daapi.view.dialogs import I18nConfirmDialogMeta, rally_dialog_meta
from gui.prb_control.context import unit_ctx, SendInvitesCtx
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.settings import REQUEST_TYPE, FUNCTIONAL_INIT_RESULT

class AbstractActionsHandler(object):

    def __init__(self, functional):
        self._functional = weakref.proxy(functional)

    def setPlayerInfoChanged(self, data = None):
        pass

    def setUsersChanged(self, data = None):
        pass

    def setUnitChanged(self, data = None):
        pass

    def executeInit(self, ctx):
        return FUNCTIONAL_INIT_RESULT.UNDEFINED

    def execute(self, customData):
        pass

    def clear(self):
        self._functional = None
        return

    def exitFromQueue(self):
        pass

    def _sendBattleQueueRequest(self, vInvID = 0):
        ctx = unit_ctx.BattleQueueUnitCtx('prebattle/battle_queue')
        ctx.selectVehInvID = vInvID
        LOG_DEBUG('Unit request', ctx)
        self._functional.doBattleQueue(ctx)


class CommonUnitActionsHandler(AbstractActionsHandler):

    def setUnitChanged(self, data = None):
        flags = self._functional.getFlags()
        pInfo = self._functional.getPlayerInfo()
        if flags.isChanged() and pInfo.isInSlot:
            prb_type = self._functional.getPrbType()
            if flags.isPreArenaChanged():
                if flags.isInPreArena():
                    g_eventDispatcher.loadPreArenaUnitFromUnit(prb_type)
                else:
                    g_eventDispatcher.loadUnitFromPreArenaUnit(prb_type)

    def executeInit(self, ctx):
        prb_type = self._functional.getPrbType()
        pInfo = self._functional.getPlayerInfo()
        flags = self._functional.getFlags()
        if flags.isInPreArena() and pInfo.isInSlot:
            g_eventDispatcher.loadPreArenaUnit(prb_type)
            return FUNCTIONAL_INIT_RESULT.LOAD_PAGE
        g_eventDispatcher.loadUnit(prb_type)
        if flags.isInIdle():
            g_eventDispatcher.setUnitProgressInCarousel(prb_type, True)
        return FUNCTIONAL_INIT_RESULT.LOAD_WINDOW

    def execute(self, customData):
        pInfo = self._functional.getPlayerInfo()
        if pInfo.isCreator():
            stats = self._functional.getStats()
            _, unit = self._functional.getUnit()
            if not unit.isRated() and stats.freeSlotsCount > self._functional.getRosterSettings().getMaxEmptySlots():
                if self._functional.isParentControlActivated():
                    return
                if self._functional.getFlags().isDevMode():
                    DialogsInterface.showDialog(rally_dialog_meta.UnitConfirmDialogMeta(PREBATTLE_TYPE.UNIT, 'startBattle'), lambda result: (self._functional.doBattleQueue(unit_ctx.BattleQueueUnitCtx('prebattle/battle_queue')) if result else None))
                else:
                    ctx = unit_ctx.AutoSearchUnitCtx('prebattle/auto_search')
                    LOG_DEBUG('Unit request', ctx)
                    self._functional.doAutoSearch(ctx)
            else:
                self._sendBattleQueueRequest()
        else:
            self._functional.togglePlayerReadyAction()


class SquadActionsHandler(AbstractActionsHandler):

    def setUnitChanged(self, flags):
        if flags.isInQueueChanged():
            if self._functional.getPlayerInfo().isReady and flags.isInQueue():
                g_eventDispatcher.loadBattleQueue()
            else:
                g_eventDispatcher.loadHangar()

    def setPlayerInfoChanged(self, data = None):
        g_eventDispatcher.updateUI()

    def setUsersChanged(self, data = None):
        g_eventDispatcher.setSquadTeamReadyInCarousel(self._functional.getPrbType(), isTeamReady=self.__getTeamReady())

    def executeInit(self, ctx):
        initResult = FUNCTIONAL_INIT_RESULT.UNDEFINED
        if self._functional.getPlayerInfo().isReady and self._functional.getFlags().isInQueue():
            g_eventDispatcher.loadBattleQueue()
            initResult = FUNCTIONAL_INIT_RESULT.LOAD_PAGE
        squadCtx = None
        if ctx is not None:
            isCreationCtx = ctx.getRequestType() is REQUEST_TYPE.CREATE
            if isCreationCtx:
                accountsToInvite = ctx.getAccountsToInvite()
                showInvitesWindow = True
                if accountsToInvite:
                    showInvitesWindow = False
                    self._functional.request(SendInvitesCtx(accountsToInvite, ''))
                squadCtx = {'showInvitesWindow': showInvitesWindow}
        g_eventDispatcher.loadSquad(squadCtx, self.__getTeamReady())
        return initResult

    def execute(self, customData):
        if self._functional.isCreator():
            fullData = self._functional.getUnitFullData(unitIdx=self._functional.getUnitIdx())
            if fullData is None:
                return {}
            _, _, _, pInfo, slotsIter = fullData
            playerIsIdle = False
            playersCount = 0
            notReadyCount = 0
            for slot in slotsIter:
                slotPlayer = slot.player
                if slotPlayer:
                    if not playerIsIdle:
                        playerIsIdle = slotPlayer.isInArena() or slotPlayer.isInPreArena() or pInfo.isInSearch() or pInfo.isInQueue()
                    playersCount += 1
                    if not slotPlayer.isReady:
                        notReadyCount += 1

            if playerIsIdle:
                DialogsInterface.showI18nInfoDialog('squadHavePlayersInBattle', lambda result: None)
                return True
            if playersCount == 1:
                DialogsInterface.showDialog(I18nConfirmDialogMeta('squadHaveNoPlayers'), self.__setCreatorReady)
                return True
            if not pInfo.isReady:
                notReadyCount -= 1
            if notReadyCount == 1:
                DialogsInterface.showDialog(I18nConfirmDialogMeta('squadHaveNotReadyPlayer'), self.__setCreatorReady)
                return True
            if notReadyCount > 1:
                DialogsInterface.showDialog(I18nConfirmDialogMeta('squadHaveNotReadyPlayers'), self.__setCreatorReady)
                return True
            self.__setCreatorReady(True)
        else:
            self._functional.togglePlayerReadyAction(True)
        return True

    def exitFromQueue(self):
        self._functional.doBattleQueue(unit_ctx.BattleQueueUnitCtx('prebattle/battle_queue', action=0))

    def __setCreatorReady(self, result):
        if not result:
            return
        self._sendBattleQueueRequest(g_currentVehicle.item.invID if not self._functional.getPlayerInfo().isReady else 0)

    def __getTeamReady(self):
        for slot in self._functional.getSlotsIterator(*self._functional.getUnit(unitIdx=self._functional.getUnitIdx())):
            if slot.player and not slot.player.isReady:
                return False

        return True
