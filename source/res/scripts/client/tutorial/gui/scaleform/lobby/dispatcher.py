# Embedded file name: scripts/client/tutorial/gui/Scaleform/lobby/dispatcher.py
from gui.Scaleform.Waiting import Waiting
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import TutorialEvent
from tutorial.logger import LOG_MEMORY, LOG_ERROR
from tutorial.control.context import GLOBAL_FLAG, GLOBAL_VAR, GlobalStorage
from tutorial.settings import TUTORIAL_SETTINGS
from tutorial.gui import GUIDispatcher

class SfLobbyDispatcher(GUIDispatcher):
    _lastHistoryID = GlobalStorage(GLOBAL_VAR.LAST_HISTORY_ID, 0)

    def __init__(self):
        super(SfLobbyDispatcher, self).__init__()
        self._exit = None
        return

    def __del__(self):
        LOG_MEMORY('SfLobbyDispatcher deleted')

    def start(self, loader):
        if not super(SfLobbyDispatcher, self).start(loader):
            return False
        addListener = g_eventBus.addListener
        addListener(TutorialEvent.START_TRAINING, self.__handleStartTraining, scope=EVENT_BUS_SCOPE.GLOBAL)
        addListener(TutorialEvent.STOP_TRAINING, self.__handleStopTraining, scope=EVENT_BUS_SCOPE.GLOBAL)
        addListener(TutorialEvent.SHOW_TUTORIAL_BATTLE_HISTORY, self.__handleShowHistory, scope=EVENT_BUS_SCOPE.DEFAULT)
        return True

    def stop(self):
        if not super(SfLobbyDispatcher, self).stop():
            return False
        removeListener = g_eventBus.removeListener
        removeListener(TutorialEvent.START_TRAINING, self.__handleStartTraining, scope=EVENT_BUS_SCOPE.GLOBAL)
        removeListener(TutorialEvent.STOP_TRAINING, self.__handleStopTraining, scope=EVENT_BUS_SCOPE.GLOBAL)
        removeListener(TutorialEvent.SHOW_TUTORIAL_BATTLE_HISTORY, self.__handleShowHistory, scope=EVENT_BUS_SCOPE.DEFAULT)
        self.clearGUI()
        return True

    def __handleStartTraining(self, event):
        if not event.settingsID:
            LOG_ERROR('Name of tutorial is not defined', event.settingsID)
            return
        Waiting.show('tutorial-chapter-loading', isSingle=True)
        self.startTraining(event.settingsID, event.getState())
        Waiting.hide('tutorial-chapter-loading')

    def __handleStopTraining(self, _):
        self.stopTraining()

    def __handleShowHistory(self, event):
        if not event.targetID:
            LOG_ERROR('Required parameters is not defined to show history', event.targetID)
            return
        isNotAvailable = self._lastHistoryID != event.targetID
        state = {'reloadIfRun': True,
         'restoreIfRun': True,
         'isAfterBattle': True,
         'globalFlags': {GLOBAL_FLAG.SHOW_HISTORY: True,
                         GLOBAL_FLAG.IS_FLAGS_RESET: True,
                         GLOBAL_FLAG.HISTORY_NOT_AVAILABLE: isNotAvailable}}
        Waiting.show('tutorial-chapter-loading', isSingle=True)
        self.startTraining(TUTORIAL_SETTINGS.OFFBATTLE.id, state)
        Waiting.hide('tutorial-chapter-loading')
