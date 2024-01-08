# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/comp7/meta_view/pages/yearly_rewards_card_model.py
from enum import Enum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.comp7.comp7_bonus_model import Comp7BonusModel
from gui.impl.gen.view_models.views.lobby.comp7.season_point_model import SeasonPointModel

class RewardsState(Enum):
    GUARANTEED = 'guaranteed'
    POSSIBLE = 'possible'
    NOTAVAILABLE = 'notAvailable'
    CLAIMED = 'claimed'


class SeasonPointState(Enum):
    ACHIEVED = 'achieved'
    POSSIBLE = 'possible'
    NOTACHIEVED = 'notAchieved'


class YearlyRewardsCardModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(YearlyRewardsCardModel, self).__init__(properties=properties, commands=commands)

    def getRewards(self):
        return self._getArray(0)

    def setRewards(self, value):
        self._setArray(0, value)

    @staticmethod
    def getRewardsType():
        return Comp7BonusModel

    def getSeasonPoints(self):
        return self._getArray(1)

    def setSeasonPoints(self, value):
        self._setArray(1, value)

    @staticmethod
    def getSeasonPointsType():
        return SeasonPointModel

    def getRewardsState(self):
        return RewardsState(self._getString(2))

    def setRewardsState(self, value):
        self._setString(2, value.value)

    def _initialize(self):
        super(YearlyRewardsCardModel, self)._initialize()
        self._addArrayProperty('rewards', Array())
        self._addArrayProperty('seasonPoints', Array())
        self._addStringProperty('rewardsState')
