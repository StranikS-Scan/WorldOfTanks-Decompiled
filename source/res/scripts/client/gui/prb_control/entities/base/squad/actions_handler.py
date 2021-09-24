# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/base/squad/actions_handler.py
from CurrentVehicle import g_currentVehicle
from PlayerEvents import g_playerEvents
from gui import DialogsInterface
from gui import SystemMessages
from gui.impl.gen import R
from gui.prb_control.entities.base import vehicleAmmoCheck
from gui.prb_control.entities.base.ctx import SendInvitesCtx
from gui.prb_control.entities.base.unit.actions_handler import AbstractActionsHandler
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.settings import REQUEST_TYPE, FUNCTIONAL_FLAG
from gui.shared.event_dispatcher import showPlatoonResourceDialog
from messenger.storage import storage_getter

class SquadActionsHandler(AbstractActionsHandler):

    def __init__(self, entity):
        super(SquadActionsHandler, self).__init__(entity)
        g_playerEvents.onKickedFromRandomQueue += self.__onKickedFromQueue

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
            self._loadBattleQueue()
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
            self._loadBattleQueue()
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

    @vehicleAmmoCheck
    def execute(self):
        if self._entity.isCommander():
            func = self._entity
            fullData = func.getUnitFullData(unitMgrID=func.getID())
            notReadyCount = 0
            for slot in fullData.slotsIterator:
                slotPlayer = slot.player
                if slotPlayer:
                    if slotPlayer.isInArena() or fullData.playerInfo.isInSearch() or fullData.playerInfo.isInQueue():
                        DialogsInterface.showI18nInfoDialog('squadHavePlayersInBattle', lambda result: None)
                        return
                    if not slotPlayer.isReady:
                        notReadyCount += 1

            if not fullData.playerInfo.isReady:
                notReadyCount -= 1
            if fullData.stats.occupiedSlotsCount == 1:
                showPlatoonResourceDialog(R.strings.dialogs.squadHaveNoPlayers, self._confirmCallback)
                return
            if notReadyCount > 0:
                showPlatoonResourceDialog(R.strings.dialogs.squadHaveNotReadyPlayer, self._confirmCallback)
                return
            self._setCreatorReady()
        else:
            self._entity.togglePlayerReadyAction(True)

    def exitFromQueue(self):
        self._sendBattleQueueRequest(action=0)

    def clear(self):
        g_playerEvents.onKickedFromRandomQueue -= self.__onKickedFromQueue
        super(SquadActionsHandler, self).clear()

    def processInvites(self, accountsToInvite):
        if accountsToInvite:
            self._entity.request(SendInvitesCtx(accountsToInvite, ''))
            self._showInviteSentMessage(accountsToInvite)

    def _loadWindow(self, ctx):
        prbType = self._entity.getEntityType()
        g_eventDispatcher.loadSquad(prbType, ctx, self._getTeamReady())

    def _confirmCallback(self, result):
        if result:
            self._setCreatorReady()

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

    @classmethod
    def _loadBattleQueue(cls):
        g_eventDispatcher.loadBattleQueue()

    def __onKickedFromQueue(self):
        SystemMessages.pushI18nMessage('#system_messages:arena_start_errors/prb/kick/timeout', type=SystemMessages.SM_TYPE.Warning)
