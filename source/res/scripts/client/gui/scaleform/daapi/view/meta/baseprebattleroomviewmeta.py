# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BasePrebattleRoomViewMeta.py
from gui.Scaleform.daapi.view.lobby.rally.AbstractRallyView import AbstractRallyView

class BasePrebattleRoomViewMeta(AbstractRallyView):

    def requestToReady(self, value):
        self._printOverrideError('requestToReady')

    def requestToLeave(self):
        self._printOverrideError('requestToLeave')

    def showPrebattleSendInvitesWindow(self):
        self._printOverrideError('showPrebattleSendInvitesWindow')

    def canSendInvite(self):
        self._printOverrideError('canSendInvite')

    def canKickPlayer(self):
        self._printOverrideError('canKickPlayer')

    def isPlayerReady(self):
        self._printOverrideError('isPlayerReady')

    def isPlayerCreator(self):
        self._printOverrideError('isPlayerCreator')

    def isReadyBtnEnabled(self):
        self._printOverrideError('isReadyBtnEnabled')

    def isLeaveBtnEnabled(self):
        self._printOverrideError('isLeaveBtnEnabled')

    def getClientID(self):
        self._printOverrideError('getClientID')

    def as_setRosterListS(self, team, assigned, rosters):
        return self.flashObject.as_setRosterList(team, assigned, rosters) if self._isDAAPIInited() else None

    def as_setPlayerStateS(self, team, assigned, data):
        return self.flashObject.as_setPlayerState(team, assigned, data) if self._isDAAPIInited() else None

    def as_enableLeaveBtnS(self, value):
        return self.flashObject.as_enableLeaveBtn(value) if self._isDAAPIInited() else None

    def as_enableReadyBtnS(self, value):
        return self.flashObject.as_enableReadyBtn(value) if self._isDAAPIInited() else None

    def as_setCoolDownForReadyButtonS(self, value):
        return self.flashObject.as_setCoolDownForReadyButton(value) if self._isDAAPIInited() else None

    def as_resetReadyButtonCoolDownS(self):
        return self.flashObject.as_resetReadyButtonCoolDown() if self._isDAAPIInited() else None

    def as_toggleReadyBtnS(self, value):
        return self.flashObject.as_toggleReadyBtn(value) if self._isDAAPIInited() else None

    def as_refreshPermissionsS(self):
        return self.flashObject.as_refreshPermissions() if self._isDAAPIInited() else None
