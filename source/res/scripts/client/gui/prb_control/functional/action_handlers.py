# Embedded file name: scripts/client/gui/prb_control/functional/action_handlers.py
import weakref
from CurrentVehicle import g_currentVehicle
from constants import PREBATTLE_TYPE, FALLOUT_BATTLE_TYPE
from debug_utils import LOG_DEBUG
from gui import DialogsInterface, SystemMessages
from gui.Scaleform.daapi.view.dialogs import I18nConfirmDialogMeta, rally_dialog_meta
from gui.prb_control.context import unit_ctx, SendInvitesCtx
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.settings import REQUEST_TYPE, FUNCTIONAL_FLAG
from messenger.storage import storage_getter

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
        return FUNCTIONAL_FLAG.UNDEFINED

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

    @storage_getter('users')
    def usersStorage(self):
        return None

    def setUnitChanged(self, flags):
        if flags.isInQueueChanged():
            if self._functional.getPlayerInfo().isReady and flags.isInQueue():
                g_eventDispatcher.loadBattleQueue()
            else:
                g_eventDispatcher.loadHangar()

    def setPlayerInfoChanged(self, data = None):
        g_eventDispatcher.updateUI()

    def setUsersChanged(self, data = None):
        g_eventDispatcher.setSquadTeamReadyInCarousel(self._functional.getEntityType(), isTeamReady=self.__getTeamReady())

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
                    self.__showInviteSentMessage(accountsToInvite)
                squadCtx = {'showInvitesWindow': showInvitesWindow}
        g_eventDispatcher.loadSquad(squadCtx, self.__getTeamReady())
        return initResult

    def execute(self, customData):
        if self._functional.isCreator():
            func = self._functional
            fullData = func.getUnitFullData(unitIdx=self._functional.getUnitIdx())
            if fullData is None:
                return {}
            _, _, unitStats, pInfo, slotsIter = fullData
            isAutoFill = func.getExtra().eventType == FALLOUT_BATTLE_TYPE.MULTITEAM
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
                    DialogsInterface.showDialog(I18nConfirmDialogMeta('squadHaveNotReadyPlayerAuto'), self.__setCreatorReady)
                    return True
                if unitStats.freeSlotsCount == 1:
                    DialogsInterface.showDialog(I18nConfirmDialogMeta('squadHaveNoPlayerAuto'), self.__setCreatorReady)
                    return True
            else:
                if unitStats.occupiedSlotsCount == 1:
                    DialogsInterface.showDialog(I18nConfirmDialogMeta('squadHaveNoPlayers'), self.__setCreatorReady)
                    return True
                if notReadyCount > 0:
                    if notReadyCount == 1:
                        DialogsInterface.showDialog(I18nConfirmDialogMeta('squadHaveNotReadyPlayer'), self.__setCreatorReady)
                        return True
                    DialogsInterface.showDialog(I18nConfirmDialogMeta('squadHaveNotReadyPlayers'), self.__setCreatorReady)
                    return True
            self.__setCreatorReady(True)
        else:
            self._functional.togglePlayerReadyAction(True)
        return True

    def exitFromQueue(self):
        self._functional.doBattleQueue(unit_ctx.BattleQueueUnitCtx('prebattle/battle_queue', action=0))

    def clear(self):
        g_eventDispatcher.unloadFallout()
        super(SquadActionsHandler, self).clear()

    def __setCreatorReady(self, result):
        if not result:
            return
        self._sendBattleQueueRequest(g_currentVehicle.item.invID if not self._functional.getPlayerInfo().isReady else 0)

    def __getTeamReady(self):
        for slot in self._functional.getSlotsIterator(*self._functional.getUnit(unitIdx=self._functional.getUnitIdx())):
            if slot.player and not slot.player.isReady:
                return False

        return True

    def __showInviteSentMessage(self, accountsToInvite):
        getUser = self.usersStorage.getUser
        for dbID in accountsToInvite:
            user = getUser(dbID)
            if user is not None:
                SystemMessages.pushI18nMessage('#system_messages:prebattle/invites/sendInvite/name', type=SystemMessages.SM_TYPE.Information, name=user.getFullName())
            else:
                SystemMessages.pushI18nMessage('#system_messages:prebattle/invites/sendInvite', type=SystemMessages.SM_TYPE.Information)

        return
