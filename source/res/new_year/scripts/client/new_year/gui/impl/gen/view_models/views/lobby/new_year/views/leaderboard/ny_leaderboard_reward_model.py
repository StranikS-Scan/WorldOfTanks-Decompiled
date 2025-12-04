# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/gen/view_models/views/lobby/new_year/views/leaderboard/ny_leaderboard_reward_model.py
from new_year.gui.impl.gen.view_models.views.lobby.new_year.components.reward_item_model import RewardItemModel

class NyLeaderboardRewardModel(RewardItemModel):
    __slots__ = ()

    def __init__(self, properties=15, commands=0):
        super(NyLeaderboardRewardModel, self).__init__(properties=properties, commands=commands)

    def getIsPreview(self):
        return self._getBool(14)

    def setIsPreview(self, value):
        self._setBool(14, value)

    def _initialize(self):
        super(NyLeaderboardRewardModel, self)._initialize()
        self._addBoolProperty('isPreview', False)
