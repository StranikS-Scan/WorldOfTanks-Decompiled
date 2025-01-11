# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/challenge/new_year_challenge_upcoming_card_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.new_year.views.challenge.challenge_reward_item_model import ChallengeRewardItemModel

class NewYearChallengeUpcomingCardModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=1, commands=0):
        super(NewYearChallengeUpcomingCardModel, self).__init__(properties=properties, commands=commands)

    def getRewards(self):
        return self._getArray(0)

    def setRewards(self, value):
        self._setArray(0, value)

    @staticmethod
    def getRewardsType():
        return ChallengeRewardItemModel

    def _initialize(self):
        super(NewYearChallengeUpcomingCardModel, self)._initialize()
        self._addArrayProperty('rewards', Array())
