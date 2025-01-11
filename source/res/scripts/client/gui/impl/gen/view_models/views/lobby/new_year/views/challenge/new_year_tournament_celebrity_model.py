# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/challenge/new_year_tournament_celebrity_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.new_year.views.challenge.new_year_challenge_card_model import NewYearChallengeCardModel
from gui.impl.gen.view_models.views.lobby.new_year.views.challenge.new_year_challenge_progress_model import NewYearChallengeProgressModel
from gui.impl.gen.view_models.views.lobby.new_year.views.challenge.new_year_challenge_upcoming_card_model import NewYearChallengeUpcomingCardModel

class NewYearTournamentCelebrityModel(ViewModel):
    __slots__ = ('onStylePreviewShow', 'onUpdateTimeTill', 'onVisited', 'onReplace')

    def __init__(self, properties=13, commands=4):
        super(NewYearTournamentCelebrityModel, self).__init__(properties=properties, commands=commands)

    def getDiscountPopoverId(self):
        return self._getString(0)

    def setDiscountPopoverId(self, value):
        self._setString(0, value)

    def getCompletedQuestsQuantity(self):
        return self._getNumber(1)

    def setCompletedQuestsQuantity(self, value):
        self._setNumber(1, value)

    def getQuestsQuantity(self):
        return self._getNumber(2)

    def setQuestsQuantity(self, value):
        self._setNumber(2, value)

    def getMaxQuestsQuantity(self):
        return self._getNumber(3)

    def setMaxQuestsQuantity(self, value):
        self._setNumber(3, value)

    def getAdvancedQuestsQuantity(self):
        return self._getNumber(4)

    def setAdvancedQuestsQuantity(self, value):
        self._setNumber(4, value)

    def getReplacementsQuantity(self):
        return self._getNumber(5)

    def setReplacementsQuantity(self, value):
        self._setNumber(5, value)

    def getIsVehicleInBattle(self):
        return self._getBool(6)

    def setIsVehicleInBattle(self, value):
        self._setBool(6, value)

    def getIsReplaceLocked(self):
        return self._getBool(7)

    def setIsReplaceLocked(self, value):
        self._setBool(7, value)

    def getTimeTill(self):
        return self._getNumber(8)

    def setTimeTill(self, value):
        self._setNumber(8, value)

    def getChallengeCards(self):
        return self._getArray(9)

    def setChallengeCards(self, value):
        self._setArray(9, value)

    @staticmethod
    def getChallengeCardsType():
        return NewYearChallengeCardModel

    def getUpcomingCards(self):
        return self._getArray(10)

    def setUpcomingCards(self, value):
        self._setArray(10, value)

    @staticmethod
    def getUpcomingCardsType():
        return NewYearChallengeUpcomingCardModel

    def getPromoAdvancedCard(self):
        return self._getArray(11)

    def setPromoAdvancedCard(self, value):
        self._setArray(11, value)

    @staticmethod
    def getPromoAdvancedCardType():
        return NewYearChallengeUpcomingCardModel

    def getProgressRewards(self):
        return self._getArray(12)

    def setProgressRewards(self, value):
        self._setArray(12, value)

    @staticmethod
    def getProgressRewardsType():
        return NewYearChallengeProgressModel

    def _initialize(self):
        super(NewYearTournamentCelebrityModel, self)._initialize()
        self._addStringProperty('discountPopoverId', '')
        self._addNumberProperty('completedQuestsQuantity', 0)
        self._addNumberProperty('questsQuantity', 0)
        self._addNumberProperty('maxQuestsQuantity', 0)
        self._addNumberProperty('advancedQuestsQuantity', 0)
        self._addNumberProperty('replacementsQuantity', 0)
        self._addBoolProperty('isVehicleInBattle', False)
        self._addBoolProperty('isReplaceLocked', False)
        self._addNumberProperty('timeTill', 0)
        self._addArrayProperty('challengeCards', Array())
        self._addArrayProperty('upcomingCards', Array())
        self._addArrayProperty('promoAdvancedCard', Array())
        self._addArrayProperty('progressRewards', Array())
        self.onStylePreviewShow = self._addCommand('onStylePreviewShow')
        self.onUpdateTimeTill = self._addCommand('onUpdateTimeTill')
        self.onVisited = self._addCommand('onVisited')
        self.onReplace = self._addCommand('onReplace')
