# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/impl/gen/view_models/views/lobby/views/frontline_reward_model.py
from enum import Enum
from gui.impl.gen.view_models.common.missions.bonuses.icon_bonus_model import IconBonusModel

class ClaimState(Enum):
    STATIC = 'static'
    CLAIMABLE = 'claimable'


class FrontlineRewardModel(IconBonusModel):
    __slots__ = ()

    def __init__(self, properties=12, commands=0):
        super(FrontlineRewardModel, self).__init__(properties=properties, commands=commands)

    def getId(self):
        return self._getString(9)

    def setId(self, value):
        self._setString(9, value)

    def getClaimState(self):
        return ClaimState(self._getString(10))

    def setClaimState(self, value):
        self._setString(10, value.value)

    def getType(self):
        return self._getString(11)

    def setType(self, value):
        self._setString(11, value)

    def _initialize(self):
        super(FrontlineRewardModel, self)._initialize()
        self._addStringProperty('id', '')
        self._addStringProperty('claimState')
        self._addStringProperty('type', '')
