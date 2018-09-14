# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/stronghold/unit/waiting.py
import BigWorld
from gui.Scaleform.Waiting import Waiting
from gui.prb_control.settings import REQUEST_TYPE
from debug_utils import LOG_DEBUG
REQUEST_HANDLER = {REQUEST_TYPE.SET_RESERVE,
 REQUEST_TYPE.UNSET_RESERVE,
 REQUEST_TYPE.CHANGE_OPENED,
 REQUEST_TYPE.SET_VEHICLE,
 REQUEST_TYPE.BATTLE_QUEUE}

class WaitingManager(object):
    """
    WaitingManager provide context waiting-screen manual control case:
    - Wait equal request IDs (from WGSH and SERVER) for handle WGSH response and Server Unit
    """

    def __init__(self):
        super(WaitingManager, self).__init__()
        self.__waitingRequestID = None
        self.__waitingID = ''
        return

    def processRequest(self, ctx):
        waitingID = ctx.getWaitingID()
        if len(waitingID) == 0:
            return
        else:
            requestType = ctx.getRequestType()
            if requestType in REQUEST_HANDLER:
                LOG_DEBUG('Show waitingID = ' + waitingID)
                Waiting.show(waitingID)
                ctx.setWaitingID('')
                self.__waitingID = waitingID
                self.__waitingRequestID = None
            return

    def stopRequest(self):
        if len(self.__waitingID):
            LOG_DEBUG('Hide waitingID = ' + self.__waitingID)
            Waiting.hide(self.__waitingID)
            self.__waitingID = ''
            self.__waitingRequestID = None
        return

    def onResponseWebReqID(self, webReqID):
        self.__processResponse(webReqID)

    def onResponseError(self):
        self.stopRequest()

    def __processResponse(self, requestID):
        if len(self.__waitingID):
            if self.__waitingRequestID is None:
                self.__waitingRequestID = requestID
            elif requestID >= self.__waitingRequestID:
                self.stopRequest()
        return
