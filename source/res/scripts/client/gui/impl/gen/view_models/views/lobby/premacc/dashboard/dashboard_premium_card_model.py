# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/premacc/dashboard/dashboard_premium_card_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.ui_kit.list_model import ListModel

class DashboardPremiumCardModel(ViewModel):
    __slots__ = ('onClick',)

    def __init__(self, properties=10, commands=1):
        super(DashboardPremiumCardModel, self).__init__(properties=properties, commands=commands)

    @property
    def withoutPremium(self):
        return self._getViewModel(0)

    @staticmethod
    def getWithoutPremiumType():
        return ListModel

    @property
    def withPremium(self):
        return self._getViewModel(1)

    @staticmethod
    def getWithPremiumType():
        return ListModel

    def getIsBasePremiumActive(self):
        return self._getBool(2)

    def setIsBasePremiumActive(self, value):
        self._setBool(2, value)

    def getIsTankPremiumActive(self):
        return self._getBool(3)

    def setIsTankPremiumActive(self, value):
        self._setBool(3, value)

    def getIsNotPremium(self):
        return self._getBool(4)

    def setIsNotPremium(self, value):
        self._setBool(4, value)

    def getBasePremTimeLeft(self):
        return self._getNumber(5)

    def setBasePremTimeLeft(self, value):
        self._setNumber(5, value)

    def getTankPremTimeLeft(self):
        return self._getNumber(6)

    def setTankPremTimeLeft(self, value):
        self._setNumber(6, value)

    def getExperienceBonus(self):
        return self._getNumber(7)

    def setExperienceBonus(self, value):
        self._setNumber(7, value)

    def getCreditsBonus(self):
        return self._getNumber(8)

    def setCreditsBonus(self, value):
        self._setNumber(8, value)

    def getSquadBonus(self):
        return self._getNumber(9)

    def setSquadBonus(self, value):
        self._setNumber(9, value)

    def _initialize(self):
        super(DashboardPremiumCardModel, self)._initialize()
        self._addViewModelProperty('withoutPremium', ListModel())
        self._addViewModelProperty('withPremium', ListModel())
        self._addBoolProperty('isBasePremiumActive', False)
        self._addBoolProperty('isTankPremiumActive', False)
        self._addBoolProperty('isNotPremium', True)
        self._addNumberProperty('basePremTimeLeft', -1)
        self._addNumberProperty('tankPremTimeLeft', -1)
        self._addNumberProperty('experienceBonus', 0)
        self._addNumberProperty('creditsBonus', 0)
        self._addNumberProperty('squadBonus', 0)
        self.onClick = self._addCommand('onClick')
