# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/prb_windows/invite_windows.py
from PlayerEvents import g_playerEvents
from adisp import process
from gui.prb_control.prb_getters import getPrebattleAutoInvites
from gui.prb_control.context.prb_ctx import JoinBattleSessionCtx
from messenger.ext import channel_num_gen
from messenger.gui import events_dispatcher
from messenger.m_constants import LAZY_CHANNEL
from predefined_hosts import g_preDefinedHosts
from gui import DialogsInterface
from gui.shared import actions
from gui.Scaleform.daapi.view.meta.ReceivedInviteWindowMeta import ReceivedInviteWindowMeta
from gui.prb_control.formatters.invites import PrbAutoInviteInfo
from gui.prb_control.prb_helpers import GlobalListener, prbPeripheriesHandlerProperty, prbAutoInvitesProperty
__author__ = 'd_savitski'

class _DisableNotify(actions.Action):

    def __init__(self, clientID):
        super(_DisableNotify, self).__init__()
        self.__clientID = clientID

    def invoke(self):
        events_dispatcher.notifyCarousel(self.__clientID, notify=False)
        self._completed = True


class _InviteWindow(GlobalListener, ReceivedInviteWindowMeta):

    def __init__(self, inviteInfo):
        super(_InviteWindow, self).__init__()
        self._inviteInfo = inviteInfo

    def onPrbFunctionalInited(self):
        self._updateReceivedInfo()

    def onPrbFunctionalFinished(self):
        self._updateReceivedInfo()

    def onTeamStatesReceived(self, functional, team1State, team2State):
        self._updateReceivedInfo()

    def onIntroUnitFunctionalInited(self):
        self._updateReceivedInfo()

    def onIntroUnitFunctionalFinished(self):
        self._updateReceivedInfo()

    def onUnitFunctionalInited(self):
        self._updateReceivedInfo()

    def onUnitFunctionalFinished(self):
        self._updateReceivedInfo()

    def onUnitFlagsChanged(self, flags, timeLeft):
        self._updateReceivedInfo()

    def cancelInvite(self):
        self.onWindowClose()

    def onWindowClose(self):
        self.destroy()

    def _populate(self):
        super(_InviteWindow, self)._populate()
        self.startGlobalListening()
        self.as_setTitleS(self._inviteInfo.getTitle())
        self._updateReceivedInfo()

    def _dispose(self):
        self._inviteInfo = None
        self.stopGlobalListening()
        super(_InviteWindow, self)._dispose()
        return

    def _updateReceivedInfo(self):
        self.as_setReceivedInviteInfoS(self._inviteInfo.as_dict())


class AutoInviteWindow(_InviteWindow):

    def __init__(self, ctx):
        super(AutoInviteWindow, self).__init__(PrbAutoInviteInfo(ctx.get('prbID')))

    @prbPeripheriesHandlerProperty
    def prbPeripheriesHandler(self):
        return None

    @prbAutoInvitesProperty
    def prbAutoInvites(self):
        return None

    @process
    def acceptInvite(self):
        yield lambda callback: callback(None)
        prbID = self._inviteInfo.getID()
        invite = self.prbAutoInvites.getInvite(prbID)
        postActions = []
        if self.prbDispatcher.hasModalEntity():
            postActions.append(actions.LeavePrbModalEntity())
        finishActions = [_DisableNotify(channel_num_gen.getClientID4LazyChannel(LAZY_CHANNEL.SPECIAL_BATTLES))]
        if g_preDefinedHosts.isRoamingPeriphery(invite.peripheryID):
            success = yield DialogsInterface.showI18nConfirmDialog('changeRoamingPeriphery')
            if not success:
                return
        self.prbPeripheriesHandler.join(invite.peripheryID, JoinBattleSessionCtx(prbID, invite.prbType, 'prebattle/join'), postActions, finishActions)

    def declineInvite(self):
        self.onWindowClose()

    def _populate(self):
        super(AutoInviteWindow, self)._populate()
        g_playerEvents.onPrebattleAutoInvitesChanged += self.__onPrbAutoInvitesChanged

    def _dispose(self):
        g_playerEvents.onPrebattleAutoInvitesChanged -= self.__onPrbAutoInvitesChanged
        super(AutoInviteWindow, self)._dispose()

    def __onPrbAutoInvitesChanged(self):
        if self._inviteInfo.getID() not in getPrebattleAutoInvites():
            self.destroy()
