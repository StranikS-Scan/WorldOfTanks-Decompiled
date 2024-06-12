# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/early_access/early_access_entry_point_view_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class ExtendedStates(Enum):
    WAITFORNEXTCHAPTER = 'waitForNextChapter'
    DISABLED = 'disabled'


class EarlyAccessEntryPointViewModel(ViewModel):
    __slots__ = ('onAction',)

    def __init__(self, properties=4, commands=1):
        super(EarlyAccessEntryPointViewModel, self).__init__(properties=properties, commands=commands)

    def getState(self):
        return self._getString(0)

    def setState(self, value):
        self._setString(0, value)

    def getProgressionLevel(self):
        return self._getNumber(1)

    def setProgressionLevel(self, value):
        self._setNumber(1, value)

    def getEndTimestamp(self):
        return self._getNumber(2)

    def setEndTimestamp(self, value):
        self._setNumber(2, value)

    def getIsFirstEnter(self):
        return self._getBool(3)

    def setIsFirstEnter(self, value):
        self._setBool(3, value)

    def _initialize(self):
        super(EarlyAccessEntryPointViewModel, self)._initialize()
        self._addStringProperty('state', '')
        self._addNumberProperty('progressionLevel', 0)
        self._addNumberProperty('endTimestamp', 0)
        self._addBoolProperty('isFirstEnter', True)
        self.onAction = self._addCommand('onAction')
