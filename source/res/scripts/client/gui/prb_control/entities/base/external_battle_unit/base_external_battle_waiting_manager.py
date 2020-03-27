# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/base/external_battle_unit/base_external_battle_waiting_manager.py
import logging
from gui.Scaleform.Waiting import Waiting
from gui.prb_control.settings import REQUEST_TYPE
REQUEST_HANDLER = {REQUEST_TYPE.SET_RESERVE,
 REQUEST_TYPE.UNSET_RESERVE,
 REQUEST_TYPE.CHANGE_OPENED,
 REQUEST_TYPE.SET_VEHICLE,
 REQUEST_TYPE.BATTLE_QUEUE}
_logger = logging.getLogger(__name__)

class BaseExternalUnitWaitingManager(object):

    def __init__(self):
        super(BaseExternalUnitWaitingManager, self).__init__()
        self.__waitingRequestID = None
        self.__waitingID = ''
        return

    def processRequest(self, ctx):
        waitingID = ctx.getWaitingID()
        if not waitingID:
            return
        else:
            requestType = ctx.getRequestType()
            if requestType in REQUEST_HANDLER:
                _logger.debug('Show waitingID = %s' + waitingID)
                Waiting.show(waitingID)
                ctx.setWaitingID('')
                self.__waitingID = waitingID
                self.__waitingRequestID = None
            return

    def stopRequest(self):
        if self.__waitingID:
            _logger.debug('Hide waitingID = %s' + self.__waitingID)
            Waiting.hide(self.__waitingID)
            self.__waitingID = ''
            self.__waitingRequestID = None
        return

    def onResponseWebReqID(self, webReqID):
        self.__processResponse(webReqID)

    def onResponseError(self):
        self.stopRequest()

    def __processResponse(self, requestID):
        if self.__waitingID:
            if self.__waitingRequestID is None:
                self.__waitingRequestID = requestID
            elif requestID >= self.__waitingRequestID:
                self.stopRequest()
        return
