# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/wt_event/wt_event_box_reward_view.py
from functools import partial
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags
from gui.impl import backport
from gui.impl.backport import createTooltipData
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.wt_event.wt_event_box_reward_view_model import WtEventBoxRewardViewModel
from gui.impl.lobby.wt_event import wt_event_sound
from gui.impl.pub import ViewImpl, WindowImpl
from gui.battle_pass.battle_pass_bonuses_packers import packBonusModelAndTooltipData
from gui.shared.event_dispatcher import showWtEventStorageBoxesWindow, showWtEventCollectionWindow, selectVehicleInHangar
from gui.shared.gui_items.Vehicle import getNationLessName
from gui.shared.utils.functions import makeTooltip
from gui.shop import showLootBoxBuyWindow
from gui.wt_event.wt_event_award import WTEventLootBoxAwardsManager
from gui.wt_event.wt_event_bonuses_packers import getWtEventBonusPacker
from gui.wt_event.wt_event_helpers import backportTooltipDecorator, vehCompCreateToolTipContentDecorator, COLLECTION_COLOR_FORMATTER
from helpers import dependency, isPlayerAccount
from skeletons.gui.game_control import IGameEventController
from skeletons.gui.impl import IGuiLoader
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.game_control import IEventLootBoxesController
from skeletons.gui.shared import IItemsCache
_WT_HUNTER_FULL_ID = 'wt_hunter'
_WT_BOSS_FULL_ID = 'wt_boss'

def _addFullCollectionTooltips(tooltipItems):
    tooltipItems[_WT_HUNTER_FULL_ID] = createTooltipData(makeTooltip(header=backport.text(R.strings.wt_event.collectionTooltip.hunterTitle()), body=backport.text(R.strings.wt_event.collectionTooltip.hunterFinalDescriptionWithColor()).format(**COLLECTION_COLOR_FORMATTER)))
    tooltipItems[_WT_BOSS_FULL_ID] = createTooltipData(makeTooltip(header=backport.text(R.strings.wt_event.collectionTooltip.tigerTitle()), body=backport.text(R.strings.wt_event.collectionTooltip.tigerFinalDescriptionWithColor()).format(**COLLECTION_COLOR_FORMATTER)))


