# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/user_missions/tooltips/challenges_restart_tooltip_model.py
from frameworks.wulf import ViewModel

class ChallengesRestartTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(ChallengesRestartTooltipModel, self).__init__(properties=properties, commands=commands)

    def getRestartCost(self):
        return self._getNumber(0)

    def setRestartCost(self, value):
        self._setNumber(0, value)

    def getCurrency(self):
        return self._getString(1)

    def setCurrency(self, value):
        self._setString(1, value)

    def getFreeRestarts(self):
        return self._getNumber(2)

    def setFreeRestarts(self, value):
        self._setNumber(2, value)

    def getUsedFreeRestarts(self):
        return self._getNumber(3)

    def setUsedFreeRestarts(self, value):
        self._setNumber(3, value)

    def _initialize(self):
        super(ChallengesRestartTooltipModel, self)._initialize()
        self._addNumberProperty('restartCost', 0)
        self._addStringProperty('currency', '')
        self._addNumberProperty('freeRestarts', 0)
        self._addNumberProperty('usedFreeRestarts', 0)
