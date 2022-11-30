# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/new_year/views/tabs_controller.py
from account_helpers.AccountSettings import AccountSettings, NY_DOG_PAGE_VISITED, NY_NARKET_PLACE_PAGE_VISITED, NY_CAT_PAGE_VISITED, NY_CELEBRITY_DAY_QUESTS_VISITED_MASK, NY_CELEBRITY_ADD_QUESTS_VISITED_MASK
from gui.impl.common.tabs_controller import TabsController, tabUpdateFunc
from gui.impl.gen.view_models.views.lobby.new_year.components.new_year_tab_model import NewYearTabModel
from gui.impl.gen.view_models.views.lobby.new_year.components.ny_main_menu_tab_model import NyMainMenuTabModel
from gui.impl.lobby.loot_box.loot_box_notification import LootBoxNotification
from gui.shared.gui_items.loot_box import NewYearCategories, NewYearLootBoxes, CATEGORIES_GUI_ORDER
from helpers import dependency
from new_year.celebrity.celebrity_quests_helpers import hasCelebrityBubble, isDogPageVisited, isUnseenCelebrityQuestsAvailable
from new_year.ny_constants import NyWidgetTopMenu, NyTabBarMainView, NyTabBarFriendGladeView, NyTabBarChallengeView, NyTabBarMarketplaceView, Collections, GuestsQuestsTokens
from items.components.ny_constants import NyATMReward
from new_year.ny_marketplace_helper import isCollectionReceived
from new_year.ny_resource_collecting_helper import isManualCollectingAvailable
from shared_utils import findFirst
from skeletons.gui.shared import IItemsCache
from skeletons.new_year import INewYearController, IGiftMachineController, IFriendServiceController

class NyTabsController(TabsController):
    __slots__ = ('_iconNamePostfix', '_selectedTabIdx')

    def __init__(self, autoCreating=True, iconNamePostfix=''):
        super(NyTabsController, self).__init__(autoCreating)
        self._iconNamePostfix = iconNamePostfix
        self._selectedTabIdx = 0

    @property
    def tabs(self):
        return self._getTabs()

    def getSelectedTabIdx(self):
        return self._selectedTabIdx

    def setSelectedTabIdx(self, idx):
        if 0 <= idx < len(self._getTabs()):
            self._selectedTabIdx = idx

    def selectTab(self, tabName):
        tabs = self._getTabs()
        self._selectedTabIdx = tabs.index(tabName) if tabName in tabs else 0

    def getSelectedName(self, tabsArray):
        return tabsArray[self._selectedTabIdx].getName() if self._selectedTabIdx < len(tabsArray) else None

    def getCurrentTabName(self):
        tabsArray = self._getTabs()
        return tabsArray[self._selectedTabIdx] if self._selectedTabIdx < len(tabsArray) else None

    def isTabActive(self, tabName):
        return tabName in self._getTabs()

    def updateTabModels(self, tabsArray):
        self._autoCreating = len(tabsArray) != len(self._getTabs())
        super(NyTabsController, self).updateTabModels(tabsArray)

    def getDefaultTab(self):
        tabs = self._getTabs()
        return tabs[0] if tabs else super(NyTabsController, self).getDefaultTab()

    def getSettingKeysForUpdate(self):
        return set()

    def clearData(self):
        pass

    def _createViewModel(self, name):
        modelCls = self._getModelCls()
        viewModel = modelCls()
        viewModel.setIconName(name + self._iconNamePostfix)
        return viewModel

    def _getModelCls(self):
        return NewYearTabModel

    def _getTabs(self, **kwargs):
        tabs = super(NyTabsController, self)._getTabs(**kwargs)
        return [ tab for tab in tabs if self._tabActive(tab) ]

    def _tabActive(self, tabName):
        return True


