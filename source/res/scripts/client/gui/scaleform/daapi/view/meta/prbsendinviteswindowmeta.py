# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/PrbSendInvitesWindowMeta.py
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class PrbSendInvitesWindowMeta(DAAPIModule):

    def showError(self, value):
        self._printOverrideError('showError')

    def searchToken(self, value):
        self._printOverrideError('searchToken')

    def setOnlineFlag(self, value):
        self._printOverrideError('setOnlineFlag')

    def sendInvites(self, accountsToInvite, comment):
        self._printOverrideError('sendInvites')

    def as_onReceiveSendInvitesCooldownS(self, value):
        if self._isDAAPIInited():
            return self.flashObject.as_onReceiveSendInvitesCooldown(value)

    def as_setDefaultOnlineFlagS(self, onlineFlag):
        if self._isDAAPIInited():
            return self.flashObject.as_setDefaultOnlineFlag(onlineFlag)

    def as_showClanOnlyS(self, showClanOnly):
        if self._isDAAPIInited():
            return self.flashObject.as_showClanOnly(showClanOnly)

    def as_getFriendsDPS(self):
        if self._isDAAPIInited():
            return self.flashObject.as_getFriendsDP()

    def as_getClanDPS(self):
        if self._isDAAPIInited():
            return self.flashObject.as_getClanDP()

    def as_getSearchDPS(self):
        if self._isDAAPIInited():
            return self.flashObject.as_getSearchDP()

    def as_getReceiverDPS(self):
        if self._isDAAPIInited():
            return self.flashObject.as_getReceiverDP()

    def as_onSearchResultReceivedS(self, result):
        if self._isDAAPIInited():
            return self.flashObject.as_onSearchResultReceived(result)

    def as_setWindowTitleS(self, value):
        if self._isDAAPIInited():
            return self.flashObject.as_setWindowTitle(value)

    def as_setInvitesS(self, value):
        if self._isDAAPIInited():
            return self.flashObject.as_setInvites(value)
