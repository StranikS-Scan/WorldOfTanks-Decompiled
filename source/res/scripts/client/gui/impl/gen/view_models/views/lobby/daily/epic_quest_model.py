# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/daily/epic_quest_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.missions.bonuses.bonus_model import BonusModel

class EpicQuestModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=8, commands=0):
        super(EpicQuestModel, self).__init__(properties=properties, commands=commands)

    def getId(self):
        return self._getString(0)

    def setId(self, value):
        self._setString(0, value)

    def getIsCompleted(self):
        return self._getBool(1)

    def setIsCompleted(self, value):
        self._setBool(1, value)

    def getCurrent(self):
        return self._getNumber(2)

    def setCurrent(self, value):
        self._setNumber(2, value)

    def getTotal(self):
        return self._getNumber(3)

    def setTotal(self, value):
        self._setNumber(3, value)

    def getEarned(self):
        return self._getNumber(4)

    def setEarned(self, value):
        self._setNumber(4, value)

    def getCountDown(self):
        return self._getNumber(5)

    def setCountDown(self, value):
        self._setNumber(5, value)

    def getBonuses(self):
        return self._getArray(6)

    def setBonuses(self, value):
        self._setArray(6, value)

    @staticmethod
    def getBonusesType():
        return BonusModel

    def getIsEnabled(self):
        return self._getBool(7)

    def setIsEnabled(self, value):
        self._setBool(7, value)

    def _initialize(self):
        super(EpicQuestModel, self)._initialize()
        self._addStringProperty('id', '')
        self._addBoolProperty('isCompleted', False)
        self._addNumberProperty('current', 0)
        self._addNumberProperty('total', 0)
        self._addNumberProperty('earned', 0)
        self._addNumberProperty('countDown', 0)
        self._addArrayProperty('bonuses', Array())
        self._addBoolProperty('isEnabled', False)
