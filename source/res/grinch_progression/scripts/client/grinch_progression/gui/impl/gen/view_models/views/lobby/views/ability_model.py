# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch_progression/scripts/client/grinch_progression/gui/impl/gen/view_models/views/lobby/views/ability_model.py
from frameworks.wulf import ViewModel

class AbilityModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(AbilityModel, self).__init__(properties=properties, commands=commands)

    def getResourceKey(self):
        return self._getString(0)

    def setResourceKey(self, value):
        self._setString(0, value)

    def getKeyString(self):
        return self._getString(1)

    def setKeyString(self, value):
        self._setString(1, value)

    def getIntCD(self):
        return self._getNumber(2)

    def setIntCD(self, value):
        self._setNumber(2, value)

    def _initialize(self):
        super(AbilityModel, self)._initialize()
        self._addStringProperty('resourceKey', '')
        self._addStringProperty('keyString', '')
        self._addNumberProperty('intCD', 0)
