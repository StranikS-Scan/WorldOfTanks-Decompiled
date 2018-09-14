# Embedded file name: scripts/client/gui/shared/view_helpers/UsersInfoHelper.py
from collections import defaultdict
from debug_utils import LOG_DEBUG
from gui.LobbyContext import g_lobbyContext
from gui.shared import formatters as shared_fmts
from gui.shared.view_helpers.UsersInfoController import UsersInfoController
from messenger import g_settings
from messenger.m_constants import USER_GUI_TYPE
from messenger.storage import storage_getter
from messenger.proto import proto_getter, PROTO_TYPE
from messenger.proto.entities import SharedUserEntity

class UsersInfoHelper(object):
    _rqCtrl = UsersInfoController()

    def __init__(self):
        self._invalid = defaultdict(set)
        self.__callback = None
        return

    def __del__(self):
        self._invalid.clear()

    @classmethod
    def clear(cls):
        LOG_DEBUG('Users info helper stop')
        cls._rqCtrl.stopProcessing()

    @classmethod
    def fini(cls):
        cls.clear()
        cls._rqCtrl.fini()

    def onUserNamesReceived(self, names):
        pass

    def onUserRatingsReceived(self, ratings):
        pass

    def onUserClanAbbrevsReceived(self, abbrevs):
        pass

    @storage_getter('users')
    def users(self):
        return None

    @proto_getter(PROTO_TYPE.XMPP)
    def proto(self):
        return None

    def getContact(self, userDbID):
        user = self.users.getUser(userDbID)
        if not user:
            user = SharedUserEntity(userDbID)
            self.users.addUser(user)
        return user

    def getUserName(self, userDbID):
        user = self.getContact(userDbID)
        if not user.hasValidName():
            self._invalid['names'].add(userDbID)
            if self.proto.isConnected():
                return ''
        return user.getName()

    def getUserClanAbbrev(self, userDbID):
        return self.getContact(userDbID).getClanAbbrev()

    def getUserRegionCode(self, userDbID):
        return g_lobbyContext.getRegionCode(userDbID)

    def getUserFullName(self, userDbID, isClan = True, isRegion = True):
        user = self.getContact(userDbID)
        if not user.hasValidName():
            self._invalid['names'].add(userDbID)
            if self.proto.isConnected():
                return ''
        return user.getFullName(isClan=isClan, isRegion=isRegion)

    def getUserRating(self, userDbID):
        user = self.getContact(userDbID)
        if not user.hasValidRating():
            self._invalid['ratings'].add(userDbID)
        return user.getGlobalRating()

    def getGuiUserData(self, userDbID):
        user = self.getContact(userDbID)
        colorGetter = g_settings.getColorScheme('rosters').getColors
        return {'userName': self.getGuiUserName(userDbID),
         'clanAbbrev': self.getUserClanAbbrev(userDbID),
         'region': self.getUserRegionCode(userDbID),
         'tags': user.getTags() if user else [],
         'dbID': userDbID,
         'colors': colorGetter(user.getGuiType() if user else USER_GUI_TYPE.OTHER)}

    def getGuiUserName(self, userDbID, formatter = lambda v: v):
        userName = self.getUserName(userDbID)
        if userName:
            return formatter(userName)
        return ''

    def getGuiUserFullName(self, userDbID, isClan = True, isRegion = True, formatter = lambda v: v):
        userFullName = self.getUserFullName(userDbID, isClan=isClan, isRegion=isRegion)
        if userFullName:
            return formatter(userFullName)
        return ''

    def getGuiUserRating(self, userDbID, formatter = lambda v: v):
        userRating = self.getUserRating(userDbID)
        if userRating != '0':
            return formatter(shared_fmts.getGlobalRatingFmt(userRating))
        return '-1'

    def syncUsersInfo(self):
        if len(self._invalid['names']):
            self._rqCtrl.requestNicknames(list(self._invalid['names']), lambda names, _: self.onUserNamesReceived(names))
        if len(self._invalid['ratings']):
            self._rqCtrl.requestGlobalRatings(list(self._invalid['ratings']), self.onUserRatingsReceived)
        self._invalid.clear()
