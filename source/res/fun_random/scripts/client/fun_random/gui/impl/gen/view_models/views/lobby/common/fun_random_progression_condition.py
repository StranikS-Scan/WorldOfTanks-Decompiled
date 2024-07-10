# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/impl/gen/view_models/views/lobby/common/fun_random_progression_condition.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from fun_random.gui.impl.gen.view_models.views.lobby.common.fun_random_quest_card_model import FunRandomQuestCardModel

class FunRandomProgressionCondition(ViewModel):
    __slots__ = ()

    def __init__(self, properties=8, commands=0):
        super(FunRandomProgressionCondition, self).__init__(properties=properties, commands=commands)

    def getCurrentPoints(self):
        return self._getNumber(0)

    def setCurrentPoints(self, value):
        self._setNumber(0, value)

    def getPrevPoints(self):
        return self._getNumber(1)

    def setPrevPoints(self, value):
        self._setNumber(1, value)

    def getMaximumPoints(self):
        return self._getNumber(2)

    def setMaximumPoints(self, value):
        self._setNumber(2, value)

    def getTitle(self):
        return self._getString(3)

    def setTitle(self, value):
        self._setString(3, value)

    def getText(self):
        return self._getString(4)

    def setText(self, value):
        self._setString(4, value)

    def getConditionIcon(self):
        return self._getString(5)

    def setConditionIcon(self, value):
        self._setString(5, value)

    def getStatusTimer(self):
        return self._getNumber(6)

    def setStatusTimer(self, value):
        self._setNumber(6, value)

    def getConditions(self):
        return self._getArray(7)

    def setConditions(self, value):
        self._setArray(7, value)

    @staticmethod
    def getConditionsType():
        return FunRandomQuestCardModel

    def _initialize(self):
        super(FunRandomProgressionCondition, self)._initialize()
        self._addNumberProperty('currentPoints', -1)
        self._addNumberProperty('prevPoints', -1)
        self._addNumberProperty('maximumPoints', -1)
        self._addStringProperty('title', '')
        self._addStringProperty('text', '')
        self._addStringProperty('conditionIcon', '')
        self._addNumberProperty('statusTimer', -1)
        self._addArrayProperty('conditions', Array())
