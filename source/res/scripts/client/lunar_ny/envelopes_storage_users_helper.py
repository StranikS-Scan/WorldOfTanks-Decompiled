# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/lunar_ny/envelopes_storage_users_helper.py
from collections import defaultdict
from gui.shared.view_helpers import UsersInfoHelper
from messenger.m_constants import UserEntityScope

class EnvelopesStorageUsersHelper(UsersInfoHelper):
    _MAX_CHUNK_SIZE = 20

    def __init__(self):
        super(EnvelopesStorageUsersHelper, self).__init__()
        self._invalid = defaultdict(list)

    def onUserNamesReceived(self, names):
        super(EnvelopesStorageUsersHelper, self).onUserNamesReceived(names)
        if self._invalid['names']:
            self.syncUsersInfo()

    def getUserName(self, userID, scope=UserEntityScope.LOBBY, withEmptyName=False):
        user = self.getContact(userID, scope=scope)
        if not user.hasValidName():
            if userID > 0 and userID not in self._invalid['names']:
                self._invalid['names'].append(userID)
            if self.proto.isConnected() or withEmptyName:
                return ''
        return user.getName()

    def getUserRating(self, userDbID):
        user = self.getContact(userDbID)
        if not user.hasValidRating():
            if userDbID > 0 and userDbID not in self._invalid['ratings']:
                self._invalid['ratings'].append(userDbID)
        return user.getGlobalRating()

    def syncUsersInfo(self):
        if self._invalid['names']:
            self._rqCtrl.requestNicknames(self._invalid['names'][:self._MAX_CHUNK_SIZE], lambda names, _: self.onUserNamesReceived(names))
            del self._invalid['names'][:self._MAX_CHUNK_SIZE]
        if self._invalid['ratings']:
            self._rqCtrl.requestGlobalRatings(list(self._invalid['ratings']), self.onUserRatingsReceived)
            self._invalid['ratings'] = []

    def clearInvalidData(self):
        self._invalid.clear()

    def hasInvalidName(self):
        return bool(self._invalid['names'])
