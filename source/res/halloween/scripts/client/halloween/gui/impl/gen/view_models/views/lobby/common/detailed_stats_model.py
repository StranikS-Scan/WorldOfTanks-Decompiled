# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/gen/view_models/views/lobby/common/detailed_stats_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from halloween.gui.impl.gen.view_models.views.lobby.common.stat_model import StatModel

class DetailedStatsModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(DetailedStatsModel, self).__init__(properties=properties, commands=commands)

    def getStats(self):
        return self._getArray(0)

    def setStats(self, value):
        self._setArray(0, value)

    @staticmethod
    def getStatsType():
        return StatModel

    def _initialize(self):
        super(DetailedStatsModel, self)._initialize()
        self._addArrayProperty('stats', Array())
