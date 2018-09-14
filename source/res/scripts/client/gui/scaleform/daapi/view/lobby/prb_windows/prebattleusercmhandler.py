# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/prb_windows/PrebattleUserCMHandler.py
from adisp import process
from gui.prb_control.context import prb_ctx
from gui.prb_control.prb_helpers import PrbListener
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.daapi.view.lobby.user_cm_handlers import AppealCMHandler, USER
from messenger.m_constants import PROTO_TYPE
from messenger.proto import proto_getter
KICK_FROM_PREBATTLE = 'kickPlayerFromPrebattle'

class PrebattleUserCMHandler(AppealCMHandler, PrbListener):

    def __init__(self, cmProxy, ctx=None):
        super(PrebattleUserCMHandler, self).__init__(cmProxy, ctx)
        self._isCreator = self.prbFunctional.isCreator()
        self.startPrbListening()

    @proto_getter(PROTO_TYPE.BW_CHAT2)
    def bwProto(self):
        return None

    def fini(self):
        self._isCreator = None
        self.stopPrbListening()
        super(PrebattleUserCMHandler, self).fini()
        return

    def onPlayerRemoved(self, functional, playerInfo):
        self.onContextMenuHide()

    def kickPlayerFromPrebattle(self):
        self._kickPlayerFromPrebattle(self.databaseID)

    def _addMutedInfo(self, options, userCMInfo):
        muted = USER.UNSET_MUTED if userCMInfo.isMuted else USER.SET_MUTED
        if not userCMInfo.isIgnored and self.bwProto.voipController.isVOIPEnabled():
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

    def _canKickPlayer(self):
        playerInfo = self.prbFunctional.getPlayerInfoByDbID(self.databaseID)
        team = self.prbFunctional.getPlayerTeam(playerInfo.accID)
        return self.prbFunctional.getPermissions().canKick(team)

    @process
    def _kickPlayerFromPrebattle(self, databaseID):
        playerInfo = self.prbFunctional.getPlayerInfoByDbID(databaseID)
        yield self.prbDispatcher.sendPrbRequest(prb_ctx.KickPlayerCtx(playerInfo.accID, 'prebattle/kick'))