class WtEventBoxRewardView(ViewImpl):
    __slots__ = ('__rewards', '_tooltipItems', '__lootBoxType', '__vehicleInRewards')
    __gameEventController = dependency.descriptor(IGameEventController)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __lootBoxesController = dependency.descriptor(IEventLootBoxesController)
    __itemsCache = dependency.descriptor(IItemsCache)
    __guiLoader = dependency.descriptor(IGuiLoader)

    def __init__(self, layoutID, rewards, lootBoxType):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.OVERLAY_VIEW
        settings.model = WtEventBoxRewardViewModel()
        self._tooltipItems = {}
        _addFullCollectionTooltips(self._tooltipItems)
        self.__rewards = rewards
        self.__lootBoxType = lootBoxType
        self.__vehicleInRewards = None
        super(WtEventBoxRewardView, self).__init__(settings)
        return

    @property
    def viewModel(self):
        return super(WtEventBoxRewardView, self).getViewModel()

    @vehCompCreateToolTipContentDecorator()
    def createToolTipContent(self, event, contentID):
        return super(WtEventBoxRewardView, self).createToolTipContent(event, contentID)

    @backportTooltipDecorator()
    def createToolTip(self, event):
        return super(WtEventBoxRewardView, self).createToolTip(event)

    def _onLoaded(self, *args, **kwargs):
        super(WtEventBoxRewardView, self)._onLoaded(self, *args, **kwargs)
        self.getParentWindow().bringToFront()
        wt_event_sound.playLootBoxRewardTape()

    def _onLoading(self, *args, **kwargs):
        super(WtEventBoxRewardView, self)._onLoading()
        openView = self.__getLootBoxOpenView()
        if openView is not None:
            openView.viewModel.setHasChildOverlay(True)
        with self.getViewModel().transaction() as model:
            if self.__lootBoxType == 'wt_special':
                model.setDescription(backport.text(R.strings.wt_event.boxReward.descriptionSpecial()))
                model.setIsSpecialBox(True)
            if self.__lootBoxType == 'wt_boss':
                model.setDescription(backport.text(R.strings.wt_event.boxReward.descriptionBoss()))
            if self.__lootBoxType == 'wt_hunter':
                model.setDescription(backport.text(R.strings.wt_event.boxReward.descriptionHunter()))
            model.setTitle(backport.text(R.strings.wt_event.boxReward.title()))
            model.setBoxId(self.__lootBoxType)
            self.__fillRewards(self.__rewards)
            self.__fillIsCollectionCollected()
            self.__updateLootBoxCount()
        return

    def _initialize(self, *args, **kwargs):
        super(WtEventBoxRewardView, self)._initialize(*args, **kwargs)
        self.__addListeners()

    def _finalize(self):
        self.__lootBoxesController.saveLastViewed()
        self.__removeListeners()
        openView = self.__getLootBoxOpenView()
        if openView is not None and isPlayerAccount():
            openView.resetLootBoxStates()
            openView.viewModel.setHasChildOverlay(False)
        super(WtEventBoxRewardView, self)._finalize()
        return

    def __addListeners(self):
        self.viewModel.onGoToStorage += self.__onGoToStorage
        self.viewModel.goToBuyBox += self.__goToBuyBox
        self.viewModel.goToCollection += self.__goToCollection
        self.viewModel.showHangar += self.__showHangar
        self.viewModel.onClose += self.__onClose
        self.__itemsCache.onSyncCompleted += self.__updateLootBoxCount

    def __removeListeners(self):
        self.viewModel.onGoToStorage -= self.__onGoToStorage
        self.viewModel.goToBuyBox -= self.__goToBuyBox
        self.viewModel.goToCollection -= self.__goToCollection
        self.viewModel.showHangar -= self.__showHangar
        self.viewModel.onClose -= self.__onClose
        self.__itemsCache.onSyncCompleted -= self.__updateLootBoxCount

    def __fillRewards(self, rewards):
        if not isinstance(rewards, list):
            rewards = [rewards]
        bonuses = WTEventLootBoxAwardsManager.composeBonuses(rewards)
        for bonus in bonuses:
            if bonus.getName() == 'vehicles':
                self.__fillVehicleRewards(bonuses)
                return
            if bonus.getName() == 'customizations' or bonus.getName() == 'crewSkins':
                self.__fillCollection(bonuses)
                return

        self.__fillCommonRewards(bonuses)

    def __fillVehicleRewards(self, allBonuses):
        vehicleBonuses = [ bonus for bonus in allBonuses if bonus.getName() == 'vehicles' ]
        vehicleBonus = vehicleBonuses[0]
        self.__vehicleInRewards, _ = vehicleBonus.getVehicles()[0]
        if vehicleBonus.checkIsCompensatedVehicle(self.__vehicleInRewards):
            self.__fillCommonRewards(allBonuses)
            return
        restBonuses = [ bonus for bonus in allBonuses if bonus.getName() != 'vehicles' ]
        packBonusModelAndTooltipData(vehicleBonuses, self.viewModel.rewards, self._tooltipItems, getWtEventBonusPacker)
        packBonusModelAndTooltipData(restBonuses, self.viewModel.additionalRewards, self._tooltipItems, getWtEventBonusPacker)
        self.viewModel.vehicle.setLevel(str(self.__vehicleInRewards.level))
        self.viewModel.vehicle.setType(self.__vehicleInRewards.type)
        self.viewModel.vehicle.setName(self.__vehicleInRewards.userName)
        self.viewModel.vehicle.setSpecName(getNationLessName(self.__vehicleInRewards.name))
        self.viewModel.setIsVehicleReward(True)

    def __fillCollection(self, allBonuses):
        self.viewModel.setIsCollectionItem(True)
        packBonusModelAndTooltipData(allBonuses, self.viewModel.rewards, self._tooltipItems, getWtEventBonusPacker)

    def __fillCommonRewards(self, allBonuses):
        packBonusModelAndTooltipData(allBonuses, self.viewModel.rewards, self._tooltipItems, partial(getWtEventBonusPacker, True))

    def __fillIsCollectionCollected(self):
        if self.__lootBoxType == _WT_HUNTER_FULL_ID:
            currentCount = self.__gameEventController.getHunterCollectedCount()
            collectionSize = self.__gameEventController.getHunterCollectionSize()
            self.viewModel.setIsCollectionCollected(currentCount == collectionSize)
        elif self.__lootBoxType == _WT_BOSS_FULL_ID:
            currentCount = self.__gameEventController.getBossCollectedCount()
            collectionSize = self.__gameEventController.getBossCollectionSize()
            self.viewModel.setIsCollectionCollected(currentCount == collectionSize)

    def __updateLootBoxCount(self, *_):
        self.viewModel.setBoxCount(self.__lootBoxesController.getEventLootBoxesCount())

    def __onGoToStorage(self):
        self.destroyWindow()
        openView = self.__getLootBoxOpenView()
        if openView is not None:
            openView.onGoToStorage()
        else:
            showWtEventStorageBoxesWindow()
        return

    def __onClose(self):
        wt_event_sound.playLootBoxRewardExit()
        if not self.__lootBoxesController.getEventLootBoxesCountByType(self.__lootBoxType):
            openView = self.__getLootBoxOpenView()
            if openView is not None:
                openView.doDestroy()
        self.destroyWindow()
        return

    def __goToBuyBox(self):
        showLootBoxBuyWindow()
        self.destroyWindow()

    def __goToCollection(self):
        showWtEventCollectionWindow()
        openView = self.__getLootBoxOpenView()
        if openView is not None:
            openView.doDestroy()
        self.destroyWindow()
        return

    def __showHangar(self):
        openView = self.__getLootBoxOpenView()
        if openView is not None:
            openView.doDestroy()
        self.destroyWindow()
        if self.__vehicleInRewards is not None:
            self.__gameEventController.runStandardHangarMode()
            selectVehicleInHangar(self.__vehicleInRewards.intCD)
        return

    def __getLootBoxOpenView(self):
        return self.__guiLoader.windowsManager.getViewByLayoutID(R.views.lobby.wt_event.WtEventLootboxOpenView())


class WtEventBoxRewardWindow(WindowImpl):
    __slots__ = ()

    def __init__(self, parent=None, rewards=None, lootBoxType=None):
        super(WtEventBoxRewardWindow, self).__init__(WindowFlags.WINDOW, content=WtEventBoxRewardView(R.views.lobby.wt_event.WtEventBoxRewardView(), rewards=rewards, lootBoxType=lootBoxType), parent=parent)
