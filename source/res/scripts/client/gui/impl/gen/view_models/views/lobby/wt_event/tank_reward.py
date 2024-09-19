# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/wt_event/tank_reward.py
from enum import Enum
from frameworks.wulf import ViewModel

class EventTankType(Enum):
    PRIMARY = 'G171_E77'
    SECONDARY = 'Cz14_Skoda_T_56_WT24_3Dst'
    TERTIARY = 'G166_LKpz_70_K'


class TankReward(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(TankReward, self).__init__(properties=properties, commands=commands)

    def getTooltipId(self):
        return self._getNumber(0)

    def setTooltipId(self, value):
        self._setNumber(0, value)

    def getIsCollected(self):
        return self._getBool(1)

    def setIsCollected(self, value):
        self._setBool(1, value)

    def getTankType(self):
        return EventTankType(self._getString(2))

    def setTankType(self, value):
        self._setString(2, value.value)

    def _initialize(self):
        super(TankReward, self)._initialize()
        self._addNumberProperty('tooltipId', 0)
        self._addBoolProperty('isCollected', False)
        self._addStringProperty('tankType')
