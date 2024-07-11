# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: races/scripts/client/races/gui/impl/gen/view_models/views/lobby/races_lobby_view/quest_item_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.missions.bonuses.bonus_model import BonusModel

class QuestItemModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(QuestItemModel, self).__init__(properties=properties, commands=commands)

    def getCurrentValue(self):
        return self._getNumber(0)

    def setCurrentValue(self, value):
        self._setNumber(0, value)

    def getMaxValue(self):
        return self._getNumber(1)

    def setMaxValue(self, value):
        self._setNumber(1, value)

    def getLastValue(self):
        return self._getNumber(2)

    def setLastValue(self, value):
        self._setNumber(2, value)

    def getDescription(self):
        return self._getString(3)

    def setDescription(self, value):
        self._setString(3, value)

    def getBonuses(self):
        return self._getArray(4)

    def setBonuses(self, value):
        self._setArray(4, value)

    @staticmethod
    def getBonusesType():
        return BonusModel

    def _initialize(self):
        super(QuestItemModel, self)._initialize()
        self._addNumberProperty('currentValue', 0)
        self._addNumberProperty('maxValue', 0)
        self._addNumberProperty('lastValue', 0)
        self._addStringProperty('description', '')
        self._addArrayProperty('bonuses', Array())
