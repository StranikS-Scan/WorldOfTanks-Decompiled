# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/gen/view_models/views/lobby/tooltips/daily_reward_tooltip_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from halloween.gui.impl.gen.view_models.views.lobby.tooltips.halloween_tooltip_ability_item import HalloweenTooltipAbilityItem

class DailyRewardTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(DailyRewardTooltipModel, self).__init__(properties=properties, commands=commands)

    def getAbilities(self):
        return self._getArray(0)

    def setAbilities(self, value):
        self._setArray(0, value)

    @staticmethod
    def getAbilitiesType():
        return HalloweenTooltipAbilityItem

    def _initialize(self):
        super(DailyRewardTooltipModel, self)._initialize()
        self._addArrayProperty('abilities', Array())
