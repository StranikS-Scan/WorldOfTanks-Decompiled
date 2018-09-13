# Embedded file name: scripts/client/SyncController.py
import BigWorld
import AccountCommands
import cPickle
import zlib
from functools import partial
from debug_utils import *

class SyncController:
    __STREAM_ERRORS_LIMIT = 3

    def __init__(self, account, sendSyncRequest, onSyncResponse, onSyncComplete):
        self.__account = account
        self.__sendSyncRequest = sendSyncRequest
        self.__onOwnerSyncResponse = onSyncResponse
        self.__onOwnerSyncComplete = onSyncComplete
        self.__syncRequests = {}
        self.__streamErrors = {}

    def destroy(self):
        self.__syncRequests.clear()
        self.__onOwnerSyncComplete = None
        self.__onOwnerSyncResponse = None
        self.__sendSyncRequest = None
        self.__account = None
        return

    def request(self, syncID, callback):
        isFirstRequest = syncID not in self.__syncRequests
        callbackList = self.__syncRequests.setdefault(syncID, [])
        if callback is not None:
            callbackList.append(callback)
        if isFirstRequest:
            self.__sendSyncRequest(syncID, partial(self.__onSyncResponse, syncID))
        return

    def __onSyncResponse(self, syncID, requestID, resultID, errorStr, ext = {}):
        if resultID != AccountCommands.RES_STREAM:
            self.__onOwnerSyncResponse(syncID, resultID, ext)
            for callback in self.__syncRequests.pop(syncID, []):
                try:
                    callback(resultID, ext)
                except:
                    LOG_CURRENT_EXCEPTION()

        else:
            self.__account._subscribeForStream(requestID, partial(self.__onSyncStreamComplete, syncID))

    def __onSyncStreamComplete(self, syncID, isSuccess, data):
        if isSuccess:
            try:
                data = zlib.decompress(data)
                data = cPickle.loads(data)
            except:
                if data is None:
                    LOG_CODEPOINT_WARNING()
                else:
                    LOG_CURRENT_EXCEPTION()
                errors = self.__streamErrors.setdefault(syncID, 0) + 1
                if errors >= self.__STREAM_ERRORS_LIMIT:
                    LOG_ERROR('Too many errors in data stream. Disconnecting.', errors, syncID)
                    BigWorld.callback(0.001, BigWorld.disconnect)
                    return
                self.__streamErrors[syncID] = errors
                self.__sendSyncRequest(syncID, partial(self.__onSyncResponse, syncID))
                return

        self.__onOwnerSyncComplete(syncID, data)
        for callback in self.__syncRequests.pop(syncID, []):
            try:
                callback(AccountCommands.RES_STREAM, data)
            except:
                LOG_CURRENT_EXCEPTION()

        return
