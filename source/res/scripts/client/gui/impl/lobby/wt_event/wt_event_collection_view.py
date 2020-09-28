# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/wt_event/wt_event_collection_view.py
import typing
from account_helpers.AccountSettings import AccountSettings, WT_EVENT_LAST_COLLECTION_SEEN, WT_EVENT_LAST_ITEMS_SEEN
from frameworks.wulf import ViewFlags, WindowFlags, ViewSettings
from gui.Scaleform.Waiting import Waiting
from gui.battle_pass.battle_pass_award import awardsFactory
from gui.battle_pass.battle_pass_bonuses_packers import packBonusModelAndTooltipData
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.wt_event.wt_event_collection_view_model import WtEventCollectionViewModel
from gui.impl.gen.view_models.views.lobby.wt_event.collection_item_model import CollectionItemModel
from gui.impl.gen.view_models.views.lobby.wt_event.progression_item_model import ProgressionItemModel
from gui.impl.lobby.wt_event import wt_event_sound
from gui.impl.pub import ViewImpl, WindowImpl
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.event_dispatcher import showBrowserOverlayView
from gui.shared.events import HangarVehicleEvent
from gui.wt_event.wt_event_bonuses_packers import getWtEventBonusPacker
from gui.wt_event.wt_event_helpers import getDaysLeftFormatted, backportTooltipDecorator, getInfoPageURL
from helpers import dependency
from shared_utils import first
from skeletons.gui.game_control import IGameEventController
if typing.TYPE_CHECKING:
    from gui.impl.wrappers.user_list_model import UserListModel

