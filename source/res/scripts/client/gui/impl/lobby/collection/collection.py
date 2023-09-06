# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/collection/collection.py
import logging
import typing
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags
from gui.Scaleform.Waiting import Waiting
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.profile.sound_constants import ACHIEVEMENTS_SOUND_SPACE
from gui.collection.sounds import COLLECTIONS_MT_BIRTHDAY23_SOUND_SPACE
from gui.collection.account_settings import getShownNewItemsCount, isItemNew, isRewardNew, isTutorialCompleted, setCollectionRenewSeen, setCollectionTutorialCompleted, setItemShown, setRewardShown, setShownNewItemsCount
from gui.collection.collections_helpers import composeBonuses, getItemResKey, setHangarState
from gui.collection.resources.cdn.models import Group, Sub, makeImageID
from gui.impl.auxiliary.collections_helper import getCollectionsBonusPacker
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.collection.collection_view_model import CollectionViewModel
from gui.impl.gen.view_models.views.lobby.collection.item_model import ItemModel, ItemState
from gui.impl.gen.view_models.views.lobby.collection.page_backgrounds_model import PageBackgroundsModel
from gui.impl.gen.view_models.views.lobby.collection.reward_info_model import RewardInfoModel, RewardState
from gui.impl.gen.view_models.views.lobby.collection.tab_model import TabModel
from gui.impl.lobby.battle_pass.tooltips.battle_pass_coin_tooltip_view import BattlePassCoinTooltipView
from gui.impl.lobby.collection.tooltips.additional_rewards_tooltip import AdditionalRewardsTooltip
from gui.impl.lobby.collection.tooltips.collection_item_tooltip_view import CollectionItemTooltipView
from gui.impl.lobby.common.view_helpers import packBonusModelAndTooltipData
from gui.impl.lobby.common.view_wrappers import createBackportTooltipDecorator
from gui.impl.pub import ViewImpl
from gui.impl.pub.lobby_window import LobbyWindow
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.shared import EVENT_BUS_SCOPE, events, g_eventBus
from gui.shared.event_dispatcher import showCollectionItemPreviewWindow, showHangar
from helpers import dependency, isPlayerAccount
from skeletons.gui.game_control import ICollectionsSystemController
_logger = logging.getLogger(__name__)
_INITIAL_PAGE = -1
_SEPARATOR = ','
if typing.TYPE_CHECKING:
    from typing import Dict
_COLLECTION_NAME_TO_SOUNDSPACE = {'mt_birthday2023': COLLECTIONS_MT_BIRTHDAY23_SOUND_SPACE}

