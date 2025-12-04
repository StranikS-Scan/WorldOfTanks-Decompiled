# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: gui_lootboxes/scripts/client/gui_lootboxes/gui/impl/gen/view_models/views/lobby/gui_lootboxes/tooltips/short_statistic_lootboxes.py
from frameworks.wulf import ViewModel

class ShortStatisticLootboxes(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(ShortStatisticLootboxes, self).__init__(properties=properties, commands=commands)

    def getId(self):
        return self._getNumber(0)

    def setId(self, value):
        self._setNumber(0, value)

    def getName(self):
        return self._getString(1)

    def setName(self, value):
        self._setString(1, value)

    def getType(self):
        return self._getString(2)

    def setType(self, value):
        self._setString(2, value)

    def getDate(self):
        return self._getNumber(3)

    def setDate(self, value):
        self._setNumber(3, value)

    def _initialize(self):
        super(ShortStatisticLootboxes, self)._initialize()
        self._addNumberProperty('id', 0)
        self._addStringProperty('name', '')
        self._addStringProperty('type', '')
        self._addNumberProperty('date', 0)
