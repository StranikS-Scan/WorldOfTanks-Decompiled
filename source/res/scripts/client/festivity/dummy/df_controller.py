# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/festivity/dummy/df_controller.py
import Event
from festivity.base import FestivityQuestsHangarFlag
from skeletons.gui.game_control import IFestivityController
_DEFAULT_QUESTS_FLAG = FestivityQuestsHangarFlag(None, None, None)

class DummyController(IFestivityController):

    def __init__(self):
        super(DummyController, self).__init__()
        self.__state = None
        self.__em = Event.EventManager()
        self.onStateChanged = Event.Event(self.__em)
        return

    def isEnabled(self):
        return False

    def getHangarQuestsFlagData(self):
        return _DEFAULT_QUESTS_FLAG
