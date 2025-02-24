# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7/scripts/client/comp7/gui/impl/gen/view_models/views/lobby/platoon/platoon_rank_data.py
from comp7.gui.impl.gen.view_models.views.lobby.enums import Division, Rank
from frameworks.wulf import ViewModel

class PlatoonRankData(ViewModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(PlatoonRankData, self).__init__(properties=properties, commands=commands)

    def getRank(self):
        return Rank(self._getNumber(0))

    def setRank(self, value):
        self._setNumber(0, value.value)

    def getDivision(self):
        return Division(self._getNumber(1))

    def setDivision(self, value):
        self._setNumber(1, value.value)

    def getScore(self):
        return self._getNumber(2)

    def setScore(self, value):
        self._setNumber(2, value)

    def getFrom(self):
        return self._getNumber(3)

    def setFrom(self, value):
        self._setNumber(3, value)

    def getTo(self):
        return self._getNumber(4)

    def setTo(self, value):
        self._setNumber(4, value)

    def _initialize(self):
        super(PlatoonRankData, self)._initialize()
        self._addNumberProperty('rank')
        self._addNumberProperty('division')
        self._addNumberProperty('score', 0)
        self._addNumberProperty('from', 0)
        self._addNumberProperty('to', 0)
