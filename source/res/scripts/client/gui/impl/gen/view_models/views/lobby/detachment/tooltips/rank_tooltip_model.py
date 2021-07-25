# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/tooltips/rank_tooltip_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class RankTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(RankTooltipModel, self).__init__(properties=properties, commands=commands)

    def getIcon(self):
        return self._getResource(0)

    def setIcon(self, value):
        self._setResource(0, value)

    def getRank(self):
        return self._getResource(1)

    def setRank(self, value):
        self._setResource(1, value)

    def _initialize(self):
        super(RankTooltipModel, self)._initialize()
        self._addResourceProperty('icon', R.invalid())
        self._addResourceProperty('rank', R.invalid())
