# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/loot_box/loot_box_reward_view.py
import logging
import BigWorld
from account_helpers.settings_core import settings_constants
from adisp import process
from frameworks.wulf import ViewFlags, WindowFlags
from gui import SystemMessages
from gui.impl.backport_tooltip import BackportTooltipWindow, TooltipData
from gui.impl.gen.resources import R
from gui.impl.gen.view_models.views.loot_box_reward_view_model import LootBoxRewardViewModel
from gui.impl.gen.view_models.views.loot_box_view.loot_congrats_types import LootCongratsTypes
from gui.impl.lobby.loot_box.loot_box_helper import getLootboxRendererModelPresenter, getRewardTooltipContent
from gui.impl.lobby.loot_box.loot_box_helper import showLootBoxSpecialReward, fireHideRewardView, getLootboxBonuses
from gui.impl.lobby.loot_box.loot_box_helper import fireCloseToHangar, LootBoxShowHideCloseHandler
from gui.impl.lobby.loot_box.loot_box_helper import showStyledVehicleByStyleCD
from gui.impl.pub import LobbyWindow
from gui.impl.pub import ViewImpl
from gui.server_events.events_dispatcher import showRecruitWindow
from gui.shared import event_dispatcher
from gui.shared.event_dispatcher import selectVehicleInHangar
from gui.shared.gui_items.loot_box import NewYearLootBoxes
from gui.shared.gui_items.processors.loot_boxes import LootBoxOpenProcessor
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import IFestivityController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from gui.impl.lobby.loot_box.loot_box_sounds import onVideoStart, onVideoDone, LootBoxVideos
_logger = logging.getLogger(__name__)

