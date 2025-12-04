# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/festivity/dummy/df_controller.py
import Event
from festivity.base import FestivityQuestsHangarFlag
from skeletons.gui.game_control import IFestivityController, IFestivityTutorialController
_DEFAULT_QUESTS_FLAG = FestivityQuestsHangarFlag(None, None, None)

class DummyController(IFestivityController):

    def __init__(self):
        super(DummyController, self).__init__()
        self.__state = None
        self.__em = Event.EventManager()
        self.onStateChanged = Event.Event(self.__em)
        self.onUpdateSlot = Event.Event(self.__em)
        self.onSetHangToyEffectEnabled = Event.Event(self.__em)
        self.__tutorial = DummyTutorialController()
        return

    def isEnabled(self):
        return False

    def getHangarQuestsFlagData(self):
        return _DEFAULT_QUESTS_FLAG

    def getHangarWidgetLinkage(self):
        return None

    def getHangarEdgeColor(self):
        return None

    def isInProgress(self):
        return False

    def isPostEvent(self):
        return False

    def isWidgetVisible(self, prbState):
        return False

    def isCreditBonusVisible(self, prbState):
        return False

    def isOnboardingFinished(self):
        return False

    @property
    def tutorial(self):
        return self.__tutorial


class DummyTutorialController(IFestivityTutorialController):

    def __init__(self):
        super(DummyTutorialController, self).__init__()
        self.__em = Event.EventManager()
        self.onIntroComplete = Event.Event(self.__em)

    def shouldStartIntro(self):
        return False

    @property
    def isActive(self):
        return False

    @property
    def tryStartIntro(self):
        return None
