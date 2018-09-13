# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/LobbyMessengerMeta.py
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class LobbyMessengerMeta(DAAPIModule):

    def requestOnRefreshMemberList(self):
        self._printOverrideError('requestOnRefreshMemberList')

    def requestRolePlayer(self):
        self._printOverrideError('requestRolePlayer')

    def requestToReadyBtn(self, value):
        self._printOverrideError('requestToReadyBtn')

    def requestToLeaveBtn(self):
        self._printOverrideError('requestToLeaveBtn')

    def showPrebattleSendInvitesWindow(self):
        self._printOverrideError('showPrebattleSendInvitesWindow')

    def as_onRefreshMemberListS(self, value):
        if self._isDAAPIInited():
            self.flashObject.as_onRefreshMemberList(value)

    def as_onRolePlayerS(self, value):
        if self._isDAAPIInited():
            self.flashObject.as_onRolePlayer(value)

    def as_enableLeaveBtnS(self, value):
        if self._isDAAPIInited():
            self.flashObject.as_enableLeaveBtn(value)

    def as_enableReadyBtnS(self, value):
        if self._isDAAPIInited():
            self.flashObject.as_enableReadyBtn(value)

    def as_coolDownForReadyButtonS(self, value):
        if self._isDAAPIInited():
            self.flashObject.as_coolDownForReadyButton(value)

    def as_toggleReadyBtnS(self, value):
        if self._isDAAPIInited():
            self.flashObject.as_toggleReadyBtn(value)

    def as_setPlayerStateS(self, uid, state, vContourIcon, vShortName, vLevel):
        if self._isDAAPIInited():
            self.flashObject.as_setPlayerState(uid, state, vContourIcon, vShortName, vLevel)