class WTEventCollectionView(ViewImpl):
    __slots__ = ('_tooltipItems', '__fromWelcome', '__isGrowingAnimation')
    __gameEventController = dependency.descriptor(IGameEventController)

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(layoutID=R.views.lobby.wt_event.WTEventCollections(), flags=ViewFlags.LOBBY_TOP_SUB_VIEW, model=WtEventCollectionViewModel())
        settings.args = args
        settings.kwargs = kwargs
        super(WTEventCollectionView, self).__init__(settings)
        self._tooltipItems = None
        self.__fromWelcome = kwargs.get('fromWelcome', False)
        self.__isGrowingAnimation = False
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
        wt_event_sound.playCollectionViewEnter()
        if self.__fromWelcome:
            Waiting.hide('loadContent')
        g_eventBus.handleEvent(HangarVehicleEvent(HangarVehicleEvent.WT_EVENT_COLLECTION_VIEW_LOADED, ctx={}), EVENT_BUS_SCOPE.LOBBY)

    def _finalize(self):
        self.__removeListeners()
        self._tooltipItems = None
        wt_event_sound.playCollectionViewExit()
        if self.__isGrowingAnimation:
            wt_event_sound.playProgressBarGrowing(False)
        g_eventBus.handleEvent(HangarVehicleEvent(HangarVehicleEvent.HERO_TANK_MARKER, ctx={'isDisable': False}), EVENT_BUS_SCOPE.LOBBY)
        if self.__fromWelcome:
            self.__gameEventController.onEventWelcomeCollectionScreensClosed()
        super(WTEventCollectionView, self)._finalize()
        return

    def __updateViewModel(self):
        self._tooltipItems = {}
        hunterCollection = self.__gameEventController.getHunterCollection()
        bossCollection = self.__gameEventController.getBossCollection()
        previousItemsSeen = AccountSettings.getSettings(WT_EVENT_LAST_ITEMS_SEEN)
        previousBossSeen = previousItemsSeen >> len(hunterCollection)
        with self.viewModel.transaction() as model:
            hunterItemsSeen = self.__fillCollection(hunterCollection, model.hunterCollection, previousItemsSeen)
            bossItemsSeen = self.__fillCollection(bossCollection, model.bossCollection, previousBossSeen)
            self.__fillProgression(model)
            newItemsSeen = hunterItemsSeen + (bossItemsSeen << len(hunterCollection))
            AccountSettings.setSettings(WT_EVENT_LAST_ITEMS_SEEN, newItemsSeen)

    def __fillProgression(self, model):
        model.progression.clearItems()
        previousCommonProgress = AccountSettings.getSettings(WT_EVENT_LAST_COLLECTION_SEEN)
        progression = self.__gameEventController.getItemProgression()
        hunterCurrentProgress = self.__gameEventController.getHunterCollectedCount()
        hunterTotalProgress = self.__gameEventController.getHunterCollectionSize()
        bossCurrentProgress = self.__gameEventController.getBossCollectedCount()
        bossTotalProgress = self.__gameEventController.getBossCollectionSize()
        model.setPreviousCommon(previousCommonProgress)
        model.setCommonCurrent(hunterCurrentProgress + bossCurrentProgress)
        model.setCommonTotal(hunterTotalProgress + bossTotalProgress)
        model.setHunterCurrent(hunterCurrentProgress)
        model.setHunterTotal(hunterTotalProgress)
        model.setBossCurrent(bossCurrentProgress)
        model.setBossTotal(bossTotalProgress)
        model.setDaysLeft(getDaysLeftFormatted(gameEventController=self.__gameEventController))
        AccountSettings.setSettings(WT_EVENT_LAST_COLLECTION_SEEN, hunterCurrentProgress + bossCurrentProgress)
        for level, bonuses in progression:
            item = ProgressionItemModel()
            item.setLevel(level)
            packBonusModelAndTooltipData(bonuses, item.rewards, self._tooltipItems, getWtEventBonusPacker)
            model.progression.addViewModel(item)

    def __fillCollection(self, collection, model, previousItemsSeen):
        model.clearItems()
        itemsSeen = 0
        for bonusId, bonus in collection.iteritems():
            tooltipId = self.__makeTooltipData(bonus, self._tooltipItems)
            isReceived = self.__gameEventController.hasItem(bonus)
            currentFlag = 1 << bonusId
            itemsSeen |= currentFlag if isReceived else 0
            isNew = isReceived and not bool(previousItemsSeen & currentFlag)
            item = CollectionItemModel()
            item.setBonusId(str(bonusId))
            item.setTooltipId(tooltipId)
            item.setIsReceived(isReceived)
            item.setIsAnimated(isNew)
            model.addViewModel(item)

        return itemsSeen

    @staticmethod
    def __makeTooltipData(reward, tooltipData):
        bonus = first(awardsFactory(reward))
        tooltipIdx = ''
        packer = getWtEventBonusPacker()
        bonusTooltipList = packer.getToolTip(bonus)
        if bonusTooltipList:
            tooltipIdx = str(len(tooltipData))
            tooltipData[tooltipIdx] = first(bonusTooltipList)
        return tooltipIdx

    @staticmethod
    def __onInfoPageOpen():
        showBrowserOverlayView(getInfoPageURL())

    def __addListeners(self):
        self.__gameEventController.onEventPrbChanged += self.__onEventPrbChanged
        self.__gameEventController.onProgressUpdated += self.__updateViewModel
        self.viewModel.onInfoPageOpen += self.__onInfoPageOpen
        self.viewModel.onProgressBarAnimation += self.__onProgressBarAnimation

    def __removeListeners(self):
        self.__gameEventController.onProgressUpdated -= self.__updateViewModel
        self.viewModel.onInfoPageOpen -= self.__onInfoPageOpen
        self.__gameEventController.onEventPrbChanged -= self.__onEventPrbChanged
        self.viewModel.onProgressBarAnimation -= self.__onProgressBarAnimation

    def __onEventPrbChanged(self, isActive):
        if not isActive:
            self.destroyWindow()

    def __onProgressBarAnimation(self, args):
        self.__isGrowingAnimation = args.get('shrink')
        wt_event_sound.playProgressBarGrowing(self.__isGrowingAnimation)


class WTEventCollectionWindow(WindowImpl):
    __slots__ = ()

    def __init__(self, parent=None):
        super(WTEventCollectionWindow, self).__init__(WindowFlags.WINDOW, content=WTEventCollectionView(), parent=parent)
