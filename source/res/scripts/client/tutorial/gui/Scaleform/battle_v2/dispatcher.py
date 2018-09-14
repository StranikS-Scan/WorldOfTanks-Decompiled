# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/tutorial/gui/Scaleform/battle_v2/dispatcher.py
from gui.battle_control import avatar_getter
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.events import TutorialEvent
from tutorial.logger import LOG_MEMORY
from tutorial.gui import GUIDispatcher

class SfBattleDispatcher(GUIDispatcher):
    """
    There is GUIDispatcher class implementation for tutorial in the battle.
    """

    def __del__(self):
        LOG_MEMORY('SfBattleDispatcher deleted')

    def start(self, loader):
        if not super(SfBattleDispatcher, self).start(loader):
            return False
        g_eventBus.addListener(TutorialEvent.STOP_TRAINING, self.__handleStopTraining, scope=EVENT_BUS_SCOPE.GLOBAL)
        return True

    def stop(self):
        if not super(SfBattleDispatcher, self).stop():
            return False
        g_eventBus.removeListener(TutorialEvent.STOP_TRAINING, self.__handleStopTraining, scope=EVENT_BUS_SCOPE.GLOBAL)
        self.clearGUI()
        return True

    def __handleStopTraining(self, _):
        self.refuseTraining()
        avatar_getter.leaveArena()
