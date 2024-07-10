# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_light_progression/scripts/client/comp7_light_progression/gui/impl/gen/view_models/views/lobby/views/leaderboard_reward_tooltip_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from comp7_light_progression.gui.impl.gen.view_models.views.lobby.views.reward_points_place_model import RewardPointsPlaceModel

class LeaderboardRewardTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(LeaderboardRewardTooltipModel, self).__init__(properties=properties, commands=commands)

    def getBattleTypes(self):
        return self._getArray(0)

    def setBattleTypes(self, value):
        self._setArray(0, value)

    @staticmethod
    def getBattleTypesType():
        return unicode

    def getBattleModes(self):
        return self._getArray(1)

    def setBattleModes(self, value):
        self._setArray(1, value)

    @staticmethod
    def getBattleModesType():
        return RewardPointsPlaceModel

    def _initialize(self):
        super(LeaderboardRewardTooltipModel, self)._initialize()
        self._addArrayProperty('battleTypes', Array())
        self._addArrayProperty('battleModes', Array())
