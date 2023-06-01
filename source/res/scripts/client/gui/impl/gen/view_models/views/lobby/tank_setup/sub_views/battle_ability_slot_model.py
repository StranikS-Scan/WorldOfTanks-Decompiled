# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/tank_setup/sub_views/battle_ability_slot_model.py
from frameworks.wulf import Array
from gui.impl.gen.view_models.views.lobby.tank_setup.sub_views.base_slot_model import BaseSlotModel
from gui.impl.gen.view_models.views.lobby.tank_setup.sub_views.battle_ability_by_rank_model import BattleAbilityByRankModel

class BattleAbilitySlotModel(BaseSlotModel):
    __slots__ = ()

    def __init__(self, properties=29, commands=0):
        super(BattleAbilitySlotModel, self).__init__(properties=properties, commands=commands)

    def getLevel(self):
        return self._getNumber(20)

    def setLevel(self, value):
        self._setNumber(20, value)

    def getCost(self):
        return self._getNumber(21)

    def setCost(self, value):
        self._setNumber(21, value)

    def getTargetSlotId(self):
        return self._getNumber(22)

    def setTargetSlotId(self, value):
        self._setNumber(22, value)

    def getSkillId(self):
        return self._getNumber(23)

    def setSkillId(self, value):
        self._setNumber(23, value)

    def getKeyName(self):
        return self._getString(24)

    def setKeyName(self, value):
        self._setString(24, value)

    def getDescription(self):
        return self._getString(25)

    def setDescription(self, value):
        self._setString(25, value)

    def getCategory(self):
        return self._getString(26)

    def setCategory(self, value):
        self._setString(26, value)

    def getRanks(self):
        return self._getArray(27)

    def setRanks(self, value):
        self._setArray(27, value)

    @staticmethod
    def getRanksType():
        return unicode

    def getAbilitiesByRank(self):
        return self._getArray(28)

    def setAbilitiesByRank(self, value):
        self._setArray(28, value)

    @staticmethod
    def getAbilitiesByRankType():
        return BattleAbilityByRankModel

    def _initialize(self):
        super(BattleAbilitySlotModel, self)._initialize()
        self._addNumberProperty('level', 0)
        self._addNumberProperty('cost', 0)
        self._addNumberProperty('targetSlotId', 0)
        self._addNumberProperty('skillId', 0)
        self._addStringProperty('keyName', '')
        self._addStringProperty('description', '')
        self._addStringProperty('category', '')
        self._addArrayProperty('ranks', Array())
        self._addArrayProperty('abilitiesByRank', Array())
