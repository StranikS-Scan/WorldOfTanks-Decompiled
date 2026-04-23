# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/game_control/ls_quests_ui_cache.py
from __future__ import absolute_import
import typing
from Event import Event
from future.utils import viewitems
from constants import EVENT_CLIENT_DATA
from gui.ClientUpdateManager import g_clientUpdateManager
from helpers import dependency
from last_stand.skeletons.ls_quests_ui_cache import ILSQuestsUICache
from last_stand_common.last_stand_constants import LS_QUESTS_PREFIX
from skeletons.gui.server_events import IEventsCache
if typing.TYPE_CHECKING:
    from typing import Optional, Dict, Callable
    from gui.server_events.event_items import Quest
    from gui.shared.events import GUICommonEvent

class LSQuestsUICache(ILSQuestsUICache):
    _eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self):
        super(LSQuestsUICache, self).__init__()
        self._cache = {}
        self.onCacheUpdated = Event()
        self.onSyncCompleted = Event()

    def fini(self):
        super(LSQuestsUICache, self).fini()
        g_clientUpdateManager.removeObjectCallbacks(self)
        self._eventsCache.onSyncCompleted -= self._onSyncCompleted
        self.onCacheUpdated.clear()
        self.onSyncCompleted.clear()
        self._cache.clear()

    def getQuests(self, filterFunc=None):
        return {questID:quest for questID, quest in viewitems(self._cache) if filterFunc(quest)} if filterFunc is not None else self._cache

    def onLobbyStarted(self, ctx):
        super(LSQuestsUICache, self).onLobbyStarted(ctx)
        g_clientUpdateManager.addCallbacks({'eventsData.' + str(EVENT_CLIENT_DATA.QUEST): self._onQuestsUpdated})
        self._eventsCache.onSyncCompleted += self._onSyncCompleted
        self._updateCache()

    def _onQuestsUpdated(self, _):
        self._updateCache()

    def _updateCache(self):
        self._cache = self._eventsCache.getAllQuests(filterFunc=lambda q: q.getID().startswith(LS_QUESTS_PREFIX))
        self.onCacheUpdated()

    def _onSyncCompleted(self, *_):
        self._updateCache()
        self.onSyncCompleted()
