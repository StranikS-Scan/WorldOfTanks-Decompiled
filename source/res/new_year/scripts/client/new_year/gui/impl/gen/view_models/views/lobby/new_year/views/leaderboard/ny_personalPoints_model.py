# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/gen/view_models/views/lobby/new_year/views/leaderboard/ny_personalPoints_model.py
from frameworks.wulf import ViewModel

class NyPersonalpointsModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(NyPersonalpointsModel, self).__init__(properties=properties, commands=commands)

    def getNextTopPoints(self):
        return self._getNumber(0)

    def setNextTopPoints(self, value):
        self._setNumber(0, value)

    def getOpponentPoints(self):
        return self._getNumber(1)

    def setOpponentPoints(self, value):
        self._setNumber(1, value)

    def _initialize(self):
        super(NyPersonalpointsModel, self)._initialize()
        self._addNumberProperty('nextTopPoints', 0)
        self._addNumberProperty('opponentPoints', 0)
