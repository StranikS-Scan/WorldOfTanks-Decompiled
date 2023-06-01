# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/tank_setup/sub_views/battle_ability_level_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.tank_setup.sub_views.battle_ability_level_param_model import BattleAbilityLevelParamModel

class BattleAbilityLevelModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(BattleAbilityLevelModel, self).__init__(properties=properties, commands=commands)

    def getId(self):
        return self._getNumber(0)

    def setId(self, value):
        self._setNumber(0, value)

    def getParams(self):
        return self._getArray(1)

    def setParams(self, value):
        self._setArray(1, value)

    @staticmethod
    def getParamsType():
        return BattleAbilityLevelParamModel

    def _initialize(self):
        super(BattleAbilityLevelModel, self)._initialize()
        self._addNumberProperty('id', 0)
        self._addArrayProperty('params', Array())
