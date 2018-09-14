# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/ProfileWindowMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class ProfileWindowMeta(AbstractWindowView):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends AbstractWindowView
    null
    """

    def userAddFriend(self):
        """
        :return :
        """
        self._printOverrideError('userAddFriend')

    def userAddToClan(self):
        """
        :return :
        """
        self._printOverrideError('userAddToClan')

    def userSetIgnored(self):
        """
        :return :
        """
        self._printOverrideError('userSetIgnored')

    def userCreatePrivateChannel(self):
        """
        :return :
        """
        self._printOverrideError('userCreatePrivateChannel')

    def as_setInitDataS(self, data):
        """
        :param data:
        :return :
        """
        return self.flashObject.as_setInitData(data) if self._isDAAPIInited() else None

    def as_addFriendAvailableS(self, value):
        """
        :param value:
        :return :
        """
        return self.flashObject.as_addFriendAvailable(value) if self._isDAAPIInited() else None

    def as_addToClanAvailableS(self, value):
        """
        :param value:
        :return :
        """
        return self.flashObject.as_addToClanAvailable(value) if self._isDAAPIInited() else None

    def as_addToClanVisibleS(self, value):
        """
        :param value:
        :return :
        """
        return self.flashObject.as_addToClanVisible(value) if self._isDAAPIInited() else None

    def as_setIgnoredAvailableS(self, value):
        """
        :param value:
        :return :
        """
        return self.flashObject.as_setIgnoredAvailable(value) if self._isDAAPIInited() else None

    def as_setCreateChannelAvailableS(self, value):
        """
        :param value:
        :return :
        """
        return self.flashObject.as_setCreateChannelAvailable(value) if self._isDAAPIInited() else None
