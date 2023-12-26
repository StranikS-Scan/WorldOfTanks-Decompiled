# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/loot_box/loot_box_auto_open_view.py
from frameworks.wulf import ViewSettings, ViewFlags, WindowLayer
from gui.impl.auxiliary.rewards_helper import getBackportTooltipData
from gui.impl.backport import BackportTooltipWindow
from gui.impl.gen.resources import R
from gui.impl.gen.view_models.views.lobby.new_year.views.lootboxes.reward_kit_auto_open_view_model import RewardKitAutoOpenViewModel
from gui.impl.lobby.loot_box.loot_box_bonuses_helpers import packBonusGroups, RewardsGroup, getNYLootBoxBonusPacker, isOptionalDevice, getItemsFilter, compareVehicles, compareCustomization, compareOtherBonuses
from gui.impl.lobby.loot_box.loot_box_helper import getTooltipContent
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from gui.shared import event_dispatcher
from gui.shared.gui_items.loot_box import NewYearLootBoxes
from helpers import dependency
from new_year.ny_constants import GuestsQuestsTokens
from items.components.ny_constants import NySackLootBox, CurrentNYConstants
from new_year.gift_machine_helper import getCoinType
from skeletons.gui.shared import IItemsCache

class _LootBoxAutoOpenView(ViewImpl):
    itemsCache = dependency.descriptor(IItemsCache)
    _SKIP_SECTIONS = (CurrentNYConstants.TOYS, 'currencies', 'tokens')
    __slots__ = ('__rewards', '__boxes', '__tooltips')

    def __init__(self, rewards, boxes):
        settings = ViewSettings(R.views.lobby.new_year.RewardKitAutoOpenView(), flags=ViewFlags.VIEW, model=RewardKitAutoOpenViewModel())
        super(_LootBoxAutoOpenView, self).__init__(settings)
        self.__rewards = self.__filterRewards(rewards)
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
        self.viewModel.onAccept += self.__onAcceptClicked
        self.__updateBoxesInfo()
        self.__updateRewards()

    def _finalize(self):
        self.viewModel.onAccept -= self.__onAcceptClicked
        super(_LootBoxAutoOpenView, self)._finalize()

    def __updateBoxesInfo(self):
        boxesCount = coinsCount = sacksCount = 0
        coinType = getCoinType()
        for lootbox in self.itemsCache.items.tokens.getLootBoxes().values():
            boxID = lootbox.getID()
            if boxID not in self.__boxes:
                continue
            count = self.__boxes[boxID]
            if lootbox.getType() == NewYearLootBoxes.PREMIUM:
                boxesCount += count
            if lootbox.getType() == coinType:
                coinsCount += count
            if lootbox.getType() == NySackLootBox.TYPE:
                sacksCount += count

        with self.viewModel.transaction() as tx:
            tx.setBoxesQuantity(boxesCount)
            tx.setCoinsQuantity(coinsCount)
            tx.setSacksQuantity(sacksCount)

    def __updateRewards(self):
        with self.getViewModel().transaction() as tx:
            packBonusGroups(bonuses=self.__rewards, groupModelsList=tx.rewardRows, groupsLayout=self.__getGroupsLayout(), packer=getNYLootBoxBonusPacker(), tooltipsData=self.__tooltips)

    def __onAcceptClicked(self, _=None):
        self.destroyWindow()
        event_dispatcher.showHangar()

    @staticmethod
    def __getGroupsLayout():
        groupNamesRes = R.strings.lootboxes.rewardGroups
        layout = (RewardsGroup(name=groupNamesRes.vehicles(), bonusTypes=('vehicles',), bonuses={}, filterFuncs=None, sortKeyFunc=compareVehicles),
         RewardsGroup(name=groupNamesRes.styles(), bonusTypes=('customizations',), bonuses={}, filterFuncs=None, sortKeyFunc=compareCustomization),
         RewardsGroup(name=groupNamesRes.optionalDevices(), bonusTypes=('items',), bonuses={}, filterFuncs=(getItemsFilter((isOptionalDevice,)),), sortKeyFunc=None),
         RewardsGroup(name=groupNamesRes.other(), bonusTypes=(), bonuses={}, filterFuncs=None, sortKeyFunc=compareOtherBonuses))
        return layout

    def __filterRewards(self, rewards):
        for section in self._SKIP_SECTIONS:
            if section == 'tokens':
                rewards[section].pop(GuestsQuestsTokens.TOKEN_CAT, None)
            rewards[section] = {}

        return rewards


class LootBoxAutoOpenWindow(LobbyNotificationWindow):
    __slots__ = ()

    def __init__(self, rewards, boxes):
        super(LootBoxAutoOpenWindow, self).__init__(content=_LootBoxAutoOpenView(rewards, boxes), layer=WindowLayer.TOP_WINDOW)
