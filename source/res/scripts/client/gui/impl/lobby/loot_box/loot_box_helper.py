# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/loot_box/loot_box_helper.py
import logging
import weakref
from collections import namedtuple
import typing
import BigWorld
import ScaleformFileLoader
from frameworks.wulf import ViewStatus
from new_year.ny_hangar_hide_manager import NewYearHangarHideManager
from shared_utils import findFirst
from gui import SystemMessages
from gui.Scaleform import SCALEFORM_SWF_PATH_V3
from gui.impl import backport
from gui.impl.auxiliary.rewards_helper import getRewardTooltipContent, LootVehicleVideoRewardPresenter, LootNewYearToyPresenter, LootNewYearFragmentsCompensationPresenter, getRewardRendererModelPresenter, DEF_COMPENSATION_PRESENTERS, LootTankmanCongratsRewardPresenter, LootStyleCongratsRewardPresenter
from gui.impl.auxiliary.rewards_helper import getVehByStyleCD
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.views.lootboxes.loot_box_guaranteed_reward_model import RewardState
from gui.impl.lobby.loot_box.loot_box_sounds import playSound, LootBoxViewEvents
from gui.impl.lobby.new_year.tooltips.ny_decoration_tooltip import NyDecorationTooltip
from gui.impl.lobby.new_year.tooltips.ny_guaranteed_reward_tooltip import NyGuaranteedRewardTooltip
from gui.impl.lobby.new_year.tooltips.ny_mega_decoration_tooltip import NyMegaDecorationTooltip
from gui.impl.pub import ViewImpl
from gui.shared import EVENT_BUS_SCOPE
from gui.shared import events
from gui.shared import g_eventBus
from gui.shared.event_dispatcher import showStylePreview
from gui.shared.events import GameEvent
from gui.shared.gui_items.loot_box import NewYearLootBoxes
from gui.shared.notifications import NotificationPriorityLevel
from helpers import dependency, isMemoryRiskySystem
from items.components.ny_constants import CurrentNYConstants
from realm import CURRENT_REALM
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.game_control import IFestivityController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from uilogging.ny.loggers import NyLootBoxesRewardPreviewFlowLogger
if typing.TYPE_CHECKING:
    from frameworks.wulf import View
MAX_PREMIUM_BOXES_TO_OPEN = 5
SpecialRewardData = namedtuple('SpecialRewardData', ('sourceName', 'congratsType', 'congratsSourceId', 'vehicleName', 'vehicleLvl', 'vehicleIsElite', 'vehicleType', 'backToSingleOpening', 'isGuaranteedReward'))
_MODEL_PRESENTERS = {'vehicles': LootVehicleVideoRewardPresenter(),
 'tmanToken': LootTankmanCongratsRewardPresenter(),
 'customizations': LootStyleCongratsRewardPresenter(),
 CurrentNYConstants.TOYS: LootNewYearToyPresenter(),
 CurrentNYConstants.TOY_FRAGMENTS: LootNewYearFragmentsCompensationPresenter()}
_logger = logging.getLogger(__name__)

def showRestrictedSysMessage():

    def _showRestrictedSysMessage():
        SystemMessages.pushMessage(text=backport.text(R.strings.lootboxes.restrictedMessage.body()), type=SystemMessages.SM_TYPE.ErrorHeader, priority=NotificationPriorityLevel.MEDIUM, messageData={'header': backport.text(R.strings.lootboxes.restrictedMessage.header())})

    BigWorld.callback(0.0, _showRestrictedSysMessage)


@dependency.replace_none_kwargs(itemsCache=IItemsCache, c11nService=ICustomizationService)
def showStyledVehicleByStyleCD(styleIntCD, isBackToMultiOpen=False, itemsCache=None, c11nService=None):
    NewYearHangarHideManager.instance().openStyle()
    _hideLootBoxWindows(isBackToMultiOpen)
    vehicle = getVehByStyleCD(styleIntCD)
    style = itemsCache.items.getItemByCD(styleIntCD)
    if vehicle.isInInventory and vehicle.isCustomizationEnabled():

        def _callback():
            c11nService.getCtx().previewStyle(style, _ExitCallback(isBackToMultiOpen))

        c11nService.showCustomization(vehicle.invID, _callback)
    else:

        def _backCallback():
            NyLootBoxesRewardPreviewFlowLogger().logStylePreviewBack()
            _showLootBoxWindows(isBackToMultiOpen)
            NewYearHangarHideManager.instance().closeStyle()

        def _exitCallback():
            NyLootBoxesRewardPreviewFlowLogger().logStylePreviewExit()
            _closeLootBoxWindows()
            NewYearHangarHideManager.instance().closeStyle()

        showStylePreview(vehCD=vehicle.intCD, style=style, styleDescr=style.getDescription(), backCallback=_backCallback, destoryCallback=_exitCallback, backBtnDescrLabel=backport.text(R.strings.vehicle_preview.header.backBtn.descrLabel.personalAwards()))


