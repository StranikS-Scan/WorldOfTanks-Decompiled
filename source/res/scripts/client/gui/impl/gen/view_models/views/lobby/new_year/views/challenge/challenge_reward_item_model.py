# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/views/challenge/challenge_reward_item_model.py
from gui.impl.gen.view_models.common.missions.bonuses.icon_bonus_model import IconBonusModel

class ChallengeRewardItemModel(IconBonusModel):
    __slots__ = ()

    def __init__(self, properties=9, commands=0):
        super(ChallengeRewardItemModel, self).__init__(properties=properties, commands=commands)

    def getIntCD(self):
        return self._getNumber(8)

    def setIntCD(self, value):
        self._setNumber(8, value)

    def _initialize(self):
        super(ChallengeRewardItemModel, self)._initialize()
        self._addNumberProperty('intCD', 0)
