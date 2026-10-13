# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/gen/view_models/views/lobby/reward_view_model.py
from frameworks.wulf import ViewModel

class RewardViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(RewardViewModel, self).__init__(properties=properties, commands=commands)

    def getId(self):
        return self._getString(0)

    def setId(self, value):
        self._setString(0, value)

    def getIcon(self):
        return self._getString(1)

    def setIcon(self, value):
        self._setString(1, value)

    def getName(self):
        return self._getString(2)

    def setName(self, value):
        self._setString(2, value)

    def getCountInStock(self):
        return self._getNumber(3)

    def setCountInStock(self, value):
        self._setNumber(3, value)

    def getMaxCount(self):
        return self._getNumber(4)

    def setMaxCount(self, value):
        self._setNumber(4, value)

    def getTooltipId(self):
        return self._getString(5)

    def setTooltipId(self, value):
        self._setString(5, value)

    def _initialize(self):
        super(RewardViewModel, self)._initialize()
        self._addStringProperty('id', '')
        self._addStringProperty('icon', '')
        self._addStringProperty('name', '')
        self._addNumberProperty('countInStock', 0)
        self._addNumberProperty('maxCount', 0)
        self._addStringProperty('tooltipId', '')