class NewYearMainTabsController(NyTabsController):
    __nyController = dependency.descriptor(INewYearController)
    __nyGiftMachineCtrl = dependency.descriptor(IGiftMachineController)
    __friendsService = dependency.descriptor(IFriendServiceController)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, autoCreating=True):
        super(NewYearMainTabsController, self).__init__(autoCreating)
        self.__isFriendHangar = False

    def getIsFriendHangar(self):
        return self.__isFriendHangar

    def updateIsFriendHangar(self, isFriendHangar):
        self.__isFriendHangar = isFriendHangar

    def selectTab(self, tabName):
        super(NewYearMainTabsController, self).selectTab(tabName)
        if tabName == NyATMReward.ShortName.MARKETPLACE:
            if AccountSettings.getUIFlag(NY_NARKET_PLACE_PAGE_VISITED) is False:
                AccountSettings.setUIFlag(NY_NARKET_PLACE_PAGE_VISITED, True)

    def _getModelCls(self):
        return NyMainMenuTabModel

    @tabUpdateFunc(NyWidgetTopMenu.GLADE)
    def _updateGlade(self, viewModel, _=False):
        viewModel.setUnseenCount(self.__nyController.checkForNewToys())

    @tabUpdateFunc(NyWidgetTopMenu.REWARDS)
    def _updateRewards(self, viewModel, _=False):
        pass

    @tabUpdateFunc(NyWidgetTopMenu.MARKETPLACE)
    def _updateMarketplace(self, viewModel, _=False):
        flag = AccountSettings.getUIFlag(NY_NARKET_PLACE_PAGE_VISITED)
        if flag is not None:
            if flag is False and self._getTabs()[self.getSelectedTabIdx()] == NyATMReward.ShortName.MARKETPLACE:
                AccountSettings.setUIFlag(NY_NARKET_PLACE_PAGE_VISITED, True)
                flag = True
            viewModel.setUnseenCount(not flag)
        return

    @tabUpdateFunc(NyWidgetTopMenu.FRIENDS)
    def _updateFriends(self, viewModel, _=False):
        viewModel.setIsEnabled(self.__friendsService.isServiceEnabled)

    @tabUpdateFunc(NyWidgetTopMenu.CHALLENGE)
    def _updateChallenge(self, viewModel, _=False):
        viewModel.setUnseenCount(hasCelebrityBubble())

    @tabUpdateFunc(NyWidgetTopMenu.GIFT_MACHINE)
    def _updateGiftMachine(self, viewModel, _=False):
        viewModel.setInfoCount(self.__nyController.currencies.getCoinsCount())
        viewModel.setUnseenCount(not self.__nyGiftMachineCtrl.isBuyCoinVisited)

    @tabUpdateFunc(NyWidgetTopMenu.FRIEND_INFO)
    def _updateFriendInfo(self, viewModel, _=False):
        pass

    @tabUpdateFunc(NyWidgetTopMenu.INFO)
    def _updateInfo(self, viewModel, _=False):
        pass

    @tabUpdateFunc(NyWidgetTopMenu.FRIEND_GLADE)
    def _updateFriendGlade(self, viewModel, _=False):
        pass

    @tabUpdateFunc(NyWidgetTopMenu.FRIEND_CHALLENGE)
    def _updateFriendChallenge(self, viewModel, _=False):
        pass

    def tabOrderKey(self, tabName):
        return self._getTabs().index(tabName)

    def _getTabs(self, **kwargs):
        return NyWidgetTopMenu.ALL_FRIEND_HANGAR if self.__isFriendHangar else NyWidgetTopMenu.ALL_PLAYER_HANGAR


class GladeTabsController(NyTabsController):
    __nyController = dependency.descriptor(INewYearController)

    @tabUpdateFunc(NyTabBarMainView.TOWN)
    def _updateTown(self, viewModel, _=False):
        pass

    @tabUpdateFunc(NyTabBarMainView.FIR)
    def _updateFir(self, viewModel, _=False):
        viewModel.setUnseenCount(self.__nyController.checkForNewToysByType(NyTabBarMainView.FIR))

    @tabUpdateFunc(NyTabBarMainView.FAIR)
    def _updateFair(self, viewModel, _=False):
        viewModel.setUnseenCount(self.__nyController.checkForNewToysByType(NyTabBarMainView.FAIR))

    @tabUpdateFunc(NyTabBarMainView.INSTALLATION)
    def _updateInstallation(self, viewModel, _=False):
        viewModel.setUnseenCount(self.__nyController.checkForNewToysByType(NyTabBarMainView.INSTALLATION))

    @tabUpdateFunc(NyTabBarMainView.RESOURCES)
    def _updateResources(self, viewModel, _=False):
        viewModel.setUnseenCount(isManualCollectingAvailable())

    def tabOrderKey(self, tabName):
        return NyTabBarMainView.ALL.index(tabName)


