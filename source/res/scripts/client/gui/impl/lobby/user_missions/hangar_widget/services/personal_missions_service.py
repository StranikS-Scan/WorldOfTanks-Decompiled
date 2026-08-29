# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/user_missions/hangar_widget/services/personal_missions_service.py
from __future__ import absolute_import
from future.utils import viewvalues
import Event
from PlayerEvents import g_playerEvents
from config_schemas.umg_config import umgConfigSchema
from constants import QUEUE_TYPE
from gui.shared import EVENT_BUS_SCOPE, g_eventBus
from gui.shared.events import PersonalMissionsEvent
from helpers import dependency
from personal_missions import PM_BRANCH
from skeletons.gui.server_events import IEventsCache
from gui.impl.lobby.user_missions.hangar_widget.services import IPersonalMissionsService
from gui.impl.lobby.user_missions.hangar_widget.services.service_events import ServiceEvents

class PersonalMissionsService(IPersonalMissionsService, ServiceEvents):
    _eventsCache = dependency.descriptor(IEventsCache)
    _enabledQueues = (QUEUE_TYPE.RANDOMS,)

    def __init__(self):
        super(PersonalMissionsService, self).__init__()
        self.onPersonalMissionsChanged = Event.Event()
        self.onWidgetQuestIDMarkedAsNew = Event.Event()
        self.onServicePMSyncCompleted = Event.Event()
        self.__widgetQuestIDMarkedAsNew = []
        self.__curPM3widgetQuests = {}
        self.startServiceEvents()
        self._eventsCache.onPMSyncCompleted += self.__onPMSyncCompleted
        self.updateCurPM3widgetQuestsID()

    def isVisible(self):
        if not self._isQueueEnabled():
            return False
        campaigns = self._eventsCache.getPersonalMissions().getAllCampaigns(PM_BRANCH.ALL_NAMES)
        for campaign in viewvalues(campaigns):
            if campaign.isStarted() and not campaign.isFullCompleted():
                return True

        return False

    def onPrbEntitySwitched(self):
        self.onPersonalMissionsChanged()

    def startListening(self):
        self.startGlobalListening()
        g_playerEvents.onConfigModelUpdated += self.__onConfigModelUpdated
        g_eventBus.addListener(PersonalMissionsEvent.NEXT_QUEST_SELECTED, self.__onNextQuestSelected, EVENT_BUS_SCOPE.LOBBY)

    def stopListening(self):
        self.stopGlobalListening()
        g_playerEvents.onConfigModelUpdated -= self.__onConfigModelUpdated
        g_eventBus.removeListener(PersonalMissionsEvent.NEXT_QUEST_SELECTED, self.__onNextQuestSelected, EVENT_BUS_SCOPE.LOBBY)

    def finalize(self):
        self._eventsCache.onPMSyncCompleted -= self.__onPMSyncCompleted
        self.stopListening()
        self.stopServiceEvents()
        self.onPersonalMissionsChanged.clear()
        self.onWidgetQuestIDMarkedAsNew.clear()
        self.onServicePMSyncCompleted.clear()

    def clearWidgetQuestIDMarkedAsNew(self):
        del self.__widgetQuestIDMarkedAsNew[:]

    def setWidgetQuestIDMarkedAsNew(self, questID, doUpdateWidget=True):
        self.__widgetQuestIDMarkedAsNew.append(questID)
        if questID and doUpdateWidget:
            self.onWidgetQuestIDMarkedAsNew()

    def getWidgetQuestIDMarkedAsNew(self):
        return self.__widgetQuestIDMarkedAsNew

    def _isQueueEnabled(self):
        return False if self.prbDispatcher is None else any((self.prbDispatcher.getFunctionalState().isQueueSelected(queueType) for queueType in self._enabledQueues))

    def __onConfigModelUpdated(self, gpKey):
        if umgConfigSchema.gpKey == gpKey:
            self.onPersonalMissionsChanged()

    def __onNextQuestSelected(self, event):
        self.setWidgetQuestIDMarkedAsNew(event.ctx.get('questID'))

    def updateCurPM3widgetQuestsID(self):
        personalMissionsCache = self._eventsCache.getPersonalMissions()
        curPM3Quests = personalMissionsCache.getSelectedQuestsForBranch(PM_BRANCH.PERSONAL_MISSION_3)
        if self.__curPM3widgetQuests:
            isUpdateNeeded = False
            for questID, quest in curPM3Quests.items():
                for widgetQuestID, widgetQuest in self.__curPM3widgetQuests.items():
                    if quest.getChainID() == widgetQuest.getChainID() and questID != widgetQuestID:
                        if widgetQuest.isCompleted():
                            isUpdateNeeded = True
                            self.setWidgetQuestIDMarkedAsNew(questID, False)

            if not isUpdateNeeded:
                return False
        self.__curPM3widgetQuests = curPM3Quests
        return True

    def __onPMSyncCompleted(self, *_):
        self.onPersonalMissionsChanged()
        if self.updateCurPM3widgetQuestsID():
            self.onServicePMSyncCompleted()
