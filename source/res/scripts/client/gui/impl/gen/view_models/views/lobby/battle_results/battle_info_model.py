# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_results/battle_info_model.py
from enum import Enum
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class WinStatus(Enum):
    DRAW = 'tie'
    WIN = 'win'
    LOSE = 'lose'


class BattleInfoModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(BattleInfoModel, self).__init__(properties=properties, commands=commands)

    def getModeName(self):
        return self._getString(0)

    def setModeName(self, value):
        self._setString(0, value)

    def getArenaName(self):
        return self._getString(1)

    def setArenaName(self, value):
        self._setString(1, value)

    def getBattleStartTime(self):
        return self._getNumber(2)

    def setBattleStartTime(self, value):
        self._setNumber(2, value)

    def getBattleDuration(self):
        return self._getNumber(3)

    def setBattleDuration(self, value):
        self._setNumber(3, value)

    def getWinStatus(self):
        return WinStatus(self._getString(4))

    def setWinStatus(self, value):
        self._setString(4, value.value)

    def getFinishReason(self):
        return self._getResource(5)

    def setFinishReason(self, value):
        self._setResource(5, value)

    def _initialize(self):
        super(BattleInfoModel, self)._initialize()
        self._addStringProperty('modeName', '')
        self._addStringProperty('arenaName', '')
        self._addNumberProperty('battleStartTime', 0)
        self._addNumberProperty('battleDuration', 0)
        self._addStringProperty('winStatus')
        self._addResourceProperty('finishReason', R.invalid())
