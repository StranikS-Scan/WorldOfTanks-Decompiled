# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_light/scripts/client/comp7_light/gui/impl/gen/view_models/views/lobby/tooltips/leaderboard_reward_tooltip_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class State(Enum):
    INPROGRESS = 'inProgress'
    COMPLETED = 'completed'
    SIMPLIFIED = 'simplified'


class LeaderboardRewardTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=2, commands=0):
        super(LeaderboardRewardTooltipModel, self).__init__(properties=properties, commands=commands)

    def getState(self):
        return State(self._getString(0))

    def setState(self, value):
        self._setString(0, value.value)

    def getSeasonEndTimestamp(self):
        return self._getNumber(1)

    def setSeasonEndTimestamp(self, value):
        self._setNumber(1, value)

    def _initialize(self):
        super(LeaderboardRewardTooltipModel, self)._initialize()
        self._addStringProperty('state')
        self._addNumberProperty('seasonEndTimestamp', 0)
