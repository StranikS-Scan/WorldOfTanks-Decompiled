# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/gen/view_models/views/lobby/reward_screen_reward_model.py
from halloween.gui.impl.gen.view_models.views.lobby.common.reward_model import RewardModel

class RewardScreenRewardModel(RewardModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(RewardScreenRewardModel, self).__init__(properties=properties, commands=commands)

    def getIcon(self):
        return self._getString(4)

    def setIcon(self, value):
        self._setString(4, value)

    def _initialize(self):
        super(RewardScreenRewardModel, self)._initialize()
        self._addStringProperty('icon', '')
