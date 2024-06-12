# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/base/squad/actions_handler.py
from BWUtil import AsyncReturn
from CurrentVehicle import g_currentVehicle
from PlayerEvents import g_playerEvents
from gui import SystemMessages
from gui.impl.gen import R
from gui.prb_control.entities.base import checkVehicleAmmoFull
from gui.prb_control.entities.base.ctx import SendInvitesCtx
from gui.prb_control.entities.base.unit.actions_handler import AbstractActionsHandler
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.settings import REQUEST_TYPE, FUNCTIONAL_FLAG
from gui.shared.event_dispatcher import showPlatoonInfoDialog, showPlatoonWarningDialog
from messenger.storage import storage_getter
from wg_async import await_callback, wg_async, wg_await

class SquadActionsHandler(AbstractActionsHandler):

    def __init__(self, entity):
        super(SquadActionsHandler, self).__init__(entity)
        g_playerEvents.onKickedFromQueue += self._onKickedFromQueue

    @storage_getter('users')
    def usersStorage(self):
        return None

    def setUnitChanged(self, loadHangar=False):
        flags = self._entity.getFlags()
        if self._entity.getPlayerInfo().isReady and flags.isInQueue():
            _, unit = self._entity.getUnit()
            pInfo = self._entity.getPlayerInfo()
            vInfos = unit.getMemberVehicles(pInfo.dbID)
            if vInfos is not None:
                g_currentVehicle.selectVehicle(vInfos[0].vehInvID)
            g_eventDispatcher.loadBattleQueue()
        elif loadHangar:
            g_eventDispatcher.loadHangar()
        return

    def setPlayerInfoChanged(self):
        g_eventDispatcher.updateUI()

    def setPlayersChanged(self):
        g_eventDispatcher.setSquadTeamReadyInCarousel(self._entity.getEntityType(), isTeamReady=self._getTeamReady())

    def executeInit(self, ctx):
        initResult = FUNCTIONAL_FLAG.UNDEFINED
        if self._entity.getPlayerInfo().isReady and self._entity.getFlags().isInQueue():
            g_eventDispatcher.loadBattleQueue()
            initResult = FUNCTIONAL_FLAG.LOAD_PAGE
        squadCtx = None
        if ctx is not None:
            initCtx = ctx.getInitCtx()
            if initCtx is not None and initCtx.getRequestType() is REQUEST_TYPE.CREATE:
                accountsToInvite = initCtx.getAccountsToInvite()
                showInvitesWindow = True
                if accountsToInvite:
                    showInvitesWindow = False
                    self.processInvites(accountsToInvite)
                squadCtx = {'showInvitesWindow': showInvitesWindow}
        self._loadWindow(squadCtx)
        return initResult

    def executeFini(self):
        prbType = self._entity.getEntityType()
        g_eventDispatcher.removeUnitFromCarousel(prbType)

    @wg_async
    def execute(self):
        entity = self._entity
        if entity is None:
            return
        else:
            result = yield wg_await(self._validateUnitState(entity))
            if not result:
                return
            if entity.isCommander():
                self._setCreatorReady()
            else:
                entity.togglePlayerReadyAction(True)
            return

    @wg_async
    def _validateUnitState(self, entity):
        fullData = entity.getUnitFullData(unitMgrID=entity.getID())
        if entity.isCommander():
            notReadyCount = 0
            for slot in fullData.slotsIterator:
                slotPlayer = slot.player
                if slotPlayer:
                    if self._isSquadHavePlayersInBattle(slotPlayer, fullData.playerInfo):
                        yield wg_await(showPlatoonInfoDialog(R.strings.dialogs.squadHavePlayersInBattle))
                        raise AsyncReturn(False)
                    if not slotPlayer.isReady:
                        notReadyCount += 1

            if not fullData.playerInfo.isReady:
                notReadyCount -= 1
            result = True
            if fullData.stats.occupiedSlotsCount == 1:
                result = yield wg_await(showPlatoonWarningDialog(R.strings.dialogs.squadHaveNoPlayers))
            elif notReadyCount > 0:
                result = yield wg_await(showPlatoonWarningDialog(R.strings.dialogs.squadHaveNotReadyPlayer))
            if not result:
                raise AsyncReturn(result)
            result = yield await_callback(checkVehicleAmmoFull)(g_currentVehicle.item)
            if not result:
                raise AsyncReturn(result)
        elif not fullData.playerInfo.isReady:
            result = yield await_callback(checkVehicleAmmoFull)(g_currentVehicle.item)
            if not result:
                raise AsyncReturn(result)
        raise AsyncReturn(True)

    def exitFromQueue(self):
        self._sendBattleQueueRequest(action=0)

    def clear(self):
        g_playerEvents.onKickedFromQueue -= self._onKickedFromQueue
        super(SquadActionsHandler, self).clear()

    def processInvites(self, accountsToInvite):
        if accountsToInvite:
            self._entity.request(SendInvitesCtx(accountsToInvite, ''))
            self._showInviteSentMessage(accountsToInvite)

    def _loadWindow(self, ctx):
        prbType = self._entity.getEntityType()
        g_eventDispatcher.loadSquad(prbType, ctx, self._getTeamReady())

    def _setCreatorReady(self):
        self._sendBattleQueueRequest(g_currentVehicle.item.invID if not self._entity.getPlayerInfo().isReady else 0)

    def _getTeamReady(self):
        for slot in self._entity.getSlotsIterator(*self._entity.getUnit(unitMgrID=self._entity.getID())):
            if slot.player and not slot.player.isReady:
                return False

        return True

    def _showInviteSentMessage(self, accountsToInvite):
        getUser = self.usersStorage.getUser
        for dbID in accountsToInvite:
            user = getUser(dbID)
            if user is not None:
                SystemMessages.pushI18nMessage('#system_messages:prebattle/invites/sendInvite/name', type=SystemMessages.SM_TYPE.Information, name=user.getFullName())
            SystemMessages.pushI18nMessage('#system_messages:prebattle/invites/sendInvite', type=SystemMessages.SM_TYPE.Information)

        return

    def _onKickedFromQueue(self, _):
        SystemMessages.pushI18nMessage('#system_messages:arena_start_errors/prb/kick/timeout', type=SystemMessages.SM_TYPE.Warning)

    @staticmethod
    def _isSquadHavePlayersInBattle(slotPlayer, playerInfo):
        return slotPlayer.isInArena() or playerInfo.isInSearch() or playerInfo.isInQueue()