class LootBoxShowHideCloseHandler(object):
    __slots__ = ('__target', '__isHidden')

    def __init__(self):
        self.__target = None
        self.__isHidden = False
        return

    @property
    def isHidden(self):
        return self.__isHidden

    def startListen(self, target):
        self.__target = weakref.proxy(target)
        g_eventBus.addListener(GameEvent.HIDE_LOOT_BOX_WINDOWS, self.__onHideLBWindow)
        g_eventBus.addListener(GameEvent.SHOW_LOOT_BOX_WINDOWS, self.__onShowLBWindow)
        g_eventBus.addListener(GameEvent.CLOSE_LOOT_BOX_WINDOWS, self.__onCloseLBWindow)

    def stopListen(self):
        self.__target = None
        self.__isHidden = False
        g_eventBus.removeListener(GameEvent.HIDE_LOOT_BOX_WINDOWS, self.__onHideLBWindow)
        g_eventBus.removeListener(GameEvent.SHOW_LOOT_BOX_WINDOWS, self.__onShowLBWindow)
        g_eventBus.removeListener(GameEvent.CLOSE_LOOT_BOX_WINDOWS, self.__onCloseLBWindow)
        return

    def __onHideLBWindow(self, _=None):
        if self.__target:
            self.__isHidden = True
            self.__target.hide()

    def __onShowLBWindow(self, _=None):
        if self.__target:
            self.__isHidden = False
            self.__target.show()
            fireSpecialRewardsClosed()

    def __onCloseLBWindow(self, _=None):
        if self.__target:
            self.__isHidden = False
            self.__target.destroy()


