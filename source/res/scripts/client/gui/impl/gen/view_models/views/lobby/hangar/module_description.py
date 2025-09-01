# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/hangar/module_description.py
from frameworks.wulf import ViewModel

class ModuleDescription(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(ModuleDescription, self).__init__(properties=properties, commands=commands)

    def getModuleType(self):
        return self._getString(0)

    def setModuleType(self, value):
        self._setString(0, value)

    def getModuleName(self):
        return self._getString(1)

    def setModuleName(self, value):
        self._setString(1, value)

    def getModuleXpCost(self):
        return self._getNumber(2)

    def setModuleXpCost(self, value):
        self._setNumber(2, value)

    def _initialize(self):
        super(ModuleDescription, self)._initialize()
        self._addStringProperty('moduleType', '')
        self._addStringProperty('moduleName', '')
        self._addNumberProperty('moduleXpCost', 0)
