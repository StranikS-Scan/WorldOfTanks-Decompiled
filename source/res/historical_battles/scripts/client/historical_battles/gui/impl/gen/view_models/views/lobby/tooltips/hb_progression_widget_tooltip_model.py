# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/gen/view_models/views/lobby/tooltips/hb_progression_widget_tooltip_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.missions.bonuses.item_bonus_model import ItemBonusModel

class HbProgressionWidgetTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(HbProgressionWidgetTooltipModel, self).__init__(properties=properties, commands=commands)

    def getFrontName(self):
        return self._getString(0)

    def setFrontName(self, value):
        self._setString(0, value)

    def getLevel(self):
        return self._getNumber(1)

    def setLevel(self, value):
        self._setNumber(1, value)

    def getMinLevelPoints(self):
        return self._getNumber(2)

    def setMinLevelPoints(self, value):
        self._setNumber(2, value)

    def getCurrentPoints(self):
        return self._getNumber(3)

    def setCurrentPoints(self, value):
        self._setNumber(3, value)

    def getMaxLevelPoints(self):
        return self._getNumber(4)

    def setMaxLevelPoints(self, value):
        self._setNumber(4, value)

    def getRewards(self):
        return self._getArray(5)

    def setRewards(self, value):
        self._setArray(5, value)

    @staticmethod
    def getRewardsType():
        return ItemBonusModel

    def _initialize(self):
        super(HbProgressionWidgetTooltipModel, self)._initialize()
        self._addStringProperty('frontName', '')
        self._addNumberProperty('level', 0)
        self._addNumberProperty('minLevelPoints', 0)
        self._addNumberProperty('currentPoints', 0)
        self._addNumberProperty('maxLevelPoints', 0)
        self._addArrayProperty('rewards', Array())
