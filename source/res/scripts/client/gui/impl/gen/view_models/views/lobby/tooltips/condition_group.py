# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/tooltips/condition_group.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel

class ConditionGroup(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(ConditionGroup, self).__init__(properties=properties, commands=commands)

    def getConditions(self):
        return self._getArray(0)

    def setConditions(self, value):
        self._setArray(0, value)

    @staticmethod
    def getConditionsType():
        return unicode

    def _initialize(self):
        super(ConditionGroup, self)._initialize()
        self._addArrayProperty('conditions', Array())
