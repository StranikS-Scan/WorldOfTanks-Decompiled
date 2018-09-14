# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/server_events/MotiveQuestsDetails.py
from gui.Scaleform.daapi.view.lobby.server_events import events_helpers
from gui.Scaleform.daapi.view.meta.TutorialHangarQuestDetailsMeta import TutorialHangarQuestDetailsMeta
from gui.server_events import settings
from helpers import dependency
from skeletons.gui.server_events import IEventsCache

class MotiveQuestDetails(TutorialHangarQuestDetailsMeta):
    eventsCache = dependency.descriptor(IEventsCache)

    def getSortedTableData(self, tableData):
        return events_helpers.getSortedTableData(tableData)

    def requestQuestInfo(self, questID):
        svrEvents = self.eventsCache.getMotiveQuests()
        event = svrEvents.get(questID)
        settings.visitEventGUI(event)
        info = None
        if event is not None:
            info = events_helpers.getEventDetails(event, svrEvents)
        self.as_updateQuestInfoS(info)
        return
