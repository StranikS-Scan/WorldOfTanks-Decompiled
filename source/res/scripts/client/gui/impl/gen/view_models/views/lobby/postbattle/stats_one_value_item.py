# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/postbattle/stats_one_value_item.py
from gui.impl.gen.view_models.views.lobby.postbattle.stats_base_item import StatsBaseItem

class StatsOneValueItem(StatsBaseItem):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(StatsOneValueItem, self).__init__(properties=properties, commands=commands)

    def getValue(self):
        return self._getNumber(4)

    def setValue(self, value):
        self._setNumber(4, value)

    def _initialize(self):
        super(StatsOneValueItem, self)._initialize()
        self._addNumberProperty('value', 0)
