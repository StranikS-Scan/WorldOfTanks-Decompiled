# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/platoon/ranked_platoon_rank_data.py
from frameworks.wulf import ViewModel

class RankedPlatoonRankData(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(RankedPlatoonRankData, self).__init__(properties=properties, commands=commands)

    def getRank(self):
        return self._getNumber(0)

    def setRank(self, value):
        self._setNumber(0, value)

    def getDivision(self):
        return self._getNumber(1)

    def setDivision(self, value):
        self._setNumber(1, value)

    def _initialize(self):
        super(RankedPlatoonRankData, self)._initialize()
        self._addNumberProperty('rank', 0)
        self._addNumberProperty('division', 0)
