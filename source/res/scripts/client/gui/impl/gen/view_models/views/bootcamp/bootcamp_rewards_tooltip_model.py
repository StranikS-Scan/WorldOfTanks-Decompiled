# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/bootcamp/bootcamp_rewards_tooltip_model.py
from frameworks.wulf import ViewModel

class BootcampRewardsTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(BootcampRewardsTooltipModel, self).__init__(properties=properties, commands=commands)

    def getIsNeedAwarding(self):
        return self._getBool(0)

    def setIsNeedAwarding(self, value):
        self._setBool(0, value)

    def _initialize(self):
        super(BootcampRewardsTooltipModel, self)._initialize()
        self._addBoolProperty('isNeedAwarding', False)
