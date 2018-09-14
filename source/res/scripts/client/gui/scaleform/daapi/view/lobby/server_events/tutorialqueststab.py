# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/server_events/TutorialQuestsTab.py
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.view.lobby.server_events.QuestsCurrentTab import QuestsCurrentTab
from gui.Scaleform.daapi.view.lobby.server_events import events_helpers
from gui.Scaleform.genConsts.QUESTS_ALIASES import QUESTS_ALIASES
from gui.Scaleform.locale.QUESTS import QUESTS
from gui.Scaleform.locale.SYSTEM_MESSAGES import SYSTEM_MESSAGES
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.server_events import g_eventsCache, formatters
from gui.server_events.formatters import PROGRESS_BAR_TYPE
from gui.shared.ItemsCache import g_itemsCache
from gui import SystemMessages
NO_PROGRESS_COUNT = -1
_EVENT_STATUS = events_helpers.EVENT_STATUS

class TutorialQuestsTab(QuestsCurrentTab):

    def __init__(self):
        super(TutorialQuestsTab, self).__init__()
        self.__questsDescriptor = events_helpers.getTutorialEventsDescriptor()

    def _populate(self):
        super(TutorialQuestsTab, self)._populate()
        g_clientUpdateManager.addCallbacks({'stats.tutorialsCompleted': self.__onEventsUpdated,
         'stats.dossier': self.__onEventsUpdated})
        self._invalidateEventsData()
        if self._navInfo.tutorial.questID:
            self._selectQuest(self._navInfo.tutorial.questID)

    def _dispose(self):
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.__questsDescriptor = None
        super(TutorialQuestsTab, self)._dispose()
        return

    def _onRegisterFlashComponent(self, viewPy, alias):
        super(TutorialQuestsTab, self)._onRegisterFlashComponent(viewPy, alias)
        if alias == QUESTS_ALIASES.TUTORIAL_HANGAR_QUEST_DETAILS_PY_ALIAS:
            self.components.get(alias).setQuestsDescriptor(self.__questsDescriptor)

    def _selectQuest(self, questID):
        if self.__questsDescriptor is not None and self.__questsDescriptor.getChapter(questID) is not None:
            return self.as_setSelectedQuestS(questID)
        else:
            SystemMessages.pushI18nMessage(SYSTEM_MESSAGES.QUESTS_NOQUESTSWITHGIVENID)
            return

    def _invalidateEventsData(self):
        result = []
        if self.__questsDescriptor is not None:
            completed = g_itemsCache.items.stats.tutorialsCompleted
            for chapter in self.__questsDescriptor:
                chapterStatus = chapter.getChapterStatus(self.__questsDescriptor, completed)
                if chapterStatus != _EVENT_STATUS.NOT_AVAILABLE:
                    qProgCur, qProgTot, progressBarType = self.__getProgressValues(chapter)
                    result.append({'questID': chapter.getID(),
                     'isNew': False,
                     'status': chapterStatus,
                     'description': chapter.getTitle(),
                     'isSelectable': True,
                     'rendererType': QUESTS_ALIASES.RENDERER_TYPE_QUEST,
                     'tooltip': TOOLTIPS.QUESTS_RENDERER_LABEL,
                     'tasksCount': NO_PROGRESS_COUNT,
                     'maxProgrVal': qProgTot,
                     'currentProgrVal': qProgCur,
                     'progrBarType': progressBarType,
                     'detailsLinkage': QUESTS_ALIASES.TUTORIAL_HANGAR_QUEST_DETAILS_LINKAGE,
                     'detailsPyAlias': QUESTS_ALIASES.TUTORIAL_HANGAR_QUEST_DETAILS_PY_ALIAS})

        self.as_setQuestsDataS({'quests': result,
         'totalTasks': len(result)})
        return

    def __onEventsUpdated(self, *args):
        self._invalidateEventsData()

    def __getProgressValues(self, chapter):
        progrCondition = chapter.getProgressCondition()
        if progrCondition.getID() == 'vehicleBattlesCount':
            vehicleCD = progrCondition.getValues().get('vehicle')
            battlesLimit = progrCondition.getValues().get('limit', NO_PROGRESS_COUNT)
            progressBarType = progrCondition.getValues().get('progressBarType', PROGRESS_BAR_TYPE.NONE)
            vehicleDossier = g_itemsCache.items.getVehicleDossier(vehicleCD)
            return (vehicleDossier.getTotalStats().getBattlesCount(), battlesLimit, progressBarType)
        return (NO_PROGRESS_COUNT, NO_PROGRESS_COUNT, PROGRESS_BAR_TYPE.NONE)
