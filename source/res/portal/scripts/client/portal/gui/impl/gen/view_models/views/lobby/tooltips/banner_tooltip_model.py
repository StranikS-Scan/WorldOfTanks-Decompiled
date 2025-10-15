# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/impl/gen/view_models/views/lobby/tooltips/banner_tooltip_model.py
from frameworks.wulf import ViewModel

class BannerTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(BannerTooltipModel, self).__init__(properties=properties, commands=commands)

    def getPerformance(self):
        return self._getNumber(0)

    def setPerformance(self, value):
        self._setNumber(0, value)

    def getStartDate(self):
        return self._getNumber(1)

    def setStartDate(self, value):
        self._setNumber(1, value)

    def getEndDate(self):
        return self._getNumber(2)

    def setEndDate(self, value):
        self._setNumber(2, value)

    def _initialize(self):
        super(BannerTooltipModel, self)._initialize()
        self._addNumberProperty('performance', 0)
        self._addNumberProperty('startDate', 0)
        self._addNumberProperty('endDate', 0)