class LootBoxHideableView(ViewImpl):
    __slots__ = ('_showHideCloseHandler', '_isMemoryRiskySystem', '_hideCompleteCallback', '_isCanClose', '_holdByViews', '__holdIDs', '__videoFiles', '__invokeFinalize')
    _VIDEOS = []

    def __init__(self, settings):
        self._isMemoryRiskySystem = isMemoryRiskySystem()
        self._isCanClose = not self._isMemoryRiskySystem
        lobbyViews = R.views.lobby
        self._holdByViews = (lobbyViews.new_year.views.NyLootBoxSpecialReward(),
         lobbyViews.loot_box.views.loot_box_entry_video_view.LootBoxEntryVideoView(),
         lobbyViews.new_year.LootBoxRewardViewGf(),
         lobbyViews.new_year.LootBoxPremiumMultiOpenView(),
         lobbyViews.loot_box.views.loot_box_opening_view.LootBoxOpeningView(),
         lobbyViews.new_year.AtmosphereLevelUp())
        self.__holdIDs = set()
        self.__videoFiles = self.__getVideoFiles()
        self.__invokeFinalize = False
        if self.__videoFiles:
            ScaleformFileLoader.enableStreaming(self.__videoFiles)
        super(LootBoxHideableView, self).__init__(settings)
        self._hideCompleteCallback = None
        self._showHideCloseHandler = LootBoxShowHideCloseHandler()
        if not NewYearHangarHideManager.isInited():
            NewYearHangarHideManager.instance()
        return

    def canBeClosed(self):
        return not self._showHideCloseHandler.isHidden

    def _initialize(self, *args, **kwargs):
        super(LootBoxHideableView, self)._initialize()
        self._showHideCloseHandler.startListen(self.getParentWindow())
        self.gui.windowsManager.onViewStatusChanged += self.__onViewStatusChanged

    def _finalize(self):
        self.gui.windowsManager.onViewStatusChanged -= self.__onViewStatusChanged
        if not self.__invokeFinalize and self.__videoFiles:
            ScaleformFileLoader.disableStreaming()
        if self._hideCompleteCallback is not None:
            self._hideCompleteCallback = None
        self._showHideCloseHandler.stopListen()
        self._showHideCloseHandler = None
        g_eventBus.removeListener(events.LootboxesEvent.HIDE_COMPLETE, self._onHideCompleteCallback, scope=EVENT_BUS_SCOPE.LOBBY)
        super(LootBoxHideableView, self)._finalize()
        return

    def _startFade(self, callback, withPause=True):
        if callback is not None:
            self._hideCompleteCallback = callback
        if self.__videoFiles:
            ScaleformFileLoader.disableStreaming()
            self.__invokeFinalize = True
        g_eventBus.addListener(events.LootboxesEvent.HIDE_COMPLETE, self._onHideCompleteCallback, scope=EVENT_BUS_SCOPE.LOBBY)
        showLootboxFadeWindow(withPause)
        return

    def _onHideCompleteCallback(self, _=None):
        g_eventBus.removeListener(events.LootboxesEvent.HIDE_COMPLETE, self._onHideCompleteCallback, scope=EVENT_BUS_SCOPE.LOBBY)
        if self._hideCompleteCallback is not None:
            try:
                self._hideCompleteCallback()
            except Exception:
                g_eventBus.handleEvent(events.LootboxesEvent(events.LootboxesEvent.REMOVE_HIDE_VIEW), EVENT_BUS_SCOPE.LOBBY)
                raise

            self._hideCompleteCallback = None
        return

    def _getVideosList(self):
        return []

    def _setIsCanClose(self, value):
        self._isCanClose = value

    def __onViewStatusChanged(self, uniqueID, newStatus):
        if self.viewStatus != ViewStatus.LOADED or not self._holdByViews:
            return
        else:
            view = self.gui.windowsManager.getView(uniqueID)
            if view is None or view.layoutID not in self._holdByViews or self.layoutID == view.layoutID:
                return
            if newStatus == ViewStatus.LOADED:
                self.__addHolder(view.uniqueID)
            elif newStatus == ViewStatus.DESTROYING:
                self.__removeHolder(view.uniqueID)
            return

    def __addHolder(self, holderId):
        if not self.__holdIDs:
            _logger.info('HOLD %r', self)
            self.setHold(True)
        self.__holdIDs.add(holderId)

    def __removeHolder(self, holderId):
        if holderId in self.__holdIDs:
            self.__holdIDs.remove(holderId)
            if not self.__holdIDs:
                _logger.info('UNHOLD %r', self)
                self.setHold(False)

    def __getVideoFiles(self):
        return [ '/videos/'.join((SCALEFORM_SWF_PATH_V3, videoName)) for videoName in self._getVideosList() ]


def showLootboxFadeWindow(withPause=True):
    from gui.impl.lobby.loot_box.loot_box_fade_view import LootBoxFadeWindow
    window = LootBoxFadeWindow(withPause)
    window.load()


def getLootboxRendererModelPresenter(reward):
    return getRewardRendererModelPresenter(reward, _MODEL_PRESENTERS, DEF_COMPENSATION_PRESENTERS)


@dependency.replace_none_kwargs(lobbyContext=ILobbyContext, itemsCache=IItemsCache)
def setGaranteedRewardData(guaranteedRewardModel, lootboxItem, isInFocus=True, enabledIfManyAttemptsLeft=False, lobbyContext=None, itemsCache=None):
    isEnabled = False
    hasLimits = False
    if lootboxItem is not None:
        isEnabled = lobbyContext.getServerSettings().isLootBoxEnabled(lootboxItem.getID())
        hasLimits = bool(lootboxItem.getGuaranteedFrequencyName())
    if isEnabled and hasLimits:
        guaranteedRewardModel.setRealm(CURRENT_REALM)
        guaranteedRewardModel.setIsPremiumType(lootboxItem.getType() == NewYearLootBoxes.PREMIUM)
        guaranteedRewardModel.setIsFocused(isInFocus)
        attemptsAfterReward = itemsCache.items.tokens.getAttemptsAfterGuaranteedRewards(lootboxItem)
        maxAttemptsToReward = lootboxItem.getGuaranteedFrequency() - attemptsAfterReward
        if enabledIfManyAttemptsLeft or maxAttemptsToReward <= 10:
            guaranteedRewardModel.setState(RewardState.NORMAL)
            guaranteedRewardModel.setMaxBoxesCount(maxAttemptsToReward)
        else:
            guaranteedRewardModel.setState(RewardState.DISABLED)
    else:
        guaranteedRewardModel.setState(RewardState.DISABLED)
    return


