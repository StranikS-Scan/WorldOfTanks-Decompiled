# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/common/selectable_reward_base.py
from collections import OrderedDict
import typing
from frameworks.wulf import ViewSettings
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.common.selectable_reward_base_model import SelectableRewardBaseModel
from gui.impl.gen.view_models.views.lobby.common.selectable_reward_item_model import SelectableRewardItemModel
from gui.impl.gen.view_models.views.lobby.common.selectable_reward_tab_model import SelectableRewardTabModel
from gui.impl.lobby.common.tooltips.selected_rewards_tooltip_view import SelectedRewardsTooltipView
from gui.impl.pub import ViewImpl
from gui.selectable_reward.common import SelectableRewardManager
from gui.shared.missions.packers.bonus import getDefaultBonusPacker
if typing.TYPE_CHECKING:
    from typing import Dict, List, Optional, Tuple, Type
    from gui.server_events.bonuses import SelectableBonus
    from gui.impl.backport import TooltipData
    from gui.SystemMessages import ResultMsg
    from frameworks.wulf import ViewModel, ViewEvent, Window, View

class SelectableRewardBase(ViewImpl):
    __slots__ = ('__selectedTab', '__tabs', '__selectableRewards', '__cart', '_packer')
    _helper = SelectableRewardManager
    _packer = getDefaultBonusPacker()

    def __init__(self, layoutID, selectableRewards, model=None):
        settings = ViewSettings(layoutID)
        settings.model = (model or SelectableRewardBaseModel)()
        self.__selectableRewards = selectableRewards
        self.__selectedTab = None
        self.__tabs = OrderedDict()
        self.__cart = OrderedDict()
        self.__processTabs()
        if self.__tabs:
            self.__processRewards()
            self._sortContent()
        super(SelectableRewardBase, self).__init__(settings)
        return

    @property
    def viewModel(self):
        return super(SelectableRewardBase, self).getViewModel()

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipData = self.getTooltipData(event)
            if tooltipData is None:
                return
            window = backport.BackportTooltipWindow(tooltipData, self.getParentWindow())
            if window is None:
                return
            window.load()
            return window
        else:
            return super(SelectableRewardBase, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.common.tooltips.SelectedRewardsTooltipView():
            self._sortCart()
            return SelectedRewardsTooltipView(self.__cart, self.__getTotalCount())
        return super(SelectableRewardBase, self).createToolTipContent(event, contentID)

    def _onLoading(self, *args, **kwargs):
        super(SelectableRewardBase, self)._onLoading()
        self.__fillTabs()
        if self.__tabs:
            self.__selectTab(self.viewModel.selectableRewardModel.getTabs()[0].getType(), initial=True)
            self.__updateTotalCount()

    def _initialize(self, *args, **kwargs):
        super(SelectableRewardBase, self)._initialize()
        selectableVM = self.viewModel.selectableRewardModel
        selectableVM.onOkClick += self._onOkClick
        selectableVM.onCloseClick += self._onCloseClick
        selectableVM.onTabClick += self._onTabClick
        selectableVM.onRewardAdd += self._onRewardAdd
        selectableVM.onRewardReduce += self._onRewardReduce

    def _finalize(self):
        selectableVM = self.viewModel.selectableRewardModel
        selectableVM.onOkClick -= self._onOkClick
        selectableVM.onCloseClick -= self._onCloseClick
        selectableVM.onTabClick -= self._onTabClick
        selectableVM.onRewardAdd -= self._onRewardAdd
        selectableVM.onRewardReduce -= self._onRewardReduce
        self.__tabs = None
        self.__selectableRewards = None
        self.__cart = None
        super(SelectableRewardBase, self)._finalize()
        return

    def _onOkClick(self):
        self._makeOrder()

    def _onCloseClick(self):
        self.destroyWindow()

    def _onTabClick(self, event):
        tabName = self.__getName(event)
        self.__selectTab(tabName, initial=False)

    def _onRewardAdd(self, event):
        rewardName = self.__getName(event)
        item = self.__tabs[self.__selectedTab]['rewards'][rewardName]
        self.__cart.setdefault(self.__selectedTab, {})
        currentTabCart = self.__cart[self.__selectedTab]
        currentTabCart.setdefault(rewardName, [])
        if (len(currentTabCart[rewardName]) < item['limit'] or item['limit'] == 0) and self.__checkTabLimit():
            currentTabCart[rewardName].append(item)
            self.__tabs[self.__selectedTab]['count'] += 1
            self.__updateTabViewModel(self.__selectedTab)
            self.__updateRewardViewModel(rewardName)
        self.__updateRewardsState()
        self.__updateTotalCount()

    def _onRewardReduce(self, event):
        rewardName = self.__getName(event)
        currentTabCart = self.__cart.get(self.__selectedTab, OrderedDict())
        if currentTabCart.get(rewardName):
            currentTabCart[rewardName].pop(-1)
            if not currentTabCart[rewardName]:
                currentTabCart.pop(rewardName)
            self.__tabs[self.__selectedTab]['count'] -= 1
            self.__updateTabViewModel(self.__selectedTab)
            self.__updateRewardViewModel(rewardName)
        if self.__selectedTab in self.__cart and not self.__cart[self.__selectedTab]:
            self.__cart.pop(self.__selectedTab)
        self.__updateRewardsState()
        self.__updateTotalCount()

    def _processReceivedRewards(self, result):
        pass

    def _iterSelectableBonus(self, cart):
        for tab in cart.itervalues():
            for reward in tab.itervalues():
                for bonus in reward:
                    yield bonus

    def _makeOrder(self):
        order = {}
        for bonus in self._iterSelectableBonus(self.__cart):
            self.__addItemToOrder(order, bonus)

        self._helper.chooseRewards(order.values(), self._processReceivedRewards)

    def _sortContent(self):
        self.__tabs = OrderedDict(sorted(self.__tabs.iteritems(), cmp=self._getTypesComparator()))
        for tabName in self.__tabs:
            self.__tabs[tabName]['rewards'] = OrderedDict(sorted(self.__tabs[tabName]['rewards'].iteritems(), cmp=self._getItemsComparator(tabName)))

    def _sortCart(self):
        self.__cart = OrderedDict(sorted(self.__cart.iteritems(), cmp=self._getTypesComparator()))
        for catName in self.__cart:
            self.__cart[catName] = OrderedDict(sorted(self.__cart[catName].iteritems(), cmp=self._getItemsComparator(catName)))

    def _getTypesComparator(self):

        def _defaultCompare(first, second):
            return cmp(first[0], second[0])

        return _defaultCompare

    def _getItemsComparator(self, tabName):

        def _defaultCompare(first, second):
            return cmp(first[0], second[0])

        return _defaultCompare

    def _getTabs(self):
        return self.__tabs

    @classmethod
    def __addItemToOrder(cls, order, item):
        for selectableReward, offerID in item['selectableReward']:
            rewardType = id(selectableReward)
            if rewardType in order:
                if len(order[rewardType][1]) < cls._helper.getRemainedChoices(selectableReward):
                    order[rewardType][1].append(offerID)
                    break
                else:
                    continue
            order[rewardType] = (selectableReward, [offerID])
            break

    def __updateTotalCount(self):
        self.viewModel.selectableRewardModel.setTotalRewardCount(self.__getTotalCount())

    def __getTotalCount(self):
        result = 0
        for tab in self.__tabs:
            result += self._getTotalTabCount(tab)

        return result

    def __checkTabLimit(self):
        result = self._getTotalTabCount(self.__selectedTab) < self.__tabs[self.__selectedTab]['limit']
        return result

    def __updateRewardsState(self):
        with self.viewModel.selectableRewardModel.getRewards().transaction() as vm:
            for rewardName, _, state in self._prepareRewardsData(self.__selectedTab):
                for rewardModel in vm:
                    if rewardModel.getType() != rewardName:
                        continue
                    if rewardModel.getState() != SelectableRewardItemModel.STATE_RECEIVED:
                        rewardModel.setState(state)

    def _getTotalTabCount(self, tabName):
        totalCount = 0
        for rewardList in self.__cart.get(tabName, {}).itervalues():
            totalCount += len(rewardList)

        return totalCount

    def _getReceivedRewards(self, rewardName):
        return self.__tabs[self.__selectedTab]['rewards'][rewardName]['receivedRewards']

    def _getRewardsInCartCount(self, rewardName):
        return len(self.__cart.get(self.__selectedTab, {}).get(rewardName, {}))

    def __updateTabViewModel(self, tabName):
        with self.viewModel.selectableRewardModel.getTabs().transaction() as vm:
            for tab in vm:
                if tab.getType() == tabName:
                    tab.setCount(self.__tabs[tabName]['count'])

    def __updateRewardViewModel(self, rewardName):
        count = self._getReceivedRewards(rewardName) + self._getRewardsInCartCount(rewardName)
        packSize = self.__tabs[self.__selectedTab]['rewards'][rewardName]['packSize']
        with self.viewModel.selectableRewardModel.getRewards().transaction() as vm:
            for reward in vm:
                if reward.getType() == rewardName:
                    reward.setCount(count)
                    resultSize = packSize * count or packSize
                    if (resultSize > 1 or resultSize <= 1 and packSize == 1) and reward.getState() != SelectableRewardItemModel.STATE_RECEIVED:
                        reward.setPackSize(resultSize)

    def __selectTab(self, tabName, initial=False):
        if self.__selectedTab != tabName:
            self.__selectedTab = tabName
            self.viewModel.selectableRewardModel.setSelectedTab(tabName)
            self.__fillRewards(self.__selectedTab, initial=initial)

    @staticmethod
    def __getName(event):
        return event.get('type', '')

    def __fillRewards(self, tabName, initial=False):
        rewards = self.viewModel.selectableRewardModel.getRewards()
        with rewards.transaction() as vm:
            vm.clear()
            for rewardName, reward, state in self._prepareRewardsData(tabName):
                newReward = SelectableRewardItemModel()
                newReward.setType(rewardName)
                newReward.setCount(0 if initial else self._getRewardsInCartCount(rewardName))
                if state != SelectableRewardItemModel.STATE_RECEIVED:
                    newReward.setPackSize(reward['packSize'])
                newReward.setStorageCount(reward['storageCount'])
                newReward.setState(state)
                vm.addViewModel(newReward)

    def _prepareRewardsData(self, tabName):
        for rewardName, reward in self.__tabs[tabName]['rewards'].iteritems():
            count = self._getRewardsInCartCount(rewardName) + reward['receivedRewards']
            if reward['receivedRewards'] >= reward['limit'] > 0:
                state = SelectableRewardItemModel.STATE_RECEIVED
            elif count >= reward['limit'] > 0 or count >= self.__tabs[tabName]['limit'] or self._getTotalTabCount(tabName) >= self.__tabs[tabName]['limit']:
                state = SelectableRewardItemModel.STATE_LIMITED
            else:
                state = SelectableRewardItemModel.STATE_NORMAL
            yield (rewardName, reward, state)

    def __fillTabs(self):
        with self.viewModel.selectableRewardModel.transaction() as vm:
            tabs = vm.getTabs()
            tabs.clear()
            for tabName, tabContent in self.__tabs.iteritems():
                newTab = SelectableRewardTabModel()
                newTab.setType(tabName)
                newTab.setCount(tabContent['count'])
                newTab.setLimit(tabContent['limit'])
                tabs.addViewModel(newTab)

    def __processTabs(self):
        for reward in self.__selectableRewards:
            tabType = reward.getType()
            if self.__tabs.get(tabType) is None:
                self.__tabs[tabType] = {}
            tabContent = self.__tabs[tabType]
            tabContent.setdefault('limit', 0)
            tabContent.setdefault('count', 0)
            tabContent.setdefault('rewards', OrderedDict())
            tabContent['limit'] += self._helper.getRemainedChoices(reward)
            tabContent['tooltip'] = self._helper.getTabTooltipData(reward)

        return

    def __processRewards(self):
        for selectableReward in self.__selectableRewards:
            offer = self._helper.getBonusOptions(selectableReward)
            currentTab = self.__tabs[selectableReward.getType()]
            for giftID, gift in offer.iteritems():
                if currentTab.get('rewards') is None:
                    currentTab['rewards'] = {}
                if gift['option'] is None:
                    continue
                rewardName = gift['option'].getLightViewModelData()[0]
                rewardOp = self.__createReward if currentTab['rewards'].get(rewardName) is None else self.__updateReward
                rewardOp(currentTab['rewards'], rewardName, gift, giftID, selectableReward)

            receivedRewards = self._helper.getBonusReceivedOptions(selectableReward)
            for receivedReward, receivedRewardCount in receivedRewards:
                rewardName = receivedReward.getLightViewModelData()[0]
                currentTab['rewards'][rewardName]['receivedRewards'] += receivedRewardCount

        return

    def __createReward(self, rewards, rewardName, gift, giftID, selectableReward):
        rewards[rewardName] = {'packSize': gift['count'],
         'limit': gift['limit'],
         'storageCount': gift['option'].getInventoryCount(),
         'selectableReward': [(selectableReward, giftID)],
         'receivedRewards': 0,
         'tooltip': self._packer.getToolTip(gift['option']),
         'displayedBonusData': gift['option'].displayedBonusData}

    @staticmethod
    def __updateReward(rewards, rewardName, gift, giftID, selectableReward):
        rewards[rewardName]['selectableReward'].append((selectableReward, giftID))
        if rewards[rewardName]['limit'] != 0 or gift['limit'] != 0:
            rewards[rewardName]['limit'] += gift['limit']
        else:
            rewards[rewardName]['limit'] = 0

    def getTooltipData(self, event):
        rewardType = event.getArgument('type')
        tooltips = self.__tabs.get(rewardType, {}).get('tooltip')
        if tooltips:
            return tooltips
        else:
            tooltips = self.__tabs[self.__selectedTab]['rewards'].get(rewardType, {}).get('tooltip')
            return tooltips[0] if tooltips else None
