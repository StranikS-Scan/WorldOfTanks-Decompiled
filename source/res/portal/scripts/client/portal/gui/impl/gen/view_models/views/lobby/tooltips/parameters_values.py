# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/impl/gen/view_models/views/lobby/tooltips/parameters_values.py
from frameworks.wulf import ViewModel

class ParametersValues(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(ParametersValues, self).__init__(properties=properties, commands=commands)

    def getValue(self):
        return self._getString(0)

    def setValue(self, value):
        self._setString(0, value)

    def getIsWorst(self):
        return self._getBool(1)

    def setIsWorst(self, value):
        self._setBool(1, value)

    def getIsBetter(self):
        return self._getBool(2)

    def setIsBetter(self, value):
        self._setBool(2, value)

    def _initialize(self):
        super(ParametersValues, self)._initialize()
        self._addStringProperty('value', '')
        self._addBoolProperty('isWorst', False)
        self._addBoolProperty('isBetter', False)
