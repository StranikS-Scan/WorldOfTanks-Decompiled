# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/impl/gen/view_models/views/lobby/common/fun_random_quest_card_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class CardState(Enum):
    ACTIVE = 'active'
    COMPLETED = 'completed'


class FunRandomQuestCardModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=8, commands=0):
        super(FunRandomQuestCardModel, self).__init__(properties=properties, commands=commands)

    def getState(self):
        return CardState(self._getString(0))

    def setState(self, value):
        self._setString(0, value.value)

    def getCurrentProgress(self):
        return self._getNumber(1)

    def setCurrentProgress(self, value):
        self._setNumber(1, value)

    def getTotalProgress(self):
        return self._getNumber(2)

    def setTotalProgress(self, value):
        self._setNumber(2, value)

    def getDescription(self):
        return self._getString(3)

    def setDescription(self, value):
        self._setString(3, value)

    def getIconKey(self):
        return self._getString(4)

    def setIconKey(self, value):
        self._setString(4, value)

    def getTotalPoints(self):
        return self._getNumber(5)

    def setTotalPoints(self, value):
        self._setNumber(5, value)

    def getMainBonusCount(self):
        return self._getNumber(6)

    def setMainBonusCount(self, value):
        self._setNumber(6, value)

    def getAltBonusCount(self):
        return self._getNumber(7)

    def setAltBonusCount(self, value):
        self._setNumber(7, value)

    def _initialize(self):
        super(FunRandomQuestCardModel, self)._initialize()
        self._addStringProperty('state')
        self._addNumberProperty('currentProgress', 0)
        self._addNumberProperty('totalProgress', 0)
        self._addStringProperty('description', '')
        self._addStringProperty('iconKey', '')
        self._addNumberProperty('totalPoints', 0)
        self._addNumberProperty('mainBonusCount', 0)
        self._addNumberProperty('altBonusCount', 0)
