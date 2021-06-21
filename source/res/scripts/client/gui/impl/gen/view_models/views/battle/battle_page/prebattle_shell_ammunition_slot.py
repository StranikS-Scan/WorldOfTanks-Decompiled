# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/battle/battle_page/prebattle_shell_ammunition_slot.py
from enum import IntEnum
from gui.impl.gen.view_models.views.lobby.tank_setup.common.shell_ammunition_slot import ShellAmmunitionSlot

class ShellBattleState(IntEnum):
    NORAML = 0
    CURRENT = 1
    NEXT = 2


class PrebattleShellAmmunitionSlot(ShellAmmunitionSlot):
    __slots__ = ()

    def __init__(self, properties=10, commands=0):
        super(PrebattleShellAmmunitionSlot, self).__init__(properties=properties, commands=commands)

    def getShellState(self):
        return ShellBattleState(self._getNumber(9))

    def setShellState(self, value):
        self._setNumber(9, value.value)

    def _initialize(self):
        super(PrebattleShellAmmunitionSlot, self)._initialize()
        self._addNumberProperty('shellState')
