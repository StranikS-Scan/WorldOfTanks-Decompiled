# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: gui_lootboxes/scripts/client/gui_lootboxes/gui/statistic_helpers/pdata_fetcher.py
import BigWorld
import AccountCommands
from account_helpers.SyncController import SyncController
from debug_utils import LOG_DEBUG, LOG_ERROR
from gui_lootboxes.gui.statistic_helpers.statistic_data_provider import LootBoxStatFetcher

class LBPDataFetcher(LootBoxStatFetcher):

    def __init__(self, storage):
        super(LBPDataFetcher, self).__init__(storage)
        self.__account = None
        self.__syncController = None
        self.__syncID = 0
        self.__isSynchronizing = False
        self.__ignore = False
        return

    def onAccountBecomePlayer(self):
        self.__setAccount(BigWorld.player())
        self.__ignore = False

    def onAccountBecomeNonPlayer(self):
        self.__ignore = True
        self.__isSynchronizing = False

    def requestData(self, callback=None):
        if not self.__canRequest():
            if callback:
                callback(None, {})
            return
        else:
            self._request(callback=callback)
            return

    def processResult(self, _, data):
        if data:
            self._storage.fillCache(data)

    def onServerSettingsChanged(self, diff):
        if diff['enabled']:
            self.__ignore = False

    def __setAccount(self, account):
        self.__account = account
        if self.__syncController is not None:
            self.__syncController.destroy()
            self.__syncController = None
        if account is not None:
            self.__syncController = SyncController(account, self.__sendSyncRequest, self.__onSyncResponse, self.__onSyncComplete)
        return

    def _request(self, callback=None):
        if not self.__canRequest():
            return
        self.__isSynchronizing = True
        self.__syncController.request(self.__getNextSyncID(), callback)

    def __canRequest(self):
        if self.__ignore:
            return False
        return False if self.__isSynchronizing else True

    def __sendSyncRequest(self, syncID, proxy):
        if self.__ignore:
            return
        self.__account._doCmdInt(AccountCommands.CMD_GET_STATISTIC_LOOTBOX, 0, proxy)

    def __onSyncResponse(self, syncID, resultID, ext):
        if resultID == AccountCommands.RES_NON_PLAYER:
            return
        if resultID in (AccountCommands.RES_NOT_AVAILABLE, AccountCommands.RES_COOLDOWN):
            self.__isSynchronizing = False
            return
        if resultID == AccountCommands.RES_DISABLED:
            self.__ignore = True
            self.__isSynchronizing = False
            return
        if syncID != self.__syncID:
            return
        if resultID < 0:
            LOG_ERROR('Synchronization failed. Repeating')
            self._request()
            return

    def __onSyncComplete(self, syncID, statData):
        if statData is None:
            return
        else:
            LOG_DEBUG('PDataFetcher.onSyncComplete')
            if syncID == self.__syncID:
                self.__isSynchronizing = False
            return

    def __getNextSyncID(self):
        self.__syncID += 1
        if self.__syncID > 30000:
            self.__syncID = 1
        return self.__syncID