class FriendGladeTabsController(NyTabsController):
    __nyController = dependency.descriptor(INewYearController)
    __friendsService = dependency.descriptor(IFriendServiceController)

    def clearData(self):
        self._selectedTabIdx = 0

    @tabUpdateFunc(NyTabBarFriendGladeView.TOWN)
    def _updateTown(self, viewModel, _=False):
        pass

    @tabUpdateFunc(NyTabBarFriendGladeView.FIR)
    def _updateFir(self, viewModel, _=False):
        pass

    @tabUpdateFunc(NyTabBarFriendGladeView.FAIR)
    def _updateFair(self, viewModel, _=False):
        pass

    @tabUpdateFunc(NyTabBarFriendGladeView.INSTALLATION)
    def _updateInstallation(self, viewModel, _=False):
        pass

    @tabUpdateFunc(NyTabBarFriendGladeView.RESOURCES)
    def _updateResources(self, viewModel, _=False):
        viewModel.setUnseenCount(not bool(self.__friendsService.getFriendCollectingCooldownTime()))

    def tabOrderKey(self, tabName):
        return NyTabBarFriendGladeView.ALL.index(tabName)


class ChallengeTabsController(NyTabsController):
    __nyController = dependency.descriptor(INewYearController)

    def __init__(self, autoCreating=True):
        super(ChallengeTabsController, self).__init__(autoCreating, iconNamePostfix='Challenge')

    def getSettingKeysForUpdate(self):
        return {NY_DOG_PAGE_VISITED, NY_CELEBRITY_DAY_QUESTS_VISITED_MASK, NY_CELEBRITY_ADD_QUESTS_VISITED_MASK}

    def getCustomTabsKeyUpdate(self):
        return {NY_CAT_PAGE_VISITED: NyTabBarChallengeView.GUEST_CAT}

    @tabUpdateFunc(NyTabBarChallengeView.TOURNAMENT)
    def _updateTournament(self, viewModel, _=False):
        viewModel.setUnseenCount(isUnseenCelebrityQuestsAvailable())

    @tabUpdateFunc(NyTabBarChallengeView.GUEST_A)
    def _updateCelebrityA(self, viewModel, _=False):
        pass

    @tabUpdateFunc(NyTabBarChallengeView.GUEST_M)
    def _updateCelebrityM(self, viewModel, _=False):
        pass

    @tabUpdateFunc(NyTabBarChallengeView.GUEST_CAT)
    def _updateCat(self, viewModel, _=False):
        if self.__isCatTabEnable():
            flag = AccountSettings.getUIFlag(NY_CAT_PAGE_VISITED)
            viewModel.setUnseenCount(not flag)

    @tabUpdateFunc(NyTabBarChallengeView.GUEST_D)
    def _updateCelebrityD(self, viewModel, _=False):
        viewModel.setUnseenCount(not isDogPageVisited())
        viewModel.setIsHintVisible(not isDogPageVisited())

    @tabUpdateFunc(NyTabBarChallengeView.HEADQUARTERS)
    def _updateStaff(self, viewModel, _=False):
        pass

    def tabOrderKey(self, tabName):
        return NyTabBarChallengeView.ALL.index(tabName)

    def _tabActive(self, tabName):
        if tabName == NyTabBarChallengeView.GUEST_CAT:
            return self.__isCatTabEnable()
        return self.__isDogTabEnable() if tabName == NyTabBarChallengeView.GUEST_D else super(ChallengeTabsController, self)._tabActive(tabName)

    def __isCatTabEnable(self):
        return self.__nyController.isTokenReceived(GuestsQuestsTokens.TOKEN_CAT)

    def __isDogTabEnable(self):
        return self.__nyController.isTokenReceived(GuestsQuestsTokens.TOKEN_DOG)


