# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/challenge/new_year_quests_celebrity_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.new_year.views.challenge.economic_bonus_model import EconomicBonusModel
from gui.impl.gen.view_models.views.lobby.new_year.views.challenge.new_year_quest_card_model import NewYearQuestCardModel

class NewYearQuestsCelebrityModel(ViewModel):
    __slots__ = ('onBuyQuest', 'onOpenActivity', 'onShowStylePreview')

    def __init__(self, properties=7, commands=3):
        super(NewYearQuestsCelebrityModel, self).__init__(properties=properties, commands=commands)

    def getCompletedQuestsQuantity(self):
        return self._getNumber(0)

    def setCompletedQuestsQuantity(self, value):
        self._setNumber(0, value)

    def getTotalQuestsQuantity(self):
        return self._getNumber(1)

    def setTotalQuestsQuantity(self, value):
        self._setNumber(1, value)

    def getQuestsCelebrity(self):
        return self._getArray(2)

    def setQuestsCelebrity(self, value):
        self._setArray(2, value)

    @staticmethod
    def getQuestsCelebrityType():
        return NewYearQuestCardModel

    def getCurrentActiveBonus(self):
        return self._getReal(3)

    def setCurrentActiveBonus(self, value):
        self._setReal(3, value)

    def getMaxActiveBonus(self):
        return self._getReal(4)

    def setMaxActiveBonus(self, value):
        self._setReal(4, value)

    def getEconomicBonuses(self):
        return self._getArray(5)

    def setEconomicBonuses(self, value):
        self._setArray(5, value)

    @staticmethod
    def getEconomicBonusesType():
        return EconomicBonusModel

    def getIsWalletAvailable(self):
        return self._getBool(6)

    def setIsWalletAvailable(self, value):
        self._setBool(6, value)

    def _initialize(self):
        super(NewYearQuestsCelebrityModel, self)._initialize()
        self._addNumberProperty('completedQuestsQuantity', 0)
        self._addNumberProperty('totalQuestsQuantity', 0)
        self._addArrayProperty('questsCelebrity', Array())
        self._addRealProperty('currentActiveBonus', 0.0)
        self._addRealProperty('maxActiveBonus', 0.0)
        self._addArrayProperty('economicBonuses', Array())
        self._addBoolProperty('isWalletAvailable', False)
        self.onBuyQuest = self._addCommand('onBuyQuest')
        self.onOpenActivity = self._addCommand('onOpenActivity')
        self.onShowStylePreview = self._addCommand('onShowStylePreview')
