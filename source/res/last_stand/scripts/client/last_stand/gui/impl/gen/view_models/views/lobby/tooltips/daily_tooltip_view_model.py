# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/gen/view_models/views/lobby/tooltips/daily_tooltip_view_model.py
from frameworks.wulf import Array, ViewModel
from last_stand.gui.impl.gen.view_models.views.common.bonus_item_view_model import BonusItemViewModel

class DailyTooltipViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=7, commands=0):
        super(DailyTooltipViewModel, self).__init__(properties=properties, commands=commands)

    def getIsBadge(self):
        return self._getBool(0)

    def setIsBadge(self, value):
        self._setBool(0, value)

    def getResetTime(self):
        return self._getNumber(1)

    def setResetTime(self, value):
        self._setNumber(1, value)

    def getName(self):
        return self._getString(2)

    def setName(self, value):
        self._setString(2, value)

    def getDescription(self):
        return self._getString(3)

    def setDescription(self, value):
        self._setString(3, value)

    def getProgress(self):
        return self._getNumber(4)

    def setProgress(self, value):
        self._setNumber(4, value)

    def getPercent(self):
        return self._getNumber(5)

    def setPercent(self, value):
        self._setNumber(5, value)

    def getRewards(self):
        return self._getArray(6)

    def setRewards(self, value):
        self._setArray(6, value)

    @staticmethod
    def getRewardsType():
        return BonusItemViewModel

    def _initialize(self):
        super(DailyTooltipViewModel, self)._initialize()
        self._addBoolProperty('isBadge', False)
        self._addNumberProperty('resetTime', 0)
        self._addStringProperty('name', '')
        self._addStringProperty('description', '')
        self._addNumberProperty('progress', 0)
        self._addNumberProperty('percent', 0)
        self._addArrayProperty('rewards', Array())
