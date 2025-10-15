# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/impl/gen/view_models/views/lobby/portal_complexity_level.py
from enum import Enum
from frameworks.wulf import ViewModel

class ComplexityLevelStatus(Enum):
    SELECTED = 'selected'
    DEFAULT = 'default'
    LOCKED = 'locked'
    LOCKED_BY_SQUAD = 'lockedBySquad'


class PortalComplexityLevel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(PortalComplexityLevel, self).__init__(properties=properties, commands=commands)

    def getLevel(self):
        return self._getNumber(0)

    def setLevel(self, value):
        self._setNumber(0, value)

    def getStatus(self):
        return ComplexityLevelStatus(self._getString(1))

    def setStatus(self, value):
        self._setString(1, value.value)

    def _initialize(self):
        super(PortalComplexityLevel, self)._initialize()
        self._addNumberProperty('level', 0)
        self._addStringProperty('status')
