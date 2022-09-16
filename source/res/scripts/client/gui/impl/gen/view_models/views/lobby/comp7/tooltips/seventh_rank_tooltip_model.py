# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/comp7/tooltips/seventh_rank_tooltip_model.py
from frameworks.wulf import ViewModel

class SeventhRankTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(SeventhRankTooltipModel, self).__init__(properties=properties, commands=commands)

    def getTopPercentage(self):
        return self._getNumber(0)

    def setTopPercentage(self, value):
        self._setNumber(0, value)

    def _initialize(self):
        super(SeventhRankTooltipModel, self)._initialize()
        self._addNumberProperty('topPercentage', 10)
