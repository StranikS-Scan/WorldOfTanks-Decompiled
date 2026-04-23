# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/gen/view_models/views/lobby/quest_model.py
from enum import Enum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from historical_battles.gui.impl.gen.view_models.views.lobby.hb_meta_view.bonus_model import BonusModel

class QuestType(Enum):
    WIN = 'win'
    TAKEPLACE = 'takePlace'
    DESTROYVEHICLES = 'destroyVehicles'
    MAKEDAMAGE = 'makeDamage'
    SPECIAL = 'special'


class QuestModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=8, commands=0):
        super(QuestModel, self).__init__(properties=properties, commands=commands)

    def getId(self):
        return self._getString(0)

    def setId(self, value):
        self._setString(0, value)

    def getType(self):
        return QuestType(self._getString(1))

    def setType(self, value):
        self._setString(1, value.value)

    def getDesc(self):
        return self._getString(2)

    def setDesc(self, value):
        self._setString(2, value)

    def getProgressCount(self):
        return self._getNumber(3)

    def setProgressCount(self, value):
        self._setNumber(3, value)

    def getProgressTotal(self):
        return self._getNumber(4)

    def setProgressTotal(self, value):
        self._setNumber(4, value)

    def getIsCompleted(self):
        return self._getBool(5)

    def setIsCompleted(self, value):
        self._setBool(5, value)

    def getBonuses(self):
        return self._getArray(6)

    def setBonuses(self, value):
        self._setArray(6, value)

    @staticmethod
    def getBonusesType():
        return BonusModel

    def getUpdateTime(self):
        return self._getNumber(7)

    def setUpdateTime(self, value):
        self._setNumber(7, value)

    def _initialize(self):
        super(QuestModel, self)._initialize()
        self._addStringProperty('id', '')
        self._addStringProperty('type')
        self._addStringProperty('desc', '')
        self._addNumberProperty('progressCount', 0)
        self._addNumberProperty('progressTotal', 0)
        self._addBoolProperty('isCompleted', False)
        self._addArrayProperty('bonuses', Array())
        self._addNumberProperty('updateTime', 0)
