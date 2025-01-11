# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/account_helpers/paragons_storage.py
import typing
from Event import Event
from account_helpers.account_data_cache import AccountDataStorage
from paragons_common import BaseParagonsStorage
if typing.TYPE_CHECKING:
    from typing import Dict

class ParagonsStorage(BaseParagonsStorage):

    def __init__(self):
        self.onParagonsStateChanged = Event()
        self.onLevelIncreased = Event()
        self.onParagonsUnlocksGranted = Event()
        self.__accountDataFields = {'paragonsUnlocks': self.onParagonsUnlocksGranted}
        self.__accountDataCache = AccountDataStorage('paragons', onAccountDataChangeCallback=self.__onAccountDataChange)
        super(ParagonsStorage, self).__init__(self.__accountDataCache.accountData)

    @property
    def accountDataCache(self):
        return self.__accountDataCache

    def clear(self):
        self.onParagonsStateChanged.clear()
        self.onLevelIncreased.clear()
        self.onParagonsUnlocksGranted.clear()
        self.__accountDataFields.clear()
        self.__accountDataCache.clear()

    def synchronize(self, isFullSync, diff):
        if self.__accountDataCache.isSynchronizationNeeded(diff):
            previousLevel = None
            if not isFullSync:
                previousLevel = self.getProgress()
            self.__accountDataCache.synchronize(isFullSync, diff)
            if not isFullSync:
                level = self.getProgress()
                if level > previousLevel:
                    self.onLevelIncreased(level)
        return

    def __onAccountDataChange(self, accountDataDiff):
        self.onParagonsStateChanged()
        for fieldName, onFieldChangeEvent in self.__accountDataFields.items():
            if fieldName in accountDataDiff:
                onFieldChangeEvent(self.__accountDataCache.accountData[fieldName])
