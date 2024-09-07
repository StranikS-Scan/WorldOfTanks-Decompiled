# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: winback/scripts/client/winback/gui/impl/gen/view_models/views/lobby/tooltips/compensation_tooltip_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.missions.bonuses.item_bonus_model import ItemBonusModel

class CompensationTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(CompensationTooltipModel, self).__init__(properties=properties, commands=commands)

    def getIsDiscount(self):
        return self._getBool(0)

    def setIsDiscount(self, value):
        self._setBool(0, value)

    def getVehicleLevel(self):
        return self._getNumber(1)

    def setVehicleLevel(self, value):
        self._setNumber(1, value)

    def getRewards(self):
        return self._getArray(2)

    def setRewards(self, value):
        self._setArray(2, value)

    @staticmethod
    def getRewardsType():
        return ItemBonusModel

    def _initialize(self):
        super(CompensationTooltipModel, self)._initialize()
        self._addBoolProperty('isDiscount', False)
        self._addNumberProperty('vehicleLevel', 0)
        self._addArrayProperty('rewards', Array())
