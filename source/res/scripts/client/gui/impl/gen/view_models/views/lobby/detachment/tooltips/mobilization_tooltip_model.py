# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/tooltips/mobilization_tooltip_model.py
from frameworks.wulf import ViewModel

class MobilizationTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(MobilizationTooltipModel, self).__init__(properties=properties, commands=commands)

    def getEndTimeConvert(self):
        return self._getNumber(0)

    def setEndTimeConvert(self, value):
        self._setNumber(0, value)

    def getEndDate(self):
        return self._getString(1)

    def setEndDate(self, value):
        self._setString(1, value)

    def _initialize(self):
        super(MobilizationTooltipModel, self)._initialize()
        self._addNumberProperty('endTimeConvert', 0)
        self._addStringProperty('endDate', '')
