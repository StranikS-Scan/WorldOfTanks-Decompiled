# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/challenge/new_year_tournament_celebrity_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.new_year.views.challenge.new_year_challenge_card_model import NewYearChallengeCardModel
from gui.impl.gen.view_models.views.lobby.new_year.views.challenge.new_year_challenge_progress_model import NewYearChallengeProgressModel

class NewYearTournamentCelebrityModel(ViewModel):
    __slots__ = ('onStylePreviewShow', 'onUpdateTimeTill', 'onCloseAdditionalCard', 'onVisited', 'onReplace')

    def __init__(self, properties=14, commands=5):
        super(NewYearTournamentCelebrityModel, self).__init__(properties=properties, commands=commands)

    def getCompletedQuestsQuantity(self):
        return self._getNumber(0)

    def setCompletedQuestsQuantity(self, value):
        self._setNumber(0, value)

    def getMaxQuestsQuantity(self):
        return self._getNumber(1)

    def setMaxQuestsQuantity(self, value):
        self._setNumber(1, value)

    def getMaxAdditionalQuestsQuantity(self):
        return self._getNumber(2)

    def setMaxAdditionalQuestsQuantity(self, value):
        self._setNumber(2, value)

    def getRerollingQuests(self):
        return self._getNumber(3)

    def setRerollingQuests(self, value):
        self._setNumber(3, value)

    def getIsRerollChargingAvailable(self):
        return self._getBool(4)

    def setIsRerollChargingAvailable(self, value):
        self._setBool(4, value)

    def getCompletedAdditionalQuestsQuantity(self):
        return self._getNumber(5)

    def setCompletedAdditionalQuestsQuantity(self, value):
        self._setNumber(5, value)

    def getReplacementsQuantity(self):
        return self._getNumber(6)

    def setReplacementsQuantity(self, value):
        self._setNumber(6, value)

    def getIsVehicleInBattle(self):
        return self._getBool(7)

    def setIsVehicleInBattle(self, value):
        self._setBool(7, value)

    def getIsReplaceLocked(self):
        return self._getBool(8)

    def setIsReplaceLocked(self, value):
        self._setBool(8, value)

    def getTimeTill(self):
        return self._getNumber(9)

    def setTimeTill(self, value):
        self._setNumber(9, value)

    def getHasTemporaryAdditionalCard(self):
        return self._getBool(10)

    def setHasTemporaryAdditionalCard(self, value):
        self._setBool(10, value)

    def getChallengeCards(self):
        return self._getArray(11)

    def setChallengeCards(self, value):
        self._setArray(11, value)

    @staticmethod
    def getChallengeCardsType():
        return NewYearChallengeCardModel

    def getAdditionalChallengeCards(self):
        return self._getArray(12)

    def setAdditionalChallengeCards(self, value):
        self._setArray(12, value)

    @staticmethod
    def getAdditionalChallengeCardsType():
        return NewYearChallengeCardModel

    def getProgressRewards(self):
        return self._getArray(13)

    def setProgressRewards(self, value):
        self._setArray(13, value)

    @staticmethod
    def getProgressRewardsType():
        return NewYearChallengeProgressModel

    def _initialize(self):
        super(NewYearTournamentCelebrityModel, self)._initialize()
        self._addNumberProperty('completedQuestsQuantity', 0)
        self._addNumberProperty('maxQuestsQuantity', 0)
        self._addNumberProperty('maxAdditionalQuestsQuantity', 0)
        self._addNumberProperty('rerollingQuests', 0)
        self._addBoolProperty('isRerollChargingAvailable', False)
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
