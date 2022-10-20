# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/gen/view_models/views/lobby/common/phase_item_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class PhaseStatus(Enum):
    ACTIVE = 'active'
    LOCKED = 'locked'
    COMPLETED = 'completed'
    OVERDUE = 'overdue'


class PhaseItemModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(PhaseItemModel, self).__init__(properties=properties, commands=commands)

    def getPhase(self):
        return self._getNumber(0)

    def setPhase(self, value):
        self._setNumber(0, value)

    def getStartDate(self):
        return self._getNumber(1)

    def setStartDate(self, value):
        self._setNumber(1, value)

    def getEndDate(self):
        return self._getNumber(2)

    def setEndDate(self, value):
        self._setNumber(2, value)

    def getStatus(self):
        return PhaseStatus(self._getString(3))

    def setStatus(self, value):
        self._setString(3, value.value)

    def _initialize(self):
        super(PhaseItemModel, self)._initialize()
        self._addNumberProperty('phase', 0)
        self._addNumberProperty('startDate', 0)
        self._addNumberProperty('endDate', 0)
        self._addStringProperty('status')
