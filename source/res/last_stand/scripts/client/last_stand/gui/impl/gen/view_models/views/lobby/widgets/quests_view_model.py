# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/gen/view_models/views/lobby/widgets/quests_view_model.py
from enum import Enum
from frameworks.wulf import ViewModel
from last_stand.gui.impl.gen.view_models.views.common.bonus_item_view_model import BonusItemViewModel

class WidgetState(Enum):
    HIDDEN = 'hidden'
    DEFAULT = 'default'
    BADGE = 'badge'


class QuestsViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=10, commands=0):
        super(QuestsViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def bonus(self):
        return self._getViewModel(0)

    @staticmethod
    def getBonusType():
        return BonusItemViewModel

    def getConditionName(self):
        return self._getString(1)

    def setConditionName(self, value):
        self._setString(1, value)

    def getResetTime(self):
        return self._getNumber(2)

    def setResetTime(self, value):
        self._setNumber(2, value)

    def getKeyBonus(self):
        return self._getNumber(3)

    def setKeyBonus(self, value):
        self._setNumber(3, value)

    def getName(self):
        return self._getString(4)

    def setName(self, value):
        self._setString(4, value)

    def getDescription(self):
        return self._getString(5)

    def setDescription(self, value):
        self._setString(5, value)

    def getIsCompleted(self):
        return self._getBool(6)

    def setIsCompleted(self, value):
        self._setBool(6, value)

    def getState(self):
        return WidgetState(self._getString(7))

    def setState(self, value):
        self._setString(7, value.value)

    def getCurrentProgress(self):
        return self._getNumber(8)

    def setCurrentProgress(self, value):
        self._setNumber(8, value)

    def getMaximumProgress(self):
        return self._getNumber(9)

    def setMaximumProgress(self, value):
        self._setNumber(9, value)

    def _initialize(self):
        super(QuestsViewModel, self)._initialize()
        self._addViewModelProperty('bonus', BonusItemViewModel())
        self._addStringProperty('conditionName', '')
        self._addNumberProperty('resetTime', 0)
        self._addNumberProperty('keyBonus', 0)
        self._addStringProperty('name', '')
        self._addStringProperty('description', '')
        self._addBoolProperty('isCompleted', False)
        self._addStringProperty('state')
        self._addNumberProperty('currentProgress', 0)
        self._addNumberProperty('maximumProgress', 0)
