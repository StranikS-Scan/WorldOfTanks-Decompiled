# Embedded file name: scripts/client/gui/server_events/__init__.py
import BigWorld
from debug_utils import LOG_DEBUG
from gui.server_events.EventsCache import g_eventsCache

def isPotapovQuestEnabled():
    try:
        return BigWorld.player().serverSettings['isPotapovQuestEnabled']
    except Exception:
        LOG_DEBUG('There is problem while getting potapov quests supporting flag.Availability value is default')
        return False
