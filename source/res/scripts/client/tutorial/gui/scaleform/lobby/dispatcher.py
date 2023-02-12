# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/tutorial/gui/Scaleform/lobby/dispatcher.py
from gui.Scaleform.Waiting import Waiting
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import TutorialEvent
from tutorial.logger import LOG_MEMORY, LOG_ERROR
from tutorial.gui import GUIDispatcher

class SfLobbyDispatcher(GUIDispatcher):

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
        return True

    def stop(self):
        if not super(SfLobbyDispatcher, self).stop():
            return False
        removeListener = g_eventBus.removeListener
        removeListener(TutorialEvent.START_TRAINING, self.__handleStartTraining, scope=EVENT_BUS_SCOPE.GLOBAL)
        removeListener(TutorialEvent.STOP_TRAINING, self.__handleStopTraining, scope=EVENT_BUS_SCOPE.GLOBAL)
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
