# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/ProfileWindowMeta.py
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class ProfileWindowMeta(DAAPIModule):

    def userAddFriend(self):
        self._printOverrideError('userAddFriend')

    def userSetIgnored(self):
        self._printOverrideError('userSetIgnored')

    def userCreatePrivateChannel(self):
        self._printOverrideError('userCreatePrivateChannel')

    def as_setInitDataS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_setInitData(data)

    def as_updateS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_update(data)

    def as_addFriendAvailableS(self, value):
        if self._isDAAPIInited():
            return self.flashObject.as_addFriendAvailable(value)

    def as_setIgnoredAvailableS(self, value):
        if self._isDAAPIInited():
            return self.flashObject.as_setIgnoredAvailable(value)

    def as_setCreateChannelAvailableS(self, value):
        if self._isDAAPIInited():
            return self.flashObject.as_setCreateChannelAvailable(value)
