# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/account_dashboard/daily_experience_view_model.py
from frameworks.wulf import ViewModel

class DailyExperienceViewModel(ViewModel):
    __slots__ = ('onBackButtonClick', 'onWotPremiumUpgradeButtonClick', 'onWotPlusSubscribeButtonClick', 'onWotPremiumDetailsButtonClick', 'onWotPlusDetailsButtonClick')

    def __init__(self, properties=8, commands=5):
        super(DailyExperienceViewModel, self).__init__(properties=properties, commands=commands)

    def getIsWotPremium(self):
        return self._getBool(0)

    def setIsWotPremium(self, value):
        self._setBool(0, value)

    def getIsWotPlus(self):
        return self._getBool(1)

    def setIsWotPlus(self, value):
        self._setBool(1, value)

    def getIsWotPlusBonusEnabled(self):
        return self._getBool(2)

    def setIsWotPlusBonusEnabled(self, value):
        self._setBool(2, value)

    def getMultiplier(self):
        return self._getNumber(3)

    def setMultiplier(self, value):
        self._setNumber(3, value)

    def getLeftBonusCount(self):
        return self._getNumber(4)

    def setLeftBonusCount(self, value):
        self._setNumber(4, value)

    def getTotalBonusCount(self):
        return self._getNumber(5)

    def setTotalBonusCount(self, value):
        self._setNumber(5, value)

    def getWotPremiumMaxApplications(self):
        return self._getNumber(6)

    def setWotPremiumMaxApplications(self, value):
        self._setNumber(6, value)

    def getWotPlusMaxApplications(self):
        return self._getNumber(7)

    def setWotPlusMaxApplications(self, value):
        self._setNumber(7, value)

    def _initialize(self):
        super(DailyExperienceViewModel, self)._initialize()
        self._addBoolProperty('isWotPremium', False)
        self._addBoolProperty('isWotPlus', False)
        self._addBoolProperty('isWotPlusBonusEnabled', False)
        self._addNumberProperty('multiplier', 1)
        self._addNumberProperty('leftBonusCount', 0)
        self._addNumberProperty('totalBonusCount', 5)
        self._addNumberProperty('wotPremiumMaxApplications', 0)
        self._addNumberProperty('wotPlusMaxApplications', 0)
        self.onBackButtonClick = self._addCommand('onBackButtonClick')
        self.onWotPremiumUpgradeButtonClick = self._addCommand('onWotPremiumUpgradeButtonClick')
        self.onWotPlusSubscribeButtonClick = self._addCommand('onWotPlusSubscribeButtonClick')
        self.onWotPremiumDetailsButtonClick = self._addCommand('onWotPremiumDetailsButtonClick')
        self.onWotPlusDetailsButtonClick = self._addCommand('onWotPlusDetailsButtonClick')
