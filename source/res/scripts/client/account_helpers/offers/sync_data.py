# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/account_helpers/offers/sync_data.py
from account_helpers.AccountSyncData import BaseSyncDataCache
from shared_utils.account_helpers.diff_utils import synchronizeDicts

class OffersSyncData(BaseSyncDataCache):

    def _synchronize(self, diff):
        itemDiff = diff.get('offersData')
        if itemDiff is not None:
            synchronizeDicts(itemDiff, self._cache.setdefault('offersData', {}))
        return
