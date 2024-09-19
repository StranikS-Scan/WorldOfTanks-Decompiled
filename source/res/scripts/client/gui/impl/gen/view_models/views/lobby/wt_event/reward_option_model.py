# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/wt_event/reward_option_model.py
from frameworks.wulf import ViewModel

class RewardOptionModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(RewardOptionModel, self).__init__(properties=properties, commands=commands)

    def getIconName(self):
        return self._getString(0)

    def setIconName(self, value):
        self._setString(0, value)

    def getName(self):
        return self._getString(1)

    def setName(self, value):
        self._setString(1, value)

    def getGiftId(self):
        return self._getNumber(2)

    def setGiftId(self, value):
        self._setNumber(2, value)

    def getTooltipId(self):
        return self._getString(3)

    def setTooltipId(self, value):
        self._setString(3, value)

    def getCount(self):
        return self._getNumber(4)

    def setCount(self, value):
        self._setNumber(4, value)

    def getDescription(self):
        return self._getString(5)

    def setDescription(self, value):
        self._setString(5, value)

    def _initialize(self):
        super(RewardOptionModel, self)._initialize()
        self._addStringProperty('iconName', '')
        self._addStringProperty('name', '')
        self._addNumberProperty('giftId', 0)
        self._addStringProperty('tooltipId', '')
        self._addNumberProperty('count', 0)
        self._addStringProperty('description', '')
