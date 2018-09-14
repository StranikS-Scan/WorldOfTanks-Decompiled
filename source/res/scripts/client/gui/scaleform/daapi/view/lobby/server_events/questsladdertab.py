# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/server_events/QuestsLadderTab.py
import re
from gui.Scaleform.daapi.view.lobby.server_events import events_helpers
from gui.server_events import g_eventsCache
from constants import EVENT_TYPE
from gui.Scaleform.daapi.view.lobby.server_events.QuestsCurrentTab import QuestsCurrentTab

class QuestsLadderTab(QuestsCurrentTab):

    def __init__(self):
        super(QuestsLadderTab, self).__init__()

    @staticmethod
    def getDivisionByName(name):
        return int(re.findall('\\d+', name)[0])

    @classmethod
    def _getEvents(cls):
        return g_eventsCache.getQuests(lambda x: x.getType() == EVENT_TYPE.CLUBS_QUEST)

    def _invalidateEventsData(self):
        svrEvents = self._getEvents()
        result = []
        for e in self._applyFilters(svrEvents.values()):
            result.append(events_helpers.getEventInfo(e, svrEvents))

        self.as_setQuestsDataS({'quests': result,
         'isSortable': False,
         'totalTasks': len(svrEvents)})

    def _filterFunc(self, a):
        return not self._hideCompleted or not a.isCompleted()

    @classmethod
    def _sortFunc(cls, a, b):
        res = cmp(a.isCompleted(), b.isCompleted())
        if res:
            return res
        return cmp(cls.getDivisionByName(a.getUserName()), cls.getDivisionByName(b.getUserName()))
