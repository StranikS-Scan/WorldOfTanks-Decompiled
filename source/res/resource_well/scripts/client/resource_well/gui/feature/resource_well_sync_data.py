# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: resource_well/scripts/client/resource_well/gui/feature/resource_well_sync_data.py
from typing import Dict
from account_helpers import AccountSyncData
from resource_well_common.feature_constants import RESOURCE_WELL_PDATA_KEY
from shared_utils.account_helpers.diff_utils import synchronizeDicts

class ResourceWellSyncData(object):

    def __init__(self):
        self.__cache = {}

    def clear(self):
        self.__cache.clear()

    def getSeason(self):
        return self.__cache.get('season', 0)

    def getCurrentPoints(self):
        return self.__cache.get('points', 0)

    def getBalance(self):
        return self.__cache.get('balance', {})

    def getReward(self):
        return self.__cache.get('reward', set())

    def getCurrentRewardID(self):
        return self.__cache.get('currentRewardId', '')

    def getInitialNumberAmounts(self):
        return self.__cache.get('initialAmounts', {})

    def update(self, clientDiff):
        isFullSync = AccountSyncData.isFullSyncDiff(clientDiff)
        if isFullSync:
            self.__cache.clear()
        synchronizeDicts(clientDiff[RESOURCE_WELL_PDATA_KEY], self.__cache)
