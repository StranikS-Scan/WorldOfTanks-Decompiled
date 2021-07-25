# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/tooltips/discount_item_tooltip_model.py
from frameworks.wulf import ViewModel

class DiscountItemTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(DiscountItemTooltipModel, self).__init__(properties=properties, commands=commands)

    def getName(self):
        return self._getString(0)

    def setName(self, value):
        self._setString(0, value)

    def getDescription(self):
        return self._getString(1)

    def setDescription(self, value):
        self._setString(1, value)

    def getDiscountLabel(self):
        return self._getString(2)

    def setDiscountLabel(self, value):
        self._setString(2, value)

    def getDiscountAmount(self):
        return self._getString(3)

    def setDiscountAmount(self, value):
        self._setString(3, value)

    def _initialize(self):
        super(DiscountItemTooltipModel, self)._initialize()
        self._addStringProperty('name', '')
        self._addStringProperty('description', '')
        self._addStringProperty('discountLabel', '')
        self._addStringProperty('discountAmount', '')
