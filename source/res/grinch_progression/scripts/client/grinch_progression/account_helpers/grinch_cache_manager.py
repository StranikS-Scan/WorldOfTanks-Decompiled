# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch_progression/scripts/client/grinch_progression/account_helpers/grinch_cache_manager.py
import logging
from shared_utils.account_helpers.diff_utils import synchronizeDicts
from shared_utils import CONST_CONTAINER
_logger = logging.getLogger(__name__)
PDATA_KEY = 'grinchProgression'

class SyncDataKeys(CONST_CONTAINER):
    PROGRESSION = 'progression'
    LAST_CHAPTER_ID = 'lastChapterID'
    LAST_STEP_ID = 'lastStepID'


class GrinchCacheManager(object):

    def __init__(self):
        self.__cache = {}

    def onDisconnected(self):
        self.__cache.clear()

    def synchronize(self, isFullSync, diff):
        if isFullSync:
            self.__cache.clear()
        itemDiff = diff.get(PDATA_KEY, None)
        _logger.debug('Syncing cache for key %s: %s', PDATA_KEY, itemDiff)
        if itemDiff is not None:
            synchronizeDicts(itemDiff, self.__cache)
        return

    def getProgression(self):
        return self.__cache.get(SyncDataKeys.PROGRESSION, {})

    def getLastChapterID(self):
        return self.__cache.get(SyncDataKeys.LAST_CHAPTER_ID, 0)

    def getLastStepID(self):
        return self.__cache.get(SyncDataKeys.LAST_STEP_ID, 0)
