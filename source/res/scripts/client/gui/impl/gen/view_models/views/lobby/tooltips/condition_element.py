# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/tooltips/condition_element.py
from enum import Enum
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class ElementType(Enum):
    OPERAND = 'operand'
    OPERATORAND = 'operatorAnd'
    OPERATOROR = 'operatorOr'


class ConditionElement(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(ConditionElement, self).__init__(properties=properties, commands=commands)

    def getType(self):
        return ElementType(self._getString(0))

    def setType(self, value):
        self._setString(0, value.value)

    def getText(self):
        return self._getResource(1)

    def setText(self, value):
        self._setResource(1, value)

    def _initialize(self):
        super(ConditionElement, self)._initialize()
        self._addStringProperty('type')
        self._addResourceProperty('text', R.invalid())
