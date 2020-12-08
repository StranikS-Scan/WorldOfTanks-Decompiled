# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/tank_setup/common/ny_style_ammunition_slot.py
from gui.impl.gen.view_models.views.lobby.tank_setup.common.base_ammunition_slot import BaseAmmunitionSlot

class NyStyleAmmunitionSlot(BaseAmmunitionSlot):
    __slots__ = ()

    def __init__(self, properties=11, commands=0):
        super(NyStyleAmmunitionSlot, self).__init__(properties=properties, commands=commands)

    def getIsSelected(self):
        return self._getBool(8)

    def setIsSelected(self, value):
        self._setBool(8, value)

    def getIsLocked(self):
        return self._getBool(9)

    def setIsLocked(self, value):
        self._setBool(9, value)

    def getIsOutfitLocked(self):
        return self._getBool(10)

    def setIsOutfitLocked(self, value):
        self._setBool(10, value)

    def _initialize(self):
        super(NyStyleAmmunitionSlot, self)._initialize()
        self._addBoolProperty('isSelected', False)
        self._addBoolProperty('isLocked', False)
        self._addBoolProperty('isOutfitLocked', False)
