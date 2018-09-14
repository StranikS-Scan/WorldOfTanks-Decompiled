# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/gui/Scaleform/meta/ContactsWindowMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class ContactsWindowMeta(AbstractWindowView):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends AbstractWindowView
    null
    """

    def searchContact(self, criteria):
        """
        :param criteria:
        :return :
        """
        self._printOverrideError('searchContact')

    def addToFriends(self, uid, name):
        """
        :param uid:
        :param name:
        :return :
        """
        self._printOverrideError('addToFriends')

    def addToIgnored(self, uid, name):
        """
        :param uid:
        :param name:
        :return :
        """
        self._printOverrideError('addToIgnored')

    def isEnabledInRoaming(self, uid):
        """
        :param uid:
        :return Boolean:
        """
        self._printOverrideError('isEnabledInRoaming')

    def as_getFriendsDPS(self):
        """
        :return Object:
        """
        return self.flashObject.as_getFriendsDP() if self._isDAAPIInited() else None

    def as_getClanDPS(self):
        """
        :return Object:
        """
        return self.flashObject.as_getClanDP() if self._isDAAPIInited() else None

    def as_getIgnoredDPS(self):
        """
        :return Object:
        """
        return self.flashObject.as_getIgnoredDP() if self._isDAAPIInited() else None

    def as_getMutedDPS(self):
        """
        :return Object:
        """
        return self.flashObject.as_getMutedDP() if self._isDAAPIInited() else None

    def as_getSearchDPS(self):
        """
        :return Object:
        """
        return self.flashObject.as_getSearchDP() if self._isDAAPIInited() else None

    def as_setSearchResultTextS(self, message):
        """
        :param message:
        :return :
        """
        return self.flashObject.as_setSearchResultText(message) if self._isDAAPIInited() else None

    def as_frozenSearchActionS(self, flag):
        """
        :param flag:
        :return :
        """
        return self.flashObject.as_frozenSearchAction(flag) if self._isDAAPIInited() else None
