# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/tooltips/additional_rewards_tooltip_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.missions.bonuses.bonus_model import BonusModel

class AdditionalRewardsTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(AdditionalRewardsTooltipModel, self).__init__(properties=properties, commands=commands)

    def getBonus(self):
        return self._getArray(0)

    def setBonus(self, value):
        self._setArray(0, value)

    def _initialize(self):
        super(AdditionalRewardsTooltipModel, self)._initialize()
        self._addArrayProperty('bonus', Array())
