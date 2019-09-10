# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/progressive_reward/progressive_reward_award_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel

class ProgressiveRewardAwardModel(ViewModel):
    __slots__ = ('onCloseAction', 'onSpecialActionBtnClick', 'onDestroyEvent')

    def getAwardType(self):
        return self._getString(0)

    def setAwardType(self, value):
        self._setString(0, value)

    def getSteps(self):
        return self._getArray(1)

    def setSteps(self, value):
        self._setArray(1, value)

    def getStepIdx(self):
        return self._getNumber(2)

    def setStepIdx(self, value):
        self._setNumber(2, value)

    def getHardReset(self):
        return self._getBool(3)

    def setHardReset(self, value):
        self._setBool(3, value)

    def getFadeOut(self):
        return self._getBool(4)

    def setFadeOut(self, value):
        self._setBool(4, value)

    def getRewards(self):
        return self._getArray(5)

    def setRewards(self, value):
        self._setArray(5, value)

    def getSpecialRewardType(self):
        return self._getString(6)

    def setSpecialRewardType(self, value):
        self._setString(6, value)

    def getInitialCongratsType(self):
        return self._getString(7)

    def setInitialCongratsType(self, value):
        self._setString(7, value)

    def _initialize(self):
        super(ProgressiveRewardAwardModel, self)._initialize()
        self._addStringProperty('awardType', '')
        self._addArrayProperty('steps', Array())
        self._addNumberProperty('stepIdx', 0)
        self._addBoolProperty('hardReset', False)
        self._addBoolProperty('fadeOut', False)
        self._addArrayProperty('rewards', Array())
        self._addStringProperty('specialRewardType', '')
        self._addStringProperty('initialCongratsType', '')
        self.onCloseAction = self._addCommand('onCloseAction')
        self.onSpecialActionBtnClick = self._addCommand('onSpecialActionBtnClick')
        self.onDestroyEvent = self._addCommand('onDestroyEvent')
