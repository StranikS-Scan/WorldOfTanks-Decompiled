# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/tooltips/crew_retrain_penalty_item.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class CrewRetrainPenaltyItem(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(CrewRetrainPenaltyItem, self).__init__(properties=properties, commands=commands)

    def getIcon(self):
        return self._getResource(0)

    def setIcon(self, value):
        self._setResource(0, value)

    def getRole(self):
        return self._getResource(1)

    def setRole(self, value):
        self._setResource(1, value)

    def getPercents(self):
        return self._getNumber(2)

    def setPercents(self, value):
        self._setNumber(2, value)

    def getValue(self):
        return self._getNumber(3)

    def setValue(self, value):
        self._setNumber(3, value)

    def _initialize(self):
        super(CrewRetrainPenaltyItem, self)._initialize()
        self._addResourceProperty('icon', R.invalid())
        self._addResourceProperty('role', R.invalid())
        self._addNumberProperty('percents', 0)
        self._addNumberProperty('value', 0)
