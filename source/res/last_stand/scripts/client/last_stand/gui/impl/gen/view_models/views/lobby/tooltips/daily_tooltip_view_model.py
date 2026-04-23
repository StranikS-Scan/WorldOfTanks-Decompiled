# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/gen/view_models/views/lobby/tooltips/daily_tooltip_view_model.py
from frameworks.wulf import Array, ViewModel
from last_stand.gui.impl.gen.view_models.views.common.bonus_item_view_model import BonusItemViewModel

class DailyTooltipViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(DailyTooltipViewModel, self).__init__(properties=properties, commands=commands)

    def getResetTime(self):
        return self._getNumber(0)

    def setResetTime(self, value):
        self._setNumber(0, value)

    def getName(self):
        return self._getString(1)

    def setName(self, value):
        self._setString(1, value)

    def getDescription(self):
        return self._getString(2)

    def setDescription(self, value):
        self._setString(2, value)

    def getCompleted(self):
        return self._getBool(3)

    def setCompleted(self, value):
        self._setBool(3, value)

    def getAllDailyCompleted(self):
        return self._getBool(4)

    def setAllDailyCompleted(self, value):
        self._setBool(4, value)

    def getRewards(self):
        return self._getArray(5)

    def setRewards(self, value):
        self._setArray(5, value)

    @staticmethod
    def getRewardsType():
        return BonusItemViewModel

    def _initialize(self):
        super(DailyTooltipViewModel, self)._initialize()
        self._addNumberProperty('resetTime', 0)
        self._addStringProperty('name', '')
        self._addStringProperty('description', '')
        self._addBoolProperty('completed', False)
        self._addBoolProperty('allDailyCompleted', False)
        self._addArrayProperty('rewards', Array())
