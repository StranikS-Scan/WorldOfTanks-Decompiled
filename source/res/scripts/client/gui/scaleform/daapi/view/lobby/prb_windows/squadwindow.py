# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/prb_windows/SquadWindow.py
from gui.Scaleform.daapi.view.lobby.prb_windows.PrebattleWindow import PrebattleWindow
from gui.prb_control.settings import PREBATTLE_ROSTER, REQUEST_TYPE
from gui.shared import events, EVENT_BUS_SCOPE
__author__ = 'd_savitski'

class SquadWindow(PrebattleWindow):

    def __init__(self, ctx):
        super(SquadWindow, self).__init__(prbName='squad')
        self._isInvitesOpen = ctx.get('isInvitesOpen', False)

    def startListening(self):
        super(SquadWindow, self).startListening()
        self.addListener(events.HideWindowEvent.HIDE_SQUAD_WINDOW, self.__handleSquadWindowHide, scope=EVENT_BUS_SCOPE.LOBBY)
        self.addListener(events.CoolDownEvent.PREBATTLE, self.__handleSetPrebattleCoolDown, scope=EVENT_BUS_SCOPE.LOBBY)

    def stopListening(self):
        super(SquadWindow, self).stopListening()
        self.removeListener(events.HideWindowEvent.HIDE_SQUAD_WINDOW, self.__handleSquadWindowHide, scope=EVENT_BUS_SCOPE.LOBBY)
        self.removeListener(events.CoolDownEvent.PREBATTLE, self.__handleSetPrebattleCoolDown, scope=EVENT_BUS_SCOPE.LOBBY)

    def canKickPlayer(self):
        if self.prbFunctional.getTeamState(team=1).isInQueue():
            return False
        return self.prbFunctional.getPermissions().canKick(team=1)

    def onSettingUpdated(self, functional, settingName, settingValue):
        pass

    def onTeamStatesReceived(self, functional, team1State, team2State):
        self.as_enableReadyBtnS(self.isReadyBtnEnabled())
        self.as_enableLeaveBtnS(self.isLeaveBtnEnabled())
        self.as_refreshPermissionsS()
        if team1State.isInQueue():
            self._closeSendInvitesWindow()

    def onRostersChanged(self, functional, rosters, full):
        self._setRosterList(rosters)
        if full:
            self.as_toggleReadyBtnS(not functional.getPlayerInfo().isReady())
        if not self.canSendInvite():
            self._closeSendInvitesWindow()

    def _populate(self):
        super(SquadWindow, self)._populate()
        self._setRosterList(self.prbFunctional.getRosters())
        if self._isInvitesOpen:
            self.showPrebattleSendInvitesWindow()

    def _setRosterList(self, rosters):
        self.as_setRosterListS(1, True, self._makeAccountsData(rosters[PREBATTLE_ROSTER.ASSIGNED_IN_TEAM1]))

    def __handleSquadWindowHide(self, _):
        self.destroy()

    def __handleSetPrebattleCoolDown(self, event):
        if event.requestID is REQUEST_TYPE.SET_PLAYER_STATE:
            self.as_setCoolDownForReadyButtonS(event.coolDown)
