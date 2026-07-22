# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/tooltips/preferred_map_slot_reward_tooltip_model.py
from frameworks.wulf import ViewModel

class PreferredMapSlotRewardTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(PreferredMapSlotRewardTooltipModel, self).__init__(properties=properties, commands=commands)

    def getSlotName(self):
        return self._getString(0)

    def setSlotName(self, value):
        self._setString(0, value)

    def getAmountDay(self):
        return self._getNumber(1)

    def setAmountDay(self, value):
        self._setNumber(1, value)

    def getExpire(self):
        return self._getNumber(2)

    def setExpire(self, value):
        self._setNumber(2, value)

    def _initialize(self):
        super(PreferredMapSlotRewardTooltipModel, self)._initialize()
        self._addStringProperty('slotName', '')
        self._addNumberProperty('amountDay', 0)
        self._addNumberProperty('expire', 0)
