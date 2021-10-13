# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/yha/reward_model.py
from frameworks.wulf import ViewModel

class RewardModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(RewardModel, self).__init__(properties=properties, commands=commands)

    def getName(self):
        return self._getString(0)

    def setName(self, value):
        self._setString(0, value)

    def getCount(self):
        return self._getNumber(1)

    def setCount(self, value):
        self._setNumber(1, value)

    def getTooltipContentId(self):
        return self._getNumber(2)

    def setTooltipContentId(self, value):
        self._setNumber(2, value)

    def getTooltipId(self):
        return self._getNumber(3)

    def setTooltipId(self, value):
        self._setNumber(3, value)

    def _initialize(self):
        super(RewardModel, self)._initialize()
        self._addStringProperty('name', '')
        self._addNumberProperty('count', 0)
        self._addNumberProperty('tooltipContentId', 0)
        self._addNumberProperty('tooltipId', 0)
