# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/tank_setup/sub_views/battle_ability_slot_model.py
from frameworks.wulf import Array
from gui.impl.gen.view_models.views.lobby.tank_setup.sub_views.base_slot_model import BaseSlotModel
from gui.impl.gen.view_models.views.lobby.tank_setup.sub_views.battle_ability_by_rank_model import BattleAbilityByRankModel

class BattleAbilitySlotModel(BaseSlotModel):
    __slots__ = ()

    def __init__(self, properties=25, commands=0):
        super(BattleAbilitySlotModel, self).__init__(properties=properties, commands=commands)

    def getLevel(self):
        return self._getNumber(19)

    def setLevel(self, value):
        self._setNumber(19, value)

    def getKeyName(self):
        return self._getString(20)

    def setKeyName(self, value):
        self._setString(20, value)

    def getDescription(self):
        return self._getString(21)

    def setDescription(self, value):
        self._setString(21, value)

    def getCategory(self):
        return self._getString(22)

    def setCategory(self, value):
        self._setString(22, value)

    def getRanks(self):
        return self._getArray(23)

    def setRanks(self, value):
        self._setArray(23, value)

    @staticmethod
    def getRanksType():
        return str

    def getAbilitiesByRank(self):
        return self._getArray(24)

    def setAbilitiesByRank(self, value):
        self._setArray(24, value)

    @staticmethod
    def getAbilitiesByRankType():
        return BattleAbilityByRankModel

    def _initialize(self):
        super(BattleAbilitySlotModel, self)._initialize()
        self._addNumberProperty('level', 0)
        self._addStringProperty('keyName', '')
        self._addStringProperty('description', '')
        self._addStringProperty('category', '')
        self._addArrayProperty('ranks', Array())
        self._addArrayProperty('abilitiesByRank', Array())
