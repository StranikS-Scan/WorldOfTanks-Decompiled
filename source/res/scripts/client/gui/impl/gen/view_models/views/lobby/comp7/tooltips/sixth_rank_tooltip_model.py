# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/comp7/tooltips/sixth_rank_tooltip_model.py
from frameworks.wulf import ViewModel

class SixthRankTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(SixthRankTooltipModel, self).__init__(properties=properties, commands=commands)

    def getFrom(self):
        return self._getNumber(0)

    def setFrom(self, value):
        self._setNumber(0, value)

    def _initialize(self):
        super(SixthRankTooltipModel, self)._initialize()
        self._addNumberProperty('from', 2000)
