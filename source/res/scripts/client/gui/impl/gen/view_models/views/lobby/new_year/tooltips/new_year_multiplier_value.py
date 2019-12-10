# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/tooltips/new_year_multiplier_value.py
from frameworks.wulf import ViewModel

class NewYearMultiplierValue(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(NewYearMultiplierValue, self).__init__(properties=properties, commands=commands)

    def getLevels(self):
        return self._getString(0)

    def setLevels(self, value):
        self._setString(0, value)

    def getMultiplier(self):
        return self._getNumber(1)

    def setMultiplier(self, value):
        self._setNumber(1, value)

    def getIsEnabled(self):
        return self._getBool(2)

    def setIsEnabled(self, value):
        self._setBool(2, value)

    def _initialize(self):
        super(NewYearMultiplierValue, self)._initialize()
        self._addStringProperty('levels', 'I-III')
        self._addNumberProperty('multiplier', 1)
        self._addBoolProperty('isEnabled', False)
