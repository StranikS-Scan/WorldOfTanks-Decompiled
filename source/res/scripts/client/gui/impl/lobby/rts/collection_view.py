# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/rts/collection_view.py
import logging
from account_helpers.AccountSettings import AccountSettings, RTS_LAST_COLLECTION_SEEN, RTS_LAST_ITEMS_SEEN
from frameworks.wulf import ViewFlags, ViewSettings
from gui.impl.backport import BackportTooltipWindow
from gui.impl.gen.view_models.views.lobby.rts.collection_view_model import CollectionViewModel
from gui.impl.gen.view_models.views.lobby.rts.meta_tab_model import Tabs
from gui.impl.pub import ViewImpl, ToolTipWindow
from gui.shared.missions.packers.bonus import packBonusModelAndTooltipData
from skeletons.gui.game_control import IRTSProgressionController, IRTSBattlesController
from helpers import dependency
from gui.impl.gen.view_models.views.lobby.rts.collection_item_model import CollectionItemModel
from gui.impl.gen.view_models.views.lobby.rts.progression_item_model import ProgressionItemModel
from gui.impl.lobby.rts.tooltips.tooltip_helpers import createRTSCurrencyTooltipView
from gui.impl.lobby.rts.rts_bonuses_packers import getRTSBonusPacker
from shared_utils import first
from gui.impl.gen import R
from gui.impl.lobby.rts.rts_i_tab_view import ITabView
from skeletons.gui.impl import IGuiLoader
_logger = logging.getLogger(__name__)

