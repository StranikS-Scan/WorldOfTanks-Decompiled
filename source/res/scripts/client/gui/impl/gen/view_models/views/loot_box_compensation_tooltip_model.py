# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/loot_box_compensation_tooltip_model.py
from frameworks.wulf import ViewModel

class LootBoxCompensationTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=7, commands=0):
        super(LootBoxCompensationTooltipModel, self).__init__(properties=properties, commands=commands)

    def getIconBefore(self):
        return self._getString(0)

    def setIconBefore(self, value):
        self._setString(0, value)

    def getIconAfter(self):
        return self._getString(1)

    def setIconAfter(self, value):
        self._setString(1, value)

    def getLabelBefore(self):
        return self._getString(2)

    def setLabelBefore(self, value):
        self._setString(2, value)

    def getLabelAfter(self):
        return self._getString(3)

    def setLabelAfter(self, value):
        self._setString(3, value)

    def getBonusName(self):
        return self._getString(4)

    def setBonusName(self, value):
        self._setString(4, value)

    def getTooltipType(self):
        return self._getString(5)

    def setTooltipType(self, value):
        self._setString(5, value)

    def getCountBefore(self):
        return self._getNumber(6)

    def setCountBefore(self, value):
        self._setNumber(6, value)

    def _initialize(self):
        super(LootBoxCompensationTooltipModel, self)._initialize()
        self._addStringProperty('iconBefore', '')
        self._addStringProperty('iconAfter', '')
        self._addStringProperty('labelBefore', '')
        self._addStringProperty('labelAfter', '')
        self._addStringProperty('bonusName', '')
        self._addStringProperty('tooltipType', 'base')
        self._addNumberProperty('countBefore', 1)
