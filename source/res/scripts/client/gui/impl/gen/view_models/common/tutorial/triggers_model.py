# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/common/tutorial/triggers_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel

class TriggersModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(TriggersModel, self).__init__(properties=properties, commands=commands)

    def getComponentId(self):
        return self._getString(0)

    def setComponentId(self, value):
        self._setString(0, value)

    def getTriggers(self):
        return self._getArray(1)

    def setTriggers(self, value):
        self._setArray(1, value)

    def _initialize(self):
        super(TriggersModel, self)._initialize()
        self._addStringProperty('componentId', '')
        self._addArrayProperty('triggers', Array())
