# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/pm_announce/tooltips/personal_missions_old_campaign_tooltip_view_model.py
from enum import Enum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.pm_announce.tooltips.personal_missions_old_campaign_tooltip_operations_model import PersonalMissionsOldCampaignTooltipOperationsModel
from gui.impl.gen.view_models.views.lobby.pm_announce.tooltips.personal_missions_old_campaign_tooltip_rewards_model import PersonalMissionsOldCampaignTooltipRewardsModel

class MissionStatus(Enum):
    ACTIVE = 'active'
    COMPLETED = 'completed'
    COMPLETEDPERFECT = 'completedPerfect'


class PersonalMissionsOldCampaignTooltipViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(PersonalMissionsOldCampaignTooltipViewModel, self).__init__(properties=properties, commands=commands)

    def getMissionStatus(self):
        return MissionStatus(self._getString(0))

    def setMissionStatus(self, value):
        self._setString(0, value.value)

    def getOperations(self):
        return self._getArray(1)

    def setOperations(self, value):
        self._setArray(1, value)

    @staticmethod
    def getOperationsType():
        return PersonalMissionsOldCampaignTooltipOperationsModel

    def getRewards(self):
        return self._getArray(2)

    def setRewards(self, value):
        self._setArray(2, value)

    @staticmethod
    def getRewardsType():
        return PersonalMissionsOldCampaignTooltipRewardsModel

    def _initialize(self):
        super(PersonalMissionsOldCampaignTooltipViewModel, self)._initialize()
        self._addStringProperty('missionStatus')
        self._addArrayProperty('operations', Array())
        self._addArrayProperty('rewards', Array())
