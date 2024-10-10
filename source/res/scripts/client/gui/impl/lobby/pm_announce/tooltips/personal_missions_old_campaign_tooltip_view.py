# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/pm_announce/tooltips/personal_missions_old_campaign_tooltip_view.py
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl.gen.view_models.views.lobby.pm_announce.tooltips.personal_missions_old_campaign_tooltip_view_model import PersonalMissionsOldCampaignTooltipViewModel, MissionStatus
from gui.impl.gen.view_models.views.lobby.pm_announce.tooltips.personal_missions_old_campaign_tooltip_rewards_model import PersonalMissionsOldCampaignTooltipRewardsModel, RewardStatus
from gui.impl.gen.view_models.views.lobby.pm_announce.tooltips.personal_missions_old_campaign_tooltip_operations_model import PersonalMissionsOldCampaignTooltipOperationsModel
from gui.impl.pub import ViewImpl
operations = [{'name': 'Stug|V',
  'completed': 35,
  'all': 75},
 {'name': 'T28Concept',
  'completed': 25,
  'all': 25},
 {'name': 'T55A',
  'completed': 15,
  'all': 35},
 {'name': 'Object 260',
  'completed': 0,
  'all': 25},
 {'name': 'Excalibur',
  'completed': 25,
  'all': 25},
 {'name': 'Chimera',
  'completed': 15,
  'all': 35},
 {'name': 'Object 279(e)',
  'completed': 0,
  'all': 25}]
rewards = [{'name': 'Stug|V',
  'icon': 'R.images.gui.maps.icons.quests.bonuses.big.germany_G104_Stug_IV',
  'status': RewardStatus.COMPLETED},
 {'name': 'T28Concept',
  'icon': 'R.images.gui.maps.icons.quests.bonuses.big.usa_A102_T28_concept',
  'status': RewardStatus.AVAILABLE},
 {'name': 'T55A',
  'icon': 'R.images.gui.maps.icons.quests.bonuses.big.germany_G105_T_55_NVA_DDR',
  'status': RewardStatus.LOCKED},
 {'name': 'Object 260',
  'icon': 'R.images.gui.maps.icons.quests.bonuses.big.ussr_R110_Object_260',
  'status': RewardStatus.LOCKED},
 {'name': 'Excalibur',
  'icon': 'R.images.gui.maps.icons.quests.bonuses.big.uk_GB96_Excalibur',
  'status': RewardStatus.LOCKED},
 {'name': 'Chimera',
  'icon': 'R.images.gui.maps.icons.quests.bonuses.big.uk_GB97_Chimera',
  'status': RewardStatus.LOCKED},
 {'name': 'Object 279(e)',
  'icon': 'R.images.gui.maps.icons.quests.bonuses.big.ussr_R157_Object_279R',
  'status': RewardStatus.LOCKED}]

class PersonalMissionsOldCampaignTooltipView(ViewImpl):
    __slots__ = ()

    def __init__(self, layoutID):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.VIEW
        settings.model = PersonalMissionsOldCampaignTooltipViewModel()
        super(PersonalMissionsOldCampaignTooltipView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(PersonalMissionsOldCampaignTooltipView, self).getViewModel()

    def _onLoading(self, *args, **kwargs):
        super(PersonalMissionsOldCampaignTooltipView, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as model:
            self.__updateModel(model)

    def __updateModel(self, model):
        model.setMissionStatus(MissionStatus.ACTIVE)
        array = model.getOperations()
        for item in operations:
            nextModel = PersonalMissionsOldCampaignTooltipOperationsModel()
            nextModel.setName(item['name'])
            nextModel.setCompleted(item['completed'])
            nextModel.setAll(item['all'])
            array.addViewModel(nextModel)

        array.invalidate()
        array = model.getRewards()
        for item in rewards:
            nextModel = PersonalMissionsOldCampaignTooltipRewardsModel()
            nextModel.setName(item['name'])
            nextModel.setIcon(item['icon'])
            nextModel.setStatus(item['status'])
            array.addViewModel(nextModel)

        array.invalidate()
