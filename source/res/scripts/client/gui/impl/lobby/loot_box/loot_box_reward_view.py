# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/loot_box/loot_box_reward_view.py
import copy
import logging
from functools import partial
from account_helpers.settings_core.settings_constants import NewYearStorageKeys
from gui.impl.lobby.new_year.tooltips.ny_shards_tooltip import NyShardsTooltip
from shared_utils import first
from adisp import process
from frameworks.wulf import ViewFlags, ViewSettings, WindowFlags, WindowLayer
from gifts.gifts_common import GiftEventID
from gui import SystemMessages
from gui.clans.formatters import getClanAbbrevString
from gui.gift_system.constants import HubUpdateReason
from gui.gift_system.mixins import GiftEventHubWatcher
from gui.impl.auxiliary.rewards_helper import getBackportTooltipData
from gui.impl.backport import BackportTooltipWindow
from gui.impl.backport import TooltipData
from gui.impl.gen.resources import R
from gui.impl.gen.view_models.views.lobby.lootboxes.loot_box_reward_view_model import LootBoxRewardViewModel
from gui.impl.gen.view_models.views.loot_box_view.loot_congrats_types import LootCongratsTypes
from gui.impl.lobby.loot_box.loot_box_bonuses_helpers import getEpicFormattedLootboxBonuses, AWARDS_MAX_COUNT
from gui.impl.lobby.loot_box.loot_box_helper import fireCloseToHangar
from gui.impl.lobby.loot_box.loot_box_helper import fireHideRewardView
from gui.impl.lobby.loot_box.loot_box_helper import getLootboxRendererModelPresenter, getTooltipContent, isLootboxValid, LootBoxHideableView
from gui.impl.lobby.loot_box.loot_box_helper import showLootBoxSpecialReward, setGaranteedRewardData
from gui.impl.lobby.loot_box.loot_box_helper import showStyledVehicleByStyleCD
from gui.impl.lobby.loot_box.loot_box_sounds import setOverlayHangarGeneral
from gui.impl.lobby.new_year.popovers.ny_loot_box_statistics_popover import NyLootBoxStatisticsPopover
from gui.impl.new_year.new_year_helper import getGiftSystemCongratulationText
from gui.impl.pub.lobby_window import LobbyNotificationWindow
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.server_events.events_dispatcher import showRecruitWindow
from gui.shared import event_dispatcher, g_eventBus, EVENT_BUS_SCOPE, events
from gui.shared.events import LootboxesEvent
from gui.shared.gui_items.loot_box import NewYearLootBoxes
from gui.shared.gui_items.processors.loot_boxes import LootBoxOpenProcessor
from gui.shared.view_helpers import UsersInfoHelper
from helpers import dependency, uniprof
from realm import CURRENT_REALM
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import IFestivityController, IGiftSystemController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from uilogging.ny.loggers import NyLootBoxesRewardsFlowLogger, NyStatisticsPopoverLogger
_logger = logging.getLogger(__name__)

class _StateKeeper(object):
    __slots__ = ('__fields', '__fieldsNames')

    def __init__(self, fieldsNames):
        self.__fieldsNames = fieldsNames
        self.__fields = {}

    @property
    def hasData(self):
        return bool(self.__fields)

    def preserve(self, obj):
        for attrName, shouldBeCopied in self.__fieldsNames.iteritems():
            value = getattr(obj, attrName)
            self.__fields[attrName] = copy.copy(value) if shouldBeCopied else value

    def restore(self, obj):
        for attrName in self.__fields:
            setattr(obj, attrName, self.__fields[attrName])

    def clear(self):
        self.__fields = {}


