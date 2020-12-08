# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/loot_box/loot_box_auto_open_view.py
from frameworks.wulf import ViewSettings, ViewFlags
from gui.impl.auxiliary.rewards_helper import LootVehicleRewardPresenter
from gui.impl.auxiliary.rewards_helper import VehicleCompensationWithoutAnimationPresenter, LootNewYearFragmentsCompensationPresenter, LootNewYearToyPresenter, getBackportTooltipData
from gui.impl.backport import BackportTooltipWindow
from gui.impl.gen.resources import R
from gui.impl.gen.view_models.views.lobby.new_year.views.lootboxes.loot_box_auto_open_view_model import LootBoxAutoOpenViewModel
from gui.impl.lobby.loot_box.loot_box_bonuses_helpers import packBonusGroups, RewardsGroup, getLootBoxBonusPacker, isBattleBooster, isConsumable, isCrewBook, getItemsFilter
from gui.impl.lobby.loot_box.loot_box_helper import getTooltipContent
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyOverlay
from gui.shared import event_dispatcher
from gui.shared.gui_items.loot_box import NewYearLootBoxes
from helpers import dependency
from items.components.ny_constants import CurrentNYConstants
from skeletons.gui.shared import IItemsCache
_COMPENSATION_PRESENTERS = {'vehicles': VehicleCompensationWithoutAnimationPresenter()}
_MODEL_PRESENTERS = {'vehicles': LootVehicleRewardPresenter(),
 CurrentNYConstants.TOYS: LootNewYearToyPresenter(),
 CurrentNYConstants.TOY_FRAGMENTS: LootNewYearFragmentsCompensationPresenter()}

class _LootBoxAutoOpenView(ViewImpl):
    itemsCache = dependency.descriptor(IItemsCache)
    __slots__ = ('__rewards', '__boxes', '__tooltips')

    def __init__(self, rewards, boxes):
        settings = ViewSettings(R.views.lobby.new_year.LootBoxAutoOpenView(), flags=ViewFlags.VIEW, model=LootBoxAutoOpenViewModel())
        super(_LootBoxAutoOpenView, self).__init__(settings)
        self.__rewards = rewards
        self.__boxes = boxes
        self.__tooltips = {}

    @property
    def viewModel(self):
        return super(_LootBoxAutoOpenView, self).getViewModel()

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId')
            if tooltipId is None:
                return
            window = BackportTooltipWindow(self.__tooltips[tooltipId], self.getParentWindow())
            window.load()
            return window
        else:
            return super(_LootBoxAutoOpenView, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        tooltipData = getBackportTooltipData(event, self.__tooltips)
        return getTooltipContent(event, tooltipData)

    def _initialize(self):
        super(_LootBoxAutoOpenView, self)._initialize()
        self.viewModel.onCloseBtnClick += self.__onWindowClose
        self.viewModel.onOkBtnClick += self.__onOkClicked
        self.__updateBoxesInfo()
        self.__updateRewards()

    def _finalize(self):
        self.viewModel.onCloseBtnClick -= self.__onWindowClose
        self.viewModel.onOkBtnClick -= self.__onOkClicked
        super(_LootBoxAutoOpenView, self)._finalize()

    def __updateBoxesInfo(self):
        premiumBoxesCount = commonBoxesCount = 0
        for lootbox in self.itemsCache.items.tokens.getLootBoxes().itervalues():
            boxID = lootbox.getID()
            if boxID not in self.__boxes:
                continue
            count = self.__boxes[boxID]
            if lootbox.getType() == NewYearLootBoxes.PREMIUM:
                premiumBoxesCount += count
            commonBoxesCount += count

        with self.viewModel.transaction() as tx:
            tx.setBigBoxesQuantity(premiumBoxesCount)
            tx.setSmallBoxesQuantity(commonBoxesCount)

    def __updateRewards(self):
        with self.getViewModel().transaction() as tx:
            packBonusGroups(bonuses=self.__rewards, groupModelsList=tx.rewardRows, groupsLayout=self.__getGroupsLayout(), packer=getLootBoxBonusPacker(), tooltipsData=self.__tooltips)

    def __onWindowClose(self, _=None):
        self.destroyWindow()

    def __onOkClicked(self, _=None):
        self.destroyWindow()
        event_dispatcher.showHangar()

    @staticmethod
    def __getGroupsLayout():
        groupNamesRes = R.strings.lootboxes.rewardGroups
        layout = (RewardsGroup(name=groupNamesRes.vehicles(), bonusTypes=('vehicles',), bonuses={}, filterFuncs=None),
         RewardsGroup(name=groupNamesRes.styles(), bonusTypes=('customizations',), bonuses={}, filterFuncs=None),
         RewardsGroup(name=groupNamesRes.toys(), bonusTypes=(CurrentNYConstants.TOYS,), bonuses={}, filterFuncs=None),
         RewardsGroup(name=groupNamesRes.consumables(), bonusTypes=('items',), bonuses={}, filterFuncs=(getItemsFilter((isConsumable,)),)),
         RewardsGroup(name=groupNamesRes.crewBooksAndBattleBoosters(), bonusTypes=('items',), bonuses={}, filterFuncs=(getItemsFilter((isBattleBooster, isCrewBook)),)),
         RewardsGroup(name=groupNamesRes.other(), bonusTypes=(), bonuses={}, filterFuncs=None))
        return layout


class LootBoxAutoOpenWindow(LobbyOverlay):
    __slots__ = ()

    def __init__(self, rewards, boxes):
        super(LootBoxAutoOpenWindow, self).__init__(content=_LootBoxAutoOpenView(rewards, boxes))
