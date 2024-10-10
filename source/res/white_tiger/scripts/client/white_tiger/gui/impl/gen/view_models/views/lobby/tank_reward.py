# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/gen/view_models/views/lobby/tank_reward.py
from frameworks.wulf import ViewModel

class TankReward(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(TankReward, self).__init__(properties=properties, commands=commands)

    def getTooltipId(self):
        return self._getNumber(0)

    def setTooltipId(self, value):
        self._setNumber(0, value)

    def getTankName(self):
        return self._getString(1)

    def setTankName(self, value):
        self._setString(1, value)

    def getIsCollected(self):
        return self._getBool(2)

    def setIsCollected(self, value):
        self._setBool(2, value)

    def _initialize(self):
        super(TankReward, self)._initialize()
        self._addNumberProperty('tooltipId', 0)
        self._addStringProperty('tankName', '')
        self._addBoolProperty('isCollected', False)
