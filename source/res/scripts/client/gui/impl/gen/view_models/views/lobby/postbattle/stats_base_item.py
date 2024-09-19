# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/postbattle/stats_base_item.py
from frameworks.wulf import ViewModel

class StatsBaseItem(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(StatsBaseItem, self).__init__(properties=properties, commands=commands)

    def getId(self):
        return self._getString(0)

    def setId(self, value):
        self._setString(0, value)

    def getBlockIdx(self):
        return self._getNumber(1)

    def setBlockIdx(self, value):
        self._setNumber(1, value)

    def getItemType(self):
        return self._getString(2)

    def setItemType(self, value):
        self._setString(2, value)

    def getHasTooltip(self):
        return self._getBool(3)

    def setHasTooltip(self, value):
        self._setBool(3, value)

    def _initialize(self):
        super(StatsBaseItem, self)._initialize()
        self._addStringProperty('id', '')
        self._addNumberProperty('blockIdx', 0)
        self._addStringProperty('itemType', '')
        self._addBoolProperty('hasTooltip', False)
