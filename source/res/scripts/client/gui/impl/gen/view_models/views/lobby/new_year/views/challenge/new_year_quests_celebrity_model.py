# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/challenge/new_year_quests_celebrity_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.new_year.views.challenge.economic_bonus_model import EconomicBonusModel
from gui.impl.gen.view_models.views.lobby.new_year.views.challenge.new_year_quest_card_model import NewYearQuestCardModel

class NewYearQuestsCelebrityModel(ViewModel):
    __slots__ = ('onBuyQuest', 'onOpenActivity', 'onShowStylePreview', 'onGoToBoxes', 'onUpdateBonus')

    def __init__(self, properties=11, commands=5):
        super(NewYearQuestsCelebrityModel, self).__init__(properties=properties, commands=commands)

    def getHasGuestC(self):
        return self._getBool(0)

    def setHasGuestC(self, value):
        self._setBool(0, value)

    def getCompletedQuestsQuantity(self):
        return self._getNumber(1)

    def setCompletedQuestsQuantity(self, value):
        self._setNumber(1, value)

    def getTotalQuestsQuantity(self):
        return self._getNumber(2)

    def setTotalQuestsQuantity(self, value):
        self._setNumber(2, value)

    def getQuestsCelebrity(self):
        return self._getArray(3)

    def setQuestsCelebrity(self, value):
        self._setArray(3, value)

    @staticmethod
    def getQuestsCelebrityType():
        return NewYearQuestCardModel

    def getCurrentActiveBonus(self):
        return self._getReal(4)

    def setCurrentActiveBonus(self, value):
        self._setReal(4, value)

    def getMaxActiveBonus(self):
        return self._getReal(5)

    def setMaxActiveBonus(self, value):
        self._setReal(5, value)

    def getEconomicBonuses(self):
        return self._getArray(6)

    def setEconomicBonuses(self, value):
        self._setArray(6, value)

    @staticmethod
    def getEconomicBonusesType():
        return EconomicBonusModel

    def getIsWalletAvailable(self):
        return self._getBool(7)

    def setIsWalletAvailable(self, value):
        self._setBool(7, value)

    def getIsBoxesAvailable(self):
        return self._getBool(8)

    def setIsBoxesAvailable(self, value):
        self._setBool(8, value)

    def getIsBonusAnimated(self):
        return self._getBool(9)

    def setIsBonusAnimated(self, value):
        self._setBool(9, value)

    def getIsExternal(self):
        return self._getBool(10)

    def setIsExternal(self, value):
        self._setBool(10, value)

    def _initialize(self):
        super(NewYearQuestsCelebrityModel, self)._initialize()
        self._addBoolProperty('hasGuestC', False)
        self._addNumberProperty('completedQuestsQuantity', 0)
        self._addNumberProperty('totalQuestsQuantity', 0)
        self._addArrayProperty('questsCelebrity', Array())
        self._addRealProperty('currentActiveBonus', 0.0)
        self._addRealProperty('maxActiveBonus', 0.0)
        self._addArrayProperty('economicBonuses', Array())
        self._addBoolProperty('isWalletAvailable', False)
        self._addBoolProperty('isBoxesAvailable', False)
        self._addBoolProperty('isBonusAnimated', False)
        self._addBoolProperty('isExternal', False)
        self.onBuyQuest = self._addCommand('onBuyQuest')
        self.onOpenActivity = self._addCommand('onOpenActivity')
        self.onShowStylePreview = self._addCommand('onShowStylePreview')
        self.onGoToBoxes = self._addCommand('onGoToBoxes')
        self.onUpdateBonus = self._addCommand('onUpdateBonus')
