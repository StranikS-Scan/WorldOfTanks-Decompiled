# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/tooltips/ny_sack_random_reward_tooltip_model.py
from frameworks.wulf import ViewModel

class NySackRandomRewardTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(NySackRandomRewardTooltipModel, self).__init__(properties=properties, commands=commands)

    def getResourceType(self):
        return self._getString(0)

    def setResourceType(self, value):
        self._setString(0, value)

    def _initialize(self):
        super(NySackRandomRewardTooltipModel, self)._initialize()
        self._addStringProperty('resourceType', '')
