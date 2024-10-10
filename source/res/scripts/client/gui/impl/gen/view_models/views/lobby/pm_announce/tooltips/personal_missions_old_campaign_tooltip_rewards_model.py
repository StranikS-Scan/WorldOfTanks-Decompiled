# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/pm_announce/tooltips/personal_missions_old_campaign_tooltip_rewards_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class RewardStatus(Enum):
    COMPLETED = 'completed'
    AVAILABLE = 'available'
    LOCKED = 'locked'


class PersonalMissionsOldCampaignTooltipRewardsModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(PersonalMissionsOldCampaignTooltipRewardsModel, self).__init__(properties=properties, commands=commands)

    def getName(self):
        return self._getString(0)

    def setName(self, value):
        self._setString(0, value)

    def getIcon(self):
        return self._getString(1)

    def setIcon(self, value):
        self._setString(1, value)

    def getStatus(self):
        return RewardStatus(self._getString(2))

    def setStatus(self, value):
        self._setString(2, value.value)

    def _initialize(self):
        super(PersonalMissionsOldCampaignTooltipRewardsModel, self)._initialize()
        self._addStringProperty('name', '')
        self._addStringProperty('icon', '')
        self._addStringProperty('status')
