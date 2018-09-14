# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/server_events/TutorialQuestsTab.py
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.view.lobby.server_events.QuestsTab import QuestsTab
from gui.Scaleform.daapi.view.lobby.server_events import events_helpers
from gui.Scaleform.genConsts.QUESTS_ALIASES import QUESTS_ALIASES
from gui.Scaleform.locale.SYSTEM_MESSAGES import SYSTEM_MESSAGES
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.server_events.formatters import PROGRESS_BAR_TYPE
from gui.shared.ItemsCache import g_itemsCache
from gui import SystemMessages
NO_PROGRESS_COUNT = -1
_EVENT_STATUS = events_helpers.EVENT_STATUS

class TutorialQuestsTab(QuestsTab):

    def __init__(self):
        super(TutorialQuestsTab, self).__init__()
        self.__questsDescriptor = events_helpers.getTutorialEventsDescriptor()

    def _populate(self):
        super(TutorialQuestsTab, self)._populate()
        g_clientUpdateManager.addCallbacks({'stats.tutorialsCompleted': self.__onEventsUpdated,
         'stats.dossier': self.__onEventsUpdated})
        self._invalidateEventsData()
        if self._navInfo.tutorial.questID is not None:
            self._selectQuest(self._navInfo.tutorial.questID)
        return

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
        if self.__questsDescriptor is None:
            return
        else:
            completed = g_itemsCache.items.stats.tutorialsCompleted
            if questID == '':
                chapterIdx = -1
                chapterID = None
                for chapter in self.__questsDescriptor:
                    if self.__getChapterStatus(self.__questsDescriptor, chapter, completed) == _EVENT_STATUS.NONE:
                        nextChapterID = chapter.getID()
                        nextChapterIdx = self.__questsDescriptor.getChapterIdx(nextChapterID)
                        if nextChapterIdx > chapterIdx:
                            chapterIdx = nextChapterIdx
                            chapterID = nextChapterID

                if chapterID is not None:
                    self.as_setSelectedQuestS(chapterID)
            elif self.__questsDescriptor.getChapter(questID) is not None:
                self.as_setSelectedQuestS(questID)
            else:
                SystemMessages.pushI18nMessage(SYSTEM_MESSAGES.QUESTS_NOQUESTSWITHGIVENID)
            return

    def _invalidateEventsData(self):
        if self.__questsDescriptor is None:
            return
        else:
            result = []
            completed = g_itemsCache.items.stats.tutorialsCompleted
            for chapter in self.__questsDescriptor:
                chapterStatus = self.__getChapterStatus(self.__questsDescriptor, chapter, completed)
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

            self.as_setQuestsDataS({'quests': result})
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

    def __getChapterStatus(self, descriptor, chapter, completed):
        unlockChapter = descriptor.getChapter(chapter.getUnlockChapter())
        if chapter.isHidden():
            return _EVENT_STATUS.NOT_AVAILABLE
        elif chapter.isBonusReceived(completed):
            return _EVENT_STATUS.COMPLETED
        elif unlockChapter is None:
            return _EVENT_STATUS.NONE
        elif unlockChapter is not None and unlockChapter.isBonusReceived(completed):
            return _EVENT_STATUS.NONE
        else:
            return _EVENT_STATUS.NOT_AVAILABLE
            return
