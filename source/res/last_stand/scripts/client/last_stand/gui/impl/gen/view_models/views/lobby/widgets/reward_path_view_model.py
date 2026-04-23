# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/gen/view_models/views/lobby/widgets/reward_path_view_model.py
from frameworks.wulf import ViewModel

class RewardPathViewModel(ViewModel):
    __slots__ = ('onClick',)

    def __init__(self, properties=5, commands=1):
        super(RewardPathViewModel, self).__init__(properties=properties, commands=commands)

    def getCurrentProgress(self):
        return self._getNumber(0)

    def setCurrentProgress(self, value):
        self._setNumber(0, value)

    def getIsCompleted(self):
        return self._getBool(1)

    def setIsCompleted(self, value):
        self._setBool(1, value)

    def getDataCollected(self):
        return self._getNumber(2)

    def setDataCollected(self, value):
        self._setNumber(2, value)

    def getDataAmount(self):
        return self._getNumber(3)

    def setDataAmount(self, value):
        self._setNumber(3, value)

    def getTimeLeft(self):
        return self._getNumber(4)

    def setTimeLeft(self, value):
        self._setNumber(4, value)

    def _initialize(self):
        super(RewardPathViewModel, self)._initialize()
        self._addNumberProperty('currentProgress', 0)
        self._addBoolProperty('isCompleted', False)
        self._addNumberProperty('dataCollected', 0)
        self._addNumberProperty('dataAmount', 0)
        self._addNumberProperty('timeLeft', 0)
        self.onClick = self._addCommand('onClick')
