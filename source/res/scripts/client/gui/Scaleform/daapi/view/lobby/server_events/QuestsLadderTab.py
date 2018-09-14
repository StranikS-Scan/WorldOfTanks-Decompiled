# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/server_events/QuestsLadderTab.py
import re
from collections import defaultdict
from gui.clubs import formatters as club_fmts
from gui.Scaleform.daapi.view.lobby.server_events import events_helpers
from gui.server_events import g_eventsCache, formatters as event_fmts
from constants import EVENT_TYPE
from gui.Scaleform.daapi.view.lobby.server_events.QuestsCurrentTab import QuestsCurrentTab

def _getGroupDividerImage(league):
    return '../maps/icons/quests/leagueDividerBack/leagueDivider%s.png' % club_fmts.getLeagueString(league)


class QuestsLadderTab(QuestsCurrentTab):

    @classmethod
    def _getEvents(cls):
        return g_eventsCache.getQuests(lambda x: x.getType() == EVENT_TYPE.CLUBS_QUEST)

    def _invalidateEventsData(self):
        svrEvents = self._getEvents()
        filteredEvents = self._applyFilters(self._getEvents().values())
        byLeague = defaultdict(list)
        for q in filteredEvents:
            _, league = q.getDivision()
            byLeague[league].append(q)

        result = []
        for l, events in byLeague.iteritems():
            result.append(event_fmts.packGroupBlock(club_fmts.getLeagueLabel(l), bgImg=_getGroupDividerImage(l)))
            for e in sorted(events, cmp=self._sortFunc):
                result.append(events_helpers.getEventInfo(e, svrEvents))

        self.as_setQuestsDataS({'quests': result,
         'isSortable': False,
         'totalTasks': len(svrEvents)})

    @classmethod
    def _isAvailableQuestForTab(cls, svrEvent):
        return svrEvent.getType() == EVENT_TYPE.CLUBS_QUEST

    def _filterFunc(self, event):
        return not self._hideCompleted or not event.isCompleted()

    def _applySort(self, quests):
        return sorted(quests, self._sortFunc)

    @classmethod
    def _sortFunc(cls, a, b):
        res = cmp(a.isCompleted(), b.isCompleted())
        if res:
            return res
        divA, _ = a.getDivision()
        divB, _ = b.getDivision()
        return cmp(divA, divB)
