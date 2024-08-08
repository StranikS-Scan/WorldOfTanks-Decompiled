# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/wot_anniversary/main_view_model.py
from enum import IntEnum
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.wot_anniversary.daily_quests_model import DailyQuestsModel
from gui.impl.gen.view_models.views.lobby.wot_anniversary.login_quests_model import LoginQuestsModel
from gui.impl.gen.view_models.views.lobby.wot_anniversary.mascot_quest_model import MascotQuestModel

class Phase(IntEnum):
    MOUSE = 0
    CAT = 1
    DEER = 2


class MainViewModel(ViewModel):
    __slots__ = ('onClose', 'onInfoPageOpen', 'onGoToStore')

    def __init__(self, properties=8, commands=3):
        super(MainViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def dailyQuests(self):
        return self._getViewModel(0)

    @staticmethod
    def getDailyQuestsType():
        return DailyQuestsModel

    @property
    def mascotQuest(self):
        return self._getViewModel(1)

    @staticmethod
    def getMascotQuestType():
        return MascotQuestModel

    @property
    def loginQuests(self):
        return self._getViewModel(2)

    @staticmethod
    def getLoginQuestsType():
        return LoginQuestsModel

    def getStartTime(self):
        return self._getNumber(3)

    def setStartTime(self, value):
        self._setNumber(3, value)

    def getEndTime(self):
        return self._getNumber(4)

    def setEndTime(self, value):
        self._setNumber(4, value)

    def getBalance(self):
        return self._getNumber(5)

    def setBalance(self, value):
        self._setNumber(5, value)

    def getIsChina(self):
        return self._getBool(6)

    def setIsChina(self, value):
        self._setBool(6, value)

    def getActivePhase(self):
        return Phase(self._getNumber(7))

    def setActivePhase(self, value):
        self._setNumber(7, value.value)

    def _initialize(self):
        super(MainViewModel, self)._initialize()
        self._addViewModelProperty('dailyQuests', DailyQuestsModel())
        self._addViewModelProperty('mascotQuest', MascotQuestModel())
        self._addViewModelProperty('loginQuests', LoginQuestsModel())
        self._addNumberProperty('startTime', 0)
        self._addNumberProperty('endTime', 0)
        self._addNumberProperty('balance', -1)
        self._addBoolProperty('isChina', False)
        self._addNumberProperty('activePhase')
        self.onClose = self._addCommand('onClose')
        self.onInfoPageOpen = self._addCommand('onInfoPageOpen')
        self.onGoToStore = self._addCommand('onGoToStore')
