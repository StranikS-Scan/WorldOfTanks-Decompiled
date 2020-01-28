# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/bob/bob_reward_model.py
from frameworks.wulf import Array
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class BobRewardModel(ViewModel):
    __slots__ = ('onCloseAction', 'onSpecialActionBtnClick', 'onDestroyEvent', 'onNextAction')

    def __init__(self, properties=9, commands=4):
        super(BobRewardModel, self).__init__(properties=properties, commands=commands)

    def getTitle(self):
        return self._getResource(0)

    def setTitle(self, value):
        self._setResource(0, value)

    def getBackground(self):
        return self._getResource(1)

    def setBackground(self, value):
        self._setResource(1, value)

    def getIsTeamReward(self):
        return self._getBool(2)

    def setIsTeamReward(self, value):
        self._setBool(2, value)

    def getDescription(self):
        return self._getString(3)

    def setDescription(self, value):
        self._setString(3, value)

    def getHardReset(self):
        return self._getBool(4)

    def setHardReset(self, value):
        self._setBool(4, value)

    def getFadeOut(self):
        return self._getBool(5)

    def setFadeOut(self, value):
        self._setBool(5, value)

    def getRewards(self):
        return self._getArray(6)

    def setRewards(self, value):
        self._setArray(6, value)

    def getSpecialRewardType(self):
        return self._getString(7)

    def setSpecialRewardType(self, value):
        self._setString(7, value)

    def getShowNextBtn(self):
        return self._getBool(8)

    def setShowNextBtn(self, value):
        self._setBool(8, value)

    def _initialize(self):
        super(BobRewardModel, self)._initialize()
        self._addResourceProperty('title', R.invalid())
        self._addResourceProperty('background', R.invalid())
        self._addBoolProperty('isTeamReward', False)
        self._addStringProperty('description', '')
        self._addBoolProperty('hardReset', False)
        self._addBoolProperty('fadeOut', False)
        self._addArrayProperty('rewards', Array())
        self._addStringProperty('specialRewardType', '')
        self._addBoolProperty('showNextBtn', False)
        self.onCloseAction = self._addCommand('onCloseAction')
        self.onSpecialActionBtnClick = self._addCommand('onSpecialActionBtnClick')
        self.onDestroyEvent = self._addCommand('onDestroyEvent')
        self.onNextAction = self._addCommand('onNextAction')
