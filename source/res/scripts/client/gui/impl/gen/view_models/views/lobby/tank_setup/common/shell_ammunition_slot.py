# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/tank_setup/common/shell_ammunition_slot.py
from gui.impl.gen.view_models.views.lobby.tank_setup.common.base_ammunition_slot import BaseAmmunitionSlot

class ShellAmmunitionSlot(BaseAmmunitionSlot):
    __slots__ = ()

    def __init__(self, properties=13, commands=0):
        super(ShellAmmunitionSlot, self).__init__(properties=properties, commands=commands)

    def getCount(self):
        return self._getNumber(11)

    def setCount(self, value):
        self._setNumber(11, value)

    def getIsInfinity(self):
        return self._getBool(12)

    def setIsInfinity(self, value):
        self._setBool(12, value)

    def _initialize(self):
        super(ShellAmmunitionSlot, self)._initialize()
        self._addNumberProperty('count', 0)
        self._addBoolProperty('isInfinity', False)
