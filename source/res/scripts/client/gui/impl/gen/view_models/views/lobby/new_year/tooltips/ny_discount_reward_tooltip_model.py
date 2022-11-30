# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/tooltips/ny_discount_reward_tooltip_model.py
from frameworks.wulf import ViewModel

class NyDiscountRewardTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(NyDiscountRewardTooltipModel, self).__init__(properties=properties, commands=commands)

    def getLevel(self):
        return self._getNumber(0)

    def setLevel(self, value):
        self._setNumber(0, value)

    def getQuestsCount(self):
        return self._getNumber(1)

    def setQuestsCount(self, value):
        self._setNumber(1, value)

    def getSelectedVehicle(self):
        return self._getString(2)

    def setSelectedVehicle(self, value):
        self._setString(2, value)

    def getDiscount(self):
        return self._getNumber(3)

    def setDiscount(self, value):
        self._setNumber(3, value)

    def _initialize(self):
        super(NyDiscountRewardTooltipModel, self)._initialize()
        self._addNumberProperty('level', 0)
        self._addNumberProperty('questsCount', 0)
        self._addStringProperty('selectedVehicle', '')
        self._addNumberProperty('discount', 0)
