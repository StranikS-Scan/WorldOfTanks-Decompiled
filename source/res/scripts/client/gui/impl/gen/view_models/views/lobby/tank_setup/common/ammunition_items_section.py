# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/tank_setup/common/ammunition_items_section.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.tank_setup.common.base_ammunition_slot import BaseAmmunitionSlot

class AmmunitionItemsSection(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(AmmunitionItemsSection, self).__init__(properties=properties, commands=commands)

    def getType(self):
        return self._getString(0)

    def setType(self, value):
        self._setString(0, value)

    def getName(self):
        return self._getString(1)

    def setName(self, value):
        self._setString(1, value)

    def getNewItemsCount(self):
        return self._getNumber(2)

    def setNewItemsCount(self, value):
        self._setNumber(2, value)

    def getSlots(self):
        return self._getArray(3)

    def setSlots(self, value):
        self._setArray(3, value)

    def _initialize(self):
        super(AmmunitionItemsSection, self)._initialize()
        self._addStringProperty('type', '')
        self._addStringProperty('name', '')
        self._addNumberProperty('newItemsCount', 0)
        self._addArrayProperty('slots', Array())
