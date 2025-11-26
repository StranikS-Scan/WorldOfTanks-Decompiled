# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/impl/gen/view_models/views/lobby/tooltips/battle_ability_tooltip_levels_model.py
from frameworks.wulf import Array, ViewModel
from frontline.gui.impl.gen.view_models.views.lobby.tooltips.battle_ability_tooltip_param_model import BattleAbilityTooltipParamModel

class BattleAbilityTooltipLevelsModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(BattleAbilityTooltipLevelsModel, self).__init__(properties=properties, commands=commands)

    def getLevel(self):
        return self._getNumber(0)

    def setLevel(self, value):
        self._setNumber(0, value)

    def getParams(self):
        return self._getArray(1)

    def setParams(self, value):
        self._setArray(1, value)

    @staticmethod
    def getParamsType():
        return BattleAbilityTooltipParamModel

    def _initialize(self):
        super(BattleAbilityTooltipLevelsModel, self)._initialize()
        self._addNumberProperty('level', 0)
        self._addArrayProperty('params', Array())
