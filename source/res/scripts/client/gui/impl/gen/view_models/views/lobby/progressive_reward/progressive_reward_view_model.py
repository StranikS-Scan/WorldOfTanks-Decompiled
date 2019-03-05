# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/progressive_reward/progressive_reward_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel

class ProgressiveRewardViewModel(ViewModel):
    __slots__ = ('onCloseAction', 'onDestroyEvent')

    def getSteps(self):
        return self._getArray(0)

    def setSteps(self, value):
        self._setArray(0, value)

    def getStepIdx(self):
        return self._getNumber(1)

    def setStepIdx(self, value):
        self._setNumber(1, value)

    def getHardReset(self):
        return self._getBool(2)

    def setHardReset(self, value):
        self._setBool(2, value)

    def getFadeOut(self):
        return self._getBool(3)

    def setFadeOut(self, value):
        self._setBool(3, value)

    def _initialize(self):
        super(ProgressiveRewardViewModel, self)._initialize()
        self._addArrayProperty('steps', Array())
        self._addNumberProperty('stepIdx', 0)
        self._addBoolProperty('hardReset', False)
        self._addBoolProperty('fadeOut', False)
        self.onCloseAction = self._addCommand('onCloseAction')
        self.onDestroyEvent = self._addCommand('onDestroyEvent')
