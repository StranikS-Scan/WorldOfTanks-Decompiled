# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/account_helpers/portal.py
import typing
from Event import Event
from account_helpers.account_data_cache import AccountDataStorage
from portal_common.portal_constants import PDATA_KEY_PORTAL_BATTLES, PORTAL_MAX_COMPLEXITY_KEY
if typing.TYPE_CHECKING:
    from typing import Dict

class Portal(object):

    def __init__(self):
        self.onMaxComplexityLevelIncreased = Event()
        self.__accountDataCache = AccountDataStorage(PDATA_KEY_PORTAL_BATTLES, onAccountDataChangeCallback=self.__onAccountDataChanged)

    def clear(self):
        self.onMaxComplexityLevelIncreased.clear()
        self.__accountDataCache.clear()

    @property
    def _data(self):
        return self.__accountDataCache.accountData

    def getMaxComplexityLevel(self):
        return self._data.get(PORTAL_MAX_COMPLEXITY_KEY, 1)

    def synchronize(self, isFullSync, diff):
        if self.__accountDataCache.isSynchronizationNeeded(diff):
            previousLevel = None
            if not isFullSync:
                previousLevel = self.getMaxComplexityLevel()
            self.__accountDataCache.synchronize(isFullSync, diff)
            if not isFullSync:
                level = self.getMaxComplexityLevel()
                if level > previousLevel:
                    self.onMaxComplexityLevelIncreased(level)
        return

    def __onAccountDataChanged(self, accountData):
        pass
