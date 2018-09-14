# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/prb_windows/PrebattleUserCMHandler.py
from adisp import process
from constants import PREBATTLE_TYPE
from gui.prb_control.context import prb_ctx
from gui.prb_control.prb_helpers import PrbListener
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.daapi.view.lobby.user_cm_handlers import AppealCMHandler, USER
KICK_FROM_PREBATTLE = 'kickPlayerFromPrebattle'

class PrebattleUserCMHandler(AppealCMHandler, PrbListener):

    def __init__(self, cmProxy, ctx = None):
        super(PrebattleUserCMHandler, self).__init__(cmProxy, ctx)
        self._isCreator = self.prbFunctional.isCreator()
        self._isSquad = self.prbFunctional.getEntityType() == PREBATTLE_TYPE.SQUAD
        self.startPrbListening()

    def fini(self):
        self._isCreator = None
        self._isSquad = None
        self.stopPrbListening()
        super(PrebattleUserCMHandler, self).fini()
        return

    def onPlayerRemoved(self, functional, playerInfo):
        self.onContextMenuHide()

    def kickPlayerFromPrebattle(self):
        self._kickPlayerFromPrebattle(self.databaseID)

    def _addMutedInfo(self, options, userCMInfo):
        muted = USER.UNSET_MUTED if userCMInfo.isMuted else USER.SET_MUTED
        if not userCMInfo.isIgnored and self.app.voiceChatManager.isVOIPEnabled():
            options.append(self._makeItem(muted, MENU.contextmenu(muted)))
        return options

    def _addPrebattleInfo(self, options, userCMInfo):
        disabled = self.prbFunctional.getTeamState().isInQueue()
        if self._canKickPlayer():
            options.append(self._makeItem(KICK_FROM_PREBATTLE, MENU.contextmenu(KICK_FROM_PREBATTLE), {'enabled': not disabled}))
        return options

    def _getHandlers(self):
        handlers = super(PrebattleUserCMHandler, self)._getHandlers()
        handlers.update({KICK_FROM_PREBATTLE: 'kickPlayerFromPrebattle'})
        return handlers

    def _isAppealsEnabled(self):
        return self._getDenunciationsLeft() > 0 and not self.prbFunctional.getEntityType() == PREBATTLE_TYPE.SQUAD

    def _canKickPlayer(self):
        playerInfo = self.prbFunctional.getPlayerInfoByDbID(self.databaseID)
        team = self.prbFunctional.getPlayerTeam(playerInfo.accID)
        return self.prbFunctional.getPermissions().canKick(team)

    @process
    def _kickPlayerFromPrebattle(self, databaseID):
        playerInfo = self.prbFunctional.getPlayerInfoByDbID(databaseID)
        yield self.prbDispatcher.sendPrbRequest(prb_ctx.KickPlayerCtx(playerInfo.accID, 'prebattle/kick'))
