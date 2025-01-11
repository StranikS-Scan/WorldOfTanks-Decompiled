# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/tooltips/ny_replacement_timer_tooltip_model.py
from frameworks.wulf import ViewModel

class NyReplacementTimerTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(NyReplacementTimerTooltipModel, self).__init__(properties=properties, commands=commands)

    def getTimeTill(self):
        return self._getNumber(0)

    def setTimeTill(self, value):
        self._setNumber(0, value)

    def getIsAvailable(self):
        return self._getBool(1)

    def setIsAvailable(self, value):
        self._setBool(1, value)

    def getIsFinished(self):
        return self._getBool(2)

    def setIsFinished(self, value):
        self._setBool(2, value)

    def _initialize(self):
        super(NyReplacementTimerTooltipModel, self)._initialize()
        self._addNumberProperty('timeTill', 0)
        self._addBoolProperty('isAvailable', False)
        self._addBoolProperty('isFinished', False)
