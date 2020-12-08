# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/lootboxes/components/loot_box_count_button_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class LootBoxCountButtonModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(LootBoxCountButtonModel, self).__init__(properties=properties, commands=commands)

    def getLabel(self):
        return self._getResource(0)

    def setLabel(self, value):
        self._setResource(0, value)

    def getIsVisible(self):
        return self._getBool(1)

    def setIsVisible(self, value):
        self._setBool(1, value)

    def getIsSelected(self):
        return self._getBool(2)

    def setIsSelected(self, value):
        self._setBool(2, value)

    def getIsEnabled(self):
        return self._getBool(3)

    def setIsEnabled(self, value):
        self._setBool(3, value)

    def getIdx(self):
        return self._getNumber(4)

    def setIdx(self, value):
        self._setNumber(4, value)

    def _initialize(self):
        super(LootBoxCountButtonModel, self)._initialize()
        self._addResourceProperty('label', R.invalid())
        self._addBoolProperty('isVisible', True)
        self._addBoolProperty('isSelected', False)
        self._addBoolProperty('isEnabled', True)
        self._addNumberProperty('idx', 0)
