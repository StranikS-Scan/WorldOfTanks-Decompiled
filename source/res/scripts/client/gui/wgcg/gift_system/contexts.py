# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/wgcg/gift_system/contexts.py
import logging
import time
import typing
from gui.gift_system.wrappers import GiftsWebState, SendGiftResponse
from gui.wgcg.base.contexts import CommonWebRequestCtx
from gui.wgcg.settings import WebRequestDataType
from shared_utils import makeTupleByDict
_logger = logging.getLogger(__name__)

def _packEventWebState(eventData):
    if eventData is None or not isinstance(eventData, dict):
        return
    else:
        try:
            result = {'sendLimit': eventData['send_limit'],
             'expireTime': eventData['expiration_time'],
             'expireDelta': eventData['expiration_delta'],
             'executionTime': eventData['execution_time'],
             'state': eventData['state']}
            result = makeTupleByDict(GiftsWebState, result)
        except (KeyError, TypeError):
            _logger.exception('Can not _packEventWebState because of invalid eventData')
            result = None

        return result


class GiftSystemStateCtx(CommonWebRequestCtx):

    def __init__(self, reqEventIds, waitingID=''):
        super(GiftSystemStateCtx, self).__init__(waitingID)
        self.__reqEventIds = reqEventIds

    def isAuthorizationRequired(self):
        return True

    def isClanSyncRequired(self):
        return False

    def isCaching(self):
        return False

    def getRequestType(self):
        return WebRequestDataType.GIFT_SYSTEM_STATE

    def getReqEventIds(self):
        return self.__reqEventIds

    def getDataObj(self, incomeData):
        return self.getDefDataObj() if incomeData is None or not isinstance(incomeData, dict) else {eventID:_packEventWebState(incomeData.get(str(eventID))) for eventID in self.__reqEventIds}

    def getDefDataObj(self):
        return {eventID:None for eventID in self.__reqEventIds}


class GiftSystemSendGiftCtx(CommonWebRequestCtx):

    def __init__(self, entitlementCode, receiverID=0, metaInfo=None, waitingID=''):
        super(GiftSystemSendGiftCtx, self).__init__(waitingID)
        self.__entitlementCode = entitlementCode
        self.__metaInfo = metaInfo or {}
        self.__receiverID = receiverID

    def isAuthorizationRequired(self):
        return True

    def isClanSyncRequired(self):
        return False

    def isCaching(self):
        return False

    def getRequestType(self):
        return WebRequestDataType.GIFT_SYSTEM_POST_GIFT

    def getEntitlementCode(self):
        return self.__entitlementCode

    def getMetaInfo(self):
        return self.__metaInfo

    def getReceiverID(self):
        return self.__receiverID

    def getDataObj(self, state, incomeData=None):
        resultData = self.getDefDataObj(state)
        if incomeData is not None and isinstance(incomeData, dict):
            resultData['outCount'] = incomeData.get('outcoming', resultData['outCount'])
            resultData['executionTime'] = incomeData.get('execution_time', resultData['executionTime'])
        return makeTupleByDict(SendGiftResponse, resultData)

    def getDefDataObj(self, state):
        return {'state': state,
         'outCount': None,
         'meta': self.__metaInfo,
         'receiverID': self.__receiverID,
         'entitlementCode': self.__entitlementCode,
         'executionTime': int(time.time())}
