# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/gen/view_models/views/lobby/widgets/reward_path_view_model.py
from frameworks.wulf import ViewModel

class RewardPathViewModel(ViewModel):
    __slots__ = ('onClick',)

    def __init__(self, properties=3, commands=1):
        super(RewardPathViewModel, self).__init__(properties=properties, commands=commands)

    def getCurrentProgress(self):
        return self._getNumber(0)

    def setCurrentProgress(self, value):
        self._setNumber(0, value)

    def getMaxProgress(self):
        return self._getNumber(1)

    def setMaxProgress(self, value):
        self._setNumber(1, value)

    def getIsCompleted(self):
        return self._getBool(2)

    def setIsCompleted(self, value):
        self._setBool(2, value)

    def _initialize(self):
        super(RewardPathViewModel, self)._initialize()
        self._addNumberProperty('currentProgress', 0)
        self._addNumberProperty('maxProgress', 0)
        self._addBoolProperty('isCompleted', False)
        self.onClick = self._addCommand('onClick')
