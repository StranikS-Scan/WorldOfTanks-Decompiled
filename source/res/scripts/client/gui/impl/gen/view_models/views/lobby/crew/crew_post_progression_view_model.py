# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/crew_post_progression_view_model.py
from enum import Enum
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class PauseReasonType(Enum):
    NONE = ''
    LOWEFFICIENCY = 'lowEfficiency'
    RETIRE = 'retire'


class CrewPostProgressionViewModel(ViewModel):
    __slots__ = ('onClaim',)

    def __init__(self, properties=7, commands=1):
        super(CrewPostProgressionViewModel, self).__init__(properties=properties, commands=commands)

    def getTitle(self):
        return self._getResource(0)

    def setTitle(self, value):
        self._setResource(0, value)

    def getDescription(self):
        return self._getString(1)

    def setDescription(self, value):
        self._setString(1, value)

    def getIcon(self):
        return self._getResource(2)

    def setIcon(self, value):
        self._setResource(2, value)

    def getCount(self):
        return self._getNumber(3)

    def setCount(self, value):
        self._setNumber(3, value)

    def getProgressCurrent(self):
        return self._getNumber(4)

    def setProgressCurrent(self, value):
        self._setNumber(4, value)

    def getProgressMax(self):
        return self._getNumber(5)

    def setProgressMax(self, value):
        self._setNumber(5, value)

    def getPauseReason(self):
        return PauseReasonType(self._getString(6))

    def setPauseReason(self, value):
        self._setString(6, value.value)

    def _initialize(self):
        super(CrewPostProgressionViewModel, self)._initialize()
        self._addResourceProperty('title', R.invalid())
        self._addStringProperty('description', '')
        self._addResourceProperty('icon', R.invalid())
        self._addNumberProperty('count', 0)
        self._addNumberProperty('progressCurrent', 0)
        self._addNumberProperty('progressMax', 0)
        self._addStringProperty('pauseReason', PauseReasonType.NONE.value)
        self.onClaim = self._addCommand('onClaim')
