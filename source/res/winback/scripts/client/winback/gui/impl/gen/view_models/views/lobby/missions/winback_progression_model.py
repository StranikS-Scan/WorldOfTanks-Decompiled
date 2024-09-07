# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: winback/scripts/client/winback/gui/impl/gen/view_models/views/lobby/missions/winback_progression_model.py
from enum import Enum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.missions.winback_quest_model import WinbackQuestModel

class OffersState(Enum):
    AVAILABLE = 'available'
    DISABLED = 'disabled'
    NO_OFFERS = 'no_offers'


class WinbackProgressionModel(ViewModel):
    __slots__ = ('onTakeReward',)

    def __init__(self, properties=6, commands=1):
        super(WinbackProgressionModel, self).__init__(properties=properties, commands=commands)

    def getCountCompleted(self):
        return self._getNumber(0)

    def setCountCompleted(self, value):
        self._setNumber(0, value)

    def getTotalQuests(self):
        return self._getNumber(1)

    def setTotalQuests(self, value):
        self._setNumber(1, value)

    def getPreviousCompletedQuests(self):
        return self._getNumber(2)

    def setPreviousCompletedQuests(self, value):
        self._setNumber(2, value)

    def getIsBattlePassActive(self):
        return self._getBool(3)

    def setIsBattlePassActive(self, value):
        self._setBool(3, value)

    def getOffersState(self):
        return OffersState(self._getString(4))

    def setOffersState(self, value):
        self._setString(4, value.value)

    def getQuests(self):
        return self._getArray(5)

    def setQuests(self, value):
        self._setArray(5, value)

    @staticmethod
    def getQuestsType():
        return WinbackQuestModel

    def _initialize(self):
        super(WinbackProgressionModel, self)._initialize()
        self._addNumberProperty('countCompleted', 0)
        self._addNumberProperty('totalQuests', 0)
        self._addNumberProperty('previousCompletedQuests', 0)
        self._addBoolProperty('isBattlePassActive', False)
        self._addStringProperty('offersState')
        self._addArrayProperty('quests', Array())
        self.onTakeReward = self._addCommand('onTakeReward')
