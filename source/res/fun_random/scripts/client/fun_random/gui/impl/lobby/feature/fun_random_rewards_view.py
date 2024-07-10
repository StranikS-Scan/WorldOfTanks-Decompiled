# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/impl/lobby/feature/fun_random_rewards_view.py
from frameworks.wulf import ViewSettings
from frameworks.wulf import WindowLayer
from fun_random.gui.feature.fun_sounds import FUN_REWARD_SCREEN_SOUND_SPACE
from fun_random.gui.feature.util.fun_mixins import FunAssetPacksMixin
from fun_random.gui.impl.gen.view_models.views.lobby.feature.fun_random_rewards_view_model import FunRandomRewardsViewModel
from fun_random.gui.impl.lobby.common.fun_view_helpers import getCompensatedFunRandomBonusPacker
from gui.impl.auxiliary.tooltips.compensation_tooltip import VehicleCompensationTooltipContent
from gui.impl.gen import R
from gui.impl.gen.view_models.views.loot_box_compensation_tooltip_types import LootBoxCompensationTooltipTypes
from gui.impl.gen.view_models.views.loot_box_vehicle_compensation_tooltip_model import LootBoxVehicleCompensationTooltipModel
from gui.impl.lobby.common.view_helpers import packBonusModelAndTooltipData
from gui.impl.lobby.common.view_wrappers import createBackportTooltipDecorator
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from gui.server_events.bonuses import getNonQuestBonuses, LootBoxTokensBonus

class FunRandomLootBoxAwardView(ViewImpl, FunAssetPacksMixin):
    __slots__ = ('__tooltipData',)
    _COMMON_SOUND_SPACE = FUN_REWARD_SCREEN_SOUND_SPACE

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.fun_random.lobby.feature.FunRandomRewardsView(), model=FunRandomRewardsViewModel(), args=args, kwargs=kwargs)
        super(FunRandomLootBoxAwardView, self).__init__(settings)
        self.__tooltips = {}

    @property
    def viewModel(self):
        return self.getViewModel()

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(FunRandomLootBoxAwardView, self).createToolTip(event)

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

    def _onLoading(self, data, *args, **kwargs):
        super(FunRandomLootBoxAwardView, self)._onLoading(*args, **kwargs)
        with self.viewModel.transaction() as vm:
            vm.setAssetsPointer(self.getModeAssetsPointer())
            packer = getCompensatedFunRandomBonusPacker()
            self.__tooltips = {}
            self.__packRewards(vm.getMainRewards(), data['mainRewards'], packer)
            self.__packRewards(vm.getAdditionalRewards(), data['addRewards'], packer)

    def _finalize(self):
        self.__tooltips = {}
        super(FunRandomLootBoxAwardView, self)._finalize()

    def _getEvents(self):
        return ((self.viewModel.onClose, self.__onCloseClick),)

    def __onCloseClick(self):
        self.destroyWindow()

    def __packRewards(self, rewardsModel, rewards, packer):
        rewardsModel.clear()
        rawDataBonuses = []
        for k, v in rewards.iteritems():
            rawDataBonuses.extend(getNonQuestBonuses(k, v))

        packBonusModelAndTooltipData([ b for b in rawDataBonuses if not isinstance(b, LootBoxTokensBonus) ], rewardsModel, tooltipData=self.__tooltips, packer=packer)
        rewardsModel.invalidate()


class FunRandomLootBoxAwardWindow(LobbyNotificationWindow):
    __slots__ = ()

    def __init__(self, data=None):
        super(FunRandomLootBoxAwardWindow, self).__init__(content=FunRandomLootBoxAwardView(data=data), layer=WindowLayer.TOP_WINDOW)
