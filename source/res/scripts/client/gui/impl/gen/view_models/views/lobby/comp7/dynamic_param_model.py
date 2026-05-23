# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/comp7/dynamic_param_model.py
from frameworks.wulf import ViewModel

class DynamicParamModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(DynamicParamModel, self).__init__(properties=properties, commands=commands)

    def getName(self):
        return self._getString(0)

    def setName(self, value):
        self._setString(0, value)

    def getValue1(self):
        return self._getString(1)

    def setValue1(self, value):
        self._setString(1, value)

    def getValue2(self):
        return self._getString(2)

    def setValue2(self, value):
        self._setString(2, value)

    def getValue3(self):
        return self._getString(3)

    def setValue3(self, value):
        self._setString(3, value)

    def _initialize(self):
        super(DynamicParamModel, self)._initialize()
        self._addStringProperty('name', '')
        self._addStringProperty('value1', '')
        self._addStringProperty('value2', '')
        self._addStringProperty('value3', '')
