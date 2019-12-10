# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/seniority_awards/seniority_reward_view_model.py
from frameworks.wulf import ViewModel

class SeniorityRewardViewModel(ViewModel):
    __slots__ = ('onCloseAction', 'onDestroyEvent', 'onOpenBtnClick')

    def __init__(self, properties=5, commands=3):
        super(SeniorityRewardViewModel, self).__init__(properties=properties, commands=commands)

    def getHardReset(self):
        return self._getBool(0)

    def setHardReset(self, value):
        self._setBool(0, value)

    def getFadeOut(self):
        return self._getBool(1)

    def setFadeOut(self, value):
        self._setBool(1, value)

    def getCountAwards(self):
        return self._getNumber(2)

    def setCountAwards(self, value):
        self._setNumber(2, value)

    def getBuyBtnOpenCount(self):
        return self._getNumber(3)

    def setBuyBtnOpenCount(self, value):
        self._setNumber(3, value)

    def getAutoOpenDate(self):
        return self._getString(4)

    def setAutoOpenDate(self, value):
        self._setString(4, value)

    def _initialize(self):
        super(SeniorityRewardViewModel, self)._initialize()
        self._addBoolProperty('hardReset', False)
        self._addBoolProperty('fadeOut', False)
        self._addNumberProperty('countAwards', 0)
        self._addNumberProperty('buyBtnOpenCount', 0)
        self._addStringProperty('autoOpenDate', '')
        self.onCloseAction = self._addCommand('onCloseAction')
        self.onDestroyEvent = self._addCommand('onDestroyEvent')
        self.onOpenBtnClick = self._addCommand('onOpenBtnClick')
