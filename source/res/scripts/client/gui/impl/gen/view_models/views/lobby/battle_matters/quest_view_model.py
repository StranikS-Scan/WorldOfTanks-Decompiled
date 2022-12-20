# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_matters/quest_view_model.py
from enum import Enum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.missions.bonuses.item_bonus_model import ItemBonusModel

class State(Enum):
    DONE = 'done'
    INPROGRESS = 'inProgress'
    UNAVAILABLE = 'unavailable'


class QuestViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=11, commands=0):
        super(QuestViewModel, self).__init__(properties=properties, commands=commands)

    def getNumber(self):
        return self._getNumber(0)

    def setNumber(self, value):
        self._setNumber(0, value)

    def getTitle(self):
        return self._getString(1)

    def setTitle(self, value):
        self._setString(1, value)

    def getDescription(self):
        return self._getString(2)

    def setDescription(self, value):
        self._setString(2, value)

    def getCondition(self):
        return self._getString(3)

    def setCondition(self, value):
        self._setString(3, value)

    def getHasAnimation(self):
        return self._getBool(4)

    def setHasAnimation(self, value):
        self._setBool(4, value)

    def getHasManualPage(self):
        return self._getBool(5)

    def setHasManualPage(self, value):
        self._setBool(5, value)

    def getState(self):
        return State(self._getString(6))

    def setState(self, value):
        self._setString(6, value.value)

    def getRewards(self):
        return self._getArray(7)

    def setRewards(self, value):
        self._setArray(7, value)

    @staticmethod
    def getRewardsType():
        return ItemBonusModel

    def getCurrentProgress(self):
        return self._getNumber(8)

    def setCurrentProgress(self, value):
        self._setNumber(8, value)

    def getLastSeenProgress(self):
        return self._getNumber(9)

    def setLastSeenProgress(self, value):
        self._setNumber(9, value)

    def getMaxProgress(self):
        return self._getNumber(10)

    def setMaxProgress(self, value):
        self._setNumber(10, value)

    def _initialize(self):
        super(QuestViewModel, self)._initialize()
        self._addNumberProperty('number', 0)
        self._addStringProperty('title', '')
        self._addStringProperty('description', '')
        self._addStringProperty('condition', '')
        self._addBoolProperty('hasAnimation', False)
        self._addBoolProperty('hasManualPage', False)
        self._addStringProperty('state')
        self._addArrayProperty('rewards', Array())
        self._addNumberProperty('currentProgress', -1)
        self._addNumberProperty('lastSeenProgress', 0)
        self._addNumberProperty('maxProgress', -1)
