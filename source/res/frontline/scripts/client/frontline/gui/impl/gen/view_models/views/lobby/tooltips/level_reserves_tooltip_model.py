# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/impl/gen/view_models/views/lobby/tooltips/level_reserves_tooltip_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel

class LevelReservesTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(LevelReservesTooltipModel, self).__init__(properties=properties, commands=commands)

    def getLevels(self):
        return self._getArray(0)

    def setLevels(self, value):
        self._setArray(0, value)

    @staticmethod
    def getLevelsType():
        return unicode

    def getHasOptionalReserves(self):
        return self._getBool(1)

    def setHasOptionalReserves(self, value):
        self._setBool(1, value)

    def _initialize(self):
        super(LevelReservesTooltipModel, self)._initialize()
        self._addArrayProperty('levels', Array())
        self._addBoolProperty('hasOptionalReserves', False)
