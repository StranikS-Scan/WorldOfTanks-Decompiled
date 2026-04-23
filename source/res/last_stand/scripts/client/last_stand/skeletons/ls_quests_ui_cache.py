# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/skeletons/ls_quests_ui_cache.py
from __future__ import absolute_import
import typing
from skeletons.gui.game_control import IGameController
if typing.TYPE_CHECKING:
    from Event import Event
    from gui.server_events.event_items import Quest
    from typing import Optional, Dict, Callable

class ILSQuestsUICache(IGameController):
    onCacheUpdated = None
    onSyncCompleted = None

    def getQuests(self, filterFunc=None):
        raise NotImplementedError