class LootBoxRewardView(ViewImpl):
    itemsCache = dependency.descriptor(IItemsCache)
    settingsCore = dependency.descriptor(ISettingsCore)
    lobbyContext = dependency.descriptor(ILobbyContext)
    _festivityController = dependency.descriptor(IFestivityController)
    __slots__ = ('__rewards', '__boxItem', '__isVideoOff', '__items', '__showHideCloseHandler')

    def __init__(self, *args, **kwargs):
        super(LootBoxRewardView, self).__init__(R.views.lootBoxRewardView, ViewFlags.VIEW, LootBoxRewardViewModel, *args, **kwargs)
        self.__items = {}
        self.__rewards = {}
        self.__boxItem = None
        self.__isVideoOff = False
        self.__showHideCloseHandler = LootBoxShowHideCloseHandler()
        return

    @property
    def viewModel(self):
        return super(LootBoxRewardView, self).getViewModel()

    def createToolTip(self, event):
        if event.contentID == R.views.backportTooltipContent:
            tooltipId = event.getArgument('tooltipId')
            window = BackportTooltipWindow(self.__items[tooltipId], self.getParentWindow()) if tooltipId is not None else None
            if window is not None:
                window.load()
            return window
        else:
            return super(LootBoxRewardView, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        return getRewardTooltipContent(event)

    def _initialize(self, *args, **kwargs):
        super(LootBoxRewardView, self)._initialize()
        self.__showHideCloseHandler.startListen(self.getParentWindow())
        self.viewModel.onCloseBtnClick += self.__onWindowClose
        if args and len(args) > 1:
            self.__boxItem = args[0]
            self.__rewards = args[1]
            self.viewModel.onNextBtnClick += self.__onOpenNextBoxes
            self.viewModel.onVideoChangeClick += self.__onVideoChange
            self.viewModel.onDestroyEvent += self.__onDestroy
            self.viewModel.onVideoStarted += self.__onVideoStarted
            self.viewModel.onVideoStopped += self.__onVideoStopped
            self.viewModel.onReadyToRestart += self.__onReadyToRestart
            self.viewModel.showSpecialReward += self.__showSpecialReward
            self.viewModel.onBuyBoxBtnClick += self.__onBuyBoxBtnClick
            self.viewModel.onSpecialActionBtnClick += self.__onSpecialActionButtonClick
            self._festivityController.onStateChanged += self.__onStateChange
            self.itemsCache.onSyncCompleted += self.__onCacheResync
            self.settingsCore.onSettingsChanged += self.__updateVideoOff
            self.lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingChanged
            self.__isVideoOff = self.settingsCore.getSetting(settings_constants.GAME.LOOT_BOX_VIDEO_OFF)
            self.viewModel.setIsVideoOff(self.__isVideoOff)
            self.__update()
            self.__setRewards()
            self.__updateRestrictedMode()
            self.viewModel.setIsOpenVideoPlay(not self.__isVideoOff)
            self.viewModel.setIsVideoPlaying(not self.__isVideoOff)
            self.viewModel.setIsNextBtnEnabled(self.lobbyContext.getServerSettings().isLootBoxesEnabled())
            BigWorld.worldDrawEnabled(False)
        else:
            _logger.error('Rewards and boxItem is not specified!')
            self.viewModel.setHardReset(True)

    def _finalize(self):
        BigWorld.worldDrawEnabled(True)
        self.__showHideCloseHandler.stopListen()
        self.__showHideCloseHandler = None
        self.viewModel.onCloseBtnClick -= self.__onWindowClose
        self.viewModel.onNextBtnClick -= self.__onOpenNextBoxes
        self.viewModel.onVideoChangeClick -= self.__onVideoChange
        self.viewModel.onDestroyEvent -= self.__onDestroy
        self.viewModel.onVideoStarted -= self.__onVideoStarted
        self.viewModel.onVideoStopped -= self.__onVideoStopped
        self.viewModel.onReadyToRestart -= self.__onReadyToRestart
        self.viewModel.showSpecialReward -= self.__showSpecialReward
        self.viewModel.onBuyBoxBtnClick -= self.__onBuyBoxBtnClick
        self.viewModel.onSpecialActionBtnClick -= self.__onSpecialActionButtonClick
        self._festivityController.onStateChanged -= self.__onStateChange
        self.itemsCache.onSyncCompleted -= self.__onCacheResync
        self.settingsCore.onSettingsChanged -= self.__updateVideoOff
        self.lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingChanged
        self.__rewards.clear()
        self.__items.clear()
        super(LootBoxRewardView, self)._finalize()
        return

    def __onDestroy(self, _=None):
        self.destroyWindow()

    def __onWindowClose(self, _=None):
        fireHideRewardView()
        if self.viewModel.getHardReset():
            self.__onDestroy()
        else:
            self.viewModel.setFadeOut(True)

    def __onVideoStarted(self, _=None):
        if self.__boxItem is not None:
            sourceID = self.__boxItem.getType() if self.__boxItem.isFree() else self.__boxItem.getType() + '_' + self.__boxItem.getCategory()
            onVideoStart(LootBoxVideos.OPEN_BOX, sourceID)
        return

    def __onVideoStopped(self, _=None):
        if self.viewModel.getIsVideoPlaying():
            self.__stopVideoPlaying()
            onVideoDone()

    def __onVideoChange(self, _=None):
        self.__stopVideoPlaying()
        self.settingsCore.applySetting(settings_constants.GAME.LOOT_BOX_VIDEO_OFF, not self.__isVideoOff)

    def __stopVideoPlaying(self):
        self.viewModel.setIsVideoPlaying(False)

    def __showSpecialReward(self, responseDict):
        showLootBoxSpecialReward(responseDict)

    def __onSpecialActionButtonClick(self, responseDict):
        congratsType = responseDict.get('congratsType')
        congratsSourceId = responseDict.get('congratsSourceId')
        if congratsType is not None and congratsSourceId is not None:
            if congratsType == LootCongratsTypes.CONGRAT_TYPE_VEHICLE:
                selectVehicleInHangar(int(congratsSourceId))
                self.__closeToHangar()
            elif congratsType == LootCongratsTypes.CONGRAT_TYPE_STYLE:
                BigWorld.worldDrawEnabled(True)
                if congratsSourceId:
                    showStyledVehicleByStyleCD(int(congratsSourceId))
            elif congratsType == LootCongratsTypes.CONGRAT_TYPE_TANKMAN:
                showRecruitWindow(congratsSourceId)
                self.__closeToHangar()
        return

    @process
    def __onOpenNextBoxes(self, _=None):
        result = yield LootBoxOpenProcessor(self.__boxItem).request()
        if result:
            if result.userMsg:
                SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)
            if result.success:
                rewardsList = result.auxData
                if not rewardsList:
                    _logger.error('Lootbox is opened, but no rewards has been received.')
                    self.__onDestroy(None)
                else:
                    self.__rewards = rewardsList[0] if rewardsList else {}
                    self.viewModel.setOpenFadeOut(True)
            else:
                self.viewModel.setHardReset(True)
        else:
            self.viewModel.setHardReset(True)
        return

    def __onReadyToRestart(self, _=None):
        self.__update()
        self.__setRewards()
        with self.viewModel.transaction() as tx:
            tx.setIsVideoPlaying(not self.viewModel.getIsVideoOff())
            tx.setIsOpenVideoPlay(not self.viewModel.getIsVideoOff())
            tx.setOpenFadeOut(False)

    def __onCacheResync(self, *_):
        self.__update()

    def __update(self):
        isValidBox = False
        boxes = self.itemsCache.items.tokens.getLootBoxes().values()
        for box in boxes:
            if box == self.__boxItem:
                isValidBox = True
                break

        with self.viewModel.transaction() as tx:
            if isValidBox:
                tx.setLeftLootBoxes(self.__boxItem.getInventoryCount())
                tx.setBoxType(self.__boxItem.getType())
                tx.setBoxCategory(self.__boxItem.getCategory())
                tx.setIsFreeBox(self.__boxItem.isFree())
            else:
                tx.setLeftLootBoxes(0)
                _logger.warning('Lootbox %r is missing on Server!', self.__boxItem)

    def __updateVideoOff(self, diff):
        if settings_constants.GAME.LOOT_BOX_VIDEO_OFF in diff:
            self.__isVideoOff = diff[settings_constants.GAME.LOOT_BOX_VIDEO_OFF]
            self.viewModel.setIsVideoOff(self.__isVideoOff)

    def __setRewards(self):
        with self.getViewModel().transaction() as tx:
            rewardsList = tx.getRewards()
            rewardsList.clear()
            bonuses, specialRewardType = getLootboxBonuses(self.__rewards)
            for index, reward in enumerate(bonuses):
                formatter = getLootboxRendererModelPresenter(reward)
                rewardRender = formatter.getModel(reward, index)
                rewardsList.addViewModel(rewardRender)
                self.__items[index] = TooltipData(tooltip=reward.get('tooltip', None), isSpecial=reward.get('isSpecial', False), specialAlias=reward.get('specialAlias', ''), specialArgs=reward.get('specialArgs', None))

            rewardsList.invalidate()
            tx.setSpecialRewardType(specialRewardType)
        return

    def __onServerSettingChanged(self, diff):
        if 'lootBoxes_config' in diff:
            self.__update()
        self.__updateRestrictedMode()

    def __updateRestrictedMode(self):
        enabled = self.lobbyContext.getServerSettings().isLootBoxesEnabled()
        self.viewModel.setIsNextBtnEnabled(enabled)
        showGiftBtn = enabled and self.__boxItem is not None and self.__boxItem.getType() == NewYearLootBoxes.PREMIUM
        self.viewModel.setIsGiftBuyBtnVisible(showGiftBtn)
        return

    def __onStateChange(self):
        if not self._festivityController.isEnabled():
            self.destroyWindow()

    def __onBuyBoxBtnClick(self, _=None):
        event_dispatcher.showLootBoxBuyWindow()

    def __closeToHangar(self):
        fireCloseToHangar()

    def __handleCloseToHangar(self):
        fireHideRewardView()
        self.__onDestroy()


class LootBoxRewardWrapperWindow(LobbyWindow):
    __slots__ = ()

    def __init__(self, *args, **kwargs):
        super(LootBoxRewardWrapperWindow, self).__init__(content=LootBoxRewardView(*args, **kwargs), wndFlags=WindowFlags.OVERLAY, decorator=None)
        return

    def show(self):
        super(LootBoxRewardWrapperWindow, self).show()
        BigWorld.worldDrawEnabled(False)

    def hide(self):
        super(LootBoxRewardWrapperWindow, self).hide()
        BigWorld.worldDrawEnabled(True)
