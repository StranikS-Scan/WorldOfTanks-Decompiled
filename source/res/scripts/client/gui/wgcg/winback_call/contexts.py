# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/wgcg/winback_call/contexts.py
import logging
from gui.wgcg.base.contexts import CommonWebRequestCtx
from gui.wgcg.settings import WebRequestDataType
_logger = logging.getLogger(__name__)

class _WinBackCallServiceCtx(CommonWebRequestCtx):

    def isAuthorizationRequired(self):
        return True

    def isClanSyncRequired(self):
        return False

    def isCaching(self):
        return False


class WinBackCallFriendListCtx(_WinBackCallServiceCtx):

    def getRequestType(self):
        return WebRequestDataType.WIN_BACK_CALL_FRIENDS


class WinBackCallSendInviteCodeCtx(_WinBackCallServiceCtx):

    def __init__(self, spaID, waitingID=''):
        super(WinBackCallSendInviteCodeCtx, self).__init__(waitingID)
        self.__spaID = spaID

    def getRequestType(self):
        return WebRequestDataType.WIN_BACK_CALL_SEND_INVITE_CODE

    def getSpaID(self):
        return self.__spaID