class LootBoxRewardView(LootBoxHideableView, GiftEventHubWatcher, UsersInfoHelper):
    itemsCache = dependency.descriptor(IItemsCache)
    settingsCore = dependency.descriptor(ISettingsCore)
    lobbyContext = dependency.descriptor(ILobbyContext)
    festivityController = dependency.descriptor(IFestivityController)
    __giftsController = dependency.descriptor(IGiftSystemController)
    __flowLogger = NyLootBoxesRewardsFlowLogger()
    __popoverLogger = NyStatisticsPopoverLogger()
    __slots__ = ('__rewards', '__boxItem', '__tooltips', '__isBackward', '__showSpecialRewardFunc', '__boxID', '__lastStatisticsResetFailed', '__isGuaranteedReward', '__giftsInfo')
    _GIFT_EVENT_ID = GiftEventID.NY_HOLIDAYS
    __stateKeeper = _StateKeeper({'_LootBoxRewardView__rewards': True,
     '_LootBoxRewardView__boxItem': False})

    def __init__(self, boxItem, rewards, isBackward=False, lastStatisticsResetFailed=None, isGuaranteedReward=False, giftsInfo=None):
        settings = ViewSettings(R.views.lobby.new_year.LootBoxRewardViewGf(), flags=ViewFlags.NON_REARRANGE_VIEW, model=LootBoxRewardViewModel())
        super(LootBoxRewardView, self).__init__(settings)
        self.__isBackward = isBackward
        self.__boxItem = boxItem
        self.__rewards = rewards
        self.__isGuaranteedReward = isGuaranteedReward
        self.__giftsInfo = giftsInfo
        if self.__isBackward and self.__stateKeeper.hasData:
            self.__stateKeeper.restore(self)
        else:
            self.__stateKeeper.clear()
        if boxItem is not None:
            self.__boxID = boxItem.getID()
        self.__lastStatisticsResetFailed = lastStatisticsResetFailed
        self.__tooltips = {}
        self.__showSpecialRewardFunc = None
        return

    @property
    def viewModel(self):
        return super(LootBoxRewardView, self).getViewModel()

    @property
    def isVideoOff(self):
        return self.settingsCore.getSetting(NewYearStorageKeys.LOOT_BOX_VIDEO_OFF)

    def createPopOverContent(self, event):
        if event.contentID == R.views.lobby.new_year.popovers.NyLootBoxStatisticsPopover():
            self.__popoverLogger.logClickInSingleOpen()
            return NyLootBoxStatisticsPopover(self.__boxID, self.__lastStatisticsResetFailed)
        return super(LootBoxRewardView, self).createPopOverContent(event)

    def createToolTip(self, event):
        if event.contentID == R.views.common.tooltip_window.backport_tooltip_content.BackportTooltipContent():
            tooltipId = event.getArgument('tooltipId')
            if tooltipId is None:
                return
            window = BackportTooltipWindow(self.__tooltips[tooltipId], self.getParentWindow())
            window.load()
            return window
        else:
            return super(LootBoxRewardView, self).createToolTip(event)

    @uniprof.regionDecorator(label='ny.lootbox.tooltip', scope='wrap')
    def createToolTipContent(self, event, contentID):
        if contentID == R.views.lobby.new_year.tooltips.NyShardsTooltip():
            return NyShardsTooltip()
        tooltipData = getBackportTooltipData(event, self.__tooltips)
        return getTooltipContent(event, tooltipData)

    def onUserNamesReceived(self, names):
        if self.__giftsInfo:
            spaID = self.__giftsInfo[0].senderID
            if spaID in names:
                self.__invalidateGiftSenderName(names[spaID], self.getUserClanAbbrev(spaID))

    @uniprof.regionDecorator(label='ny.lootbox.open', scope='enter')
    def _initialize(self, *args, **kwargs):
        super(LootBoxRewardView, self)._initialize()
        self.catchGiftEventHub()
        self.viewModel.onCloseBtnClick += self.__onWindowClose
        self.viewModel.onNextBtnClick += self.__onOpenNextBox
        self.viewModel.onVideoChangeClick += self.__onVideoSettingsChanged
        self.viewModel.onDestroyEvent += self.__onDestroy
        self.viewModel.showSpecialReward += self.__showSpecialReward
        self.viewModel.onBuyBoxBtnClick += self.__onBuyBoxBtnClick
        self.viewModel.onSpecialActionBtnClick += self.__onSpecialActionButtonClick
        self.viewModel.guaranteedReward.onInfoClick += self.__onGuaranteedRewardsInfo
        self.festivityController.onStateChanged += self.__onStateChange
        self.itemsCache.onSyncCompleted += self.__onCacheResync
        self.settingsCore.onSettingsChanged += self.__onSettingsChanged
        self.lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingChanged
        if not self._isMemoryRiskySystem:
            g_eventBus.addListener(LootboxesEvent.ON_SHOW_SPECIAL_REWARDS_CLOSED, self.__onSpecialRewardsClosed, scope=EVENT_BUS_SCOPE.LOBBY)
        if self._isMemoryRiskySystem:
            g_eventBus.addListener(LootboxesEvent.ON_VIDEO_OFF_MOVIE_LOADED, self.__onVideoOffMovieLoaded, scope=EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.addListener(LootboxesEvent.ON_OPENING_START, self.__onOpeningStart, scope=EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.addListener(LootboxesEvent.NEED_SHOW_REWARDS, self.__needShowRewards, scope=EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.addListener(events.LootboxesEvent.ON_STATISTICS_RESET, self.__onStatisticsReset, scope=EVENT_BUS_SCOPE.LOBBY)
        self.__updateAvailability()
        self.__updateBoxInfo()
        self.__updateRewards()
        g_eventBus.handleEvent(events.LootboxesEvent(events.LootboxesEvent.ON_OPEN_LOOTBOX, ctx={'boxItem': self.__boxItem,
         'specialRewardType': self.viewModel.getSpecialRewardType(),
         'withReload': False,
         'isForcedToEnd': self.__isBackward}), EVENT_BUS_SCOPE.LOBBY)
        with self.viewModel.transaction() as model:
            model.setIsForcedRendering(self.__isBackward)
            model.setIsVideoOff(self.isVideoOff)
            model.setIsMemoryRiskySystem(self._isMemoryRiskySystem)
            model.setRealm(CURRENT_REALM)

    def _onLoaded(self, *args, **kwargs):
        super(LootBoxRewardView, self)._onLoaded()
        self.getParentWindow().bringToFront()

    @uniprof.regionDecorator(label='ny.lootbox.open', scope='exit')
    def _finalize(self):
        setOverlayHangarGeneral(False)
        self.releaseGiftEventHub()
        self.viewModel.onCloseBtnClick -= self.__onWindowClose
        self.viewModel.onNextBtnClick -= self.__onOpenNextBox
        self.viewModel.onVideoChangeClick -= self.__onVideoSettingsChanged
        self.viewModel.onDestroyEvent -= self.__onDestroy
        self.viewModel.showSpecialReward -= self.__showSpecialReward
        self.viewModel.onBuyBoxBtnClick -= self.__onBuyBoxBtnClick
        self.viewModel.onSpecialActionBtnClick -= self.__onSpecialActionButtonClick
        self.viewModel.guaranteedReward.onInfoClick -= self.__onGuaranteedRewardsInfo
        self.festivityController.onStateChanged -= self.__onStateChange
        self.itemsCache.onSyncCompleted -= self.__onCacheResync
        self.settingsCore.onSettingsChanged -= self.__onSettingsChanged
        self.lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingChanged
        if not self._isMemoryRiskySystem:
            g_eventBus.removeListener(LootboxesEvent.ON_SHOW_SPECIAL_REWARDS_CLOSED, self.__onSpecialRewardsClosed, scope=EVENT_BUS_SCOPE.LOBBY)
        if self._isMemoryRiskySystem:
            g_eventBus.removeListener(LootboxesEvent.ON_VIDEO_OFF_MOVIE_LOADED, self.__onVideoOffMovieLoaded, scope=EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.removeListener(LootboxesEvent.ON_OPENING_START, self.__onOpeningStart, scope=EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.removeListener(LootboxesEvent.NEED_SHOW_REWARDS, self.__needShowRewards, scope=EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.removeListener(events.LootboxesEvent.ON_STATISTICS_RESET, self.__onStatisticsReset, scope=EVENT_BUS_SCOPE.LOBBY)
        if self._isMemoryRiskySystem:
            self.__stateKeeper.preserve(self)
        self.__rewards.clear()
        self.__tooltips.clear()
        self.__giftsInfo = None
        super(LootBoxRewardView, self)._finalize()
        return

    def _getVideosList(self):
        return ['lootboxes/opening/Christmas.usm',
         'lootboxes/opening/Fairytale.usm',
         'lootboxes/opening/free.usm',
         'lootboxes/opening/NewYear.usm',
         'lootboxes/opening/Oriental.usm',
         'lootboxes/opening/idles/Christmas.usm',
         'lootboxes/opening/idles/Fairytale.usm',
         'lootboxes/opening/idles/free.usm',
         'lootboxes/opening/idles/NewYear.usm',
         'lootboxes/opening/idles/Oriental.usm'] if self._isMemoryRiskySystem else []

    def _onGiftHubUpdate(self, reason, _=None):
        if reason == HubUpdateReason.SETTINGS:
            self.__updateBoxInfo()

    def __onStatisticsReset(self, event):
        self.__lastStatisticsResetFailed = event.ctx['serverError']

    def __onDestroy(self, _=None):
        if self._isMemoryRiskySystem:
            if not self._isCanClose:
                return
            self._startFade(self.__showEntryAndDestroy, withPause=True)
        else:
            self.destroyWindow()

    def __showEntryAndDestroy(self):
        event_dispatcher.showLootBoxEntry(category=self.__boxItem.getCategory(), lootBoxType=self.__boxItem.getType())
        self.destroyWindow()

    def __onWindowClose(self, _=None):
        if not self._isMemoryRiskySystem:
            fireHideRewardView()
        self.__onDestroy()

    def __onOpeningStart(self, _=None):
        if self._isMemoryRiskySystem:
            self.__sendRemoveHideView()
        self.viewModel.setIsOpening(True)

    def __needShowRewards(self, _=None):
        isVideoSkipped = self.__isBackward or self.isVideoOff
        if self._isMemoryRiskySystem and isVideoSkipped:
            self.__sendRemoveHideView()
        self.viewModel.setIsOpening(False)

    def __onVideoSettingsChanged(self, _=None):
        self.settingsCore.applySetting(NewYearStorageKeys.LOOT_BOX_VIDEO_OFF, not self.isVideoOff)

    def __showSpecialReward(self, responseDict):
        if self._isMemoryRiskySystem and self.__isBackward:
            return
        if self._isMemoryRiskySystem and responseDict:
            responseDict['backToSingleOpening'] = True
            self.__showSpecialRewardFunc = partial(showLootBoxSpecialReward, responseDict, isGuaranteedReward=self.__isGuaranteedReward)
            self._startFade(self.__showSpecialRewardCallback, withPause=True)
        else:
            showLootBoxSpecialReward(responseDict, self.getParentWindow(), self.__isGuaranteedReward)

    def __showSpecialRewardCallback(self):
        if self.__showSpecialRewardFunc is not None:
            self.__showSpecialRewardFunc()
            self.__showSpecialRewardFunc = None
        self.destroyWindow()
        return

    def __onSpecialRewardsClosed(self, _=None):
        self.viewModel.setIsSpecialRewardClosed(True)

    def __onOpenNextBox(self, _=None):
        self.__showSpecialRewardFunc = None
        self.__isBackward = False
        with self.viewModel.transaction() as model:
            model.setIsForcedRendering(self.__isBackward)
            model.setIsReload(True)
        self.__openBox()
        self.viewModel.setIsReload(False)
        return

    @process
    def __openBox(self):
        result = yield LootBoxOpenProcessor(self.__boxItem).request()
        if not result:
            _logger.error('Failed to open lootbox. Missing result.')
            self.viewModel.setHardReset(True)
            return
        else:
            if result.userMsg:
                SystemMessages.pushI18nMessage(result.userMsg, type=result.sysMsgType)
            if not result.success:
                _logger.error('Failed to open lootbox. Failed result.')
                self.viewModel.setHardReset(True)
                return
            rewards = first(result.auxData['bonus'])
            if rewards is None:
                _logger.error('Failed to open lootbox. Missing rewards.')
                self.viewModel.setHardReset(True)
                return
            self.__rewards = rewards
            self.__isGuaranteedReward = 'usedLimits' in result.auxData['extData']
            self.__giftsInfo = result.auxData['giftsInfo']
            self.__updateBoxInfo()
            self.__updateRewards()
            g_eventBus.handleEvent(events.LootboxesEvent(events.LootboxesEvent.ON_OPEN_LOOTBOX, ctx={'boxItem': self.__boxItem,
             'specialRewardType': self.viewModel.getSpecialRewardType(),
             'withReload': True,
             'isForcedToEnd': False}), EVENT_BUS_SCOPE.LOBBY)
            return

    def __updateAvailability(self):
        if self.__boxItem is None:
            _logger.error('Failed to update lootbox availability. Missing lootbox item.')
            lootboxEnabled = buyBtnEnabled = False
        else:
            serverSettings = self.lobbyContext.getServerSettings()
            lootboxEnabled = serverSettings.isLootBoxesEnabled() and serverSettings.isLootBoxEnabled(self.__boxItem.getID())
            buyBtnEnabled = lootboxEnabled and self.__boxItem.getType() == NewYearLootBoxes.PREMIUM
        with self.getViewModel().transaction() as tx:
            tx.setIsNextBtnEnabled(lootboxEnabled)
            tx.setIsGiftBuyBtnVisible(buyBtnEnabled)
        return

    def __updateBoxInfo(self):
        isValidBox = isLootboxValid(self.__boxItem.getType())
        with self.viewModel.transaction() as tx:
            setGaranteedRewardData(tx.guaranteedReward, self.__boxItem)
            if isValidBox:
                tx.setLeftLootBoxes(self.__boxItem.getInventoryCount())
                tx.setBoxType(self.__boxItem.getType())
                tx.setBoxCategory(self.__boxItem.getCategory())
                tx.setIsFreeBox(self.__boxItem.isFree())
                self.__updateGiftInfoModel(tx)
            else:
                tx.setLeftLootBoxes(0)
                _logger.warning('Lootbox %r is missing on Server!', self.__boxItem)

    def __updateGiftInfoModel(self, model):
        showGiftInfo = bool(self.__giftsInfo) and not self.isGiftEventDisabled()
        model.setIsBoxFromFriend(showGiftInfo)
        if showGiftInfo:
            congratulationText = getGiftSystemCongratulationText(self.__giftsInfo[0].metaInfo.get('message_id', 0))
            model.friendGiftLootBoxInfo.setUserCongratulation(congratulationText)
            spaID = self.__giftsInfo[0].senderID
            self.__invalidateGiftSenderName(self.getUserName(spaID), self.getUserClanAbbrev(spaID), model=model)
            self.syncUsersInfo()

    @replaceNoneKwargsModel
    def __invalidateGiftSenderName(self, userName, clanAbbrev, model=None):
        clanAbbrev = getClanAbbrevString(clanAbbrev) if clanAbbrev else ''
        model.friendGiftLootBoxInfo.setUserClanAbbrev(clanAbbrev)
        model.friendGiftLootBoxInfo.setUserName(userName)

    def __updateRewards(self):
        with self.getViewModel().transaction() as tx:
            rewardsList = tx.getRewards()
            rewardsList.clear()
            bonuses, specialRewardType = getEpicFormattedLootboxBonuses(self.__rewards, AWARDS_MAX_COUNT)
            for index, reward in enumerate(bonuses):
                presenter = getLootboxRendererModelPresenter(reward)
                rewardRender = presenter.getModel(reward, index, showCongrats=True)
                rewardsList.addViewModel(rewardRender)
                self.__addTooltip(index, reward)

            rewardsList.invalidate()
            tx.setSyncInitiator((tx.getSyncInitiator() + 1) % 1000)
            tx.setSpecialRewardType(specialRewardType)
            tx.setIsSpecialRewardClosed(self.__isBackward)
        setOverlayHangarGeneral(True)

    def __onSettingsChanged(self, diff):
        if NewYearStorageKeys.LOOT_BOX_VIDEO_OFF in diff:
            isVideoOff = diff[NewYearStorageKeys.LOOT_BOX_VIDEO_OFF]
            self.viewModel.setIsVideoOff(isVideoOff)

    def __onCacheResync(self, *_):
        self.__updateBoxInfo()

    def __onServerSettingChanged(self, diff):
        if 'lootBoxes_config' in diff:
            self.__updateBoxInfo()
        self.__updateAvailability()

    def __onStateChange(self):
        if not self.festivityController.isEnabled():
            self.destroyWindow()

    def __addTooltip(self, tooltipId, reward):
        self.__tooltips[tooltipId] = TooltipData(tooltip=reward.get('tooltip'), isSpecial=reward.get('isSpecial', False), specialAlias=reward.get('specialAlias', ''), specialArgs=reward.get('specialArgs'))

    def __onBuyBoxBtnClick(self, _=None):
        event_dispatcher.showLootBoxBuyWindow(category=self.__boxItem.getCategory())

    def __onSpecialActionButtonClick(self, responseDict):
        congratsType = responseDict.get('congratsType')
        congratsSourceId = responseDict.get('congratsSourceId')
        hasError = False
        if congratsType == LootCongratsTypes.CONGRAT_TYPE_VEHICLE:
            self.__flowLogger.logVehicleShow()
            event_dispatcher.selectVehicleInHangar(int(congratsSourceId))
            fireCloseToHangar()
        elif congratsType == LootCongratsTypes.CONGRAT_TYPE_STYLE:
            self.__flowLogger.logStylePreview()
            showStyledVehicleByStyleCD(int(congratsSourceId))
        elif congratsType == LootCongratsTypes.CONGRAT_TYPE_TANKMAN:
            showRecruitWindow(congratsSourceId)
            fireCloseToHangar()
        else:
            hasError = True
            _logger.error('Wrong NY Lootbox CongratsType: %s', congratsType)
        if not hasError and self._isMemoryRiskySystem:
            self.destroyWindow()

    def __sendRemoveHideView(self):
        g_eventBus.handleEvent(events.LootboxesEvent(events.LootboxesEvent.REMOVE_HIDE_VIEW), EVENT_BUS_SCOPE.LOBBY)
        self._setIsCanClose(True)

    def __onVideoOffMovieLoaded(self, _=None):
        self.__sendRemoveHideView()

    @staticmethod
    def __onGuaranteedRewardsInfo(_=None):
        event_dispatcher.showLootBoxGuaranteedRewardsInfo()


class LootBoxRewardWrapperWindow(LobbyNotificationWindow):
    __slots__ = ()

    def __init__(self, lootBoxItem, rewards, parent=None, isBackward=False, lastStatisticsResetFailed=False, isGuaranteedReward=False, giftsInfo=None):
        super(LootBoxRewardWrapperWindow, self).__init__(wndFlags=WindowFlags.WINDOW | WindowFlags.WINDOW_FULLSCREEN, content=LootBoxRewardView(lootBoxItem, rewards, isBackward, lastStatisticsResetFailed, isGuaranteedReward, giftsInfo), parent=parent, layer=WindowLayer.TOP_WINDOW, isModal=False)
