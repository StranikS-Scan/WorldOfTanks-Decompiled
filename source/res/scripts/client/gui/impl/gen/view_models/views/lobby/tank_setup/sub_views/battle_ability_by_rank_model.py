# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/tank_setup/sub_views/battle_ability_by_rank_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel

class BattleAbilityByRankModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(BattleAbilityByRankModel, self).__init__(properties=properties, commands=commands)

    def getName(self):
        return self._getString(0)

    def setName(self, value):
        self._setString(0, value)

    def getRankValues(self):
        return self._getArray(1)

    def setRankValues(self, value):
        self._setArray(1, value)

    def _initialize(self):
        super(BattleAbilityByRankModel, self)._initialize()
        self._addStringProperty('name', '')
        self._addArrayProperty('rankValues', Array())
