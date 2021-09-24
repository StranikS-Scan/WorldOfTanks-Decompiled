# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/wt_event/wt_event_collection_view.py
import typing
import logging
import constants
from account_helpers.AccountSettings import AccountSettings, EVENT_LAST_COLLECTION_SEEN, EVENT_LAST_ITEMS_SEEN
from frameworks.wulf import ViewFlags, ViewSettings
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.header.LobbyHeader import HeaderMenuVisibilityState
from gui.Scaleform.Waiting import Waiting
from gui.battle_pass.battle_pass_bonuses_packers import packBonusModelAndTooltipData
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.wt_event.wt_event_collection_view_model import WtEventCollectionViewModel, Collection
from gui.impl.gen.view_models.views.lobby.wt_event.collection_item_model import CollectionItemModel
from gui.impl.gen.view_models.views.lobby.wt_event.progression_item_model import ProgressionItemModel
from gui.impl.lobby.wt_event import wt_event_sound
from gui.impl.pub import ViewImpl
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from gui.shared.event_dispatcher import showBrowserOverlayView
from gui.wt_event.wt_event_bonuses_packers import getWtEventBonusPacker
from gui.wt_event.wt_event_helpers import getDaysLeftFormatted, backportTooltipDecorator, getInfoPageURL
from helpers import dependency
from shared_utils import first
from skeletons.gui.game_control import IGameEventController
from skeletons.gui.app_loader import IAppLoader
from gui.Scaleform.framework.entities.View import ViewKey
if typing.TYPE_CHECKING:
    from gui.impl.wrappers.user_list_model import UserListModel
_logger = logging.getLogger(__name__)