def showLootBoxSpecialMultiOpen(lootBoxItem, rewards, giftsInfo, openedCount=1):
    from gui.impl.lobby.new_year.gift_system.ny_gift_system_rewards_view import NyGiftSystemRewardsWindow, RewardsTypes
    window = NyGiftSystemRewardsWindow(RewardsTypes.GIFTS_OPENED, rewards, giftsInfo, lootBoxItem, openedCount)
    window.load()


def showLootBoxPremiumMultiOpen(lootBoxItem, rewards, boxesToOpen, parent=None, guaranteedReward=False):
    from gui.impl.lobby.loot_box.loot_box_premium_multi_open_view import LootBoxPremiumMultiOpenWindow
    window = LootBoxPremiumMultiOpenWindow(lootBoxItem, rewards, boxesToOpen, parent, guaranteedReward)
    window.load()


def showLootBoxMultiOpen(lootBoxItem, rewards, countToOpen, parent=None):
    from gui.impl.lobby.loot_box.loot_box_multi_open_view import LootBoxMultiOpenWindow
    window = LootBoxMultiOpenWindow(lootBoxItem, rewards, countToOpen, parent)
    window.load()


def showLootBoxReward(lootBoxItem, rewards, parent=None, isBackward=False, lastStatisticsResetFailed=False, guaranteedReward=False, giftsInfo=None):
    from gui.impl.lobby.loot_box.loot_box_opening_view import LootBoxOpeningWindow
    from gui.impl.lobby.loot_box.loot_box_reward_view import LootBoxRewardWrapperWindow
    rewardWindow = LootBoxRewardWrapperWindow(lootBoxItem, rewards, parent, isBackward, lastStatisticsResetFailed, guaranteedReward, giftsInfo)
    openingWindow = LootBoxOpeningWindow(parent=rewardWindow)
    rewardWindow.load()
    openingWindow.load()


def fireHideRewardView():
    g_eventBus.handleEvent(events.LootboxesEvent(events.LootboxesEvent.ON_REWARD_VIEW_CLOSED), EVENT_BUS_SCOPE.LOBBY)


def fireCloseToHangar():
    playSound(LootBoxViewEvents.ENTRY_VIEW_EXIT)
    _closeLootBoxWindows()


def fireHideMultiOpenView():
    g_eventBus.handleEvent(events.LootboxesEvent(events.LootboxesEvent.ON_MULTI_OPEN_VIEW_CLOSED), EVENT_BUS_SCOPE.LOBBY)


def fireSpecialRewardsClosed():
    g_eventBus.handleEvent(events.LootboxesEvent(events.LootboxesEvent.ON_SHOW_SPECIAL_REWARDS_CLOSED), EVENT_BUS_SCOPE.LOBBY)


def showLootBoxSpecialReward(responseDict, parent=None, isGuaranteedReward=False):
    from gui.impl.lobby.loot_box.loot_box_special_reward_view import LootBoxSpecialRewardWindow
    congratsType = responseDict.get('congratsType')
    congratsSourceId = responseDict.get('congratsSourceId')
    sourceName = responseDict.get('sourceName')
    if sourceName and congratsSourceId is not None and congratsType is not None:
        specialRewardData = SpecialRewardData(sourceName=sourceName, congratsType=congratsType, congratsSourceId=int(congratsSourceId), vehicleName=responseDict.get('vehicleName'), vehicleIsElite=responseDict.get('vehicleIsElite'), vehicleLvl=responseDict.get('vehicleLvl'), vehicleType=responseDict.get('vehicleType'), backToSingleOpening=responseDict.get('backToSingleOpening'), isGuaranteedReward=isGuaranteedReward)
        window = LootBoxSpecialRewardWindow(specialRewardData, parent)
        window.load()
    return