class MarketplaceTabsController(NyTabsController):
    __nyController = dependency.descriptor(INewYearController)

    def __init__(self, autoCreating=True):
        super(MarketplaceTabsController, self).__init__(autoCreating, iconNamePostfix='Reward')
        idx, _ = self.__nyController.getFirstNonReceivedMarketPlaceCollectionData()
        self._selectedTabIdx = idx

    @tabUpdateFunc(NyTabBarMarketplaceView.NY18_CATEGORY)
    def _updateCategory2018(self, viewModel, _=False):
        viewModel.setIsCompleted(isCollectionReceived(Collections.NewYear18))

    @tabUpdateFunc(NyTabBarMarketplaceView.NY19_CATEGORY)
    def _updateCategory2019(self, viewModel, _=False):
        viewModel.setIsCompleted(isCollectionReceived(Collections.NewYear19))

    @tabUpdateFunc(NyTabBarMarketplaceView.NY20_CATEGORY)
    def _updateCategory2020(self, viewModel, _=False):
        viewModel.setIsCompleted(isCollectionReceived(Collections.NewYear20))

    @tabUpdateFunc(NyTabBarMarketplaceView.NY21_CATEGORY)
    def _updateCategory2021(self, viewModel, _=False):
        viewModel.setIsCompleted(isCollectionReceived(Collections.NewYear21))

    @tabUpdateFunc(NyTabBarMarketplaceView.NY22_CATEGORY)
    def _updateCategory2022(self, viewModel, _=False):
        viewModel.setIsCompleted(isCollectionReceived(Collections.NewYear22))

    def tabOrderKey(self, tabName):
        return NyTabBarMarketplaceView.REVERSED_ALL.index(tabName)


class RewardKitsEntryViewTabsController(NyTabsController):
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, autoCreating=True):
        super(RewardKitsEntryViewTabsController, self).__init__(autoCreating)
        self.__availableBoxes = {}

    def tabOrderKey(self, tabName):
        return CATEGORIES_GUI_ORDER.index(tabName)

    def setInitState(self, initRewardKitType, initCategory):
        if initRewardKitType in CATEGORIES_GUI_ORDER:
            self.selectTab(initRewardKitType)
        elif initRewardKitType == NewYearLootBoxes.PREMIUM and not initCategory:
            category = self.getInitCategory()
            if category is not None:
                self.selectTab(category)
        elif initCategory in CATEGORIES_GUI_ORDER:
            self.selectTab(initCategory)
        return

    def updateAvailableBoxes(self, availableBoxes):
        self.__availableBoxes = availableBoxes

    def getSelectedBoxCategory(self):
        return CATEGORIES_GUI_ORDER[self._selectedTabIdx]

    def getSelectedBoxName(self):
        return CATEGORIES_GUI_ORDER[self._selectedTabIdx]

    def getSelectedBoxID(self):
        lootbox = findFirst(lambda l: l.getCategory() == self.getSelectedBoxCategory(), self.__itemsCache.items.tokens.getLootBoxes().itervalues())
        return lootbox.getID() if lootbox else None

    def _getModelCls(self):
        return NewYearTabModel

    @tabUpdateFunc(NewYearCategories.NEWYEAR)
    def _updateNewYear(self, viewModel, _=False):
        self._updatePremiumLootBox(viewModel, NewYearCategories.NEWYEAR)

    @tabUpdateFunc(NewYearCategories.CHRISTMAS)
    def _updateChristmas(self, viewModel, _=False):
        self._updatePremiumLootBox(viewModel, NewYearCategories.CHRISTMAS)

    @tabUpdateFunc(NewYearCategories.ORIENTAL)
    def _updateOriental(self, viewModel, _=False):
        self._updatePremiumLootBox(viewModel, NewYearCategories.ORIENTAL)

    @tabUpdateFunc(NewYearCategories.FAIRYTALE)
    def _updateFairytale(self, viewModel, _=False):
        self._updatePremiumLootBox(viewModel, NewYearCategories.FAIRYTALE)

    def _updatePremiumLootBox(self, viewModel, category):
        viewModel.setInfoCount(self._getBoxCountByCategory(category))
        viewModel.setUnseenCount(LootBoxNotification.hasNewBox(NewYearLootBoxes.PREMIUM, category))

    def _getBoxCountByCategory(self, category):
        return self.__availableBoxes.get(NewYearLootBoxes.PREMIUM, {}).get('categories', {}).get(category, 0)

    def getInitCategory(self):
        category = None
        for categoryName in CATEGORIES_GUI_ORDER:
            if LootBoxNotification.hasDeliveredBox(categoryName):
                return categoryName
            if category is None and self._getBoxCountByCategory(categoryName):
                category = categoryName

        return category
