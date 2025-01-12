# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/persistent_data_cache_common/events.py
from Event import EventManager, SafeEvent

class DefaultPDCEventsDispatcher(object):
    __slots__ = ('onDataDeserialized', 'onCachedDataLoaded', 'onFailedToLoadCachedData', 'onCachedDataSaved', 'onFailedToSaveCachedData', '_manager', 'onCacheDataSavingStarted')

    def __init__(self):
        super(DefaultPDCEventsDispatcher, self).__init__()
        self._manager = EventManager()
        self.onDataDeserialized = SafeEvent(self._manager)
        self.onCachedDataLoaded = SafeEvent(self._manager)
        self.onFailedToLoadCachedData = SafeEvent(self._manager)
        self.onCacheDataSavingStarted = SafeEvent(self._manager)
        self.onCachedDataSaved = SafeEvent(self._manager)
        self.onFailedToSaveCachedData = SafeEvent(self._manager)

    def fini(self):
        if self._manager:
            self._manager.clear()
            self._manager = None
        return
