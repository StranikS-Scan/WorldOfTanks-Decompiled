# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/lootbox_system/tooltips/guaranteed_reward_info_tooltip_view_model.py
from frameworks.wulf import ViewModel

class GuaranteedRewardInfoTooltipViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(GuaranteedRewardInfoTooltipViewModel, self).__init__(properties=properties, commands=commands)

    def getEventName(self):
        return self._getString(0)

    def setEventName(self, value):
        self._setString(0, value)

    def getGuaranteedFrequency(self):
        return self._getNumber(1)

    def setGuaranteedFrequency(self, value):
        self._setNumber(1, value)

    def _initialize(self):
        super(GuaranteedRewardInfoTooltipViewModel, self)._initialize()
        self._addStringProperty('eventName', '')
        self._addNumberProperty('guaranteedFrequency', 0)