def showLootBoxSpecialReward2(specialRewardData, parent=None):
    from gui.impl.lobby.loot_box.loot_box_special_reward_view import LootBoxSpecialRewardWindow
    window = LootBoxSpecialRewardWindow(specialRewardData, parent)
    window.load()


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def isLootboxValid(boxType, itemsCache=None):
    return any((box.getType() == boxType for box in itemsCache.items.tokens.getLootBoxes().itervalues()))


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def getLootBoxByTypeAndCategory(boxType, boxCategory=None, isInInventory=False, itemsCache=None):
    boxes = itemsCache.items.tokens.getLootBoxes().values()
    for box in boxes:
        if box.getType() == boxType and (not isInInventory or box.getInventoryCount() > 0):
            isCommonBox = boxType == NewYearLootBoxes.COMMON
            if boxType == NewYearLootBoxes.PREMIUM and boxCategory == box.getCategory() or isCommonBox:
                return box

    return None


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def getLootboxStatisticsKey(lootboxID, itemsCache=None):
    lootboxItem = findFirst(lambda l: l.getID() == lootboxID, itemsCache.items.tokens.getLootBoxes().itervalues())
    return lootboxItem.getHistoryName() or lootboxID if lootboxItem is not None else None


def getTooltipContent(event, storedTooltipData):
    tooltipContent = getRewardTooltipContent(event, storedTooltipData)
    if tooltipContent is not None:
        return tooltipContent
    tooltipContentRes = R.views.lobby.new_year.tooltips
    if event.contentID == tooltipContentRes.NyDecorationTooltip():
        toyID = event.getArgument('toyID')
        return NyDecorationTooltip(toyID, isToyIconEnabled=False, isPureToy=True)
    elif event.contentID == tooltipContentRes.NyMegaDecorationTooltip():
        toyID = event.getArgument('toyID')
        return NyMegaDecorationTooltip(toyID, isToyIconEnabled=False, isPureToy=True)
    else:
        return NyGuaranteedRewardTooltip() if event.contentID == R.views.lobby.new_year.tooltips.NyGuaranteedRewardTooltip() else None


class _ExitCallback(object):
    _c11nService = dependency.descriptor(ICustomizationService)

    def __init__(self, isBackToMultiOpen=False):
        self.__wasCalled = False
        self.__isBackToMultiOpen = isBackToMultiOpen

    def apply(self):
        if not self.__wasCalled:
            _showLootBoxWindows(self.__isBackToMultiOpen)
            self.__wasCalled = True

    def close(self):
        if not self.__wasCalled:
            self._c11nService.getCtx().events.onCloseWindow(force=True)
            _showLootBoxWindows(self.__isBackToMultiOpen)
            self.__wasCalled = True

    def destroy(self):
        NyLootBoxesRewardPreviewFlowLogger().logStylePreviewExit()
        if not self.__wasCalled:
            _closeLootBoxWindows()
            self.__wasCalled = True


@dependency.replace_none_kwargs(festivityController=IFestivityController)
def _showLootBoxWindows(isBackToMultiOpen=False, festivityController=None):
    if not festivityController.isEnabled():
        return
    else:
        isRiskySystem = isMemoryRiskySystem()
        if isRiskySystem and not isBackToMultiOpen:
            showLootboxFadeWindow()
            showLootBoxReward(lootBoxItem=None, rewards=None, parent=None, isBackward=True)
        else:
            if not isRiskySystem:
                playSound(LootBoxViewEvents.ENTRY_VIEW_ENTER)
            g_eventBus.handleEvent(GameEvent(GameEvent.SHOW_LOOT_BOX_WINDOWS))
        return


def _hideLootBoxWindows(isBackToMultiOpen=False):
    isRiskySystem = isMemoryRiskySystem()
    if isRiskySystem and not isBackToMultiOpen:
        return
    if not isRiskySystem:
        playSound(LootBoxViewEvents.ENTRY_VIEW_EXIT)
    g_eventBus.handleEvent(GameEvent(GameEvent.HIDE_LOOT_BOX_WINDOWS))


def _closeLootBoxWindows():
    g_eventBus.handleEvent(GameEvent(GameEvent.CLOSE_LOOT_BOX_WINDOWS))
