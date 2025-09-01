# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/lobby/feature/white_tiger_reward_view.py
from frameworks.wulf import ViewSettings
from gui.impl.auxiliary.tooltips.compensation_tooltip import VehicleCompensationTooltipContent
from gui.impl.gen import R
from gui.impl.gen.view_models.views.loot_box_compensation_tooltip_types import LootBoxCompensationTooltipTypes
from gui.impl.gen.view_models.views.loot_box_vehicle_compensation_tooltip_model import LootBoxVehicleCompensationTooltipModel
from gui.impl.lobby.common.view_helpers import packBonusModelAndTooltipData
from gui.impl.lobby.common.view_wrappers import createBackportTooltipDecorator
from gui.impl.pub import ViewImpl
from gui.server_events.bonuses import getNonQuestBonuses
from frameworks.wulf import ViewFlags
from white_tiger.gui.wt_bonus_packers import getWTEventBonusPacker
from white_tiger.gui.impl.gen.view_models.views.lobby.reward_screen_view_model import RewardScreenViewModel
from white_tiger.gui.sounds.sound_constants import WT_REWARD_VIEW_SOUND_SPACE

class WhiteTigerRewardView(ViewImpl):
    __slots__ = ('__rewardData', '__addRewards', '__tooltips', '__hasCompletedProgression')
    _COMMON_SOUND_SPACE = WT_REWARD_VIEW_SOUND_SPACE

    def __init__(self, layoutID, ctx):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.VIEW
        settings.model = RewardScreenViewModel()
        super(WhiteTigerRewardView, self).__init__(settings)
        self.__tooltips = {}
        self.__rewardData = ctx['rewardData']
        self.__addRewards = ctx['addRewards']
        self.__hasCompletedProgression = ctx['hasCompletedProgression']

    @property
    def viewModel(self):
        return self.getViewModel()

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(WhiteTigerRewardView, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        tooltipId = event.getArgument('tooltipId')
        tc = R.views.lobby.awards.tooltips.RewardCompensationTooltip()
        if event.contentID == tc:
            if tooltipId in self.__tooltips:
                tooltipData = {'iconBefore': event.getArgument('iconBefore', ''),
                 'labelBefore': event.getArgument('labelBefore', ''),
                 'iconAfter': event.getArgument('iconAfter', ''),
                 'labelAfter': event.getArgument('labelAfter', ''),
                 'bonusName': event.getArgument('bonusName', ''),
                 'countBefore': event.getArgument('countBefore', 1),
                 'tooltipType': LootBoxCompensationTooltipTypes.VEHICLE}
                tooltipData.update(self.__tooltips[tooltipId].specialArgs)
                settings = ViewSettings(tc, model=LootBoxVehicleCompensationTooltipModel(), kwargs=tooltipData)
                return VehicleCompensationTooltipContent(settings)
        return None

    def getTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        return None if tooltipId is None else self.__tooltips.get(tooltipId)

    def _onLoading(self, *args, **kwargs):
        super(WhiteTigerRewardView, self)._onLoading(*args, **kwargs)
        rewardData = self.__rewardData
        addRewards = self.__addRewards
        with self.viewModel.transaction() as vm:
            vm.setAssetsPointer('undefined')
            vm.setHasCompleted(self.__hasCompletedProgression)
            packer = getWTEventBonusPacker()
            self.__tooltips = {}
            self.__packRewards(vm.getMainRewards(), rewardData if rewardData else addRewards, packer)
            self.__packRewards(vm.getAdditionalRewards(), addRewards if rewardData else {}, packer)

    def _finalize(self):
        self.__tooltips = {}
        super(WhiteTigerRewardView, self)._finalize()

    def _getEvents(self):
        return ((self.viewModel.onClose, self.__onCloseClick),)

    def __onCloseClick(self):
        self.destroyWindow()

    def __packRewards(self, rewardsModel, rewards, packer):
        rawDataBonuses = []
        for k, v in rewards.iteritems():
            rawDataBonuses.extend(getNonQuestBonuses(k, v))

        packBonusModelAndTooltipData(rawDataBonuses, rewardsModel, tooltipData=self.__tooltips, packer=packer)
