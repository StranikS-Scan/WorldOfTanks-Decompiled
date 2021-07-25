# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/tank_setup/common/battle_ability_ammunition_slot.py
from gui.impl.gen.view_models.views.lobby.tank_setup.common.base_ammunition_slot import BaseAmmunitionSlot

class BattleAbilityAmmunitionSlot(BaseAmmunitionSlot):
    __slots__ = ()

    def __init__(self, properties=13, commands=0):
        super(BattleAbilityAmmunitionSlot, self).__init__(properties=properties, commands=commands)

    def getLevel(self):
        return self._getNumber(11)

    def setLevel(self, value):
        self._setNumber(11, value)

    def getRank(self):
        return self._getString(12)

    def setRank(self, value):
        self._setString(12, value)

    def _initialize(self):
        super(BattleAbilityAmmunitionSlot, self)._initialize()
        self._addNumberProperty('level', 0)
        self._addStringProperty('rank', 'private')
