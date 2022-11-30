# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/challenge/new_year_tournament_celebrity_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.new_year.views.challenge.new_year_challenge_card_model import NewYearChallengeCardModel
from gui.impl.gen.view_models.views.lobby.new_year.views.challenge.new_year_challenge_progress_model import NewYearChallengeProgressModel

class NewYearTournamentCelebrityModel(ViewModel):
    __slots__ = ('onStylePreviewShow', 'onUpdateTimeTill', 'onCloseAdditionalCard', 'onVisited', 'onReplace')

    def __init__(self, properties=12, commands=5):
        super(NewYearTournamentCelebrityModel, self).__init__(properties=properties, commands=commands)

    def getCompletedQuestsQuantity(self):
        return self._getNumber(0)

    def setCompletedQuestsQuantity(self, value):
        self._setNumber(0, value)

    def getMaxQuestsQuantity(self):
        return self._getNumber(1)

    def setMaxQuestsQuantity(self, value):
        self._setNumber(1, value)

    def getRerollingQuests(self):
        return self._getNumber(2)

    def setRerollingQuests(self, value):
        self._setNumber(2, value)

    def getCompletedAdditionalQuestsQuantity(self):
        return self._getNumber(3)

    def setCompletedAdditionalQuestsQuantity(self, value):
        self._setNumber(3, value)

    def getReplacementsQuantity(self):
        return self._getNumber(4)

    def setReplacementsQuantity(self, value):
        self._setNumber(4, value)

    def getIsVehicleInBattle(self):
        return self._getBool(5)

    def setIsVehicleInBattle(self, value):
        self._setBool(5, value)

    def getIsReplaceLocked(self):
        return self._getBool(6)

    def setIsReplaceLocked(self, value):
        self._setBool(6, value)

    def getTimeTill(self):
        return self._getNumber(7)

    def setTimeTill(self, value):
        self._setNumber(7, value)

    def getHasTemporaryAdditionalCard(self):
        return self._getBool(8)

    def setHasTemporaryAdditionalCard(self, value):
        self._setBool(8, value)

    def getChallengeCards(self):
        return self._getArray(9)

    def setChallengeCards(self, value):
        self._setArray(9, value)

    @staticmethod
    def getChallengeCardsType():
        return NewYearChallengeCardModel

    def getAdditionalChallengeCards(self):
        return self._getArray(10)

    def setAdditionalChallengeCards(self, value):
        self._setArray(10, value)

    @staticmethod
    def getAdditionalChallengeCardsType():
        return NewYearChallengeCardModel

    def getProgressRewards(self):
        return self._getArray(11)

    def setProgressRewards(self, value):
        self._setArray(11, value)

    @staticmethod
    def getProgressRewardsType():
        return NewYearChallengeProgressModel

    def _initialize(self):
        super(NewYearTournamentCelebrityModel, self)._initialize()
        self._addNumberProperty('completedQuestsQuantity', 0)
        self._addNumberProperty('maxQuestsQuantity', 0)
        self._addNumberProperty('rerollingQuests', 0)
        self._addNumberProperty('completedAdditionalQuestsQuantity', 0)
        self._addNumberProperty('replacementsQuantity', 0)
        self._addBoolProperty('isVehicleInBattle', False)
        self._addBoolProperty('isReplaceLocked', False)
        self._addNumberProperty('timeTill', 0)
        self._addBoolProperty('hasTemporaryAdditionalCard', False)
        self._addArrayProperty('challengeCards', Array())
        self._addArrayProperty('additionalChallengeCards', Array())
        self._addArrayProperty('progressRewards', Array())
        self.onStylePreviewShow = self._addCommand('onStylePreviewShow')
        self.onUpdateTimeTill = self._addCommand('onUpdateTimeTill')
        self.onCloseAdditionalCard = self._addCommand('onCloseAdditionalCard')
        self.onVisited = self._addCommand('onVisited')
        self.onReplace = self._addCommand('onReplace')
