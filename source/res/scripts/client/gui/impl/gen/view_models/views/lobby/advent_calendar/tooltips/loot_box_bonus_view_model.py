# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/advent_calendar/tooltips/loot_box_bonus_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.advent_calendar.tooltips.bonus_item_view_model import BonusItemViewModel

class LootBoxBonusViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(LootBoxBonusViewModel, self).__init__(properties=properties, commands=commands)

    def getProbability(self):
        return self._getReal(0)

    def setProbability(self, value):
        self._setReal(0, value)

    def getIsGuaranteed(self):
        return self._getBool(1)

    def setIsGuaranteed(self, value):
        self._setBool(1, value)

    def getBonusItems(self):
        return self._getArray(2)

    def setBonusItems(self, value):
        self._setArray(2, value)

    @staticmethod
    def getBonusItemsType():
        return BonusItemViewModel

    def _initialize(self):
        super(LootBoxBonusViewModel, self)._initialize()
        self._addRealProperty('probability', 0.0)
        self._addBoolProperty('isGuaranteed', False)
        self._addArrayProperty('bonusItems', Array())
