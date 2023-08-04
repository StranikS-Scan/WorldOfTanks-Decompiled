# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: gui_lootboxes/scripts/client/gui_lootboxes/gui/impl/gen/view_models/views/lobby/gui_lootboxes/tooltips/compensation_tooltip_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.missions.bonuses.bonus_model import BonusModel

class CompensationTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(CompensationTooltipModel, self).__init__(properties=properties, commands=commands)

    def getItemBefore(self):
        return self._getArray(0)

    def setItemBefore(self, value):
        self._setArray(0, value)

    @staticmethod
    def getItemBeforeType():
        return BonusModel

    def getItemAfter(self):
        return self._getArray(1)

    def setItemAfter(self, value):
        self._setArray(1, value)

    @staticmethod
    def getItemAfterType():
        return BonusModel

    def _initialize(self):
        super(CompensationTooltipModel, self)._initialize()
        self._addArrayProperty('itemBefore', Array())
        self._addArrayProperty('itemAfter', Array())
