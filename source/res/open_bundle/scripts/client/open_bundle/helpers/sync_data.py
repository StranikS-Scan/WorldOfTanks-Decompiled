# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: open_bundle/scripts/client/open_bundle/helpers/sync_data.py
from __future__ import absolute_import
import typing
from account_helpers import AccountSyncData
from open_bundle_common.constants import OPEN_BUNDLE_PDATA_KEY
from shared_utils.account_helpers.diff_utils import synchronizeDicts
if typing.TYPE_CHECKING:
    from typing import Dict

class OpenBundleSyncData(object):

    def __init__(self):
        self.__cache = {}

    def clear(self):
        self.__cache.clear()

    def update(self, clientDiff):
        isFullSync = AccountSyncData.isFullSyncDiff(clientDiff)
        if isFullSync:
            self.__cache.clear()
        synchronizeDicts(clientDiff[OPEN_BUNDLE_PDATA_KEY], self.__cache)

    def getTrackedByNameSections(self, bundleID):
        return (self.__cache.get(bundleID) or {}).get('trackedByNameSections') or {}
