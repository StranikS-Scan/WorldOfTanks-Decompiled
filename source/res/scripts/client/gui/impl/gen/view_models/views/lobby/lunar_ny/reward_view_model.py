# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/lunar_ny/reward_view_model.py
from enum import IntEnum
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class RewardType(IntEnum):
    SIMPLE = 0
    CURRENCY = 1
    CUSTOMIZATIONDECAL = 2
    BADGE = 3
    ACHIEVEMENT = 4
    CHARMRARE = 5
    CHARMCOMMON = 6
    ENVELOPE = 7


class RewardViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(RewardViewModel, self).__init__(properties=properties, commands=commands)

    def getRewardType(self):
        return RewardType(self._getNumber(0))

    def setRewardType(self, value):
        self._setNumber(0, value.value)

    def getCount(self):
        return self._getNumber(1)

    def setCount(self, value):
        self._setNumber(1, value)

    def getRewardID(self):
        return self._getString(2)

    def setRewardID(self, value):
        self._setString(2, value)

    def getName(self):
        return self._getResource(3)

    def setName(self, value):
        self._setResource(3, value)

    def getTooltipContentID(self):
        return self._getNumber(4)

    def setTooltipContentID(self, value):
        self._setNumber(4, value)

    def getTooltipID(self):
        return self._getNumber(5)

    def setTooltipID(self, value):
        self._setNumber(5, value)

    def _initialize(self):
        super(RewardViewModel, self)._initialize()
        self._addNumberProperty('rewardType')
        self._addNumberProperty('count', 0)
        self._addStringProperty('rewardID', '')
        self._addResourceProperty('name', R.invalid())
        self._addNumberProperty('tooltipContentID', 0)
        self._addNumberProperty('tooltipID', 0)
