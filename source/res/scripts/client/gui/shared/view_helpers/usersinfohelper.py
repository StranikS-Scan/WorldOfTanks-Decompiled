# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/view_helpers/UsersInfoHelper.py
import logging
from collections import defaultdict
from Event import Event
from constants import IGR_TYPE
from debug_utils import LOG_DEBUG
from gui.shared import formatters as shared_fmts
from gui.shared.view_helpers.UsersInfoController import UsersInfoController
from helpers import dependency
from messenger import g_settings
from messenger.m_constants import USER_GUI_TYPE, UserEntityScope, USER_TAG
from messenger.storage import storage_getter
from messenger.proto import proto_getter, PROTO_TYPE
from messenger.proto.entities import SharedUserEntity
from skeletons.gui.lobby_context import ILobbyContext
_logger = logging.getLogger(__name__)

class UsersInfoHelper(object):
    lobbyContext = dependency.descriptor(ILobbyContext)
    _rqCtrl = UsersInfoController()

    def __init__(self):
        self._invalid = defaultdict(set)
        self.__callback = None
        self.onNamesReceived = Event()
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
        self.onNamesReceived()

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

    def getContact(self, userID, scope=UserEntityScope.LOBBY):
        user = self.users.getUser(userID, scope=scope)
        if not user:
            user = SharedUserEntity(userID)
            self.users.addUser(user)
        return user

    def getUserName(self, userID, scope=UserEntityScope.LOBBY):
        user = self.getContact(userID, scope=scope)
        if not user.hasValidName():
            self._invalid['names'].add(userID)
            if self.proto.isConnected():
                return ''
        return user.getName()

    def getUserClanAbbrev(self, userDbID):
        return self.getContact(userDbID).getClanAbbrev()

    def getUserRegionCode(self, userDbID):
        return self.lobbyContext.getRegionCode(userDbID)

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

    def getGuiUserName(self, userID, formatter=lambda v: v, scope=UserEntityScope.LOBBY):
        userName = self.getUserName(userID, scope=scope)
        return formatter(userName) if userName else ''

    def getGuiUserRating(self, userDbID, formatter=lambda v: v):
        userRating = self.getUserRating(userDbID)
        return formatter(shared_fmts.getGlobalRatingFmt(userRating)) if userRating != '0' else '-1'

    def getUserTags(self, userID, igrType):
        contact = self.users.getUser(userID, scope=UserEntityScope.BATTLE)
        if contact is not None:
            userTags = contact.getTags()
        else:
            userTags = set()
        if igrType == IGR_TYPE.BASE:
            userTags.add(USER_TAG.IGR_BASE)
        elif igrType == IGR_TYPE.PREMIUM:
            userTags.add(USER_TAG.IGR_PREMIUM)
        return userTags

    def syncUsersInfo(self):
        if self._invalid['names']:
            self._rqCtrl.requestNicknames(list(self._invalid['names']), lambda names, _: self.onUserNamesReceived(names))
        if self._invalid['ratings']:
            self._rqCtrl.requestGlobalRatings(list(self._invalid['ratings']), self.onUserRatingsReceived)
        self._invalid.clear()
