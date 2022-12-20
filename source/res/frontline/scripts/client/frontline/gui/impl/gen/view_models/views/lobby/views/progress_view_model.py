# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/impl/gen/view_models/views/lobby/views/progress_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from frontline.gui.impl.gen.view_models.views.lobby.views.frontline_reward_model import FrontlineRewardModel

class ProgressViewModel(ViewModel):
    __slots__ = ('onShopClick',)

    def __init__(self, properties=9, commands=1):
        super(ProgressViewModel, self).__init__(properties=properties, commands=commands)

    def getFrontlineState(self):
        return self._getString(0)

    def setFrontlineState(self, value):
        self._setString(0, value)

    def getCountdownSeconds(self):
        return self._getNumber(1)

    def setCountdownSeconds(self, value):
        self._setNumber(1, value)

    def getPendingDate(self):
        return self._getNumber(2)

    def setPendingDate(self, value):
        self._setNumber(2, value)

    def getLevel(self):
        return self._getNumber(3)

    def setLevel(self, value):
        self._setNumber(3, value)

    def getIsMaxLevel(self):
        return self._getBool(4)

    def setIsMaxLevel(self, value):
        self._setBool(4, value)

    def getIsShopBannerVisible(self):
        return self._getBool(5)

    def setIsShopBannerVisible(self, value):
        self._setBool(5, value)

    def getCurrentPoints(self):
        return self._getNumber(6)

    def setCurrentPoints(self, value):
        self._setNumber(6, value)

    def getNeededPoints(self):
        return self._getNumber(7)

    def setNeededPoints(self, value):
        self._setNumber(7, value)

    def getRewards(self):
        return self._getArray(8)

    def setRewards(self, value):
        self._setArray(8, value)

    @staticmethod
    def getRewardsType():
        return FrontlineRewardModel

    def _initialize(self):
        super(ProgressViewModel, self)._initialize()
        self._addStringProperty('frontlineState', '')
        self._addNumberProperty('countdownSeconds', 0)
        self._addNumberProperty('pendingDate', 0)
        self._addNumberProperty('level', 0)
        self._addBoolProperty('isMaxLevel', False)
        self._addBoolProperty('isShopBannerVisible', False)
        self._addNumberProperty('currentPoints', 0)
        self._addNumberProperty('neededPoints', 0)
        self._addArrayProperty('rewards', Array())
        self.onShopClick = self._addCommand('onShopClick')
