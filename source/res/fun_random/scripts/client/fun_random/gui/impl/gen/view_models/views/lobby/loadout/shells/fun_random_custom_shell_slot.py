# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/impl/gen/view_models/views/lobby/loadout/shells/fun_random_custom_shell_slot.py
from gui.impl.gen.view_models.views.lobby.tank_setup.common.base_ammunition_slot import BaseAmmunitionSlot

class FunRandomCustomShellSlot(BaseAmmunitionSlot):
    __slots__ = ()

    def __init__(self, properties=17, commands=0):
        super(FunRandomCustomShellSlot, self).__init__(properties=properties, commands=commands)

    def getCount(self):
        return self._getNumber(13)

    def setCount(self, value):
        self._setNumber(13, value)

    def getOriginalIdx(self):
        return self._getNumber(14)

    def setOriginalIdx(self, value):
        self._setNumber(14, value)

    def getImageNameOverride(self):
        return self._getString(15)

    def setImageNameOverride(self, value):
        self._setString(15, value)

    def getTooltipOverride(self):
        return self._getString(16)

    def setTooltipOverride(self, value):
        self._setString(16, value)

    def _initialize(self):
        super(FunRandomCustomShellSlot, self)._initialize()
        self._addNumberProperty('count', 0)
        self._addNumberProperty('originalIdx', 0)
        self._addStringProperty('imageNameOverride', '')
        self._addStringProperty('tooltipOverride', '')
