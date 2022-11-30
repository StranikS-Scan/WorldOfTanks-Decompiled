# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/wgcg/friends_service/contexts.py
import logging
from gui.wgcg.base.contexts import CommonWebRequestCtx
from gui.wgcg.settings import WebRequestDataType
_logger = logging.getLogger(__name__)

class _FriendServiceCtx(CommonWebRequestCtx):

    def isAuthorizationRequired(self):
        return True

    def isClanSyncRequired(self):
        return False

    def isCaching(self):
        return False


class _SpaIdCtx(_FriendServiceCtx):

    def __init__(self, spaId, waitingID=''):
        super(_SpaIdCtx, self).__init__(waitingID)
        self.__spaId = spaId

    def getSpaId(self):
        return self.__spaId


class FriendStateCtx(_SpaIdCtx):

    def getRequestType(self):
        return WebRequestDataType.FRIEND_STATE


class FriendListCtx(_FriendServiceCtx):

    def getRequestType(self):
        return WebRequestDataType.FRIEND_LIST


class PutBestFriendCtx(_SpaIdCtx):

    def getRequestType(self):
        return WebRequestDataType.PUT_BEST_FRIEND


class DeleteBestFriendCtx(_SpaIdCtx):

    def getRequestType(self):
        return WebRequestDataType.DELETE_BEST_FRIEND


class GatherFriendsResourcesCtx(_SpaIdCtx):

    def getRequestType(self):
        return WebRequestDataType.POST_GATHER_FRIEND_NY_RESOURCES
