# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/challenge/new_year_tournament_celebrity_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.new_year.views.challenge.new_year_challenge_card_model import NewYearChallengeCardModel
from gui.impl.gen.view_models.views.lobby.new_year.views.challenge.new_year_challenge_progress_model import NewYearChallengeProgressModel

class NewYearTournamentCelebrityModel(ViewModel):
    __slots__ = ('onStylePreviewShow', 'onUpdateTimeTill', 'onVisited', 'onReplace')

    def __init__(self, properties=8, commands=4):
        super(NewYearTournamentCelebrityModel, self).__init__(properties=properties, commands=commands)

    def getCompletedQuestsQuantity(self):
        return self._getNumber(0)

    def setCompletedQuestsQuantity(self, value):
        self._setNumber(0, value)

    def getMaxQuestsQuantity(self):
        return self._getNumber(1)

    def setMaxQuestsQuantity(self, value):
        self._setNumber(1, value)

    def getReplacementsQuantity(self):
        return self._getNumber(2)

    def setReplacementsQuantity(self, value):
        self._setNumber(2, value)

    def getIsVehicleInBattle(self):
        return self._getBool(3)

    def setIsVehicleInBattle(self, value):
        self._setBool(3, value)

    def getIsReplaceLocked(self):
        return self._getBool(4)

    def setIsReplaceLocked(self, value):
        self._setBool(4, value)

    def getTimeTill(self):
        return self._getNumber(5)

    def setTimeTill(self, value):
        self._setNumber(5, value)

    def getChallengeCards(self):
        return self._getArray(6)

    def setChallengeCards(self, value):
        self._setArray(6, value)

    @staticmethod
    def getChallengeCardsType():
        return NewYearChallengeCardModel

    def getProgressRewards(self):
        return self._getArray(7)

    def setProgressRewards(self, value):
        self._setArray(7, value)

    @staticmethod
    def getProgressRewardsType():
        return NewYearChallengeProgressModel

    def _initialize(self):
        super(NewYearTournamentCelebrityModel, self)._initialize()
        self._addNumberProperty('completedQuestsQuantity', 0)
        self._addNumberProperty('maxQuestsQuantity', 0)
        self._addNumberProperty('replacementsQuantity', 0)
        self._addBoolProperty('isVehicleInBattle', False)
        self._addBoolProperty('isReplaceLocked', False)
        self._addNumberProperty('timeTill', 0)
        self._addArrayProperty('challengeCards', Array())
        self._addArrayProperty('progressRewards', Array())
        self.onStylePreviewShow = self._addCommand('onStylePreviewShow')
        self.onUpdateTimeTill = self._addCommand('onUpdateTimeTill')
        self.onVisited = self._addCommand('onVisited')
        self.onReplace = self._addCommand('onReplace')
