# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: winback/scripts/client/winback/gui/impl/gen/view_models/views/lobby/tooltips/selectable_reward_tooltip_model.py
from frameworks.wulf import ViewModel

class SelectableRewardTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(SelectableRewardTooltipModel, self).__init__(properties=properties, commands=commands)

    def getLevel(self):
        return self._getNumber(0)

    def setLevel(self, value):
        self._setNumber(0, value)

    def getPurchaseDiscount(self):
        return self._getNumber(1)

    def setPurchaseDiscount(self, value):
        self._setNumber(1, value)

    def getResearchDiscount(self):
        return self._getNumber(2)

    def setResearchDiscount(self, value):
        self._setNumber(2, value)

    def getIsDiscount(self):
        return self._getBool(3)

    def setIsDiscount(self, value):
        self._setBool(3, value)

    def _initialize(self):
        super(SelectableRewardTooltipModel, self)._initialize()
        self._addNumberProperty('level', 0)
        self._addNumberProperty('purchaseDiscount', 0)
        self._addNumberProperty('researchDiscount', 0)
        self._addBoolProperty('isDiscount', False)
