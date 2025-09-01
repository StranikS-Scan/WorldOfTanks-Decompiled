# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/tank_setup/common/battle_ability_ammunition_slot.py
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.tank_setup.common.base_ammunition_slot import BaseAmmunitionSlot

class BattleAbilityAmmunitionSlot(BaseAmmunitionSlot):
    __slots__ = ()

    def __init__(self, properties=15, commands=0):
        super(BattleAbilityAmmunitionSlot, self).__init__(properties=properties, commands=commands)

    def getLevel(self):
        return self._getNumber(13)

    def setLevel(self, value):
        self._setNumber(13, value)

    def getRank(self):
        return self._getResource(14)

    def setRank(self, value):
        self._setResource(14, value)

    def _initialize(self):
        super(BattleAbilityAmmunitionSlot, self)._initialize()
        self._addNumberProperty('level', 0)
        self._addResourceProperty('rank', R.invalid())
