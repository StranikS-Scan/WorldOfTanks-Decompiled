# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/gen/view_models/views/lobby/tooltips/daily_tooltip_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from last_stand.gui.impl.gen.view_models.views.common.bonus_item_view_model import BonusItemViewModel

class DailyTooltipViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
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

    def getRewards(self):
        return self._getArray(4)

    def setRewards(self, value):
        self._setArray(4, value)

    @staticmethod
    def getRewardsType():
        return BonusItemViewModel

    def _initialize(self):
        super(DailyTooltipViewModel, self)._initialize()
        self._addBoolProperty('isBadge', False)
        self._addNumberProperty('resetTime', 0)
        self._addStringProperty('name', '')
        self._addStringProperty('description', '')
        self._addArrayProperty('rewards', Array())
