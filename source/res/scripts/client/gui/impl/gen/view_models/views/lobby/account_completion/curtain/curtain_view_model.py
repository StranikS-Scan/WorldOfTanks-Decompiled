# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/account_completion/curtain/curtain_view_model.py
from enum import IntEnum
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class CurtainStateEnum(IntEnum):
    CLOSED = 0
    OPENING = 1
    OPENED = 2
    CLOSING = 3
    HIDING = 4
    HIDDEN = 5
    REVEALING = 6


class CurtainViewModel(ViewModel):
    __slots__ = ('onMoveSpace', 'onStateTransitionComplete')

    def __init__(self, properties=4, commands=2):
        super(CurtainViewModel, self).__init__(properties=properties, commands=commands)

    def getState(self):
        return CurtainStateEnum(self._getNumber(0))

    def setState(self, value):
        self._setNumber(0, value.value)

    def getIsWaiting(self):
        return self._getBool(1)

    def setIsWaiting(self, value):
        self._setBool(1, value)

    def getWaitingText(self):
        return self._getResource(2)

    def setWaitingText(self, value):
        self._setResource(2, value)

    def getCurrentSubViewID(self):
        return self._getNumber(3)

    def setCurrentSubViewID(self, value):
        self._setNumber(3, value)

    def _initialize(self):
        super(CurtainViewModel, self)._initialize()
        self._addNumberProperty('state')
        self._addBoolProperty('isWaiting', False)
        self._addResourceProperty('waitingText', R.invalid())
        self._addNumberProperty('currentSubViewID', 0)
        self.onMoveSpace = self._addCommand('onMoveSpace')
        self.onStateTransitionComplete = self._addCommand('onStateTransitionComplete')
