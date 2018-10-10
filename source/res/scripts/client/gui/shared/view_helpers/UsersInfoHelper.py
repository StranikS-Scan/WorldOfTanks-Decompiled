# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/view_helpers/UsersInfoHelper.py
from collections import defaultdict
from debug_utils import LOG_DEBUG
from gui.shared import formatters as shared_fmts
from gui.shared.view_helpers.UsersInfoController import UsersInfoController
from helpers import dependency
from messenger import g_settings
from messenger.m_constants import USER_GUI_TYPE
from messenger.storage import storage_getter
from messenger.proto import proto_getter, PROTO_TYPE
from messenger.proto.entities import SharedUserEntity
from skeletons.gui.lobby_context import ILobbyContext

class UsersInfoHelper(object):
    _rqCtrl = UsersInfoController()
    lobbyContext = dependency.descriptor(ILobbyContext)

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
        return self.lobbyContext.getRegionCode(userDbID)

    def getUserFullName(self, userDbID, isClan=True, isRegion=True):
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

    def buildGuiUserData(self, user):
        userDbID = user.getID()
        colorGetter = g_settings.getColorScheme('rosters').getColors
        return {'userName': self.getGuiUserName(userDbID),
         'clanAbbrev': self.getUserClanAbbrev(userDbID),
         'region': self.getUserRegionCode(userDbID),
         'tags': user.getTags() if user else [],
         'dbID': userDbID,
         'colors': colorGetter(user.getGuiType() if user else USER_GUI_TYPE.OTHER)}

    def getGuiUserData(self, userDbID):
        user = self.getContact(userDbID)
        return self.buildGuiUserData(user)

    def getGuiUserDataWithStatus(self, userDbID):
        user = self.getContact(userDbID)
        return (user.hasValidName() and user.hasValidRating(), self.buildGuiUserData(user))

    def getGuiUserName(self, userDbID, formatter=lambda v: v):
        userName = self.getUserName(userDbID)
        return formatter(userName) if userName else ''

    def getGuiUserFullName(self, userDbID, isClan=True, isRegion=True, formatter=lambda v: v):
        userFullName = self.getUserFullName(userDbID, isClan=isClan, isRegion=isRegion)
        return formatter(userFullName) if userFullName else ''

    def getGuiUserRating(self, userDbID, formatter=lambda v: v):
        userRating = self.getUserRating(userDbID)
        return formatter(shared_fmts.getGlobalRatingFmt(userRating)) if userRating != '0' else '-1'

    def syncUsersInfo(self):
        if self._invalid['names']:
            self._rqCtrl.requestNicknames(list(self._invalid['names']), lambda names, _: self.onUserNamesReceived(names))
        if self._invalid['ratings']:
            self._rqCtrl.requestGlobalRatings(list(self._invalid['ratings']), self.onUserRatingsReceived)
        self._invalid.clear()
