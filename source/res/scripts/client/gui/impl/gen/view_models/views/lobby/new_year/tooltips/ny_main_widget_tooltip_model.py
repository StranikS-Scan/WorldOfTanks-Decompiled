# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/tooltips/ny_main_widget_tooltip_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.new_year.tooltips.ny_level_info import NyLevelInfo

class NyMainWidgetTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(NyMainWidgetTooltipModel, self).__init__(properties=properties, commands=commands)

    def getCurrentLevel(self):
        return self._getNumber(0)

    def setCurrentLevel(self, value):
        self._setNumber(0, value)

    def getCurrentPoints(self):
        return self._getNumber(1)

    def setCurrentPoints(self, value):
        self._setNumber(1, value)

    def getToPoints(self):
        return self._getNumber(2)

    def setToPoints(self, value):
        self._setNumber(2, value)

    def getIsRomanNumbersAllowed(self):
        return self._getBool(3)

    def setIsRomanNumbersAllowed(self, value):
        self._setBool(3, value)

    def getLevels(self):
        return self._getArray(4)

    def setLevels(self, value):
        self._setArray(4, value)

    @staticmethod
    def getLevelsType():
        return NyLevelInfo

    def _initialize(self):
        super(NyMainWidgetTooltipModel, self)._initialize()
        self._addNumberProperty('currentLevel', 1)
        self._addNumberProperty('currentPoints', 0)
        self._addNumberProperty('toPoints', 0)
        self._addBoolProperty('isRomanNumbersAllowed', False)
        self._addArrayProperty('levels', Array())
