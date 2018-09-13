# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/prb_windows/SquadView.py
from adisp import process
from debug_utils import LOG_DEBUG
from prebattle_shared import decodeRoster
from gui.prb_control.context import prb_ctx
from gui.Scaleform.daapi.view.meta.SquadViewMeta import SquadViewMeta
from gui.Scaleform.daapi.view.lobby.rally import vo_converters
from gui.Scaleform.locale.MENU import MENU
from gui.prb_control.prb_helpers import PrbListener
from gui.prb_control.settings import CTRL_ENTITY_TYPE, REQUEST_TYPE
from gui.shared import events, EVENT_BUS_SCOPE

class SquadView(SquadViewMeta, PrbListener):

    def inviteFriendRequest(self):
        if self.canSendInvite():
            self.fireEvent(events.ShowWindowEvent(events.ShowWindowEvent.SHOW_SEND_INVITES_WINDOW, {'prbName': 'squad',
             'ctrlType': CTRL_ENTITY_TYPE.PREBATTLE}), scope=EVENT_BUS_SCOPE.LOBBY)

    def canSendInvite(self):
        return self.prbFunctional.getPermissions().canSendInvite()

    @process
    def toggleReadyStateRequest(self):
        value = not self.prbFunctional.getPlayerInfo().isReady()
        if value:
            waitingID = 'prebattle/player_ready'
        else:
            waitingID = 'prebattle/player_not_ready'
        yield self.prbDispatcher.sendPrbRequest(prb_ctx.SetPlayerStateCtx(value, waitingID=waitingID))

    def chooseVehicleRequest(self):
        pass

    def leaveSquad(self):
        self.prbDispatcher.doLeaveAction(prb_ctx.LeavePrbCtx(waitingID='prebattle/leave'))

    def onPlayerAdded(self, functional, playerInfo):
        super(SquadView, self).onPlayerAdded(functional, playerInfo)
        self._setActionButtonState()

    def onPlayerRemoved(self, functional, playerInfo):
        super(SquadView, self).onPlayerRemoved(functional, playerInfo)
        self._setActionButtonState()

    def onPlayerStateChanged(self, functional, roster, playerInfo):
        self._updateRallyData()
        self._setActionButtonState()

    def onTeamStatesReceived(self, functional, team1State, team2State):
        self._setActionButtonState()
        if team1State.isInQueue():
            self._closeSendInvitesWindow()

    def onRostersChanged(self, functional, rosters, full):
        self._updateRallyData()
        if full:
            self._setActionButtonState()
        if not self.canSendInvite():
            self._closeSendInvitesWindow()

    def _populate(self):
        super(SquadView, self)._populate()
        self.startPrbListening()
        self.addListener(events.CoolDownEvent.PREBATTLE, self.__handleSetPrebattleCoolDown, scope=EVENT_BUS_SCOPE.LOBBY)
        self.as_updateBattleTypeS(MENU.HEADERBUTTONS_BATTLE_MENU_STANDART)

    def _dispose(self):
        self.removeListener(events.CoolDownEvent.PREBATTLE, self.__handleSetPrebattleCoolDown, scope=EVENT_BUS_SCOPE.LOBBY)
        self.stopPrbListening()
        super(SquadView, self)._dispose()

    def _setActionButtonState(self):
        self.as_updateInviteBtnStateS(self._isInviteBtnEnabled())
        self.as_setActionButtonStateS(vo_converters.makeSquadActionButtonVO(self.prbFunctional))

    def _updateRallyData(self):
        self.as_updateRallyS(vo_converters.makeSquadVO(self.prbFunctional, app=self.app))

    def _isInviteBtnEnabled(self):
        functional = self.prbFunctional
        team, assigned = decodeRoster(functional.getRosterKey())
        return not (functional.getTeamState().isInQueue() and functional.getPlayerInfo().isReady() and assigned) and self.canSendInvite()

    def __handleSetPrebattleCoolDown(self, event):
        if event.requestID is REQUEST_TYPE.SET_PLAYER_STATE:
            self.as_setCoolDownForReadyButtonS(event.coolDown)