class RTSCollectionView(ViewImpl, ITabView):
    __slots__ = ('_tooltipItems', '__isGrowingAnimation')
    __progressionCtrl = dependency.descriptor(IRTSProgressionController)
    __rtsController = dependency.descriptor(IRTSBattlesController)

    def __init__(self, layoutID):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.LOBBY_SUB_VIEW
        settings.model = CollectionViewModel()
        self._tooltipItems = None
        self.__isGrowingAnimation = False
        self.__isShowing = False
        super(RTSCollectionView, self).__init__(settings)
        return

    @property
    def viewModel(self):
        return super(RTSCollectionView, self).getViewModel()

    def createToolTip(self, event):
        window = None
        tooltipID = event.getArgument('tooltipId', None)
        if tooltipID is None:
            _logger.warning('Expected TooltipID, none found.')
            return super(RTSCollectionView, self).createToolTip(event)
        else:
            tooltipID = int(tooltipID)
            contentID = event.contentID
            tooltipData = self._tooltipItems[tooltipID]
            _logger.debug('[RTS_COLLECTIONS_VIEW] createTooltip tooltipID %s contentID %s, ', tooltipID or '', contentID)
            if contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
                window = BackportTooltipWindow(tooltipData, self.getParentWindow())
            elif contentID == R.views.lobby.rts.StrategistCurrencyTooltip():
                arg = tooltipData.specialArgs[0]
                content = createRTSCurrencyTooltipView(contentID, arg)
                if content:
                    window = ToolTipWindow(event, content, self.getParentWindow())
                    window.move(event.mouse.positionX, event.mouse.positionY)
            if window is not None:
                window.load()
            return window

    def hasNewContent(self):
        previousProgress = AccountSettings.getSettings(RTS_LAST_COLLECTION_SEEN)
        currentProgress = self.__progressionCtrl.getCollectionProgress()
        return previousProgress != currentProgress

    def markSeen(self):
        currentProgress = self.__progressionCtrl.getCollectionProgress()
        AccountSettings.setSettings(RTS_LAST_COLLECTION_SEEN, currentProgress)

    def showTab(self):
        soundManager = self.__rtsController.getSoundManager()
        soundManager.onOpenCollectionsPage()
        self.__isShowing = True

    def hideTab(self):
        soundManager = self.__rtsController.getSoundManager()
        soundManager.onCloseCollectionsPage()
        if self.__isGrowingAnimation:
            soundManager.onCollectionProgressBarAnimation(False)
        self.__isShowing = False

    def _onLoading(self, *args, **kwargs):
        self.__updateViewModel()
        self.__addListeners()

    def _onLoaded(self, *args, **kwargs):
        soundManager = self.__rtsController.getSoundManager()
        soundManager.onOpenPage()

    def _finalize(self):
        self.__removeListeners()
        self._tooltipItems = None
        soundManager = self.__rtsController.getSoundManager()
        soundManager.onClosePage()
        soundManager.onCloseCollectionsPage()
        if self.__isGrowingAnimation:
            soundManager.onCollectionProgressBarAnimation(False)
        return

    def __updateViewModel(self):
        self._tooltipItems = {}
        collection = self.__progressionCtrl.getCollection()
        previousItemsSeen = AccountSettings.getSettings(RTS_LAST_ITEMS_SEEN)
        with self.viewModel.transaction() as model:
            collectionArray = model.getCollection()
            collectionArray.clear()
            itemsSeen, _ = self.__fillCollection(collection, collectionArray, previousItemsSeen, offset=0)
            collectionArray.invalidate()
            self.__fillProgression(model)
            AccountSettings.setSettings(RTS_LAST_ITEMS_SEEN, itemsSeen)

    def __fillProgression(self, model):
        previousProgress = AccountSettings.getSettings(RTS_LAST_COLLECTION_SEEN)
        currentProgress = self.__progressionCtrl.getCollectionProgress()
        totalProgress = self.__progressionCtrl.getCollectionSize()
        model.setPrevious(previousProgress)
        model.setCurrent(currentProgress)
        model.setTotal(totalProgress)
        progression = self.__progressionCtrl.getItemsProgression()
        progressionArray = model.getProgression()
        progressionArray.clear()
        for level, rewards in progression:
            item = ProgressionItemModel()
            item.setLevel(level)
            packBonusModelAndTooltipData(rewards, getRTSBonusPacker(), item.getRewards(), self._tooltipItems)
            progressionArray.addViewModel(item)

        progressionArray.invalidate()

    def __fillCollection(self, collection, model, previousItemsSeen, offset=0):
        model.clear()
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
            if tooltipId is not None:
                item.setTooltipId(str(tooltipId))
            item.setIsReceived(isReceived)
            item.setIsAnimated(isNew)
            model.addViewModel(item)

        return (itemsSeen, numItemsNew)

    @staticmethod
    def __makeTooltipData(bonus, tooltipData):
        tooltipIdx = None
        packer = getRTSBonusPacker()
        bonusTooltipList = packer.getToolTip(bonus)
        if bonusTooltipList:
            tooltipIdx = len(tooltipData)
            tooltipData[tooltipIdx] = first(bonusTooltipList)
        return tooltipIdx

    def __addListeners(self):
        self.viewModel.onProgressBarAnimation += self.__onProgressBarAnimation
        self.viewModel.onMissionClick += self.__onMissionClicked
        self.__progressionCtrl.onProgressUpdated += self.__updateViewModel
        self.__progressionCtrl.onUpdated += self.__onUpdated

    def __removeListeners(self):
        self.viewModel.onProgressBarAnimation -= self.__onProgressBarAnimation
        self.viewModel.onMissionClick -= self.__onMissionClicked
        self.__progressionCtrl.onProgressUpdated -= self.__updateViewModel
        self.__progressionCtrl.onUpdated -= self.__onUpdated

    def __onUpdated(self, *args, **kwargs):
        pass

    def __onMissionClicked(self):
        rootView = self.getParentView()
        if rootView is None:
            _logger.warning('[RTS_COLLECTIONS_VIEW] Failed to find root view.')
            return
        else:
            rootView.changeTab(Tabs.QUESTS.value)
            return

    def __onProgressBarAnimation(self, args):
        self.__isGrowingAnimation = args.get('shrink')
        if self.__canPlayProgressBarSound():
            soundManager = self.__rtsController.getSoundManager()
            soundManager.onCollectionProgressBarAnimation(self.__isGrowingAnimation)
        if not self.__isGrowingAnimation:
            self.__updateViewModel()

    def __canPlayProgressBarSound(self):
        guiLoader = dependency.instance(IGuiLoader)
        view = guiLoader.windowsManager.getViewByLayoutID(R.views.lobby.rts.RewardsView())
        return self.__isShowing and not self.__progressionCtrl.hasCurrentProgressRewards() and view is None
