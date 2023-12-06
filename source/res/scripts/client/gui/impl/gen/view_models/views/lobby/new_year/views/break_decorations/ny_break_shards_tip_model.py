# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/break_decorations/ny_break_shards_tip_model.py
from frameworks.wulf import ViewModel

class NyBreakShardsTipModel(ViewModel):
    __slots__ = ()
    SHARDS_ENOUGH_TO_CREATE = 0
    SHARDS_NOT_ENOUGH_TO_CREATE = 1

    def __init__(self, properties=3, commands=0):
        super(NyBreakShardsTipModel, self).__init__(properties=properties, commands=commands)

    def getDecorationType(self):
        return self._getString(0)

    def setDecorationType(self, value):
        self._setString(0, value)

    def getShardsCountLeft(self):
        return self._getNumber(1)

    def setShardsCountLeft(self, value):
        self._setNumber(1, value)

    def getCurrentState(self):
        return self._getNumber(2)

    def setCurrentState(self, value):
        self._setNumber(2, value)

    def _initialize(self):
        super(NyBreakShardsTipModel, self)._initialize()
        self._addStringProperty('decorationType', 'random')
        self._addNumberProperty('shardsCountLeft', 0)
        self._addNumberProperty('currentState', 0)
