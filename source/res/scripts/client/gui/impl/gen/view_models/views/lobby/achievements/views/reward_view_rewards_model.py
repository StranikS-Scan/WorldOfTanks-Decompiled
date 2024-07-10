# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/achievements/views/reward_view_rewards_model.py
from gui.impl.gen.view_models.views.lobby.achievements.views.catalog.rewards_model import RewardsModel

class RewardViewRewardsModel(RewardsModel):
    __slots__ = ()

    def __init__(self, properties=16, commands=0):
        super(RewardViewRewardsModel, self).__init__(properties=properties, commands=commands)

    def getCurrentProgress(self):
        return self._getNumber(14)

    def setCurrentProgress(self, value):
        self._setNumber(14, value)

    def getAnimation(self):
        return self._getString(15)

    def setAnimation(self, value):
        self._setString(15, value)

    def _initialize(self):
        super(RewardViewRewardsModel, self)._initialize()
        self._addNumberProperty('currentProgress', 0)
        self._addStringProperty('animation', '')
