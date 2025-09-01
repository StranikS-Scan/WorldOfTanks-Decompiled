# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/page/footer/session_stats_model.py
from frameworks.wulf import ViewModel

class SessionStatsModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(SessionStatsModel, self).__init__(properties=properties, commands=commands)

    def getBattleCount(self):
        return self._getNumber(0)

    def setBattleCount(self, value):
        self._setNumber(0, value)

    def getEnabled(self):
        return self._getBool(1)

    def setEnabled(self, value):
        self._setBool(1, value)

    def getSessionStatsEnabled(self):
        return self._getBool(2)

    def setSessionStatsEnabled(self, value):
        self._setBool(2, value)

    def getWinback(self):
        return self._getBool(3)

    def setWinback(self, value):
        self._setBool(3, value)

    def _initialize(self):
        super(SessionStatsModel, self)._initialize()
        self._addNumberProperty('battleCount', 0)
        self._addBoolProperty('enabled', False)
        self._addBoolProperty('sessionStatsEnabled', False)
        self._addBoolProperty('winback', False)
