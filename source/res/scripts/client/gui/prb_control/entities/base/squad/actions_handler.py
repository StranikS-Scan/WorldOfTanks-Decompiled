# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/base/squad/actions_handler.py
from CurrentVehicle import g_currentVehicle
from PlayerEvents import g_playerEvents
from gui import DialogsInterface, SystemMessages
from gui.Scaleform.daapi.view.dialogs import I18nConfirmDialogMeta
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.prb_control.entities.base import vehicleAmmoCheck
from gui.prb_control.entities.base.ctx import SendInvitesCtx
from gui.prb_control.entities.base.unit.actions_handler import AbstractActionsHandler
from gui.prb_control.settings import REQUEST_TYPE, FUNCTIONAL_FLAG
from messenger.storage import storage_getter
from helpers import dependency
from skeletons.new_year import ICustomizableObjectsManager

class SquadActionsHandler(AbstractActionsHandler):
    """
    Squad base actions handler
    """

    def __init__(self, entity):
        super(SquadActionsHandler, self).__init__(entity)
        g_playerEvents.onKickedFromRandomQueue += self.__onKickedFromQueue

    @storage_getter('users')
    def usersStorage(self):
        """
        User's storage getter property.
        """
        return None

    def setUnitChanged(self):
        flags = self._entity.getFlags()
        if self._entity.getPlayerInfo().isReady and flags.isInQueue():
            g_eventDispatcher.loadBattleQueue()
        else:
            g_eventDispatcher.loadHangar()

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
        customizableObjMgr = dependency.instance(ICustomizableObjectsManager)
        if not customizableObjMgr.state:
            g_eventDispatcher.loadHangar()

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
                        return True
                    if not slotPlayer.isReady:
                        notReadyCount += 1

            if not fullData.playerInfo.isReady:
                notReadyCount -= 1
            if fullData.stats.occupiedSlotsCount == 1:
                DialogsInterface.showDialog(I18nConfirmDialogMeta('squadHaveNoPlayers'), self._confirmCallback)
                return True
            if notReadyCount > 0:
                if notReadyCount == 1:
                    DialogsInterface.showDialog(I18nConfirmDialogMeta('squadHaveNotReadyPlayer'), self._confirmCallback)
                    return True
                DialogsInterface.showDialog(I18nConfirmDialogMeta('squadHaveNotReadyPlayers'), self._confirmCallback)
                return True
            self._setCreatorReady()
        else:
            self._entity.togglePlayerReadyAction(True)
        return True

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
        """
        Routine musk be invoked to load squad's prebattle window
        Args:
            ctx: initialization's request context
        """
        prbType = self._entity.getEntityType()
        g_eventDispatcher.loadSquad(prbType, ctx, self._getTeamReady())

    def _confirmCallback(self, result):
        """
        Set creator ready confirm dialog callback
        Args:
            result: confirm result
        """
        if result:
            self._setCreatorReady()

    def _setCreatorReady(self):
        """
        Routine to set creator ready at system's level
        """
        self._sendBattleQueueRequest(g_currentVehicle.item.invID if not self._entity.getPlayerInfo().isReady else 0)

    def _getTeamReady(self):
        """
        Routine to set team ready at system's level
        """
        for slot in self._entity.getSlotsIterator(*self._entity.getUnit(unitMgrID=self._entity.getID())):
            if slot.player and not slot.player.isReady:
                return False

        return True

    def _showInviteSentMessage(self, accountsToInvite):
        """
        Shows invitation send result message
        """
        getUser = self.usersStorage.getUser
        for dbID in accountsToInvite:
            user = getUser(dbID)
            if user is not None:
                SystemMessages.pushI18nMessage('#system_messages:prebattle/invites/sendInvite/name', type=SystemMessages.SM_TYPE.Information, name=user.getFullName())
            SystemMessages.pushI18nMessage('#system_messages:prebattle/invites/sendInvite', type=SystemMessages.SM_TYPE.Information)

        return

    def __onKickedFromQueue(self):
        """
        Listener for queue kick event. Is fix for for WOTD-43677
        """
        SystemMessages.pushI18nMessage('#system_messages:arena_start_errors/prb/kick/timeout', type=SystemMessages.SM_TYPE.Warning)
