# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/messenger/gui/Scaleform/meta/ContactsWindowMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class ContactsWindowMeta(AbstractWindowView):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends AbstractWindowView
    """

    def searchContact(self, criteria):
        self._printOverrideError('searchContact')

    def addToFriends(self, uid, name):
        self._printOverrideError('addToFriends')

    def addToIgnored(self, uid, name):
        self._printOverrideError('addToIgnored')

    def isEnabledInRoaming(self, uid):
        self._printOverrideError('isEnabledInRoaming')

    def as_getFriendsDPS(self):
        return self.flashObject.as_getFriendsDP() if self._isDAAPIInited() else None

    def as_getClanDPS(self):
        return self.flashObject.as_getClanDP() if self._isDAAPIInited() else None

    def as_getIgnoredDPS(self):
        return self.flashObject.as_getIgnoredDP() if self._isDAAPIInited() else None

    def as_getMutedDPS(self):
        return self.flashObject.as_getMutedDP() if self._isDAAPIInited() else None

    def as_getSearchDPS(self):
        return self.flashObject.as_getSearchDP() if self._isDAAPIInited() else None

    def as_setSearchResultTextS(self, message):
        return self.flashObject.as_setSearchResultText(message) if self._isDAAPIInited() else None

    def as_frozenSearchActionS(self, flag):
        return self.flashObject.as_frozenSearchAction(flag) if self._isDAAPIInited() else None