class CollectionView(ViewImpl):
    __slots__ = ('__backCallback', '__backBtnText', '__collection', '__page', '__pagesCount', '__rewardTooltips', '__content', '__bonusData', '_COMMON_SOUND_SPACE')
    __collectionsSystem = dependency.descriptor(ICollectionsSystemController)

    def __init__(self, collectionId, backCallback, backBtnText, page):
        settings = ViewSettings(R.views.lobby.collection.CollectionView())
        settings.flags = ViewFlags.LOBBY_TOP_SUB_VIEW
        settings.model = CollectionViewModel()
        self.__backCallback = backCallback
        self.__backBtnText = backBtnText
        self.__collection = self.__collectionsSystem.getCollection(collectionId)
        self.__rewardTooltips = {}
        self.__bonusData = []
        self.__page = page
        self.__pagesCount = 0
        self.__content = {}
        self._COMMON_SOUND_SPACE = _COLLECTION_NAME_TO_SOUNDSPACE.get(self.__collection.name, ACHIEVEMENTS_SOUND_SPACE)
        super(CollectionView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(CollectionView, self).getViewModel()

    @createBackportTooltipDecorator()
    def createToolTip(self, event):
        return super(CollectionView, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.battle_pass.tooltips.BattlePassCoinTooltipView():
            return BattlePassCoinTooltipView()
        else:
            if contentID == R.views.lobby.collection.tooltips.CollectionItemTooltipView():
                if event.hasArgument('itemId'):
                    return CollectionItemTooltipView(itemId=event.getArgument('itemId'), collectionId=self.__collection.collectionId)
                tooltipData = self.getTooltipData(event)
                if tooltipData is not None:
                    return CollectionItemTooltipView(*tooltipData.specialArgs)
            if contentID == R.views.lobby.tooltips.AdditionalRewardsTooltip():
                tooltipIds = map(int, event.getArgument('hiddenRewards').split(_SEPARATOR))
                bonuses = [ bonus for index, bonus in enumerate(self.__bonusData) if index in tooltipIds ]
                return AdditionalRewardsTooltip(bonuses)
            return super(CollectionView, self).createToolTipContent(event, contentID)

    def getTooltipData(self, event):
        tooltipId = event.getArgument('tooltipId')
        return None if tooltipId is None else self.__rewardTooltips.get(tooltipId)

    def _onLoaded(self, *args, **kwargs):
        setCollectionRenewSeen(self.__collection.collectionId)

    def _finalize(self):
        self.__backCallback = None
        self.__rewardTooltips = None
        g_eventBus.handleEvent(events.CollectionsEvent(events.CollectionsEvent.COLLECTION_VIEW_CLOSED), scope=EVENT_BUS_SCOPE.LOBBY)
        super(CollectionView, self)._finalize()
        return

    def _getEvents(self):
        return ((self.__collectionsSystem.onServerSettingsChanged, self.__onSettingsChanged),
         (self.__collectionsSystem.onBalanceUpdated, self.__onBalanceUpdated),
         (self.viewModel.onViewLoaded, self.__onViewLoaded),
         (self.viewModel.onSetItemReceived, self.__onSetItemReceived),
         (self.viewModel.onSetRewardReceived, self.__onSetRewardReceived),
         (self.viewModel.onSetProgressItemsReceived, self.__onSetProgressItemsReceived),
         (self.viewModel.onOpenItemPreview, self.__onOpenItemPreview),
         (self.viewModel.onFinishTutorial, self.__onFinishTutorial),
         (self.viewModel.onTabSelected, self.__onTabSelected),
         (self.viewModel.onClose, self.__onClose))

    def _getListeners(self):
        return ((events.LobbyHeaderMenuEvent.MENU_CLICK, self.__onHeaderMenuClick, EVENT_BUS_SCOPE.LOBBY),)

    def __onViewLoaded(self, args):
        self.__pagesCount = int(args.get('pagesCount'))
        with self.viewModel.transaction() as model:
            model.setBackButtonText(self.__backBtnText)
            self.__fillTabs(model=model)
            self.__fillTabData(model=model)
            if self.__page is not None:
                model.setPage(self.__page)
        return

    @replaceNoneKwargsModel
    def __fillTabData(self, model=None):
        model.setIsCompleted(self.__collectionsSystem.isCollectionCompleted(self.__collection.collectionId))
        self.__clearContent(model=model)
        model.setCurrentCollection(self.__collection.name)
        model.setIsTutorial(not isTutorialCompleted(self.__collection.collectionId))
        self.__updateContentData()
        self.__fillProgression(model=model)

    def __fillTabs(self, model=None):
        tabModels = model.getTabs()
        tabModels.clear()
        for collectionId in self.__collectionsSystem.getLinkedCollections(self.__collection.collectionId):
            tabModel = TabModel()
            self.__fillTabModel(collectionId, tabModel)
            tabModels.addViewModel(tabModel)

        tabModels.invalidate()

    @replaceNoneKwargsModel
    def __fillItems(self, model=None):
        itemModels = model.getItems()
        itemModels.clear()
        for item in self.__collection.items.itervalues():
            itemModel = ItemModel()
            self.__fillItemModel(item, itemModel)
            itemModels.addViewModel(itemModel)

        itemModels.invalidate()

    def __fillItemModel(self, item, itemModel):
        itemId = item.itemId
        itemModel.setItemId(itemId)
        itemModel.setState(self.__getItemState(itemId))
        itemResKey = getItemResKey(self.__collection.collectionId, item)
        receivedImg = self.__getContent(Group.ITEM, Sub.RECEIVED, itemResKey)
        unreceivedImg = self.__getContent(Group.ITEM, Sub.UNRECEIVED, itemResKey)
        if receivedImg:
            itemModel.setReceivedImagePath(receivedImg)
        if unreceivedImg:
            itemModel.setUnreceivedImagePath(unreceivedImg)

    def __fillTabModel(self, collectionId, tabModel):
        tabModel.setCollectionName(self.__collectionsSystem.getCollection(collectionId).name)
        tabModel.setHasNewItems(bool(self.__collectionsSystem.getNewCollectionItemCount(collectionId)))

    @replaceNoneKwargsModel
    def __fillPagesBackgrounds(self, model=None):
        generalBg = self.__getContent(Group.BG, self.__collection.name, 'bgMain')
        if generalBg:
            model.setGeneralBackground(generalBg)
        pagesBackgroundsModels = model.getPagesBackgrounds()
        pagesBackgroundsModels.clear()
        for pbg in range(1, self.__pagesCount + 1):
            pageBackgroundsModel = PageBackgroundsModel()
            pageBg = self.__getContent(Group.BG, self.__collection.name, 'bgPage{}'.format(pbg), optionalContent=True)
            if pageBg:
                pageBackgroundsModel.setMain(pageBg)
            pagesBackgroundsModels.addViewModel(pageBackgroundsModel)

        pagesBackgroundsModels.invalidate()

    @replaceNoneKwargsModel
    def __clearContent(self, model=None):
        itemModels = model.getItems()
        itemModels.clear()
        itemModels.invalidate()
        pagesBackgroundsModels = model.getPagesBackgrounds()
        pagesBackgroundsModels.clear()
        pagesBackgroundsModels.invalidate()
        model.setGeneralBackground('')

    def __updateContentData(self):
        Waiting.show('loadContent')
        self.__collectionsSystem.cache.getImagesPaths(self.__generateContentData(), self.__onContentUpdated)

    def __generateContentData(self):
        contentIDs = [makeImageID(Group.BG, self.__collection.name, 'bgMain')]
        for pbgID in range(1, self.__pagesCount + 1):
            contentIDs.append(makeImageID(Group.BG, self.__collection.name, 'bgPage{}'.format(pbgID)))

        for item in self.__collection.items.itervalues():
            resKey = getItemResKey(self.__collection.collectionId, item)
            contentIDs.append(makeImageID(Group.ITEM, Sub.RECEIVED, resKey))
            contentIDs.append(makeImageID(Group.ITEM, Sub.UNRECEIVED, resKey))

        return contentIDs

    def __onContentUpdated(self, isOk, data):
        if isOk:
            self.__content = data
            with self.viewModel.transaction() as model:
                self.__fillPagesBackgrounds(model=model)
                self.__fillItems(model=model)
        else:
            self.viewModel.setIsError(True)
        Waiting.hide('loadContent')

    @replaceNoneKwargsModel
    def __updateCurrentNewItems(self, model=None):
        tabs = model.getTabs()
        for tab in tabs:
            if tab.getCollectionName() == self.__collection.name:
                tab.setHasNewItems(bool(self.__collectionsSystem.getNewCollectionItemCount(self.__collection.collectionId)))
                break

    @replaceNoneKwargsModel
    def __fillProgression(self, model=None):
        self.__fillProgressInfo(model=model)
        self.__fillRewardsInfo(model=model)

    @replaceNoneKwargsModel
    def __fillProgressInfo(self, model=None):
        collectionId = self.__collection.collectionId
        receivedItemsCount = self.__collectionsSystem.getReceivedProgressItemCount(collectionId)
        model.setReceivedItemsCount(receivedItemsCount)
        model.setPrevReceivedItemsCount(min(getShownNewItemsCount(collectionId), receivedItemsCount))
        model.setMaxItemsCount(self.__collectionsSystem.getMaxProgressItemCount(collectionId))

    @replaceNoneKwargsModel
    def __fillRewardsInfo(self, model=None):
        rewardItems = sorted(self.__collection.rewards.items(), key=lambda (reqCount, _): reqCount)
        rewardInfoModels = model.getRewardsInfo()
        rewardInfoModels.clear()
        self.__rewardTooltips.clear()
        self.__bonusData = []
        for requiredCount, rewards in rewardItems:
            rewardInfoModel = RewardInfoModel()
            rewardInfoModel.setRequiredItemsCount(requiredCount)
            rewardInfoModel.setState(self.__getRewardState(requiredCount))
            composedBonuses = composeBonuses([rewards])
            packBonusModelAndTooltipData(composedBonuses, rewardInfoModel.getRewards(), self.__rewardTooltips, getCollectionsBonusPacker())
            self.__bonusData.extend((bonus for bonus in composedBonuses if bonus.isShowInGUI()))
            rewardInfoModels.addViewModel(rewardInfoModel)

        rewardInfoModels.invalidate()

    def __getRewardState(self, requiredCount):
        if not self.__collectionsSystem.isRewardReceived(self.__collection.collectionId, requiredCount):
            return RewardState.UNRECEIVED
        return RewardState.JUSTRECEIVED if isRewardNew(self.__collection.collectionId, requiredCount) else RewardState.RECEIVED

    def __getItemState(self, itemId):
        if not self.__collectionsSystem.isItemReceived(self.__collection.collectionId, itemId):
            return ItemState.UNRECEIVED
        return ItemState.NEW if isItemNew(self.__collection.collectionId, itemId) else ItemState.RECEIVED

    def __onSetItemReceived(self, args):
        itemId = int(args.get('itemId'))
        setItemShown(self.__collection.collectionId, itemId)
        with self.viewModel.transaction() as model:
            self.__updateContentData()
            self.__updateCurrentNewItems(model=model)

    def __onSetRewardReceived(self, args):
        requiredCount = int(args.get('requiredItemsCount'))
        setRewardShown(self.__collection.collectionId, requiredCount)
        self.__fillRewardsInfo()

    def __onSetProgressItemsReceived(self):
        collectionId = self.__collection.collectionId
        setShownNewItemsCount(collectionId, self.__collectionsSystem.getReceivedProgressItemCount(collectionId))
        self.__fillProgression()

    @replaceNoneKwargsModel
    def __onFinishTutorial(self, model=None):
        collectionId = self.__collection.collectionId
        setCollectionTutorialCompleted(collectionId)
        model.setIsTutorial(not isTutorialCompleted(self.__collection.collectionId))

    def __onOpenItemPreview(self, args):
        itemId = int(args.get('itemId'))
        page = int(args.get('currentPage'))
        collectionId = self.__collection.collectionId
        showCollectionItemPreviewWindow(itemId, collectionId, page, self.__pagesCount, self.__backCallback, self.__backBtnText)

    def __onTabSelected(self, args):
        collectionName = args.get('collectionName')
        collection = self.__collectionsSystem.getCollectionByName(collectionName)
        if collection is not None:
            self.__collection = self.__collectionsSystem.getCollection(collection.collectionId)
            self.__rewardTooltips.clear()
            with self.viewModel.transaction() as model:
                self.__fillTabData(model=model)
                model.setPage(_INITIAL_PAGE)
        return

    @replaceNoneKwargsModel
    def __onBalanceUpdated(self, model=None):
        self.__updateContentData()
        self.__fillProgression(model=model)

    def __onSettingsChanged(self):
        if not self.__collectionsSystem.isEnabled():
            showHangar()
            self.destroyWindow()

    def __onClose(self):
        if callable(self.__backCallback) and isPlayerAccount():
            self.__backCallback()
        self.__backCallback = None
        self.destroyWindow()
        return

    def __getContent(self, group, sub, name, optionalContent=False):
        path = self.__content.get(group, {}).get(sub, {}).get(name, '')
        if not path and not optionalContent:
            _logger.warning('Resource: %s not found', '/'.join((group, sub, name)))
        return path

    def __onHeaderMenuClick(self, event):
        if event.ctx.get('alias') == VIEW_ALIAS.LOBBY_HANGAR:
            setHangarState()
        self.destroyWindow()


class CollectionWindow(LobbyWindow):
    __slots__ = ()

    def __init__(self, collectionId, page, backCallback, backBtnText, parent=None):
        super(CollectionWindow, self).__init__(WindowFlags.WINDOW, content=CollectionView(collectionId, backCallback, backBtnText, page), parent=parent)
