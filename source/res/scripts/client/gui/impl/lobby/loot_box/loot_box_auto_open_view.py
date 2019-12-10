# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/loot_box/loot_box_auto_open_view.py
from frameworks.wulf import ViewSettings, ViewFlags
from gui.impl.backport import BackportTooltipWindow
from gui.impl.backport import TooltipData
from gui.impl.gen.view_models.views.lobby.lootboxes.components.loot_box_multi_open_renderer_model import LootBoxMultiOpenRendererModel
from gui.impl.gen.view_models.views.lobby.lootboxes.loot_box_auto_open_view_model import LootBoxAutoOpenViewModel
from gui.impl.lobby.loot_box.loot_box_helper import getTooltipContent, getAutoOpenLootboxBonuses
from gui.impl.pub import ViewImpl
from gui.impl.gen.resources import R
from gui.impl.pub.lobby_window import LobbyOverlay
from gui.shared import event_dispatcher
from gui.impl.auxiliary.rewards_helper import getRewardRendererModelPresenter, VehicleCompensationWithoutAnimationPresenter, LootNewYearFragmentsPresenter, LootNewYearToyPresenter, getBackportTooltipData
from gui.impl.auxiliary.rewards_helper import LootVehicleRewardPresenter
from new_year.ny_constants import CURRENT_NY_TOYS_BONUS
_COMPENSATION_PRESENTERS = {'vehicles': VehicleCompensationWithoutAnimationPresenter()}
_MODEL_PRESENTERS = {'vehicles': LootVehicleRewardPresenter(),
 CURRENT_NY_TOYS_BONUS: LootNewYearToyPresenter(),
 'ny19ToyFragments': LootNewYearFragmentsPresenter()}
_ONE_LINE_LIMIT = 6

class _LootBoxAutoOpenView(ViewImpl):
    __slots__ = ('__tooltipData',)

    def __init__(self, rewards):
        settings = ViewSettings(R.views.lobby.loot_box.views.loot_box_auto_open_view.LootBoxAutoOpenView(), flags=ViewFlags.VIEW, model=LootBoxAutoOpenViewModel())
        settings.args = (rewards,)
        super(_LootBoxAutoOpenView, self).__init__(settings)
        self.__tooltipData = {}

    @property
    def viewModel(self):
        return super(_LootBoxAutoOpenView, self).getViewModel()

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId')
            window = None
            if tooltipId is not None:
                window = BackportTooltipWindow(self.__tooltipData[tooltipId], self.getParentWindow())
                window.load()
            return window
        else:
            return super(_LootBoxAutoOpenView, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        tooltipData = getBackportTooltipData(event, self.__tooltipData)
        return getTooltipContent(event, tooltipData)

    def _initialize(self, rewards):
        super(_LootBoxAutoOpenView, self)._initialize()
        self.viewModel.onCloseBtnClick += self.__onWindowClose
        self.viewModel.onOkBtnClick += self.__onOkClicked
        self.__setRewards(rewards)

    def _finalize(self):
        self.viewModel.onCloseBtnClick -= self.__onWindowClose
        self.viewModel.onOkBtnClick -= self.__onOkClicked
        super(_LootBoxAutoOpenView, self)._finalize()

    def __setRewards(self, rewards):
        with self.getViewModel().transaction() as model:
            rewardsLineList = model.getRewards()
            rewardsLineList.clear()
            bonuses = getAutoOpenLootboxBonuses(rewards, size='big')
            splittedBonuses = [ bonuses[i:i + _ONE_LINE_LIMIT] for i in range(0, len(bonuses), _ONE_LINE_LIMIT) ]
            tooltipIdx = 0
            for lineIndex, bonusGroup in enumerate(splittedBonuses):
                lootboxRewardRenderer = LootBoxMultiOpenRendererModel()
                lootboxRewardRenderer.setIndx(lineIndex + 1)
                rewardsList = lootboxRewardRenderer.getRewards()
                rewardsList.clear()
                for bonus in bonusGroup:
                    formatter = getRewardRendererModelPresenter(bonus, _MODEL_PRESENTERS, _COMPENSATION_PRESENTERS)
                    rewardRender = formatter.getModel(bonus, tooltipIdx, isSmall=False)
                    rewardsList.addViewModel(rewardRender)
                    self.__tooltipData[tooltipIdx] = TooltipData(tooltip=bonus.get('tooltip', None), isSpecial=bonus.get('isSpecial', False), specialAlias=bonus.get('specialAlias', ''), specialArgs=bonus.get('specialArgs', None))
                    tooltipIdx += 1

                rewardsList.invalidate()
                rewardsLineList.addViewModel(lootboxRewardRenderer)

            rewardsLineList.invalidate()
        return

    def __onWindowClose(self, _=None):
        self.destroyWindow()

    def __onOkClicked(self, _=None):
        self.destroyWindow()
        event_dispatcher.showHangar()


class LootBoxAutoOpenWindow(LobbyOverlay):
    __slots__ = ()

    def __init__(self, rewards):
        super(LootBoxAutoOpenWindow, self).__init__(decorator=None, content=_LootBoxAutoOpenView(rewards), parent=None)
        return
