# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/LSAccountComponent.py
import AccountCommands
from BaseAccountExtensionComponent import BaseAccountExtensionComponent
from PlayerEvents import g_playerEvents as events
from helpers import dependency
from last_stand_common import last_stand_constants
from last_stand_common.ls_account_commands import CMD_LS_UNLOCK_TOKEN, CMD_LS_LOCK_TOKEN, CMD_LS_ARTEFACT_OPEN, CMD_LS_BUY_BUNDLE
from shared_utils.account_helpers.diff_utils import synchronizeDicts
from skeletons.connection_mgr import IConnectionManager

class LSInfoSessionCache(object):
    DATA_KEY = last_stand_constants.LS_INFO_PDATA_KEY
    cache = None

    @classmethod
    def vehicleDailyCompleted(cls):
        return cls.cache.get(cls.DATA_KEY, {}).get('vehicleDaily', {}).get(cls.curDay(), set())

    @classmethod
    def curDay(cls):
        return cls.cache.get(cls.DATA_KEY, {}).get('curDay')

    @classmethod
    def init(cls):
        if cls.cache is not None:
            return
        else:
            cls.cache = {}
            events.onClientSynchronize += cls._onClientSynchronize
            connectionMgr = dependency.instance(IConnectionManager)
            connectionMgr.onDisconnected += cls.__deleteInstance
            return

    @classmethod
    def _onClientSynchronize(cls, isFullSync, diff):
        cache = cls.cache
        if isFullSync:
            cache.clear()
        dataResetKey = (cls.DATA_KEY, '_r')
        if dataResetKey in diff:
            cache[cls.DATA_KEY] = diff[dataResetKey]
        if cls.DATA_KEY in diff:
            synchronizeDicts(diff[cls.DATA_KEY], cache.setdefault(cls.DATA_KEY, {}))

    @classmethod
    def __deleteInstance(cls):
        cls.cache = None
        events.onClientSynchronize -= cls._onClientSynchronize
        connectionMgr = dependency.instance(IConnectionManager)
        connectionMgr.onDisconnected -= cls.__deleteInstance
        return


class LSAccountComponent(BaseAccountExtensionComponent):

    def __init__(self):
        super(LSAccountComponent, self).__init__()
        LSInfoSessionCache.init()

    @property
    def vehicleDailyCompleted(self):
        return LSInfoSessionCache.vehicleDailyCompleted()

    @property
    def curDay(self):
        return LSInfoSessionCache.curDay()

    def enqueueBattle(self, queueType, vehInvID):
        if not events.isPlayerEntityChanging:
            self.base.doCmdIntArr(AccountCommands.REQUEST_ID_NO_RESPONSE, AccountCommands.CMD_ENQUEUE_IN_BATTLE_QUEUE, (queueType, vehInvID))

    def dequeueBattle(self, queueType):
        if not events.isPlayerEntityChanging:
            self.base.doCmdInt(AccountCommands.REQUEST_ID_NO_RESPONSE, AccountCommands.CMD_DEQUEUE_FROM_BATTLE_QUEUE, queueType)

    def unlockToken(self, token, tokenCount=1, callback=None):
        if callback is not None:
            proxy = lambda requestID, resultID, errorStr, ext={}: callback(resultID)
        else:
            proxy = None
        self.account._doCmdIntStr(CMD_LS_UNLOCK_TOKEN, tokenCount, token, proxy)
        return

    def lockToken(self, token, callback=None):
        if callback is not None:
            proxy = lambda requestID, resultID, errorStr, ext={}: callback(resultID)
        else:
            proxy = None
        self.account._doCmdStr(CMD_LS_LOCK_TOKEN, token, proxy)
        return

    def openArtefact(self, artefactID, isSkipQuest, callback=None):
        if callback is not None:
            proxy = lambda requestID, resultID, errorStr, ext={}: callback(requestID, resultID, errorStr)
        else:
            proxy = None
        self.account._doCmdInt2Str(CMD_LS_ARTEFACT_OPEN, self.account.shop.getCacheRevision(), int(isSkipQuest), artefactID, proxy)
        return

    def buyBundle(self, bundleID, count=1, callback=None):
        if callback is not None:
            proxy = lambda requestID, resultID, errorStr, ext={}: callback(requestID, resultID, errorStr)
        else:
            proxy = None
        self.account._doCmdInt2Str(CMD_LS_BUY_BUNDLE, self.account.shop.getCacheRevision(), int(count), bundleID, proxy)
        return
