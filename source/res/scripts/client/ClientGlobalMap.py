# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/ClientGlobalMap.py
from GlobalMapBase import GlobalMapBase, GM_CLIENT_METHOD
from debug_utils import LOG_DEBUG_DEV
import Event

class ClientGlobalMap(GlobalMapBase):

    def __init__(self, account=None):
        self.__account = account
        self.__eManager = Event.EventManager()
        GlobalMapBase.__init__(self)
        self.__requestID = 0

    def clear(self):
        self.__eManager.clear()

    def setAccount(self, account=None):
        self.__account = account

    def __getNextRequestID(self):
        self.__requestID += 1
        return self.__requestID

    def __callGlobalMapMethod(self, *args):
        requestID = self.__getNextRequestID()
        LOG_DEBUG_DEV('base.callGlobalMapMethod', requestID, args)
        self.__account.base.accountGlobalMapConnector_callGlobalMapMethod(requestID, *args)
        return requestID

    def onGlobalMapReply(self, reqID, resultCode, resultString):
        LOG_DEBUG_DEV('onGlobalMapReply: reqID=%s, resultCode=%s, resultString=%r' % (reqID, resultCode, resultString))

    def subscribe(self):
        return self.__callGlobalMapMethod(GM_CLIENT_METHOD.SUBSCRIBE, 0, '')

    def unsubscribe(self):
        return self.__callGlobalMapMethod(GM_CLIENT_METHOD.UNSUBSCRIBE, 0, '')

    def joinBattle(self, battleID):
        return self.__callGlobalMapMethod(GM_CLIENT_METHOD.JOIN_BATTLE, battleID, '')

    def setDevMode(self, isOn):
        return self.__callGlobalMapMethod(GM_CLIENT_METHOD.SET_DEV_MODE, int(isOn), '')

    def keepAlive(self):
        return self.__callGlobalMapMethod(GM_CLIENT_METHOD.KEEP_ALIVE, 0, '')

    def onGlobalMapUpdate(self, packedOps, packedUpdate):
        LOG_DEBUG_DEV('onGlobalMapUpdate: packedOps len=%s, packedUpdate len=%s' % (len(packedOps), len(packedUpdate)))
        if packedUpdate:
            self.unpack(packedUpdate)
        elif packedOps:
            self.unpackOps(packedOps)

    def _unpackBattle(self, packedData):
        LOG_DEBUG_DEV('_unpackBattle: packedData len=%s' % (len(packedData),))
        packedData = GlobalMapBase._unpackBattle(self, packedData)
        return packedData

    def _removeBattle(self, battleID):
        LOG_DEBUG_DEV('_removeBattle: battleID=%s' % (battleID,))
        GlobalMapBase._removeBattle(self, battleID)

    def _unpackBattleUnit(self, packedData):
        LOG_DEBUG_DEV('_unpackBattleUnit: packedData len=%s' % (len(packedData),))
        packedData = GlobalMapBase._unpackBattleUnit(self, packedData)
        return packedData

    def _removeBattleUnit(self, battleID):
        LOG_DEBUG_DEV('_removeBattleUnit: battleID=%s' % (battleID,))
        GlobalMapBase._removeBattleUnit(self, battleID)
