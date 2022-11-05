# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/impl/gen/view_models/views/lobby/common/fun_random_progression_state.py
from enum import Enum
from frameworks.wulf import ViewModel

class FunRandomProgressionStatus(Enum):
    DISABLED = 'disabled'
    ACTIVE_FINAL = 'activeFinal'
    ACTIVE_RESETTABLE = 'activeResettable'
    COMPLETED_FINAL = 'completedFinal'
    COMPLETED_RESETTABLE = 'completedResettable'


class FunRandomProgressionState(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(FunRandomProgressionState, self).__init__(properties=properties, commands=commands)

    def getStatus(self):
        return FunRandomProgressionStatus(self._getString(0))

    def setStatus(self, value):
        self._setString(0, value.value)

    def getCurrentStage(self):
        return self._getNumber(1)

    def setCurrentStage(self, value):
        self._setNumber(1, value)

    def getMaximumStage(self):
        return self._getNumber(2)

    def setMaximumStage(self, value):
        self._setNumber(2, value)

    def getResetTimer(self):
        return self._getNumber(3)

    def setResetTimer(self, value):
        self._setNumber(3, value)

    def _initialize(self):
        super(FunRandomProgressionState, self)._initialize()
        self._addStringProperty('status')
        self._addNumberProperty('currentStage', -1)
        self._addNumberProperty('maximumStage', -1)
        self._addNumberProperty('resetTimer', -1)
