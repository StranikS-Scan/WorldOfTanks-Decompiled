# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/ranked/ranked_state_model.py
from frameworks.wulf import ViewModel

class RankedStateModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(RankedStateModel, self).__init__(properties=properties, commands=commands)

    def getDivision(self):
        return self._getNumber(0)

    def setDivision(self, value):
        self._setNumber(0, value)

    def getRank(self):
        return self._getNumber(1)

    def setRank(self, value):
        self._setNumber(1, value)

    def getStep(self):
        return self._getNumber(2)

    def setStep(self, value):
        self._setNumber(2, value)

    def getDivisionStart(self):
        return self._getNumber(3)

    def setDivisionStart(self, value):
        self._setNumber(3, value)

    def getDivisionFinish(self):
        return self._getNumber(4)

    def setDivisionFinish(self, value):
        self._setNumber(4, value)

    def _initialize(self):
        super(RankedStateModel, self)._initialize()
        self._addNumberProperty('division', 0)
        self._addNumberProperty('rank', 0)
        self._addNumberProperty('step', 0)
        self._addNumberProperty('divisionStart', 0)
        self._addNumberProperty('divisionFinish', 0)
