# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/bm2021/reward_item_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class RewardItemModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=7, commands=0):
        super(RewardItemModel, self).__init__(properties=properties, commands=commands)

    def getName(self):
        return self._getString(0)

    def setName(self, value):
        self._setString(0, value)

    def getIcon(self):
        return self._getResource(1)

    def setIcon(self, value):
        self._setResource(1, value)

    def getBigIcon(self):
        return self._getResource(2)

    def setBigIcon(self, value):
        self._setResource(2, value)

    def getTooltipId(self):
        return self._getString(3)

    def setTooltipId(self, value):
        self._setString(3, value)

    def getValue(self):
        return self._getNumber(4)

    def setValue(self, value):
        self._setNumber(4, value)

    def getItemCD(self):
        return self._getNumber(5)

    def setItemCD(self, value):
        self._setNumber(5, value)

    def getItemType(self):
        return self._getString(6)

    def setItemType(self, value):
        self._setString(6, value)

    def _initialize(self):
        super(RewardItemModel, self)._initialize()
        self._addStringProperty('name', '')
        self._addResourceProperty('icon', R.invalid())
        self._addResourceProperty('bigIcon', R.invalid())
        self._addStringProperty('tooltipId', '')
        self._addNumberProperty('value', 0)
        self._addNumberProperty('itemCD', 0)
        self._addStringProperty('itemType', '')
