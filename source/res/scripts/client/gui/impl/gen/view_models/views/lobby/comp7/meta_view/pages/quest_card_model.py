# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/comp7/meta_view/pages/quest_card_model.py
from enum import Enum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.comp7.comp7_bonus_model import Comp7BonusModel

class CardState(Enum):
    LOCKEDBYNOXVEHICLES = 'lockedByNoXVehicles'
    LOCKEDBYINACTIVESEASON = 'lockedByInactiveSeason'
    LOCKEDBYPREVIOUSQUEST = 'lockedByPreviousQuest'
    ACTIVE = 'active'
    COMPLETED = 'completed'


class QuestCardModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(QuestCardModel, self).__init__(properties=properties, commands=commands)

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

    def getRewards(self):
        return self._getArray(5)

    def setRewards(self, value):
        self._setArray(5, value)

    @staticmethod
    def getRewardsType():
        return Comp7BonusModel

    def _initialize(self):
        super(QuestCardModel, self)._initialize()
        self._addStringProperty('state')
        self._addNumberProperty('currentProgress', 0)
        self._addNumberProperty('totalProgress', 0)
        self._addStringProperty('description', '')
        self._addStringProperty('iconKey', '')
        self._addArrayProperty('rewards', Array())
