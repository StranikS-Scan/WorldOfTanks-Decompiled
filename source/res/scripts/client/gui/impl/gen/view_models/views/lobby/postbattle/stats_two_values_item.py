# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/postbattle/stats_two_values_item.py
from frameworks.wulf import Array
from gui.impl.gen.view_models.views.lobby.postbattle.stats_base_item import StatsBaseItem

class StatsTwoValuesItem(StatsBaseItem):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(StatsTwoValuesItem, self).__init__(properties=properties, commands=commands)

    def getValue(self):
        return self._getArray(4)

    def setValue(self, value):
        self._setArray(4, value)

    def _initialize(self):
        super(StatsTwoValuesItem, self)._initialize()
        self._addArrayProperty('value', Array())