class WTEventCollectionView(ViewImpl):
    __slots__ = ('_tooltipItems', '__isGrowingAnimation', '__itemsSeen', '__fromWelcome')
    __gameEventController = dependency.descriptor(IGameEventController)
    __appLoader = dependency.descriptor(IAppLoader)

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(layoutID=R.views.lobby.wt_event.WTEventCollections(), flags=ViewFlags.LOBBY_TOP_SUB_VIEW, model=WtEventCollectionViewModel())
        settings.args = args
        settings.kwargs = kwargs
        super(WTEventCollectionView, self).__init__(settings)
        self._tooltipItems = None
        self.__isGrowingAnimation = False
        self.__itemsSeen = {Collection.BOSS: 0,
         Collection.HUNTER: 0}
        self.__fromWelcome = kwargs.get('fromWelcome', False)
        return

    @property
    def viewModel(self):
        return super(WTEventCollectionView, self).getViewModel()

    @backportTooltipDecorator()
    def createToolTip(self, event):
        return super(WTEventCollectionView, self).createToolTip(event)

    def _onLoading(self, *args, **kwargs):
        if self.__fromWelcome:
            Waiting.show('loadContent')
        super(WTEventCollectionView, self)._onLoading()
        self.__updateViewModel()
        self.__addListeners()

    def _onLoaded(self, *args, **kwargs):
        super(WTEventCollectionView, self)._onLoaded(*args, **kwargs)
        if self.__fromWelcome:
            Waiting.hide('loadContent')
        wt_event_sound.playCollectionViewEnter()
        g_eventBus.handleEvent(events.LobbyHeaderMenuEvent(events.LobbyHeaderMenuEvent.TOGGLE_VISIBILITY, ctx={'state': HeaderMenuVisibilityState.NOTHING}), EVENT_BUS_SCOPE.LOBBY)

    def _finalize(self):
        self.__removeListeners()
        self._tooltipItems = None
        wt_event_sound.playCollectionViewExit()
        if self.__isGrowingAnimation:
            wt_event_sound.playProgressBarGrowing(False)
        g_eventBus.handleEvent(events.LobbyHeaderMenuEvent(events.LobbyHeaderMenuEvent.TOGGLE_VISIBILITY, ctx={'state': HeaderMenuVisibilityState.ALL}), EVENT_BUS_SCOPE.LOBBY)
        super(WTEventCollectionView, self)._finalize()
        return

    def __updateViewModel(self):
        self._tooltipItems = {}
        hunterCollection = self.__gameEventController.getHunterCollection()
        bossCollection = self.__gameEventController.getBossCollection()
        previousItemsSeen = AccountSettings.getSettings(EVENT_LAST_ITEMS_SEEN)
        previousBossSeen = previousItemsSeen >> len(hunterCollection)
        with self.viewModel.transaction() as model:
            model.setIsCN(constants.IS_CHINA)
            hunterItemsSeen, numHunterItemsNew = self.__fillCollection(hunterCollection, model.hunterCollection, previousItemsSeen, offset=0)
            bossItemsSeen, numBossItemsNew = self.__fillCollection(bossCollection, model.bossCollection, previousBossSeen, offset=len(hunterCollection))
            self.__fillProgression(model)
            model.setHunterNew(numHunterItemsNew)
            model.setBossNew(numBossItemsNew)
            self.__itemsSeen.update({Collection.HUNTER: hunterItemsSeen,
             Collection.BOSS: bossItemsSeen})

    def __fillProgression(self, model):
        model.progression.clearItems()
        previousCommonProgress = AccountSettings.getSettings(EVENT_LAST_COLLECTION_SEEN)
        hunterCurrentProgress = self.__gameEventController.getHunterCollectionProgress()
        hunterTotalProgress = self.__gameEventController.getHunterCollectionSize()
        bossCurrentProgress = self.__gameEventController.getBossCollectionProgress()
        bossTotalProgress = self.__gameEventController.getBossCollectionSize()
        model.setPreviousCommon(previousCommonProgress)
        model.setCommonCurrent(hunterCurrentProgress + bossCurrentProgress)
        model.setCommonTotal(hunterTotalProgress + bossTotalProgress)
        model.setHunterCurrent(hunterCurrentProgress)
        model.setHunterTotal(hunterTotalProgress)
        model.setBossCurrent(bossCurrentProgress)
        model.setBossTotal(bossTotalProgress)
        model.setDaysLeft(getDaysLeftFormatted(gameEventController=self.__gameEventController))
        AccountSettings.setSettings(EVENT_LAST_COLLECTION_SEEN, hunterCurrentProgress + bossCurrentProgress)
        progression = self.__getItemsProgression()
        for level, rewards in progression:
            item = ProgressionItemModel()
            item.setLevel(level)
            packBonusModelAndTooltipData(rewards, item.rewards, self._tooltipItems, getWtEventBonusPacker)
            model.progression.addViewModel(item)

    def __getItemsProgression(self):
        result = [(0, {})]
        for data in self.__gameEventController.getConfig().progression:
            rewards = self.__gameEventController.getQuestRewards(data.get('quest', ''))
            result.append((data.get('itemsCount', 0), rewards))

        return result

    def __fillCollection(self, collection, model, previousItemsSeen, offset=0):
        model.clearItems()
        itemsSeen = 0
        numItemsNew = 0
        for bonusId, bonus in enumerate(collection):
            bonusId = bonusId + offset
            tooltipId = self.__makeTooltipData(bonus, self._tooltipItems)
            isReceived = bonus.isReceived()
            currentFlag = 1 << bonusId
            itemsSeen |= currentFlag if isReceived else 0
            isNew = isReceived and not bool(previousItemsSeen & currentFlag)
            numItemsNew += 1 if isNew else 0
            item = CollectionItemModel()
            item.setBonusId(str(bonusId))
            item.setTooltipId(tooltipId)
            item.setIsReceived(isReceived)
            item.setIsAnimated(isNew)
            model.addViewModel(item)

        return (itemsSeen, numItemsNew)

    @staticmethod
    def __makeTooltipData(bonus, tooltipData):
        tooltipIdx = ''
        packer = getWtEventBonusPacker()
        bonusTooltipList = packer.getToolTip(bonus)
        if bonusTooltipList:
            tooltipIdx = str(len(tooltipData))
            tooltipData[tooltipIdx] = first(bonusTooltipList)
        return tooltipIdx

    @staticmethod
    def __onInfoPageOpen():
        showBrowserOverlayView(getInfoPageURL(), VIEW_ALIAS.BROWSER_OVERLAY)

    def __addListeners(self):
        self.__gameEventController.onEventPrbChanged += self.__onEventPrbChanged
        self.__gameEventController.onProgressUpdated += self.__updateViewModel
        self.viewModel.onInfoPageOpen += self.__onInfoPageOpen
        self.viewModel.onProgressBarAnimation += self.__onProgressBarAnimation
        self.viewModel.onCollectionVisit += self.__onCollectionVisit
        self.viewModel.onAnimationStart += self.__onAnimationStart

    def __removeListeners(self):
        self.__gameEventController.onProgressUpdated -= self.__updateViewModel
        self.viewModel.onInfoPageOpen -= self.__onInfoPageOpen
        self.__gameEventController.onEventPrbChanged -= self.__onEventPrbChanged
        self.viewModel.onProgressBarAnimation -= self.__onProgressBarAnimation
        self.viewModel.onCollectionVisit -= self.__onCollectionVisit
        self.viewModel.onAnimationStart -= self.__onAnimationStart

    def __onEventPrbChanged(self, isActive):
        self.__checkAndCloseBrowserView()
        if not isActive:
            self.destroyWindow()

    def __onProgressBarAnimation(self, args):
        self.__isGrowingAnimation = args.get('shrink')
        wt_event_sound.playProgressBarGrowing(self.__isGrowingAnimation)

    def __onCollectionVisit(self, args):
        collection = args['collection']
        hunterCollection = self.__gameEventController.getHunterCollection()
        newItemsSeen = prevItemsSeen = AccountSettings.getSettings(EVENT_LAST_ITEMS_SEEN)
        prevHunterSeen = prevItemsSeen & (1 << len(hunterCollection)) - 1
        prevBossSeen = prevItemsSeen >> len(hunterCollection)
        newHunterSeen = self.__itemsSeen[Collection.HUNTER]
        newBossSeen = self.__itemsSeen[Collection.BOSS]
        if collection == Collection.BOSS.value:
            newItemsSeen = prevHunterSeen + (newBossSeen << len(hunterCollection))
            self.viewModel.setBossNew(0)
        elif collection == Collection.HUNTER.value:
            newItemsSeen = newHunterSeen + (prevBossSeen << len(hunterCollection))
            self.viewModel.setHunterNew(0)
        AccountSettings.setSettings(EVENT_LAST_ITEMS_SEEN, newItemsSeen)

    def __onAnimationStart(self, args):
        tooltipId = args['tooltipId']
        collection = args['collection']

        def _findPredicate(item):
            return item.getTooltipId() == tooltipId

        if collection == Collection.BOSS.value:
            model = self.viewModel.bossCollection
        else:
            model = self.viewModel.hunterCollection
        for item in model.findItems(_findPredicate):
            if item:
                item.setIsAnimated(False)

    def __checkAndCloseBrowserView(self):
        app = self.__appLoader.getApp()
        if app is None:
            return
        else:
            view = app.containerManager.getViewByKey(ViewKey(VIEW_ALIAS.BROWSER_OVERLAY))
            if view is None:
                return
            view.destroy()
            return
