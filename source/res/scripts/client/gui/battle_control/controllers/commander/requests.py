# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/commander/requests.py
from typing import TYPE_CHECKING
import time
import logging
from enum import Enum
import BigWorld
import Math
from RTSShared import RTSQuery, RTSQueryResult, RTSQueryResultCode, packerVector
from wotdecorators import noexcept
from gui.battle_control.controllers.commander.interfaces import IRequester
if TYPE_CHECKING:
    from typing import Any, Callable, Dict, Optional
_logger = logging.getLogger(__name__)

class _RequestType(Enum):
    UPDATE_ORDER, UPDATE_GROUP, QUERY = range(3)


class Requester(IRequester):
    _REQUEST_SIZE = 7
    _COMPANIONS_SIZE = 7
    _QUERY_EXPIRE_TIME = 60
    _queryIDCounter = 0

    def __init__(self):
        super(Requester, self).__init__()
        self.__requests = {_RequestType.UPDATE_ORDER: [],
         _RequestType.UPDATE_GROUP: [],
         _RequestType.QUERY: []}
        self.__pendingQueries = {}

    @noexcept
    def updateTick(self):
        player = BigWorld.player()
        if player is None:
            return
        else:
            cell = player.cell
            for reqType, requests in self.__requests.iteritems():
                if requests:
                    sendData = None
                    if reqType == _RequestType.UPDATE_ORDER:
                        sendData = cell.updateRTSOrder
                    elif reqType == _RequestType.UPDATE_GROUP:
                        sendData = cell.updateRTSGroup
                    elif reqType == _RequestType.QUERY:
                        sendData = cell.queryRTSData
                    else:
                        _logger.error('Unknown request type %s', reqType)
                    if sendData is not None:
                        for i in range(0, len(requests), self._REQUEST_SIZE):
                            chunk = requests[i:i + self._REQUEST_SIZE]
                            if len(chunk) < self._REQUEST_SIZE:
                                chunk.extend([None] * (self._REQUEST_SIZE - len(chunk)))
                            sendData(chunk)

                    del requests[:]

            self.__checkQueryTimeouts()
            return

    def updateRTSOrder(self, vehicleID, order, manner, position, isPositionModified, target, heading, baseID, baseTeam, companions, commandID=0):
        if len(companions) < self._COMPANIONS_SIZE:
            companions.extend([-1] * (self._COMPANIONS_SIZE - len(companions)))
        self.__addRequest(_RequestType.UPDATE_ORDER, {'vehicleID': vehicleID,
         'order': order,
         'manner': manner,
         'position': position,
         'isPositionModified': isPositionModified,
         'target': target,
         'heading': heading,
         'baseID': baseID,
         'baseTeam': baseTeam,
         'companions': companions})

    def updateRTSGroup(self, vehicleID, groupID):
        self.__addRequest(_RequestType.UPDATE_GROUP, {'vehicleID': vehicleID,
         'groupID': groupID})

    def queryRTSData(self, vehicleID, queryType, context, callback):
        self._queryIDCounter += 1
        queryID = self._queryIDCounter
        position = context.get('position', None)
        companions = context.get('companions') or []
        if len(companions) < self._COMPANIONS_SIZE:
            companions.extend([-1] * (self._COMPANIONS_SIZE - len(companions)))
        self.__addRequest(_RequestType.QUERY, {'vehicleID': vehicleID,
         'queryID': queryID,
         'queryType': queryType.value,
         'packedPosition': packerVector.pack(position),
         'companions': companions})
        self.__pendingQueries[queryID] = {'vehicleID': vehicleID,
         'queryType': queryType,
         'callback': callback,
         'expireTime': time.time() + self._QUERY_EXPIRE_TIME}
        return queryID

    def cancelRTSQuery(self, queryID):
        if queryID in self.__pendingQueries:
            callbackData = self.__pendingQueries.pop(queryID)
            self.__dispatchRTSQueryResult(callbackData, queryID, RTSQueryResultCode.CANCELED)
            return True
        return False

    def onRTSQueryResult(self, queryResultsList):
        for queryResult in queryResultsList:
            queryID = queryResult.queryID
            if queryID in self.__pendingQueries:
                resultCode = RTSQueryResultCode(queryResult.resultCode)
                callbackData = self.__pendingQueries.pop(queryID)
                position = packerVector.unpack(queryResult.packedPosition)
                self.__dispatchRTSQueryResult(callbackData, queryID, resultCode, position)

    def __addRequest(self, key, args):
        self.__requests[key].append(args)

    def __checkQueryTimeouts(self):
        currentTime = time.time()
        for queryID, callbackData in list(self.__pendingQueries.items()):
            if callbackData['expireTime'] < currentTime:
                del self.__pendingQueries[queryID]
                self.__dispatchRTSQueryResult(callbackData, queryID, RTSQueryResultCode.TIMEOUT)

    @staticmethod
    def __dispatchRTSQueryResult(callbackData, queryID, resultCode, position=None):
        queryResultCallback = callbackData['callback']
        vehicleID = callbackData['vehicleID']
        queryType = callbackData['queryType']
        queryResultCallback(RTSQueryResult(queryID, queryType, vehicleID, resultCode, position))
