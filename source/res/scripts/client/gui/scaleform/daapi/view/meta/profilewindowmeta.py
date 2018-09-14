# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/ProfileWindowMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class ProfileWindowMeta(AbstractWindowView):

    def userAddFriend(self):
        self._printOverrideError('userAddFriend')

    def userAddToClan(self):
        self._printOverrideError('userAddToClan')

    def userSetIgnored(self):
        self._printOverrideError('userSetIgnored')

    def userCreatePrivateChannel(self):
        self._printOverrideError('userCreatePrivateChannel')

    def as_setInitDataS(self, data):
        """
        :param data: Represented by ProfileWindowInitVO (AS)
        """
        return self.flashObject.as_setInitData(data) if self._isDAAPIInited() else None

    def as_addFriendAvailableS(self, value):
        return self.flashObject.as_addFriendAvailable(value) if self._isDAAPIInited() else None

    def as_addToClanAvailableS(self, value):
        return self.flashObject.as_addToClanAvailable(value) if self._isDAAPIInited() else None

    def as_addToClanVisibleS(self, value):
        return self.flashObject.as_addToClanVisible(value) if self._isDAAPIInited() else None

    def as_setIgnoredAvailableS(self, value):
        return self.flashObject.as_setIgnoredAvailable(value) if self._isDAAPIInited() else None

    def as_setCreateChannelAvailableS(self, value):
        return self.flashObject.as_setCreateChannelAvailable(value) if self._isDAAPIInited() else None
